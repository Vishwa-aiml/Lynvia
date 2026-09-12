import razorpay
import hmac
import hashlib
from app.core.config import settings
from .client import get_razorpay_client

def create_order(amount: int, currency: str, receipt: str, notes: dict = None) -> dict:
    """
    Creates a Razorpay order.
    Amount should be in minor units (e.g. paise).
    """
    client = get_razorpay_client()
    data = {
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "notes": notes or {}
    }
    order = client.order.create(data=data)
    return order


def verify_payment_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    """
    Verifies the payment signature returned by the client-side checkout.
    """
    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
