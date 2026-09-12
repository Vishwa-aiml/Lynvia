import razorpay
from app.core.config import settings

def get_razorpay_client() -> razorpay.Client:
    """Returns a configured Razorpay client instance."""
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    return client
