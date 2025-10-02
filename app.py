import streamlit as st
from config.styles import apply_custom_css
from core.session import SessionManager
from core.page_router import PageRouter
import os
from config.airtableapi import email_form,commentaire_form
from TrailPacer.data_loader import select_event , info_social_media
import yaml
from Quest.sex_quest import show_quest_banner
from BETA.beta_bandeau import show_beta_banner
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
                    page_icon= "TrailPacer/image/icon_web.png",
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
        self.session_manager.initialize_session()
        self._show_main_interface()
    
 
    def show_banner(self) :
        html_code=show_quest_banner()
        st.components.v1.html(html_code)

    def _show_main_interface(self):
        self._show_sidebar()
        main_container = st.container()
        with main_container:
            self._display_waning_if_beta()
            self.show_banner()
            current_page = self.session_manager.get_current_page()
            self.page_router.render_page(current_page)
    
    def _show_user_message(self) :

        with st.sidebar:

            with st.expander("En savoir plus", icon=":material/info:") : 

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
        info_social_media()

    
    def _display_waning_if_beta(self):
        # Récupérer l'environnement
        app_env = os.getenv("APP_ENV", "prod")
        txt_beta=show_beta_banner()
        # Afficher bannière si on est en beta
        if app_env == "beta":
             st.components.v1.html(txt_beta)

                    
                    
if __name__ == "__main__":
    app = TSXApplication()
    app.run()