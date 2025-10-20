import streamlit as st
from core.supabase_client import supabase
from core.mongo_client import create_user_profile

def supabase_login():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = None  # None, "login", "signup"

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

    

    if st.session_state['user'] is None:

        # -------------------------
        # Choix login / signup
        # -------------------------
        if st.session_state['auth_mode'] is None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se connecter"):
                    st.session_state['auth_mode'] = "login"
            with col2:
                if st.button("S'inscrire"):
                    st.session_state['auth_mode'] = "signup"
            st.stop()

        # -------------------------
        # Formulaire centré dans un conteneur avec largeur limitée
        # -------------------------
        # On utilise 3 colonnes : la colonne centrale contient le formulaire
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:


            st.subheader(
                "Connexion" if st.session_state['auth_mode'] == "login" else "Créer un compte"
            )
            st.write("")

            # Champs communs
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")

            # Champs spécifiques à l'inscription
            name = None
            if st.session_state['auth_mode'] == "signup":
                name = st.text_input("Prénom et Nom")

            st.write("")  # petit espace

            # Boutons centrés
            col_btn_left, col_btn_center, col_btn_right = st.columns([1,2,1])
            with col_btn_center:
                if st.session_state['auth_mode'] == "login":
                    if st.button("Se connecter"):
                        try:
                            user = supabase.auth.sign_in({"email": email, "password": password})
                            if user.user:
                                st.session_state['user'] = user.user
                                st.success(f"Bienvenue {email} !")
                                st.rerun()
                            else:
                                st.error("Email ou mot de passe invalide")
                        except Exception as e:
                            st.error(f"Erreur : {e}")

                elif st.session_state['auth_mode'] == "signup":
                    if st.button("S'inscrire"):
                        try:
                            user = supabase.auth.sign_up({"email": email, "password": password})
                            if user.user:
                                create_user_profile(
                                    user_id=user.user.id,
                                    email=email,
                                    name=name or None
                                )
                                st.success("Compte créé ! Vérifiez votre email pour confirmer.")
                                st.session_state['auth_mode'] = None
                                st.rerun()
                            else:
                                st.error("Erreur lors de l'inscription")
                        except Exception as e:
                            st.error(f"Erreur : {e}")

            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Utilisateur connecté
        st.sidebar.write(f"Connecté : {st.session_state['user']['email']}")
        if st.sidebar.button("Se déconnecter"):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.rerun()

