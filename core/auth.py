# core/auth.py
import streamlit as st
from typing import Optional
from core.session import SessionManager
from core.supabase_client import get_supabase_client
from core.mongo_client import create_user_profile, list_integrations, db
from core.fitness_connect import connect_strava, connect_garmin

def supabase_login():
    """Authentifie et restaure automatiquement la session utilisateur."""
    supabase = get_supabase_client()
    params = st.query_params

    # 1️⃣ Gérer le lien de récupération
    if _handle_recovery_link(params, supabase):
        return

    # 2️⃣ Restaurer la session depuis cookie / token local
    _restore_session_from_supabase(supabase)

    # 3️⃣ Valider la session si existante
    if SessionManager.is_authenticated():
        _validate_existing_session(supabase)

    # 4️⃣ Interface
    if SessionManager.is_authenticated() and not SessionManager.is_resetting_password():
        return
    _show_auth_interface(supabase)


# ============ RESTAURATION ET VALIDATION ============

def _restore_session_from_supabase(supabase):
    """Restaure la session depuis st.session_state ou cookie."""
    if SessionManager.is_authenticated():
        return

    # Priorité 1 : session en mémoire
    token = st.session_state.get("supabase_token")
    refresh_token = st.session_state.get("supabase_refresh_token")

    # Priorité 2 : cookie navigateur (si on a persisté)
    if not token:
        token = st.experimental_get_cookie("sb_access_token")
        refresh_token = st.experimental_get_cookie("sb_refresh_token")

    if not token:
        return  # pas de session connue

    try:
        # Essayer de recharger la session
        supabase.auth.set_session(access_token=token, refresh_token=refresh_token)
        user = supabase.auth.get_user()
        if user and user.user:
            SessionManager.set_user(user.user)
    except Exception:
        # Token invalide → on nettoie
        SessionManager.logout()


def _validate_existing_session(supabase):
    """Vérifie que le token est toujours valide."""
    try:
        user = supabase.auth.get_user()
        if not user or not user.user:
            SessionManager.logout()
    except Exception:
        SessionManager.logout()


# ============ LIEN DE RÉCUPÉRATION ============

def _handle_recovery_link(params, supabase) -> bool:
    if (
        "type" in params 
        and params.get("type") == "recovery"
        and "access_token" in params
        and not SessionManager.is_recovery_verified()
    ):
        token_hash = params.get("access_token")
        try:
            resp = supabase.auth.verify_otp({"token_hash": token_hash, "type": "recovery"})
            if resp.session:
                SessionManager.set_user(resp.session.user)
                SessionManager.set_auth_mode(SessionManager.AUTH_MODES['RESET_PASSWORD'])
                SessionManager.set_recovery_verified(True)
                st.success("Lien valide ! Vous pouvez choisir un nouveau mot de passe.")
            else:
                st.error("Lien invalide ou expiré.")
                st.stop()
        except Exception as e:
            st.error(f"Erreur : {e}")
            st.stop()
        return True
    return False


# ============ INTERFACE D'AUTHENTIFICATION ============

def _show_auth_interface(supabase):
    _show_welcome_banner()
    mode = SessionManager.get_auth_mode()

    if mode == SessionManager.AUTH_MODES['RESET_PASSWORD']:
        _show_reset_password_form(supabase)
    elif mode == SessionManager.AUTH_MODES['FORGOT']:
        _show_forgot_password_form(supabase)
    elif mode is None:
        _show_auth_choice()
    else:
        _show_login_signup_form(supabase, mode)


def _show_welcome_banner():
    st.markdown(
        """
        <div style='background-color:#4CAF50; padding:20px; border-radius:10px; color:white; text-align:center;'>
            <h2>Bienvenue sur la bêta de Trail Pacer !</h2>
            <p>Veuillez créer un compte pour accéder à la bêta et connecter vos appareils Strava/Garmin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


def _show_auth_choice():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter", use_container_width=True, type="primary"):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['LOGIN'])
            st.rerun()
    with col2:
        if st.button("S'inscrire", use_container_width=True):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['SIGNUP'])
            st.rerun()
    st.stop()


def _show_login_signup_form(supabase, mode: str):
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        is_login = mode == SessionManager.AUTH_MODES['LOGIN']
        st.subheader("Connexion" if is_login else "Créer un compte")

        email = st.text_input("Email", key=f"{mode}_email")
        password = st.text_input("Mot de passe", type="password", key=f"{mode}_password")
        name = st.text_input("Nom complet") if not is_login else None

        if is_login:
            _handle_login_form(supabase, email, password)
        else:
            _handle_signup_form(supabase, email, password, name)


def _handle_login_form(supabase, email, password):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Veuillez remplir tous les champs.")
                return
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if user and user.user:
                    SessionManager.set_user(user.user)
                    SessionManager.set_auth_mode(None)
                    # Stocker tokens
                    st.session_state["supabase_token"] = user.session.access_token
                    st.session_state["supabase_refresh_token"] = user.session.refresh_token
                    # Optionnel : cookies navigateur
                    st.experimental_set_cookie("sb_access_token", user.session.access_token)
                    st.experimental_set_cookie("sb_refresh_token", user.session.refresh_token)
                    st.success(f"Bienvenue {email} !")
                    st.rerun()
                else:
                    st.error("Email ou mot de passe invalide.")
            except Exception:
                st.error("Email ou mot de passe invalide.")
    with col2:
        if st.button("Mot de passe oublié ?", use_container_width=True):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['FORGOT'])
            st.rerun()

    if st.button("⬅️ Retour", use_container_width=True):
        SessionManager.set_auth_mode(None)
        st.rerun()


def _handle_signup_form(supabase, email, password, name: Optional[str]):
    if st.button("S'inscrire", use_container_width=True, type="primary"):
        if not email or not password:
            st.error("Veuillez remplir tous les champs.")
            return
        elif len(password) < 6:
            st.error("Le mot de passe doit contenir au moins 6 caractères.")
            return

        try:
            user = supabase.auth.sign_up({"email": email, "password": password})
            if user.user:
                existing = db["users"].find_one({"mail": email})
                if not existing:
                    create_user_profile(internal_id=user.user.id, email=email, name=name or None)

                SessionManager.set_user(user.user)
                SessionManager.set_auth_mode(None)
                st.session_state["supabase_token"] = user.session.access_token
                st.session_state["supabase_refresh_token"] = user.session.refresh_token
                st.experimental_set_cookie("sb_access_token", user.session.access_token)
                st.experimental_set_cookie("sb_refresh_token", user.session.refresh_token)
                st.success(f"Bienvenue {name or email} !")
                st.rerun()
            else:
                st.error("Erreur lors de l'inscription.")
        except Exception as e:
            st.error(f"Erreur : {e}")

    if st.button("⬅️ Retour", use_container_width=True):
        SessionManager.set_auth_mode(None)
        st.rerun()

def show_sidebar():
    """Affiche les informations utilisateur dans la sidebar"""
    with st.sidebar:
        if not SessionManager.is_authenticated():
            st.info("Connectez-vous pour apparier vos appareils")
            return
        
        user = SessionManager.get_user()
        email = user.email if hasattr(user, 'email') else 'Utilisateur'
        
        st.write(f"Connecté : {email}")
        
        # Bouton de déconnexion
        if st.button("Se déconnecter", use_container_width=True):
            try:
                supabase.auth.sign_out()
            except:
                pass
            SessionManager.logout()
            st.rerun()
        
        st.markdown("---")
        st.subheader("Connectez vos appareils")
        
        # Intégrations
        internal_id = user.id
        integrations = list_integrations(internal_id)
        
        # Bouton Strava
        if not integrations.get("strava", False):
            auth_strava_url = connect_strava()
            # st.markdown(
            #     f"""
            #     <a href="{auth_strava_url}" style="
            #         display:block;
            #         text-align:center;
            #         padding:10px;
            #         background-color:#fc4c02;
            #         color:white;
            #         text-decoration:none;
            #         border-radius:5px;
            #         font-weight:bold;">
            #         Connecter Strava
            #     </a>
            #     """,
            #     unsafe_allow_html=True
            # )
            st.markdown(
                f"""<div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;">
                    <a href={auth_strava_url}" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style="transition: transform 0.2s;"
                    onmouseover="this.style.transform='scale(1.1)'"
                    onmouseout="this.style.transform='scale(1)'">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/63/Strava_icon.png" 
                            width="30" height="30" alt="Strava">
                    </a>
                </div>""")

        
        # Bouton Garmin
        if not integrations.get("garmin", False):
            auth_garmin_url = connect_garmin()
            st.markdown(
                f"""
                <a href="{auth_garmin_url}" style="
                    display:block;
                    text-align:center;
                    padding:10px;
                    background-color:#0073cf;
                    color:white;
                    text-decoration:none;
                    border-radius:5px;
                    font-weight:bold;">
                    Connecter Garmin
                </a>
                """,
                unsafe_allow_html=True
            )
        
        if integrations.get("strava") and integrations.get("garmin"):
            st.write("Vous avez déjà connecté tous vos appareils")
        
        st.markdown("---")