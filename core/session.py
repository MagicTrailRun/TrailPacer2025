# core/session.py
import streamlit as st
from typing import Dict, Any, Optional
from core.page_registry import PageRegistry

class SessionManager:
    """Gestionnaire centralisé de l'état de session Streamlit"""
    
    # Clés de session
    CURRENT_PAGE = 'current_page'

    
    # Pages disponibles
    PAGES = {
        "⏱️ Trail Pacer": "trail_pacer"
    }

    @classmethod
    def initialize_session(cls):
        """Initialise les variables de session"""
        cls._ensure_session_id()
        
        if cls.SESSION_INITIALIZED not in st.session_state:
            st.session_state[cls.SESSION_INITIALIZED] = True
            st.session_state[cls.USER] = None
            st.session_state[cls.AUTH_MODE] = None
        
        default_values = {
            cls.CURRENT_PAGE: PageRegistry.get_default_page(),
            cls.AUTH_MODE: None,
            cls.RECOVERY_VERIFIED: False,
        }
        
        for key, default_value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @classmethod
    def set_current_page(cls, page: str):
        """Définit la page courante (avec validation)"""
        if PageRegistry.page_exists(page):
            st.session_state[cls.CURRENT_PAGE] = page
        else:
            st.warning(f"⚠️ Page '{page}' non disponible")