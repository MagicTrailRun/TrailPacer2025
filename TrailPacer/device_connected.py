
import streamlit as st
from core.mongo_client import list_integrations, delete_integration, get_access_token
from core.fitness_connect import revoke_strava_token, revoke_garmin_token


def device_connected():
    st.header("Mes appareils connectés")

    internal_id = st.session_state['user'].id  # ID interne de l'utilisateur
    integrations = list_integrations(internal_id)  # Utilise ta fonction qui retourne {"strava": True/False, "garmin": True/False}

    # --- Strava ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("TrailPacer/image/strava_logo.png", width=80)
    with col2:
        if integrations.get("strava", False):
            if st.button("Désapparier Strava"):
                # Récupération du token
                token = get_access_token(internal_id, "strava")
                if token:
                    revoke_strava_token(token)  # Révocation côté Strava
                delete_integration(internal_id, "strava")  # Suppression en base
                st.success("Strava désapparié")
                st.rerun()

    # --- Garmin ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("TrailPacer/image/garmin_logo.png", width=80)
    with col2:
        if integrations.get("garmin", False):
            if st.button("Désapparier Garmin"):
                token = get_access_token(internal_id, "garmin")
                if token:
                    revoke_garmin_token(token)  # Révocation côté Garmin
                delete_integration(internal_id, "garmin")
                st.success("Garmin désapparié")
                st.rerun()
