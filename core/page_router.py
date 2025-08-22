# core/page_router.py
import streamlit as st
import tsx_pages.trail_pacer as trail_pacer

class PageRouter:
    """Routeur qui appelle la bonne page selon le nom"""

    def render_page(self, page_name: str):
        if page_name == "⏱️ Trail Pacer":
            trail_pacer.show()
        else:
            st.error(f"Page inconnue : {page_name}")
