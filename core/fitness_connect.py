import streamlit as st
import requests
import os
import secrets, string, hashlib, base64
from datetime import datetime, timezone
from core.mongo_client import save_integration


# ==========================
# 🔧 Helpers génériques
# ==========================
def _get_query_params():
    """Compatibilité entre les versions de Streamlit."""
    if hasattr(st, "query_params"):
        return st.query_params
    else:
        return st.experimental_get_query_params()

def _get_single_param(qparams, key):
    """Normalise la valeur d'un param (string unique)."""
    if not qparams or key not in qparams:
        return None
    val = qparams[key]
    if isinstance(val, list):
        return val[0] if len(val) > 0 else None
    return val

def _clear_query_params():
    """Efface les query params pour éviter les relances du flow OAuth."""
    try:
        if hasattr(st, "query_params"):
            st.query_params.clear()
        else:
            st.experimental_set_query_params()
    except Exception:
        pass


# ==========================
# ---------- STRAVA ----------
# ==========================
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "170263")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "6abf41a2581b5d14d88811d1496d593ca36f55e4")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "https://magictrailrun-trailpacer2025-app-featauthentification-nkgwld.streamlit.app/")
STRAVA_DEAUTHORIZE_URL = "https://www.strava.com/oauth/deauthorize"


def connect_strava():
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={STRAVA_REDIRECT_URI}"
        "&scope=read,profile:read_all,activity:read_all"
        "&approval_prompt=force"
        f"&state=strava"
    )

    return auth_url


def handle_strava_callback():

    qparams = _get_query_params()
    if qparams.get("state")!="strava":
        return
    code = _get_single_param(qparams, "code")

    if not code:
        return

    if code:
        # Échange du code contre des tokens
        token_response = requests.post("https://www.strava.com/oauth/token", data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        })
        if token_response.status_code != 200:
            st.error("❌ Impossible d'obtenir le token Strava")
            return
        tokens = token_response.json()

        # Récupération des infos utilisateur
        athlete_response = requests.get(
            "https://www.strava.com/api/v3/athlete",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        if athlete_response.status_code != 200:
            st.error("❌ Impossible de récupérer les infos de l'athlète Strava")
            return
        athlete = athlete_response.json()

        # Sauvegarde dans MongoDB
        save_integration(
            internal_id=st.session_state['user'].id,
            platform="strava",
            tokens={
                "external_id": str(athlete["id"]),
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_at": tokens["expires_at"]
            }
        )
        st.success("✅ Compte Strava connecté et sauvegardé !")

        # Nettoyage de l’URL
        _clear_query_params()




def revoke_strava_token(access_token: str) -> bool:
    """
    Révoque le token Strava (déconnexion côté Strava).

    Args:
        access_token (str): Access token Strava (obligatoire).

    Returns:
        bool: True si succès, False sinon.
    """
    try:
        response = requests.post(
            STRAVA_DEAUTHORIZE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.status_code == 200

    except Exception:
        return False



# ==========================
# ---------- GARMIN ----------
# ==========================
GARMIN_CLIENT_ID = os.getenv("GARMIN_CLIENT_ID", "77baf226-a45b-4304-b705-a8fda39a7c53")
GARMIN_CLIENT_SECRET = os.getenv("GARMIN_CLIENT_SECRET", "IPW4Jew8lxWIL957SA5SSVX8aFm6GrMP/ghFP0IkD6M")
GARMIN_REDIRECT_URI = os.getenv("GARMIN_REDIRECT_URI", "https://magictrailrun-trailpacer2025-app-featauthentification-nkgwld.streamlit.app/")
GARMIN_AUTH_URL = "https://connect.garmin.com/oauth2Confirm"
GARMIN_TOKEN_URL = "https://diauth.garmin.com/di-oauth2-service/oauth/token"
GARMIN_DEAUTHORIZE_URL = "https://apis.garmin.com/wellness-api/rest/user/registration"

def generate_code_verifier(length: int = 64) -> str:
    allowed = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(allowed) for _ in range(length))

def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

CODE_VERIFIER = generate_code_verifier()
CODE_CHALLENGE = generate_code_challenge(CODE_VERIFIER)

def connect_garmin():
    auth_url = (
        f"{GARMIN_AUTH_URL}"
        f"?client_id={GARMIN_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={GARMIN_REDIRECT_URI}"
        f"&code_challenge={CODE_CHALLENGE}"
        "&code_challenge_method=S256"
        f"&state=garmin"
    )
    return auth_url

def handle_garmin_callback():

    qparams = _get_query_params()
    if qparams.get("state")!="garmin":
        return
    code = _get_single_param(qparams, "code")

    if code:
        token_response = requests.post(GARMIN_TOKEN_URL, data={
            "client_id": GARMIN_CLIENT_ID,
            "client_secret": GARMIN_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": GARMIN_REDIRECT_URI,
            "code_verifier": CODE_VERIFIER
        })
        if token_response.status_code != 200:
            st.error("❌ Impossible d'obtenir le token Garmin")
            return
        tokens = token_response.json()

        access_token = tokens.get("access_token")
        if not access_token:
            st.error("❌ Pas de token d'accès reçu de Garmin")
            return

        # Récupération du userId Garmin
        user_response = requests.get(
            "https://apis.garmin.com/wellness-api/rest/user/id",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_response.status_code != 200:
            st.error("❌ Impossible de récupérer le userId Garmin")
            return
        user_id_garmin = user_response.json().get("userId")

        # Sauvegarde dans MongoDB
        save_integration(
            internal_id=st.session_state['user'].id,
            platform="garmin",
            tokens={
                "external_id": user_id_garmin,
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_at": tokens.get("expires_in"),
            }
        )
        st.success("✅ Compte Garmin connecté et sauvegardé !")

        # Nettoyage de l’URL
        _clear_query_params()



def revoke_garmin_token(access_token: str) -> bool:
    """
    Révoque l'accès Garmin côté Garmin (déconnexion complète).

    Args:
        access_token (str): Access token Garmin.

    Returns:
        bool: True si succès, False sinon.
    """
    try:
        response = requests.delete(
            GARMIN_DEAUTHORIZE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.status_code == 200
    except Exception:
        return False
