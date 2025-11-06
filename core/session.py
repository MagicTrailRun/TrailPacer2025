# core/session.py
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import uuid
from typing import Dict, Any, Optional
from core.page_registry import PageRegistry
from streamlit_cookies_manager import CookieManager

class SessionManager:
    """Gestionnaire centralisé de l'état de session et authentification"""

    # ==========================================
    # CLÉS DE SESSION
    # ==========================================
    CURRENT_PAGE = 'current_page'
    USER = 'user'
    AUTH_MODE = 'auth_mode'
    SESSION_ID = 'session_id'
    SESSION_INITIALIZED = 'session_initialized'
    RECOVERY_VERIFIED = 'recovery_verified'

    # ==========================================
    # MODES D'AUTHENTIFICATION
    # ==========================================
    AUTH_MODES = {
        'LOGIN': 'login',
        'SIGNUP': 'signup',
        'FORGOT': 'forgot',
        'RESET_PASSWORD': 'reset_password'
    }

    # Instance unique de CookieManager pour éviter les conflits de clé
    _cookie_manager = None

    @classmethod
    def _get_cookie_manager(cls):
        """Retourne une instance unique de CookieManager"""
        if cls._cookie_manager is None:
            cls._cookie_manager = CookieManager(key=f"cookie_manager_{uuid.uuid4()}")
        return cls._cookie_manager

    @classmethod
    def initialize_session(cls):
        """Initialise les variables de session si elles n'existent pas"""
        cookies = cls._get_cookie_manager()
        session_id = cookies.get("session_id")

        # Si pas de cookie, crée un nouvel ID de session
        if session_id is None:
            cls._ensure_session_id()
        else:
            st.session_state[cls.SESSION_ID] = session_id

        # Forcer nouvelle authentification pour nouvelle session
        if cls.SESSION_INITIALIZED not in st.session_state:
            st.session_state[cls.SESSION_INITIALIZED] = True
            st.session_state[cls.USER] = None
            st.session_state[cls.AUTH_MODE] = None

        # Valeurs par défaut
        default_values = {
            cls.CURRENT_PAGE: PageRegistry.get_default_page(),
            cls.AUTH_MODE: None,
            cls.RECOVERY_VERIFIED: False,
        }

        for key, default_value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

        # Affiche le cookie actuel pour le débogage
        current_session_id = cookies.get("session_id")
        st.write(f"Cookie session_id actuel : {current_session_id}")

    @classmethod
    def _ensure_session_id(cls):
        """Crée un ID unique pour cette session navigateur et définit le cookie"""
        ctx = get_script_run_ctx()
        session_id = ctx.session_id if ctx else str(uuid.uuid4())
        st.session_state[cls.SESSION_ID] = session_id
        cls._set_session_cookie(session_id)

    @classmethod
    def _set_session_cookie(cls, session_id: str):
        """Définit un cookie HTTP-only et sécurisé pour la session"""
        cookies = cls._get_cookie_manager()
        cookies.set(
            "session_id",
            session_id,
            max_age=86400,  # 1 jour
            httponly=True,
            secure=True,    # Assure-toi que ton app est en HTTPS
            samesite="Lax",
            path="/"
        )

    # ==========================================
    # GESTION DE L'UTILISATEUR
    # ==========================================

    @classmethod
    def get_user(cls) -> Optional[Any]:
        """Retourne l'utilisateur connecté ou None"""
        return st.session_state.get(cls.USER)

    @classmethod
    def set_user(cls, user: Any):
        """Définit l'utilisateur connecté"""
        st.session_state[cls.USER] = user

    @classmethod
    def is_authenticated(cls) -> bool:
        """Vérifie si un utilisateur est connecté"""
        return st.session_state.get(cls.USER) is not None

    @classmethod
    def logout(cls):
        """Déconnecte l'utilisateur et nettoie la session"""
        st.session_state.clear()
        # Supprime aussi le cookie
        cookies = cls._get_cookie_manager()
        cookies.delete("session_id")
        cls._cookie_manager = None  # Réinitialise l'instance pour la prochaine session
    # ==========================================
    # GESTION DU MODE D'AUTHENTIFICATION
    # ==========================================
    
    @classmethod
    def get_auth_mode(cls) -> Optional[str]:
        """Retourne le mode d'authentification actuel"""
        return st.session_state.get(cls.AUTH_MODE)
    
    @classmethod
    def set_auth_mode(cls, mode: Optional[str]):
        """Définit le mode d'authentification"""
        if mode is None or mode in cls.AUTH_MODES.values():
            st.session_state[cls.AUTH_MODE] = mode
    
    @classmethod
    def is_resetting_password(cls) -> bool:
        """Vérifie si on est en mode reset password"""
        return cls.get_auth_mode() == cls.AUTH_MODES['RESET_PASSWORD']
    
    # ==========================================
    # GESTION DES PAGES
    # ==========================================
    
    @classmethod
    def get_current_page(cls) -> str:
        """Retourne la page courante"""
        return st.session_state.get(cls.CURRENT_PAGE, PageRegistry.get_default_page())
    
    @classmethod
    def set_current_page(cls, page: str):
        """Définit la page courante (avec validation)"""
        if PageRegistry.page_exists(page):
            st.session_state[cls.CURRENT_PAGE] = page
        else:
            st.warning(f"⚠️ Page '{page}' non disponible")
    
    # ==========================================
    # RÉCUPÉRATION DE MOT DE PASSE
    # ==========================================
    
    @classmethod
    def is_recovery_verified(cls) -> bool:
        """Vérifie si la récupération a été vérifiée"""
        return st.session_state.get(cls.RECOVERY_VERIFIED, False)
    
    @classmethod
    def set_recovery_verified(cls, verified: bool = True):
        """Marque la récupération comme vérifiée"""
        st.session_state[cls.RECOVERY_VERIFIED] = verified
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    @classmethod
    def get_session_id(cls) -> str:
        """Retourne l'ID de session unique"""
        return st.session_state.get(cls.SESSION_ID, "unknown")