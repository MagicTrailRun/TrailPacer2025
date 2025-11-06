# core/auth.py
import streamlit as st
from core.session import SessionManager
from core.supabase_client import supabase
from core.mongo_client import create_user_profile, list_integrations, db
from core.fitness_connect import connect_strava, connect_garmin

def supabase_login():
    """Gestion complète de l'authentification Supabase"""
    
    params = st.query_params
    
    # -------------------------
    # 1. GÉRER LIEN DE RÉCUPÉRATION
    # -------------------------
    if _handle_recovery_link(params):
        return
    
    # -------------------------
    # 2. VALIDER SESSION EXISTANTE (CRITIQUE!)
    # -------------------------
    if SessionManager.is_authenticated():
        _validate_existing_session()
    
    # -------------------------
    # 3. AFFICHER INTERFACE APPROPRIÉE
    # -------------------------
    if SessionManager.is_authenticated() and not SessionManager.is_resetting_password():
        return
    
    _show_auth_interface()


def _handle_recovery_link(params) -> bool:
    """Gère le lien de récupération depuis l'email"""
    if (
        "type" in params 
        and params.get("type") == "recovery"
        and "access_token" in params
        and not SessionManager.is_recovery_verified()
    ):
        token_hash = params.get("access_token")
        try:
            resp = supabase.auth.verify_otp({
                "token_hash": token_hash,
                "type": "recovery"
            })
            if resp.session:
                SessionManager.set_user(resp.session.user)
                SessionManager.set_auth_mode(SessionManager.AUTH_MODES['RESET_PASSWORD'])
                SessionManager.set_recovery_verified(True)
                st.success("Lien valide ! Vous pouvez maintenant choisir un nouveau mot de passe.")
            else:
                st.error("Le lien de réinitialisation est invalide ou a expiré.")
                st.stop()
        except Exception as e:
            st.error(f"Impossible de vérifier le lien : {e}")
            st.stop()
        return True
    return False


def _validate_existing_session():
    """Valide que la session utilisateur est toujours valide"""
    try:
        user = supabase.auth.get_user()
        if not user or not user.user:
            SessionManager.logout()
    except Exception:
        SessionManager.logout()


def _show_auth_interface():
    """Affiche l'interface d'authentification appropriée"""
    _show_welcome_banner()
    
    mode = SessionManager.get_auth_mode()
    
    if mode == SessionManager.AUTH_MODES['RESET_PASSWORD']:
        _show_reset_password_form()
    elif mode == SessionManager.AUTH_MODES['FORGOT']:
        _show_forgot_password_form()
    elif mode is None:
        _show_auth_choice()
    else:
        _show_login_signup_form(mode)


def _show_welcome_banner():
    """Affiche la bannière de bienvenue"""
    st.markdown(
        """
        <div style='background-color:#4CAF50; padding:20px; border-radius:10px; color:white; text-align:center;'>
            <h2>Bienvenue sur la bêta de Trail Pacer !</h2>
            <p>
            Nous vous demandons maintenant de créer un compte pour contrôler qui a accès à la bêta, 
            ainsi que pour personnaliser l'expérience. <br><br>
            Vous pouvez également appareiller votre compte Garmin ou Strava afin que nous récupérions vos données 
            pour mettre en place de nouveaux modèles et analyses qui arriveront par la suite. Merci de votre aide.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


def _show_auth_choice():
    """Affiche le choix entre connexion et inscription"""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Se connecter", use_container_width=True):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['LOGIN'])
            st.rerun()
    with col2:
        if st.button("S'inscrire", use_container_width=True):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['SIGNUP'])
            st.rerun()
    st.stop()


def _show_reset_password_form():
    """Formulaire de réinitialisation du mot de passe"""
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.subheader("🔒 Nouveau mot de passe")
        new_password = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
        confirm_password = st.text_input("Confirmez le mot de passe", type="password", key="confirm_pwd")
        
        if st.button("Valider le nouveau mot de passe"):
            if new_password != confirm_password:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                try:
                    supabase.auth.update_user({"password": new_password})
                    st.success("✅ Mot de passe mis à jour avec succès.")
                    SessionManager.set_auth_mode(SessionManager.AUTH_MODES['LOGIN'])
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
        
        if st.button("⬅️ Retour à la connexion"):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['LOGIN'])
            st.rerun()
    st.stop()


def _show_forgot_password_form():
    """Formulaire de mot de passe oublié"""
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.subheader("🔁 Réinitialiser le mot de passe")
        email = st.text_input("Email", key="forgot_email")
        
        if st.button("Envoyer le lien de réinitialisation"):
            try:
                supabase.auth.reset_password_for_email(
                    email,
                    options={"redirectTo": "https://magictrailrun-trailpacer2025-app-featauthentification-nkgwld.streamlit.app/"}
                )
                st.success("✅ Un lien de réinitialisation a été envoyé à votre adresse email.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
        
        if st.button("⬅️ Retour à la connexion"):
            SessionManager.set_auth_mode(SessionManager.AUTH_MODES['LOGIN'])
            st.rerun()
    st.stop()


def _show_login_signup_form(mode: str):
    """Formulaire de connexion ou inscription"""
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.subheader("Connexion" if mode == SessionManager.AUTH_MODES['LOGIN'] else "Créer un compte")
        
        email = st.text_input("Email", key=f"{mode}_email")
        password = st.text_input("Mot de passe", type="password", key=f"{mode}_password")
        name = st.text_input("Prénom et Nom", key="signup_name") if mode == SessionManager.AUTH_MODES['SIGNUP'] else None

        col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
        with col_btn_center:
            if mode == SessionManager.AUTH_MODES['LOGIN']:
                _handle_login_form(email, password)
            elif mode == SessionManager.AUTH_MODES['SIGNUP']:
                _handle_signup_form(email, password, name)


def _handle_login_form(email: str, password: str):
    """Gère le formulaire de connexion"""
    if st.button("Se connecter", use_container_width=True):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user.user:
                SessionManager.set_user(user.user)
                SessionManager.set_auth_mode(None)
                st.success(f"Bienvenue {email} !")
                st.rerun()
            else:
                st.error("Email ou mot de passe invalide")
        except Exception:
            st.error("Email ou mot de passe invalide")
    
    if st.button("Mot de passe oublié ?"):
        SessionManager.set_auth_mode(SessionManager.AUTH_MODES['FORGOT'])
        st.rerun()
    
    if st.button("⬅️ Retour"):
        SessionManager.set_auth_mode(None)
        st.rerun()


def _handle_signup_form(email: str, password: str, name: str):
    """Gère le formulaire d'inscription"""
    if st.button("S'inscrire", use_container_width=True):
        try:
            user = supabase.auth.sign_up({"email": email, "password": password})
            if user.user:
                existing = db["users"].find_one({"mail": email})
                if not existing:
                    create_user_profile(
                        internal_id=user.user.id,
                        email=email,
                        name=name or None,
                    )
                SessionManager.set_user(user.user)
                st.success(f"Bienvenue {name or email} ! Votre compte a été créé.")
                SessionManager.set_auth_mode(None)
                st.rerun()
            else:
                st.error("Erreur lors de l'inscription")
        except Exception as e:
            st.error(f"Erreur : {e}")
    
    if st.button("⬅️ Retour"):
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