import pandas as pd
import numpy as np
import json
import streamlit as st
from TrailPacer.race_id import  get_df_for_gpx
import os
from pathlib import Path
@st.cache_data
def load_data(event,race="UTMB",year=2025, version="vf"):
    """Charge les données CSV"""
    try:
        csv_path = f"data/TrailPacer/{event}/{race}/pred_pacing/pred_{year}_{version}.csv"
        df = pd.read_csv(csv_path)
        df_checkpoints=pd.read_csv(f"data/TrailPacer/{event}/{race}/checkpoints/detail_checkpoints_{year}.csv")
        if "checkpoint" in df.columns:
            df = df.drop_duplicates(subset=["checkpoint"], keep="first")
            df["checkpoint"]=df["checkpoint"].str.strip()
        df_checkpoints["checkpoint"]=df_checkpoints["checkpoint"].str.strip()
        if "ravitaillement" in df_checkpoints.columns :
            df=df.merge(df_checkpoints[["checkpoint", "ravitaillement"]], on="checkpoint")
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data
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
        # Utilisez st.container pour le placer en dernier
        st.markdown("<br>" * 10, unsafe_allow_html=True)  # Spacer
        st.markdown(
            """
            <div style="
                width: 100%;
                text-align: center;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 5px;
            ">
                    📱 Suivez-nous sur les réseaux
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 10px;">
                    <a href="https://www.instagram.com/trail_pacer/" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style="transition: transform 0.2s;"
                       onmouseover="this.style.transform='scale(1.1)'"
                       onmouseout="this.style.transform='scale(1)'">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" 
                             width="30" height="30" alt="Instagram">
                    </a>
                    <a href="https://www.facebook.com/TrailPacer.IA" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       style="transition: transform 0.2s;"
                       onmouseover="this.style.transform='scale(1.1)'"
                       onmouseout="this.style.transform='scale(1)'">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg" 
                             width="30" height="30" alt="Facebook">
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
def select_event():
    # --- CSS custom pour le container et les selects
    st.markdown("""
    <style>
    /* --------- CONTAINER PRINCIPAL --------- */
    .event-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin: 1.5rem 0 2rem 0;
        transition: box-shadow 0.3s ease;
    }

    .event-container:hover {
        box-shadow: 0 6px 22px rgba(46,125,50,0.25);
    }

    /* --------- TITRE --------- */
    .event-container h3 {
        color: #2E7D32;
        font-weight: 700;
        margin-bottom: 1.2rem;
        text-align: center;
    }

    /* --------- SELECTBOX --------- */
    div[data-baseweb="select"] {
        background-color: #f9f9f9;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 6px 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.25s ease;
    }

    div[data-baseweb="select"]:hover {
        border: 2px solid #2E7D32;
        box-shadow: 0 4px 10px rgba(46,125,50,0.25);
    }

    div[data-baseweb="select"] span {
        font-size: 1.05em;
        font-weight: 500;
        color: #333;
    }

    /* --------- LABELS --------- */
    label {
        font-size: 1.05em !important;
        font-weight: 600 !important;
        color: #1B5E20 !important;
    }

    /* --------- MESSAGE DE VALIDATION --------- */
    .success-message {
        background-color: #E8F5E9;
        color: #1B5E20;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        border-left: 5px solid #2E7D32;
        font-weight: 500;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Définition des events/courses
    EVENT_CONFIG = st.session_state.get("EVENT_CONFIG", {})
    if not EVENT_CONFIG:
        st.error("Aucune configuration d'événement trouvée")
        return

    # --- CONTENU DU CONTAINER
    st.markdown('<div class="event-container">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sélectionnez votre événement Trail</h3>", unsafe_allow_html=True)

    event = st.selectbox("🏔️ Événement", list(EVENT_CONFIG.keys()))
    course = st.selectbox("🏃‍♀️ Course", list(EVENT_CONFIG[event]["races"].keys()))
    year = st.selectbox("📅 Année", EVENT_CONFIG[event]["races"][course]["year"])

    st.markdown(
        f'<div class="success-message">✅ Vous avez choisi <strong>{event}</strong> – <strong>{course}</strong> – <strong>{year}</strong></div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)  # fermeture du container

    # --- Sauvegarde en session_state
    st.session_state["event"] = event
    st.session_state["course"] = course
    st.session_state["year"] = year
    st.session_state["event_code"] = EVENT_CONFIG[event]['tenant']
    st.session_state["course_code"] = EVENT_CONFIG[event]['races'][course]["code"]
    st.session_state["post_course_year"] = EVENT_CONFIG[event]["races"][course]["post_course_year"]

    event_code = st.session_state["event_code"]
    course_code = st.session_state["course_code"]
    config = get_config(f"data/TrailPacer/{event_code}/{course_code}/config/config_{year}.json")
    st.session_state["config"] = config

    df = load_data(event=event_code, race=course_code, year=year)
    st.session_state['df'] = df

    tracks_dir = Path(f"data/TrailPacer/{event_code}/{course_code}/tracks/")
    track_file_json = tracks_dir / f"track_{year}.json"
    track_tile_csv = tracks_dir / f"track_{year}.csv"
    track_file_gpx = tracks_dir / f"gpx_{year}.gpx"

    # On calcule un "file_hash" basé sur la date de modification
    file_hash = None
    for f in [track_file_json, track_tile_csv, track_file_gpx]:
        if f.exists():
            file_hash = os.path.getmtime(f)
            break

    df_gpx, has_terrain_type = get_df_for_gpx(event_code, course_code, year, file_hash)
    st.session_state["df_gpx"] = df_gpx
    st.session_state["has_terrain_type"] = has_terrain_type
