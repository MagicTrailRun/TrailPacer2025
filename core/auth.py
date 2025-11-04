import streamlit as st
from core.supabase_client import supabase
from core.mongo_client import create_user_profile, list_integrations
from core.mongo_client import db
from core.fitness_connect import connect_strava, connect_garmin


# --- Sidebar avec appariement ---
def show_sidebar():
    st.sidebar.title("Trail Pacer")
    user = st.session_state.get("user")

    if not user:
        st.sidebar.info("Connectez-vous pour apparier vos appareils")
        return

    email = user.email
    st.sidebar.write(f"Connecté : {email}")

    # Déconnexion Trail Pacer
    if st.sidebar.button("Se déconnecter"):
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Connectez vos appareils")

    internal_id = user.id
    integrations = list_integrations(internal_id)  # {"strava": True/False, "garmin": True/False}

    # --- Strava (affiché uniquement si non connecté) ---
    if not integrations.get("strava", False):
        strava_logo = st.sidebar.image("TrailPacer/image/strava_logo.png", use_container_width=True)
        if st.sidebar.button(" ", key="pair_strava_logo"):
            connect_strava()  # Tu appelles ta fonction existante
            st.success("Strava appairé avec succès ✅")
            st.rerun()

    # --- Garmin (affiché uniquement si non connecté) ---
    if not integrations.get("garmin", False):
        garmin_logo = st.sidebar.image("TrailPacer/image/garmin_logo.png", use_container_width=True)
        if st.sidebar.button(" ", key="pair_garmin_logo"):
            connect_garmin()
            st.success("Garmin appairé avec succès ✅")
            st.rerun()
    
    if not integrations.get("garmin", False) and not integrations.get("strava", False):
        st.sidebar.write("Vous avez déjà connecté tous vos appareils")

    st.sidebar.markdown("---")




def supabase_login():
    params = st.query_params

    # -------------------------
    # Lien réinitialisation depuis email
    # -------------------------
    if (
        "type" in params and params.get("type") == "recovery"
        and "access_token" in params
        and st.session_state.get("recovery_verified") is not True
    ):

        token_hash = params.get("access_token")
        try:
            resp = supabase.auth.verify_otp({
                "token_hash": token_hash,
                "type": "recovery"
            })
            if resp.session:
                st.session_state["user"] = resp.session.user
                st.session_state["auth_mode"] = "reset_password"
                st.session_state["recovery_verified"] = True
                st.success("Lien valide ! Vous pouvez maintenant choisir un nouveau mot de passe.")
            else:
                st.error("Le lien de réinitialisation est invalide ou a expiré.")
                st.stop()
        except Exception as e:
            st.error(f"Impossible de vérifier le lien : {e}")
            st.stop()

    # -------------------------
    # Gestion utilisateur connecté
    # -------------------------
    user = supabase.auth.get_user()
    if user:
        st.session_state["user"] = user.user
    else:
        st.session_state["user"] = None

    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = None

    # -------------------------
    # Bannière d'accueil
    # -------------------------

    if st.session_state.get("user") is None or st.session_state.get("auth_mode") == "reset_password":
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

    # -------------------------
    # Si utilisateur connecté
    # -------------------------
    if st.session_state.get("user") is not None and st.session_state.get("auth_mode") != "reset_password":
        show_sidebar()
        return  # tout le reste est pour les non-connectés

    # -------------------------
    # Pages spéciales pour les non-connectés
    # -------------------------
    mode = st.session_state["auth_mode"]

    # 1️⃣ Réinitialisation mot de passe via lien
    if mode == "reset_password":
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.subheader("🔒 Nouveau mot de passe")
            new_password = st.text_input("Nouveau mot de passe", type="password")
            confirm_password = st.text_input("Confirmez le mot de passe", type="password")
            if st.button("Valider le nouveau mot de passe"):
                if new_password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    try:
                        supabase.auth.update_user({"password": new_password})
                        st.success("✅ Mot de passe mis à jour avec succès. Vous pouvez maintenant vous reconnecter.")
                        st.session_state["auth_mode"] = "login"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")
            if st.button("⬅️ Retour à la connexion"):
                st.session_state["auth_mode"] = "login"
                st.rerun()
        st.stop()

    # 2️⃣ Mot de passe oublié
    if mode == "forgot":
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            st.subheader("🔁 Réinitialiser le mot de passe")
            email = st.text_input("Email")
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
                st.session_state["auth_mode"] = "login"
                st.rerun()
        st.stop()

    # 3️⃣ Page d’accueil (choix login/signup)
    if mode is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Se connecter"):
                st.session_state["auth_mode"] = "login"
                st.rerun()
        with col2:
            if st.button("S'inscrire"):
                st.session_state["auth_mode"] = "signup"
                st.rerun()
        st.stop()

    # 4️⃣ Formulaire login/signup
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.subheader("Connexion" if mode == "login" else "Créer un compte")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        name = st.text_input("Prénom et Nom") if mode == "signup" else None

        col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
        with col_btn_center:
            if mode == "login":
                if st.button("Se connecter"):
                    try:
                        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if user.user:
                            st.session_state["user"] = user.user
                            st.success(f"Bienvenue {email} !")
                            st.rerun()
                        else:
                            st.error("Email ou mot de passe invalide")
                    except Exception:
                        st.error("Email ou mot de passe invalide")
                if st.button("Mot de passe oublié ?"):
                    st.session_state["auth_mode"] = "forgot"
                    st.rerun()
                if st.button("⬅️ Retour"):
                    st.session_state["auth_mode"] = None
                    st.rerun()
            elif mode == "signup":
                if st.button("S'inscrire"):
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
                                st.success(f"Bienvenue {name or email} ! Votre compte a été créé et connecté.")
                                st.session_state["auth_mode"] = None
                                st.rerun()
                            else:
                                st.info("Un profil existe déjà pour cet email — aucun nouveau profil créé.")
                        else:
                            st.error("Erreur lors de l'inscription")
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                if st.button("⬅️ Retour"):
                    st.session_state["auth_mode"] = None
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

