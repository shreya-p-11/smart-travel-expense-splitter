from config.firebase_config import get_db

db = get_db()
print("Firestore client:", db)
