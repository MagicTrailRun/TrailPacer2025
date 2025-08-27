import streamlit as st
from config.styles import apply_custom_css
from core.session import SessionManager
from core.page_router import PageRouter
import os
from config.airtableapi import email_form,commentaire_form
class TSXApplication:
    """Application principale TSX Trail"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.page_router = PageRouter()
        
        # Configuration Streamlit
        self._configure_streamlit()
        
    def _configure_streamlit(self):
        """Configuration initiale de Streamlit"""
        try:
            st.set_page_config(
                page_title=self.config.APP_TITLE,
                page_icon=self.config.APP_ICON,
                layout="wide"
            )
        except Exception:
            # Fallback si erreur de configuration
            pass
        
        # Application des styles CSS
        apply_custom_css()
    
    def run(self):
        """Point d'entrée principal de l'application"""
        # Initialisation de la session
        self.session_manager.initialize_session()
        
        # Gestion de l'authentification
       
        self._show_main_interface()
    
    def _show_main_interface(self):
        """Interface principale pour utilisateurs authentifiés"""
        # Affichage de la sidebar
        self._show_sidebar()
        
        # Routage et affichage de la page courante
        current_page = self.session_manager.get_current_page()
        self.page_router.render_page(current_page)
    def _show_sidebar(self):
        
        """Affichage de la barre latérale"""
        with st.sidebar:
            

            st.write("Trail Pacer n’est qu’un début d’une initiative plus ambitieuse… \n " \
            "Entrez votre email pour découvrir nos nouveautés et être parmi les premiers informés de la suite du projet.")
            email_form()
            st.divider()
            st.write("Votre avis nous intéresse, n'hésitez pas à nous laissez un commentaire")
            commentaire_form()
            
                        
if __name__ == "__main__":
    app = TSXApplication()
    app.run()