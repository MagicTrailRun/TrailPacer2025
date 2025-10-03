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
from config.styles import apply_custom_css
import traceback
import streamlit.components.v1 as components


print("___________________________________________")


def show(): 
    apply_custom_css()
    year=st.session_state.get("year",2025)
    event_code=st.session_state["event_code"]
    course_code=st.session_state["course_code"]
    event=st.session_state["event"]
    course=st.session_state["course"]
    config=st.session_state["config"]
    df=st.session_state["df"]
    if not all(k in st.session_state for k in ["event", "course", "year", "df", "config"]):
        st.warning("⚠️ Merci de sélectionner un événement et une course dans le menu de gauche")
        st.stop()
    
    show_hero_banner(event, course, event_code, df)


    plan_course1, explorer3, postcourse4, pacing2, avis5, qui6 , cnil7= st.tabs([
        "Plan de course",
        "Explorer les courses",
        "Analyse post-course",
         "Le pacing selon TrailPacer",
        "Suivre le projet",
        "Qui sommes-nous?",
        "Politique de confidentialité"

    ])
     
    st.markdown("------------")
    with plan_course1:
       show_plan_pacing()

        

    with explorer3 : 
        explore_race()




    with postcourse4:
        post_course_year=st.session_state["post_course_year"]
        try:
            # 1️⃣ Essai sur l'année sélectionnée
            
            show_post_course(course, event_code, course_code, post_course_year)

        except Exception as e:
            st.error("❌ Cette page n'est pas encore disponible pour la course sélectionnée !")
            print(f"[DEBUG] Erreur lors de show_post_course pour l'année {post_course_year} : {e}")
            traceback.print_exc()


    with pacing2 : 
            pacing()
 

    with avis5 :

        votreavis()

    with qui6 :
        quisommesnous()
        

    with cnil7 :
        cnil()

if __name__ == "__main__":
    show()
