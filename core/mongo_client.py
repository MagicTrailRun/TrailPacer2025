import os
from datetime import datetime, timezone
import requests
from core.supabase_client import supabase

BACKEND_GARMIN_DEREGISTRATION_URL = os.getenv("BACKEND_GARMIN_DEREGISTRATION_URL")
BACKEND_STRAVA_DEREGISTRATION_URL = os.getenv("BACKEND_STRAVA_DEREGISTRATION_URL")
BACKEND_STRAVA_IS_LINKED_URL = os.getenv("BACKEND_STRAVA_IS_LINKED_URL")
BACKEND_GARMIN_IS_LINKED_URL = os.getenv("BACKEND_GARMIN_IS_LINKED_URL")


# 💾 Crée un profil utilisateur
def create_user_profile(internal_id, email, name=None):
    """
    Crée un profil utilisateur avec les champs :
    - internal_id, mail, name
    - integrations.strava et integrations.garmin initialisés à None
    - created_at, updated_at
    """
    now = datetime.now(timezone.utc)

    supabase.table("users").upsert({
        "internal_id": internal_id,
        "email": email,
        "first name": name,
        "created_at": now,
        "updated_at": now
    }).execute()


# 💾 Ajoute ou met à jour les tokens d'une intégration
def save_integration(internal_id, platform, tokens):
    """
    internal_id: ID interne de l'utilisateur
    platform: "strava" ou "garmin"
    tokens: dictionnaire contenant au minimum :
        external_id, access_token, refresh_token, expires_at
    """
    now = datetime.now(timezone.utc)
    data = {
        "internal_id": internal_id,
        "platform": platform,
        "external_id": tokens.get("external_id"),
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_at": tokens.get("expires_at"),
        "connected_at": now
    }

    response = supabase.table("integrations").upsert(
        data,
        on_conflict="internal_id,platform"
    ).execute()
    return bool(response.data)


# 🔍 Lister les intégrations connectées sous forme de dict
def list_integrations(internal_id):
    response = supabase.table("integrations") \
        .select("platform") \
        .eq("internal_id", internal_id) \
        .execute()

    # Par défaut, tout est False
    integrations_status = {"strava": False, "garmin": False}

    if not response.data:
        return integrations_status

    for row in response.data:
        platform = row.get("platform")
        if platform in integrations_status:
            integrations_status[platform] = True
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
    response = supabase.table("integrations") \
        .delete() \
        .eq("internal_id", internal_id) \
        .eq("platform", platform) \
        .execute()
    return len(response.data) > 0


def get_access_token(internal_id, platform):
    """
    Récupère l'access token pour une plateforme donnée pour un utilisateur donné.

    Args:
        internal_id (str): ID interne de l'utilisateur.
        platform (str): Nom de la plateforme ("strava", "garmin", ...)

    Returns:
        str | None: access_token si trouvé, None sinon.
    """
    response = supabase.table("integrations") \
        .select("access_token, external_id") \
        .eq("internal_id", internal_id) \
        .eq("platform", platform) \
        .single() \
        .execute()

    if response.data:
        return (
            response.data["access_token"],
            response.data["external_id"]
        )

    return None



def send_deregistration_garmin(user_id: str,
                        url: str = BACKEND_GARMIN_DEREGISTRATION_URL,
                        headers: dict | None = None,
                        timeout: float = 10.0) -> requests.Response:
    """
    Envoie un webhook 'deregistration' minimal au backend.

    Args:
        user_id: userId Garmin à inclure dans le payload.
        url: URL complète de l'endpoint backend.
        headers: headers supplémentaires (ex: {"Authorization": "Bearer ..."}). Si None, Content-Type est géré automatiquement par requests.
        timeout: timeout en secondes pour la requête HTTP.

    Returns:
        requests.Response: réponse HTTP du backend.
    """
    payload = {
        "deregistrations": [
            {"userId": user_id}
        ]
    }

    # use requests.json param to set Content-Type and serialize
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    return resp


def send_deregistration_strava(user_id: str,
                        url: str = BACKEND_STRAVA_DEREGISTRATION_URL,
                        headers: dict | None = None,
                        timeout: float = 10.0) -> requests.Response:
    """
    Envoie un webhook 'deregistration' minimal au backend.

    Args:
        user_id: userId strava à inclure dans le payload.
        url: URL complète de l'endpoint backend.
        headers: headers supplémentaires (ex: {"Authorization": "Bearer ..."}). Si None, Content-Type est géré automatiquement par requests.
        timeout: timeout en secondes pour la requête HTTP.

    Returns:
        requests.Response: réponse HTTP du backend.
    """
    payload = {"owner_id": user_id, "object_id" : user_id, "object_type": "athlete", "aspect_type": "delete" }

    # use requests.json param to set Content-Type and serialize
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    return resp



def send_connection_webhook(user_id: str,
                        access_token: str,
                        device : str,
                        headers: dict | None = None,
                        timeout: float = 10.0) -> requests.Response:
    """
    Envoie un webhook 'connexion' minimal au backend.

    Args:
        user_id: userId du device à inclure dans le payload.
        url: URL complète de l'endpoint backend.
        headers: headers supplémentaires (ex: {"Authorization": "Bearer ..."}). Si None, Content-Type est géré automatiquement par requests.
        timeout: timeout en secondes pour la requête HTTP.

    Returns:
        requests.Response: réponse HTTP du backend.
    """

    if device == "strava":
        url = BACKEND_STRAVA_IS_LINKED_URL

    if device == "garmin":
        url = BACKEND_GARMIN_IS_LINKED_URL


    
    payload = {"userId": user_id, "access_token": access_token}

    # use requests.json param to set Content-Type and serialize
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    return resp
