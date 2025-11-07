# app.py
import streamlit as st
from config.styles import apply_custom_css
from core.session import SessionManager
from core.page_router import PageRouter
from core.auth import supabase_login, show_sidebar
from config.airtableapi import email_form, commentaire_form
from TrailPacer.data_loader import select_event, info_social_media
from Quest.sex_quest import show_quest_banner
from BETA.beta_bandeau import show_beta_banner
from core.fitness_connect import handle_garmin_callback, handle_strava_callback
import yaml
import os

class TSXApplication:
    """Application principale TSX Trail"""
    
    def __init__(self):
        self.page_router = PageRouter()
        self.EVENT_CONFIG_PATH = "config/event_config.yml"
        
        # Configuration Streamlit
        self._configure_streamlit()
        self._configure_event(self.EVENT_CONFIG_PATH)
    
    def _configure_streamlit(self):
        """Configuration initiale de Streamlit"""
        try:
            st.set_page_config(
                page_title="TrailPacer",
                page_icon="TrailPacer/image/icon_web.png",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except Exception:
            pass
        
        apply_custom_css()
    
    def _configure_event(self, path):
        """Charge la configuration des événements"""
        with open(path, "r", encoding="utf-8") as f:
            EVENT_CONFIG = yaml.safe_load(f)
        st.session_state['EVENT_CONFIG'] = EVENT_CONFIG
    
    def run(self):
        """Point d'entrée principal de l'application"""
        # 1. Initialiser la session
        SessionManager.initialize_session()
        
        # 2. Gérer l'authentification
        supabase_login()
        
        # 3. Si pas connecté, arrêter ici
        if not SessionManager.is_authenticated():
            st.stop()
        
        # 4. Afficher l'interface principale
        self._show_main_interface()
    
    def _show_main_interface(self):
        """Affiche l'interface principale pour utilisateur connecté"""
        # Gérer les callbacks OAuth
        handle_strava_callback()
        handle_garmin_callback()
        
        # Sidebar
        self._show_sidebar()
        
        # Contenu principal
        main_container = st.container()
        with main_container:
            self._display_if_beta()
            show_quest_banner()
            
            current_page = SessionManager.get_current_page()
            self.page_router.render_page(current_page)
    
    
    def _show_sidebar(self):
        """Affiche la barre latérale"""
        # Infos utilisateur + déconnexion
        show_sidebar()
        
        # Sélection d'événement
        #select_event()
        
        # Messages utilisateur
        self._show_user_message()
        
        # Réseaux sociaux
        info_social_media()
    
    def _show_user_message(self):
        """Affiche les messages et formulaires utilisateur"""
        with st.sidebar:
            with st.expander("En savoir plus", icon=":material/info:"):
                st.write(
                    "Trail Pacer n'est qu'un début d'une initiative plus ambitieuse… \n "
                    "Entrez votre email pour découvrir nos nouveautés et être parmi les premiers informés de la suite du projet. \n "
                    "Votre avis nous intéresse, n'hésitez pas à nous laisser un commentaire"
                )
                email_form()
                commentaire_form()
    
    def _display_if_beta(self):
        """Affiche la bannière beta si nécessaire"""
        app_env = os.getenv("APP_ENV", "prod")
        if app_env == "beta":
            show_beta_banner()



if __name__ == "__main__":
    app = TSXApplication()
    app.run()