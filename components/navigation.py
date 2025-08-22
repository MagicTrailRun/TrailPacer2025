# components/navigation.py

import streamlit as st

class NavigationMenu:
    """Composant de menu horizontal et gestion de navigation."""

    def __init__(self, menu_items=None):
        if menu_items is None:
            self.menu_items = [
                "⏱️ Trail Pacer"
            ]
        else:
            self.menu_items = menu_items

        if 'current_page' not in st.session_state:
            st.session_state.current_page = self.menu_items[0]

  
