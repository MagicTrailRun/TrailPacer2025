import streamlit as st
from core.supabase_client import supabase
from core.mongo_client import create_user_profile

def supabase_login():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = None  # None, "login", "signup"

    
    # Message d'accueil / encadré
    st.info(
        "Bienvenue sur la bêta de Trail Pacer !\n\n"
        "Nous vous demandons maintenant de créer un compte pour contrôler qui a accès à la bêta, "
        "ainsi que pour personnaliser l'expérience. \n\n"
        "Vous pouvez également appareiller votre compte Garmin ou Strava afin que nous récupérions vos données "
        "pour mettre en place de nouveaux modèles et analyses qui arriveront par la suite. Merci de votre aide."
    )

    if st.session_state['user'] is None:


        # Affichage des boutons uniquement si aucun mode choisi
        if st.session_state['auth_mode'] is None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se connecter"):
                    st.session_state['auth_mode'] = "login"
            with col2:
                if st.button("S'inscrire"):
                    st.session_state['auth_mode'] = "signup"
            st.stop()  # On arrête ici pour attendre le choix

        
        # Champ commun : email + mot de passe
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")


        # Si inscription, afficher les champs prénom/nom
        name = None
        if st.session_state['auth_mode'] == "signup":
            name = st.text_input("Prénom et Nom")


        col1, col2 = st.columns(2)
        with col1:
            if st.session_state['auth_mode'] == "login":
                if st.button("Se connecter"):
                    try:
                        user = supabase.auth.sign_in({"email": email, "password": password})
                        if user.user:
                            st.session_state['user'] = user.user
                            st.success(f"Bienvenue {email} !")
                            st.experimental_rerun()
                        else:
                            st.error("Email ou mot de passe invalide")
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        with col2:
            if st.session_state['auth_mode'] == "signup":
                if st.button("S'inscrire"):
                    try:
                        user = supabase.auth.sign_up({"email": email, "password": password})
                        if user.user:
                            # Création du profil MongoDB
                            create_user_profile(
                                user_id=user.user.id,
                                email=email,
                                name=name or None
                            )
                            st.info("Compte créé ! Vérifiez votre email pour confirmer.")
                            st.session_state['auth_mode'] = None
                            st.experimental_rerun()
                        else:
                            st.error("Erreur lors de l'inscription")
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    else:
        # Utilisateur connecté
        st.sidebar.write(f"Connecté : {st.session_state['user']['email']}")
        if st.sidebar.button("Se déconnecter"):
            supabase.auth.sign_out()
            st.session_state['user'] = None
            st.experimental_rerun()
