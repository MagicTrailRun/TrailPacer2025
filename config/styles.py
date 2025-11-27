import streamlit as st
from pathlib import Path

def apply_custom_css():
    # --- Chemin du fichier CSS
    css_path = Path("assets/styles.css")

    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Fichier CSS introuvable : assets/styles.css")

    # Viewport responsive
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        unsafe_allow_html=True,
    )

    # Bannière mobile
    st.markdown(
        '<div class="mobile-warning">📱 Pour une meilleure expérience, visitez le site sur un ordinateur</div>',
        unsafe_allow_html=True
    )
