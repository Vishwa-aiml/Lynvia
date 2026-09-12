import razorpay
from app.core.config import settings
from .client import get_razorpay_client

def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verifies the Razorpay webhook signature.
    """
    client = get_razorpay_client()
    try:
        client.utility.verify_webhook_signature(
            body.decode("utf-8"),
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
