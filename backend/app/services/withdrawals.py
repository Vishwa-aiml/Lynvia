import uuid
from datetime import datetime, timezone
from typing import List, Tuple
from fastapi import HTTPException, status
from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional

from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut, WalletOut, WithdrawalStatus
from app.schemas.payment import EarningStatus
from app.core.config import settings


def get_wallet_balance(db: FirestoreClient, designer_id: str) -> WalletOut:
    earnings = db.collection("designerEarnings").where("designerId", "==", designer_id).stream()
    pending = 0
    available = 0
    processing = 0
    withdrawn = 0

    for doc in earnings:
        data = doc.to_dict()
        net = data.get("netAmount", 0)
        st = data.get("status")
        
        if st == EarningStatus.PENDING.value:
            pending += net
        elif st == EarningStatus.AVAILABLE.value:
            available += net
        elif st == "WITHDRAWAL_PROCESSING": # Internal status used during withdrawal
            processing += net
        elif st == EarningStatus.WITHDRAWN.value:
            withdrawn += net

    return WalletOut(
        pendingBalance=pending,
        availableBalance=available,
        processingBalance=processing,
        withdrawnBalance=withdrawn,
        currency="INR"
    )


def request_withdrawal(db: FirestoreClient, user_id: str, designer_profile_id: str, req: WithdrawalCreate) -> WithdrawalOut:
    if req.amount < settings.MINIMUM_WITHDRAWAL_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Minimum withdrawal amount is {settings.MINIMUM_WITHDRAWAL_AMOUNT} paise"
        )

    # Check balance
    wallet = get_wallet_balance(db, designer_profile_id)
    if wallet.availableBalance < req.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient available balance")
        
    withdrawal_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    data = {
        "id": withdrawal_id,
        "designerProfileId": designer_profile_id,
        "userId": user_id,
        "amount": req.amount,
        "currency": "INR",
        "status": WithdrawalStatus.REQUESTED.value,
        "payoutReference": None,
        "failureReason": None,
        "idempotencyKey": req.idempotencyKey,
        "requestedAt": now,
        "processingAt": None,
        "completedAt": None,
        "failedAt": None,
        "createdAt": now,
        "updatedAt": now
    }
    
    db.collection("withdrawals").document(withdrawal_id).set(data)
    return WithdrawalOut(**data)


@transactional
def _process_withdrawal_transaction(transaction: Transaction, db: FirestoreClient, withdrawal_id: str, payout_ref: str) -> WithdrawalOut:
    withdrawal_ref = db.collection("withdrawals").document(withdrawal_id)
    doc = withdrawal_ref.get(transaction=transaction)
    
    if not doc.exists:
        raise ValueError("Withdrawal not found")
        
    data = doc.to_dict()
    if data["status"] != WithdrawalStatus.REQUESTED.value:
        raise ValueError("Only REQUESTED withdrawals can be processed")
        
    designer_id = data["designerProfileId"]
    amount_to_reserve = data["amount"]
    
    # Get available earnings
    earnings_query = db.collection("designerEarnings").where("designerId", "==", designer_id).where("status", "==", EarningStatus.AVAILABLE.value).get(transaction=transaction)
    
    available_sum = 0
    earnings_to_update = []
    
    for e in earnings_query:
        if available_sum >= amount_to_reserve:
            break
        edata = e.to_dict()
        available_sum += edata["netAmount"]
        earnings_to_update.append(e.reference)
        
    if available_sum < amount_to_reserve:
        raise ValueError("Insufficient available balance during processing")
        
    now = datetime.now(timezone.utc)
    
    # Update earnings to PROCESSING
    for ref in earnings_to_update:
        transaction.update(ref, {"status": "WITHDRAWAL_PROCESSING", "withdrawalId": withdrawal_id, "updatedAt": now})
        
    # Update withdrawal
    updated = {
        "status": WithdrawalStatus.PROCESSING.value,
        "payoutReference": payout_ref,
        "processingAt": now,
        "updatedAt": now
    }
    transaction.update(withdrawal_ref, updated)
    data.update(updated)
    
    return WithdrawalOut(**data)
    
def process_withdrawal(db: FirestoreClient, withdrawal_id: str, payout_ref: str) -> WithdrawalOut:
    transaction = db.transaction()
    return _process_withdrawal_transaction(transaction, db, withdrawal_id, payout_ref)


@transactional
def _complete_withdrawal_transaction(transaction: Transaction, db: FirestoreClient, withdrawal_id: str, payout_ref: str) -> WithdrawalOut:
    withdrawal_ref = db.collection("withdrawals").document(withdrawal_id)
    doc = withdrawal_ref.get(transaction=transaction)
    
    if not doc.exists:
        raise ValueError("Withdrawal not found")
        
    data = doc.to_dict()
    if data["status"] != WithdrawalStatus.PROCESSING.value:
        raise ValueError("Only PROCESSING withdrawals can be completed")
        
    # Get processing earnings
    earnings_query = db.collection("designerEarnings").where("withdrawalId", "==", withdrawal_id).where("status", "==", "WITHDRAWAL_PROCESSING").get(transaction=transaction)
    
    now = datetime.now(timezone.utc)
    
    for e in earnings_query:
        transaction.update(e.reference, {"status": EarningStatus.WITHDRAWN.value, "updatedAt": now})
        
    updated = {
        "status": WithdrawalStatus.COMPLETED.value,
        "payoutReference": payout_ref,
        "completedAt": now,
        "updatedAt": now
    }
    transaction.update(withdrawal_ref, updated)
    data.update(updated)
    
    return WithdrawalOut(**data)

def complete_withdrawal(db: FirestoreClient, withdrawal_id: str, payout_ref: str) -> WithdrawalOut:
    transaction = db.transaction()
    return _complete_withdrawal_transaction(transaction, db, withdrawal_id, payout_ref)


@transactional
def _fail_withdrawal_transaction(transaction: Transaction, db: FirestoreClient, withdrawal_id: str, reason: str) -> WithdrawalOut:
    withdrawal_ref = db.collection("withdrawals").document(withdrawal_id)
    doc = withdrawal_ref.get(transaction=transaction)
    
    if not doc.exists:
        raise ValueError("Withdrawal not found")
        
    data = doc.to_dict()
    if data["status"] not in [WithdrawalStatus.REQUESTED.value, WithdrawalStatus.PROCESSING.value]:
        raise ValueError("Cannot fail a withdrawal in this state")
        
    now = datetime.now(timezone.utc)
        
    if data["status"] == WithdrawalStatus.PROCESSING.value:
        # Revert earnings
        earnings_query = db.collection("designerEarnings").where("withdrawalId", "==", withdrawal_id).where("status", "==", "WITHDRAWAL_PROCESSING").get(transaction=transaction)
        for e in earnings_query:
            transaction.update(e.reference, {"status": EarningStatus.AVAILABLE.value, "withdrawalId": None, "updatedAt": now})
            
    updated = {
        "status": WithdrawalStatus.FAILED.value,
        "failureReason": reason,
        "failedAt": now,
        "updatedAt": now
    }
    transaction.update(withdrawal_ref, updated)
    data.update(updated)
    
    return WithdrawalOut(**data)
    
def fail_withdrawal(db: FirestoreClient, withdrawal_id: str, reason: str) -> WithdrawalOut:
    transaction = db.transaction()
    return _fail_withdrawal_transaction(transaction, db, withdrawal_id, reason)
