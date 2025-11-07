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
    
    # Conteneur avec classe unique pour cibler seulement ces boutons
    st.markdown("""
<style>
/* Style pour les boutons de navigation uniquement (via leur key) */
button[kind="primary"][data-testid="baseButton-primary"],
button[data-testid="baseButton-primary"] {
    /* On cible d'abord tous les boutons, puis on utilise les keys */
}

/* Ciblage spécifique via les keys des boutons */
div[data-testid="column"] button[kind="primary"] {
    background: linear-gradient(135deg, #2e7d32, #81c784) !important;
    color: green !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border-radius: 12px !important;
    padding: 10px 0 !important;
    box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

/* Hover */
div[data-testid="column"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #388e3c, #a5d6a7) !important;
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(0,0,0,0.15) !important;
}

/* Active (clic) */
div[data-testid="column"] button[kind="primary"]:active {
    transform: translateY(0);
    box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
}
</style>
""", unsafe_allow_html=True)
    
    # Conteneur avec ID unique pour cibler spécifiquement ces boutons
    with st.container():
        st.markdown('<div id="navigation-tabs">', unsafe_allow_html=True)
        
        trailpacer, avis5, cnil7, connect8 = st.columns(4)
        
        with trailpacer:
            if st.button("TrailPacer", key="nav_trailpacer", use_container_width=True, type="primary"):
                st.session_state["onglet"] = "TrailPacer"
        
        with avis5:
            if st.button("Suivre le projet", key="nav_suivre", use_container_width=True, type="primary"):
                st.session_state["onglet"] = "Suivre le projet"
        
        with cnil7:
            if st.button("Politique de confidentialité", key="nav_cnil", use_container_width=True, type="primary"):
                st.session_state["onglet"] = "Politique de confidentialité"
        
        with connect8:
            if st.button("Appareils connectés", key="nav_connect", use_container_width=True, type="primary"):
                st.session_state["onglet"] = "Appareils connectés"
        
      
        
        # Affichage en fonction du choix
        if st.session_state.get("onglet") == "TrailPacer":
            st.markdown('AHG')
            #trail_pacer_display()
        elif st.session_state.get("onglet") == "Suivre le projet":
            st.markdown("###  Suivre le projet")
            st.markdown("Partagez votre expérience et découvrez l'équipe derrière TrailPacer.")

            with st.container():
                with st.expander("Votre avis nous intéresse", expanded=False):
                    votreavis()

                with st.expander("Qui sommes-nous ?", expanded=False):
                    quisommesnous()

        elif st.session_state.get("onglet") == "Politique de confidentialité":
            cnil()
       

        elif st.session_state.get("onglet") == "Appareils connectés":
            device_connected()

        else:
            trail_pacer_display()
        st.markdown('</div>', unsafe_allow_html=True)


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
