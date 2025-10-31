import streamlit as st
from core.supabase_client import supabase
from core.mongo_client import create_user_profile
from core.mongo_client import db

def supabase_login():

    # -------------------------
    # Gestion utilisateur actuel
    # -------------------------

    # --- Détection d'un lien de réinitialisation envoyé par Supabase ---
    params = st.query_params
    if "type" in params and params.get("type") == "recovery" and "access_token" in params:
        access_token = params.get("access_token")
        # On initialise la session temporaire pour permettre la mise à jour du mot de passe
        supabase.auth.set_session(access_token, None)
        st.session_state["auth_mode"] = "reset_password"
        st.rerun()


    
    user = supabase.auth.get_user()
    if user:
        st.session_state["user"] = user.user
    else:
        st.session_state["user"] = None

    # Modes possibles : None, "login", "signup", "forgot"
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = None

    # -------------------------
    # Bannière d'accueil
    # -------------------------
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
    # Si aucun utilisateur connecté
    # -------------------------
    if st.session_state["user"] is None:

        # -------------------------
        # Page d’accueil (choix login/signup)
        # -------------------------
        if st.session_state["auth_mode"] is None:
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

        # -------------------------
        # Page "Mot de passe oublié"
        # -------------------------
        if st.session_state["auth_mode"] == "forgot":
            col_left, col_center, col_right = st.columns([1, 2, 1])
            with col_center:
                st.subheader("🔁 Réinitialiser le mot de passe")
                email = st.text_input("Email")

                if st.button("Envoyer le lien de réinitialisation"):
                    try:
                        supabase.auth.reset_password_for_email(email, options={"redirectTo": "https://magictrailrun-trailpacer2025-app-featauthentification-nkgwld.streamlit.app/"})
                        st.success("✅ Un lien de réinitialisation a été envoyé à votre adresse email.")
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

                if st.button("⬅️ Retour à la connexion"):
                    st.session_state["auth_mode"] = "login"
                    st.rerun()

            st.stop()



            # --- Page de réinitialisation après clic sur le mail ---
        if st.session_state["auth_mode"] == "reset_password":
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


        # -------------------------
        # Formulaire centré
        # -------------------------
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:

            mode = st.session_state["auth_mode"]

            st.subheader("Connexion" if mode == "login" else "Créer un compte")
            st.write("")

            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")

            name = None
            if mode == "signup":
                name = st.text_input("Prénom et Nom")

            st.write("")

            col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
            with col_btn_center:

                # --- Connexion ---
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

                    # 🔹 Bouton mot de passe oublié
                    if st.button("Mot de passe oublié ?"):
                        st.session_state["auth_mode"] = "forgot"
                        st.rerun()

                    # 🔹 Bouton retour
                    if st.button("⬅️ Retour"):
                        st.session_state["auth_mode"] = None
                        st.rerun()

                # --- Inscription ---
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

                    # 🔹 Bouton retour
                    if st.button("⬅️ Retour"):
                        st.session_state["auth_mode"] = None
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # Si utilisateur connecté
    # -------------------------
    else:
        st.sidebar.write(f"Connecté : {st.session_state['user'].email}")
        if st.sidebar.button("Se déconnecter"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()
