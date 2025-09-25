import streamlit as st
from config.styles import apply_custom_css
from core.session import SessionManager
from core.page_router import PageRouter
import os
from config.airtableapi import email_form,commentaire_form
from tsx_pages.trail_pacer import select_event
import yaml

 
class TSXApplication:
    """Application principale TSX Trail"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.page_router = PageRouter()
        self.EVENT_CONFIG_PATH= "config/event_config.yml"
        # Configuration Streamlit
        self._configure_streamlit()
        self._configure_event(self.EVENT_CONFIG_PATH)
    def _configure_streamlit(self):
        """Configuration initiale de Streamlit"""
        try:
            st.set_page_config(
                    page_title="TrailPacer",
                    page_icon= "TrailPacer\image\icon.png",
                    layout="wide",
                    initial_sidebar_state="expanded"
                    
                )
        except Exception:
            # Fallback si erreur de configuration
            pass
        
        # Application des styles CSS
        apply_custom_css()
    

    def _configure_event(self, path):
        with open(path, "r", encoding="utf-8") as f:
            EVENT_CONFIG= yaml.safe_load(f)
        st.session_state['EVENT_CONFIG']=EVENT_CONFIG

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
        # Routage et affichage de la page courante
        current_page = self.session_manager.get_current_page()
        self.page_router.render_page(current_page)
    
    def _show_user_message(self) :

        with st.sidebar:

            with st.expander("ℹ️ En savoir plus") : 

                st.write("Trail Pacer n’est qu’un début d’une initiative plus ambitieuse… \n " \
                "Entrez votre email pour découvrir nos nouveautés et être parmi les premiers informés de la suite du projet. \n " \
                "Votre avis nous intéresse, n'hésitez pas à nous laissez un commentaire")
                email_form()
                commentaire_form()

            #st.info('Plans de course à venir : Sainté Lyon, Grand Trail des templiers et Grand Raid Réunion...')
    def _show_sidebar(self):
        
        """Affichage de la barre latérale"""
        select_event()
        self._show_user_message()


 
    def _display_waning_if_beta(self):
        # Récupérer l'environnement
        app_env = os.getenv("APP_ENV", "prod")
        txt_beta=""" Merci de participer à la version <span style="color:#FFD700;">BETA</span> de TrailPacer ! <br><br>
                    Si vous avez des remarques, des suggestions, des retours , envoyez-nous un mail à 
                    <a href="mailto: trailpacer.ia@gmail.com" style="color:#FFD700;">trailpacer.ia@gmail.com</a> <br>
                    ou utilisez directement l'espace commentaire."""
        # Afficher bannière si on est en beta
        if app_env == "beta":
            st.markdown(
                f"""
                <div style="
                    background-color:#4CAF50;
                    padding:15px;
                    border-radius:10px;
                    text-align:center;
                    color:white;
                    font-size:18px;
                    font-weight:bold;
                ">
                    {txt_beta}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.divider()
                    
                    
if __name__ == "__main__":
    app = TSXApplication()
    app.run()