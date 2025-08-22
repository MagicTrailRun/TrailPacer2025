import streamlit as st
from config.styles import apply_custom_css
from core.session import SessionManager
from core.page_router import PageRouter
import os
import re

import csv 

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def save_email(email,name, file_path="emails.csv"):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Écrire les en-têtes si le fichier n'existe pas encore
            writer.writerow(["email,name"])
        writer.writerow([email,name])


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
            st.markdown("### ✉️ Restez informés")
            st.write("Pour vous tenir au courant de la suite, laissez-nous votre adresse mail :")
            nom= st.text_input("Prénom Nom")
            email = st.text_input("Votre email", placeholder="exemple@domaine.com")

            if st.button("📩 Envoyer"):
                if email and is_valid_email(email):
                    # Ici tu pourrais stocker l'email en DB / fichier / API
                    save_email(email,nom)  

                    st.success("Merci ! Vous serez tenu(e) informé(e) 😉")
                else:
                    st.warning("Veuillez entrer une adresse email valide.")


                        
                        
if __name__ == "__main__":
    app = TSXApplication()
    app.run()