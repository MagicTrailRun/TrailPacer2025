from pymongo import MongoClient
import os
from datetime import datetime, timezone

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = "Magic_Trail"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def create_user_profile(user_id, email, name=None):
    users = db["users"]
    now = datetime.now(timezone.utc)
    profile = {
        "internal_id": user_id,
        "mail": email,
        "name": name,
        "created_at": now,
        "updated_at": now,
    }
    users.insert_one(profile)

