import streamlit as st
from core.supabase_client import get_supabase_client
from core.mongo_client import create_user_profile
from core.mongo_client import db

def supabase_login():
    supabase= get_supabase_client()

    user = supabase.auth.get_user()
    if user:
        st.session_state["user"] = user.user
    else:
        st.session_state['user'] = None
    
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = None  # None, "login", "signup", "forgot"

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
        unsafe_allow_html=True
    )

    st.write("")  # petit espace

    def reset_password(email):
        try:
            supabase.auth.reset_password_for_email(email)
            st.success("✅ Un lien de réinitialisation a été envoyé à votre email.")
        except Exception as e:
            st.error(f"❌ Impossible d'envoyer le lien : {e}")

    # -------------------------
    # Utilisateur non connecté
    # -------------------------
    if st.session_state['user'] is None:

        # Choix login / signup
        if st.session_state['auth_mode'] is None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se connecter"):
                    st.session_state['auth_mode'] = "login"
            with col2:
                if st.button("S'inscrire"):
                    st.session_state['auth_mode'] = "signup"
            st.stop()

        # Formulaire centré
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:

            mode = st.session_state['auth_mode']
            st.subheader("Connexion" if mode=="login" else "Créer un compte" if mode=="signup" else "Mot de passe oublié")
            st.write("")

            # Champs communs
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password") if mode != "forgot" else None

            # Champs inscription
            name = st.text_input("Prénom et Nom") if mode=="signup" else None

            st.write("")

            # Boutons
            col_btn_left, col_btn_center, col_btn_right = st.columns([1,2,1])
            with col_btn_center:
                if mode == "login":
                    if st.button("Se connecter"):
                        try:
                            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                            if res.user:
                                st.session_state['user'] = res.user
                                st.success(f"Bienvenue {email} !")
                                st.rerun()
                            else:
                                st.error("Email ou mot de passe invalide")
                        except Exception:
                            st.error("Email ou mot de passe invalide")

                    if st.button("Mot de passe oublié ?"):
                        st.session_state['auth_mode'] = "forgot"
                        st.rerun()

                elif mode == "signup":
                    if st.button("S'inscrire"):
                        try:
                            res = supabase.auth.sign_up({"email": email, "password": password})
                            if res.user:
                                existing = db["users"].find_one({"mail": email})
                                if not existing:
                                    create_user_profile(
                                        internal_id=res.user.id,
                                        email=email,
                                        name=name or None
                                    )
                                    st.success(f"Bienvenue {name or email} ! Votre compte a été créé et connecté.")
                                    st.session_state['auth_mode'] = None
                                    st.rerun()
                                else:
                                    st.info("Un profil existe déjà pour cet email — aucun nouveau profil créé.")
                            else:
                                st.error("Erreur lors de l'inscription")
                        except Exception as e:
                            st.error(f"Erreur : {e}")

                elif mode == "forgot":
                    if st.button("Envoyer le lien"):
                        reset_password(email)

                # Bouton retour pour signup ou forgot
                if mode in ["signup", "forgot"]:
                    if st.button("⬅️ Retour"):
                        st.session_state['auth_mode'] = "login"
                        st.rerun()

    else:
        # Utilisateur connecté
        st.sidebar.write(f"Connecté : {st.session_state['user'].email}")
        if st.sidebar.button("Se déconnecter"):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()
