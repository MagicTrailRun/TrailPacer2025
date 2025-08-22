# config/styles.py

import streamlit as st

def apply_custom_css():
    """Applique le CSS personnalisé à l'application Streamlit."""
    custom_css = """
    <style>
        /* Général */
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
        }

        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }

        /* Titres */
        h1, h2, h3, h4 {
            color: #2E7D32;
        }

        /* Boutons */
        button {
            border-radius: 5px !important;
        }

        /* Messages (success, warning, etc.) */
        .stAlert {
            border-left: 5px solid #2E7D32;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
