import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

_db = None

def get_db():
    global _db
    if _db:
        return _db

    try:
        # Render / production (env variable)
        if "FIREBASE_SERVICE_ACCOUNT" in os.environ:
            cred_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Local fallback (optional)
            cred = credentials.Certificate("config/serviceAccountKey.json")

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        _db = firestore.client()
        return _db

    except Exception as e:
        raise RuntimeError(f"Firebase init failed: {e}")
