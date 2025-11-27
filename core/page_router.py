# core/page_router.py (version simplifiée)
import streamlit as st
from core.page_registry import PageRegistry
from core.session import SessionManager

class PageRouter:
    """Routeur léger qui utilise le Registry"""
    
    def render_page(self, page_name: str):
        """Affiche la page demandée"""
        if not PageRegistry.page_exists(page_name):
            self._show_404(page_name)
            return
        
        # Vérifier les permissions
        page_info = PageRegistry.get_page_info(page_name)
        if page_info.get("requires_auth") and not SessionManager.is_authenticated():
            st.warning("🔒 Cette page nécessite une authentification")
            st.stop()
        
        # Afficher la page
        try:
            page_function = PageRegistry.get_page_function(page_name)
            page_function()
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement de la page : {e}")
            if st.button("🔄 Recharger la page"):
                st.rerun()
    
    def _show_404(self, page_name: str):
        """Page 404 élégante"""
        st.error(f"🚫 Page inconnue : `{page_name}`")
        
        st.write("### Pages disponibles :")
        for name in PageRegistry.get_page_names():
            info = PageRegistry.get_page_info(name)
            icon = info.get("icon", "📄")
            desc = info.get("description", "")
            st.write(f"{icon} **{name}** - {desc}")
        
        if st.button("🏠 Retour à l'accueil"):
            SessionManager.set_current_page(PageRegistry.get_default_page())
            st.rerun()
    
    def get_available_pages(self) -> list:
        """Retourne les pages disponibles"""
        return PageRegistry.get_page_names()