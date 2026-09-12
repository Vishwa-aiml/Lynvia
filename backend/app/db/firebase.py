import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# Path to the service account JSON key provided by the user
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lynvia-58164-firebase-adminsdk-fbsvc-fd7e92ca4f.json")

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error initializing Firebase: {e}")

# Export Firestore DB client
db = firestore.client()

def get_db():
    """Dependency to inject Firestore client into routes."""
    yield db
