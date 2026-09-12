"""
Razorpay Payout provider abstraction.

In prototype mode this is a STUB — Razorpay X Payouts requires verified
fund accounts (KYC). The abstraction is kept clean so that real
implementation can replace the stub without touching business logic.

The service layer (withdrawals.py) calls only:
    initiate_payout(amount, currency, notes) -> dict
"""
import uuid
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def initiate_payout(amount: int, currency: str, notes: dict = None) -> dict:
    """
    Initiate a payout to the designer.

    Args:
        amount: payout amount in minor units (paise)
        currency: currency code ("INR")
        notes: optional metadata dict

    Returns:
        dict with keys:
            reference (str): provider payout ID / mock reference
            status (str): "created" | "processing" | "failed"
    """
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        # Prototype mode: return a mock reference
        mock_ref = f"mock_payout_{uuid.uuid4().hex[:16]}"
        logger.info(
            "PROTOTYPE MODE: Returning mock payout reference=%s amount=%d %s",
            mock_ref, amount, currency,
        )
        return {"reference": mock_ref, "status": "created"}

    # Real Razorpay X Payout implementation would go here.
    # Requires a verified fund_account_id from designer KYC.
    # Example:
    #   client = get_razorpay_client()
    #   payout = client.payout.create({
    #       "account_number": settings.RAZORPAY_FUND_ACCOUNT,
    #       "fund_account_id": fund_account_id,
    #       "amount": amount,
    #       "currency": currency,
    #       "mode": "IMPS",
    #       "purpose": "payout",
    #       "notes": notes or {},
    #   })
    #   return {"reference": payout["id"], "status": payout["status"]}
    raise NotImplementedError(
        "Real Razorpay payout requires a verified fund account. "
        "Set up Razorpay X and implement fund_account_id flow."
    )
