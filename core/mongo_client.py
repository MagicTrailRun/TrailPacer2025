from pymongo import MongoClient
import os
from datetime import datetime, timezone

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = "Magic_Trail"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["users"]

# 💾 Crée un profil utilisateur
def create_user_profile(internal_id, email, name=None):
    """
    Crée un profil utilisateur avec les champs :
    - internal_id, mail, name
    - integrations.strava et integrations.garmin initialisés à None
    - created_at, updated_at
    """
    now = datetime.now(timezone.utc)
    profile = {
        "internal_id": internal_id,
        "mail": email,
        "name": name,
        "integrations": {
            "strava": None,
            "garmin": None
        },
        "created_at": now,
        "updated_at": now
    }
    collection.insert_one(profile)


# 💾 Ajoute ou met à jour les tokens d'une intégration
def save_integration(internal_id, platform, tokens):
    """
    internal_id: ID interne de l'utilisateur
    platform: "strava" ou "garmin"
    tokens: dictionnaire contenant au minimum :
        external_id, access_token, refresh_token, expires_at
    """
    now = datetime.now(timezone.utc)
    update_path = f"integrations.{platform}"
    update = {
        f"{update_path}.external_id": tokens.get("external_id"),
        f"{update_path}.access_token": tokens.get("access_token"),
        f"{update_path}.refresh_token": tokens.get("refresh_token"),
        f"{update_path}.expires_at": tokens.get("expires_at"),
        f"{update_path}.connected_at": now,
        "updated_at": now
    }

    result = collection.update_one(
        {"internal_id": internal_id},
        {"$set": update, "$setOnInsert": {"created_at": now}},
        upsert=True
    )
    return result.modified_count > 0
