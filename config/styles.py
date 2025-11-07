import streamlit as st

def apply_custom_css():
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

        /* Ajuste les marges et paddings pour mobile */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            h1, h2, h3 {
                font-size: 1.2rem !important;
            }
            .stButton button {
                width: 100% !important;
            }
            .stTextInput>div>div>input {
                font-size: 16px !important; /* évite le zoom iOS */
            }

            /* Colonnes Streamlit -> empilement vertical sur mobile */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
        }

        /* Taille et style des labels de tabs */
        div[data-baseweb="tab"] > button p {
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        /* 🚨 Warning affiché uniquement sur mobile */
        @media (max-width: 768px) {
            .mobile-warning {
                display: block !important;
                background-color: #fff3cd;
                border-left: 6px solid #ff9800;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                color: #856404;
                font-weight: bold;
            }
        }
        @media (min-width: 769px) {
            .mobile-warning {
                display: none !important;
            }
        }
        /* Réduire les marges par défaut de Streamlit */
        .css-1aumxhk {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        /* Réduire les marges autour des boutons */
        .stButton>button {
            margin: 0.5rem 0;
        }
        /* Réduire les marges autour des titres */
        .stTitle {
            margin-bottom: 1rem;
        }

    </style>
    """

    # Viewport responsive
    st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1">', unsafe_allow_html=True)
    # CSS
    st.markdown(custom_css, unsafe_allow_html=True)
    # Bannière mobile
    st.markdown(
        '<div class="mobile-warning">📱 Pour une meilleure expérience, visitez le site sur un ordinateur</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
    <style>
    /* ======================= TABS NIVEAU 1 ======================= */
    div[data-baseweb="tab-list"] {
        justify-content: center;
        gap: 2rem;
        border-bottom: 2px solid #ddd;
        padding-bottom: 0.3rem;
        margin-bottom: 1rem;
    }

    button[data-baseweb="tab"] {
        font-size: 1.05em;
        font-weight: 600;
        color: #666;
        background-color: transparent !important;
        border: none !important;
        transition: color 0.3s ease;
    }

    button[data-baseweb="tab"]:hover {
        color: #2e7d32; /* vert hover TrailPacer */
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1b5e20; /* vert actif plus foncé */
        border-bottom: 3px solid #1b5e20 !important;
        border-radius: 0;
        transition: all 0.3s ease;
    }

    /* ======================= TABS NIVEAU 2 ======================= */
    div[data-testid="stHorizontalBlock"] div[data-baseweb="tab-list"] {
        justify-content: flex-start;
        gap: 1.5rem;
        border-bottom: 1px solid #eee;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        padding-left: 1rem;
    }

    div[data-testid="stHorizontalBlock"] button[data-baseweb="tab"] {
        font-size: 0.95em;
        font-weight: 500;
        color: #777;
    }

    div[data-testid="stHorizontalBlock"] button[data-baseweb="tab"]:hover {
        color: #2e7d32;
    }

    div[data-testid="stHorizontalBlock"] button[data-baseweb="tab"][aria-selected="true"] {
        color: #1b5e20;
        border-bottom: 2px solid #1b5e20 !important;
    }

    /* ======================= CONTAINER ======================= */
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

