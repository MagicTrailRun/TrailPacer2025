import streamlit as st
import requests
import os
from core.mongo_client import save_integration

# ---------- STRAVA ----------
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "170263")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "6abf41a2581b5d14d88811d1496d593ca36f55e4")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8501")

def connect_strava():
    # Lien d'autorisation Strava
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={STRAVA_REDIRECT_URI}"
        "&scope=read,profile:read_all,activity:read_all"
        "&approval_prompt=force"
    )
    st.markdown(f"[🔗 Connecter mon compte Strava]({auth_url})")

    # Gestion du callback : si le paramètre "code" est dans l'URL
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        # Échange code contre tokens
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
            internal_id=st.session_state['user']['id'],
            service="strava",
            external_id=str(athlete["id"]),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_at=tokens["expires_at"]
        )
        st.success("✅ Compte Strava connecté et sauvegardé !")

# ---------- GARMIN ----------
GARMIN_CLIENT_ID = os.getenv("GARMIN_CLIENT_ID", "77baf226-a45b-4304-b705-a8fda39a7c53")
GARMIN_CLIENT_SECRET = os.getenv("GARMIN_CLIENT_SECRET", "IPW4Jew8lxWIL957SA5SSVX8aFm6GrMP/ghFP0IkD6M")
GARMIN_REDIRECT_URI = os.getenv("GARMIN_REDIRECT_URI", "http://localhost:8501/callback")
GARMIN_AUTH_URL = "https://connect.garmin.com/oauth2Confirm"
GARMIN_TOKEN_URL = "https://diauth.garmin.com/di-oauth2-service/oauth/token"

import secrets, string, hashlib, base64
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
    )
    st.markdown(f"[🔗 Connecter mon compte Garmin]({auth_url})")

    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
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
        access_token = tokens["access_token"]
        # Récupération userId Garmin
        user_response = requests.get(
            "https://apis.garmin.com/wellness-api/rest/user/id",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_response.status_code != 200:
            st.error("❌ Impossible de récupérer le userId Garmin")
            return
        user_id_garmin = user_response.json()["userId"]
        # Sauvegarde dans MongoDB
        save_integration(
            internal_id=st.session_state['user']['id'],
            service="garmin",
            external_id=user_id_garmin,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_at=tokens.get("expires_in")  # ou timestamp calculé
        )
        st.success("✅ Compte Garmin connecté et sauvegardé !")
