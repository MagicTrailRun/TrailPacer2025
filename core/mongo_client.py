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
        "integrations": {},
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


# 🔍 Lister les intégrations connectées sous forme de dict
def list_integrations(internal_id):
    user = collection.find_one(
        {"internal_id": internal_id},
        {"integrations": 1, "_id": 0}
    )

    # Par défaut, tout est False
    integrations_status = {"strava": False, "garmin": False}

    if not user or "integrations" not in user:
        return integrations_status

    # On met à True si l’intégration est présente
    for key in integrations_status.keys():
        if key in user["integrations"] and user["integrations"][key]:
            integrations_status[key] = True

    return integrations_status



def delete_integration(internal_id, platform):
    """
    Supprime entièrement l'intégration d'une plateforme (strava/garmin) pour un utilisateur.

    Args:
        internal_id (str): ID interne de l'utilisateur
        platform (str): "strava" ou "garmin"

    Returns:
        bool: True si suppression effectuée, False sinon
    """
    result = db["users"].update_one(
        {"internal_id": internal_id, f"integrations.{platform}": {"$exists": True}},
        {
            "$unset": {f"integrations.{platform}": ""},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    return result.modified_count > 0


def get_access_token(internal_id, platform):
    """
    Récupère l'access token pour une plateforme donnée pour un utilisateur donné.

    Args:
        internal_id (str): ID interne de l'utilisateur.
        platform (str): Nom de la plateforme ("strava", "garmin", ...)

    Returns:
        str | None: access_token si trouvé, None sinon.
    """
    user = db["users"].find_one(
        {"internal_id": internal_id},
        {"integrations." + platform: 1, "_id": 0}
    )
    if user and "integrations" in user and platform in user["integrations"]:
        return user["integrations"][platform].get("access_token")
    return None


