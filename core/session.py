# core/session.py
import streamlit as st
from typing import Dict, Any, Optional

class SessionManager:
    """Gestionnaire centralisé de l'état de session Streamlit"""
    
    # Clés de session
    CURRENT_PAGE = 'current_page'

    
    # Pages disponibles
    PAGES = {
        "⏱️ Trail Pacer": "trail_pacer"
    }

    def initialize_session(cls):
        """Initialise les variables de session si elles n'existent pas"""
        default_values = {
            cls.CURRENT_PAGE: "⏱️ Trail Pacer",

        }
        
        for key, default_value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    

    @classmethod
    def get_current_page(cls) -> str:
        """Retourne la page courante"""
        return st.session_state.get(cls.CURRENT_PAGE, "📊 Dashboard")
    
    @classmethod
    def set_current_page(cls, page: str):
        """Définit la page courante"""
        if page in cls.PAGES:
            st.session_state[cls.CURRENT_PAGE] = page
    
    