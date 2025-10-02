import pandas as pd
import numpy as np
import json
import streamlit as st
from TrailPacer.race_id import  get_df_for_gpx
import streamlit.components.v1 as components

def load_data(event,race="UTMB",year=2025, version="vf"):
    """Charge les données CSV"""
    try:
        csv_path = f"data/TrailPacer/{event}/{race}/pred_pacing/pred_{year}_{version}.csv"
        df = pd.read_csv(csv_path)
        df_checkpoints=pd.read_csv(f"data/TrailPacer/{event}/{race}/checkpoints/detail_checkpoints_{year}.csv")

        if "checkpoint" in df.columns:
            df = df.drop_duplicates(subset=["checkpoint"], keep="first")
        if "ravitaillement" in df_checkpoints.columns :
            df=df.merge(df_checkpoints[["checkpoint", "ravitaillement"]], on="checkpoint")
        return df
    except Exception as e:
        return pd.DataFrame()

def get_config(path):
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config['startDate'] = pd.to_datetime(config['startDate'])

    temps_cible = np.arange(config['temps_cible'][0], config['temps_cible'][1], config.get('step',1))
    config['temps_cible'] = temps_cible.astype(int).tolist()

    config['temps_cible_start'] = int(config['temps_cible'][0])
    config['temps_cible_end'] = int(config['temps_cible'][-1])
    config['temps_cible_middle'] = int(np.round((config['temps_cible_start'] + config['temps_cible_end'])/2))

    return config #, dic_config['mapping_ckpt']

def info_social_media():
    with st.sidebar:
        st.markdown( """ <div style=" position: fixed; bottom: 20px; left: 6%; transform: translateX(-50%); width: 90%; text-align: center; padding: 15px; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); "> <p style=" font-weight: bold; font-size: 16px; margin-bottom: 10px; color: inherit; "> 📱 Suivez-nous sur les réseaux </p> <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;"> <a href="https://www.instagram.com/trail_pacer/" target="_blank" rel="noopener noreferrer" style="transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'"> <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="30" height="30" alt="Instagram"> </a> <a href="https://www.facebook.com/TrailPacer.IA" target="_blank" rel="noopener noreferrer" style="transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'"> <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg" width="30" height="30" alt="Facebook"> </a> </div> </div> """, unsafe_allow_html=True )
def select_event():
    
    # --- CSS custom pour styliser les selectbox
    st.markdown("""
    <style>
    /* Conteneur général du selectbox */
    div[data-baseweb="select"] {
        background-color: #f9f9f9;      /* fond clair */
        border: 2px solid #e0e0e0;      /* bord fin */
        border-radius: 12px;            /* arrondi */
        padding: 6px 10px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease-in-out;
    }

    /* Hover effect */
    div[data-baseweb="select"]:hover {
        border: 2px solid #007bff;      /* bleu au survol */
        box-shadow: 0 4px 12px rgba(0,123,255,0.25);
    }

    /* Texte */
    div[data-baseweb="select"] span {
        font-size: 1.05em;
        font-weight: 500;
        color: #333;
    }

    /* Label au-dessus du selectbox */
    .css-10trblm, label {
        font-size: 1.1em !important;
        font-weight: bold !important;
        color: #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Définition des events/courses
    EVENT_CONFIG = st.session_state.get("EVENT_CONFIG", {})
    if not EVENT_CONFIG:
        st.error("Aucune configuration d'événement trouvée")
        st.stop()

    with st.sidebar:

        event = st.selectbox("🎯 Choisir un événement", list(EVENT_CONFIG.keys()))

        course = st.selectbox("🏃 Choisir une course", list(EVENT_CONFIG[event]["races"].keys()))

        year = st.selectbox("📅 Année", EVENT_CONFIG[event]["races"][course]["year"])

        st.success(f"Vous avez choisi **{event} – {course} – {year}**")

        # Sauvegarde en session_state
        st.session_state["event"] = event
        st.session_state["course"] = course
        st.session_state["year"] = year
        st.session_state["event_code"] = EVENT_CONFIG[event]['tenant']
        st.session_state["course_code"] = EVENT_CONFIG[event]['races'][course]["code"]
        event_code=st.session_state["event_code"]
        course_code=st.session_state["course_code"]
        config = get_config(f"data/TrailPacer/{event_code}/{course_code}/config/config_{year}.json")
        st.session_state["config"]=config
        df = load_data(event=event_code,race=course_code, year=year)
        st.session_state['df']=df
        st.session_state["df_gpx"], st.session_state["has_terrain_type"] =get_df_for_gpx()
