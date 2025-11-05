# core/page_registry.py
"""
Registry centralisé pour les pages de l'application.
Source unique de vérité pour les pages disponibles.
"""
from typing import Dict, Callable
import tsx_pages.trail_pacer as trail_pacer

class PageRegistry:
    """Registry Pattern pour gérer les pages de manière centralisée"""
    
    # ==========================================
    # DÉFINITION DES PAGES (source unique)
    # ==========================================
    PAGES: Dict[str, Dict[str, any]] = {
        "⏱️ Trail Pacer": {
            "function": trail_pacer.show,
            "icon": "⏱️",
            "description": "Calculez votre allure idéale",
            "requires_auth": True,
        },
        # Futures pages :
        # "📊 Analyses": {
        #     "function": analytics.show,
        #     "icon": "📊",
        #     "description": "Analysez vos performances",
        #     "requires_auth": True,
        # },
        # "👤 Profil": {
        #     "function": profile.show,
        #     "icon": "👤",
        #     "description": "Gérez votre profil",
        #     "requires_auth": True,
        # },
    }
    
    @classmethod
    def get_page_names(cls) -> list:
        """Retourne la liste des noms de pages"""
        return list(cls.PAGES.keys())
    
    @classmethod
    def get_page_function(cls, page_name: str) -> Callable:
        """Retourne la fonction d'une page"""
        return cls.PAGES.get(page_name, {}).get("function")
    
    @classmethod
    def get_page_info(cls, page_name: str) -> Dict:
        """Retourne toutes les infos d'une page"""
        return cls.PAGES.get(page_name, {})
    
    @classmethod
    def page_exists(cls, page_name: str) -> bool:
        """Vérifie si une page existe"""
        return page_name in cls.PAGES
    
    @classmethod
    def get_default_page(cls) -> str:
        """Retourne la première page (page par défaut)"""
        return cls.get_page_names()[0] if cls.PAGES else None