import streamlit as st
import pandas as pd
import io
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
from TrailPacer.formatting import get_base64_image,show_hero_banner
from TrailPacer.explore_race import explore_race
from TrailPacer.text import pacing, quisommesnous, votreavis, cnil
from TrailPacer.post_course import show_post_course
from TrailPacer.plan_pacing import show_plan_pacing
from TrailPacer.device_connected import device_connected
from core.fitness_connect import connect_strava, connect_garmin
import traceback
import streamlit.components.v1 as components
from TrailPacer.data_loader import select_event


print("___________________________________________")


def show():
    show_hero_banner()

    # --- CSS spécifique aux onglets
    st.markdown("""
    <style>
    /* Container pour les onglets */
    div#tabs-container {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    div#tabs-container button {
        flex: 1;
        padding: 10px 0;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
        background: linear-gradient(135deg, #2e7d32, #81c784);
        color: white;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }

    div#tabs-container button:hover {
        background: linear-gradient(135deg, #388e3c, #a5d6a7);
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.15);
    }

    div#tabs-container button.active-tab {
        background: linear-gradient(135deg, #1b5e20, #66bb6a);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Onglets HTML
    st.markdown('<div id="tabs-container"></div>', unsafe_allow_html=True)
    
    tabs = ["TrailPacer", "Suivre le projet", "Politique de confidentialité", "Appareils connectés"]
    
    # Initialisation de l'onglet
    if "onglet" not in st.session_state:
        st.session_state["onglet"] = tabs[0]

    # Création des boutons via columns pour largeur égale
    cols = st.columns(len(tabs))
    for idx, tab_name in enumerate(tabs):
        with cols[idx]:
            # Active class
            class_attr = "active-tab" if st.session_state["onglet"] == tab_name else ""
            if st.button(tab_name, key=f"tab_{idx}", use_container_width=True):
                st.session_state["onglet"] = tab_name

    # --- Affichage du contenu selon l'onglet actif
    if st.session_state["onglet"] == "TrailPacer":
        trail_pacer_display()

    elif st.session_state["onglet"] == "Suivre le projet":
        st.markdown("### Suivre le projet")
        st.markdown("Partagez votre expérience et découvrez l’équipe derrière TrailPacer.")
        with st.container():
            with st.expander("Votre avis nous intéresse", expanded=False):
                votreavis()
            with st.expander("Qui sommes-nous ?", expanded=False):
                quisommesnous()

    elif st.session_state["onglet"] == "Politique de confidentialité":
        cnil()

    elif st.session_state["onglet"] == "Appareils connectés":
        device_connected()



def trail_pacer_display():
    with st.container(border=True):
        st.subheader("Sélection de l'événement")
        select_event()
    required_keys = ["event", "course", "year", "df", "config"]
    if not all(k in st.session_state for k in required_keys):
        st.info("➡️ Veuillez d'abord sélectionner un événement et une course.")
        st.stop()  
    year=st.session_state.get("year",2025)
    event_code=st.session_state["event_code"]
    course_code=st.session_state["course_code"]
    event=st.session_state["event"]
    course=st.session_state["course"]
    config=st.session_state["config"]
    df=st.session_state["df"]

    plan_course1, explorer3, postcourse4, pacing2= st.tabs([
    "Plan de course",
    "Explorer la course",
    "Analyse post-course",
    "Le pacing selon TrailPacer"])

    with plan_course1:
        show_plan_pacing()
    with explorer3 : 
        explore_race()
    with postcourse4:
        post_course_year=st.session_state["post_course_year"]
        try:

            show_post_course(course, event_code, course_code, post_course_year)

        except Exception as e:
            #st.error("❌ Cette page n'est pas encore disponible pour la course sélectionnée !")
            print(f"[DEBUG] Erreur lors de show_post_course pour l'année {post_course_year} : {e}")
            traceback.print_exc()
    with pacing2 : 
            pacing()


if __name__ == "__main__":
    show()
