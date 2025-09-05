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

        self._display_waning_if_beta()
        st.divider()
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
    

    def _display_waning_if_beta(self):
        # Récupérer l'environnement
        app_env = os.getenv("APP_ENV", "prod")

        # Afficher bannière si on est en beta
        if app_env == "beta":
            st.markdown(
                """
                <div style="
                    background-color:#FFA500;
                    padding:15px;
                    border-radius:10px;
                    text-align:center;
                    color:white;
                    font-size:18px;
                    font-weight:bold;
                ">
                    🚧 ATTENTION : Vous êtes sur la version BETA de TrailPacer.<br>
                    Certaines fonctionnalités peuvent être instables ou incomplètes.
                </div>

                """,
                unsafe_allow_html=True
        )
            
             
if __name__ == "__main__":
    app = TSXApplication()
    app.run()