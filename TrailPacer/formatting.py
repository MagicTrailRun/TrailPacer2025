import streamlit as st
import pandas as pd

import base64 


def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        print(f"⚠️ Image non trouvée : {image_path}")
        return None


def format_time_input_to_seconds(time_str):
    """Convertit une entrée HH:MM en secondes"""
    try:
        if ':' in time_str:
            h, m = map(int, time_str.split(':'))
            return h * 3600 + m * 60
        return int(time_str) * 3600
    except:
        return 0

def seconds_to_time_str(seconds):
    """Convertit des secondes en HHhMM"""
    h, m = divmod(seconds // 60, 60)
    return f"{h:02d}h{m:02d}"

def decimal_to_hhmm(x):
    if pd.isna(x):
        return ""
    heures = int(x)
    minutes = int(round((x - heures) * 60))
    return f"{heures}h{minutes:02d}"
def format_pace(time_h, dist_km):
    """
    time_h : temps en heures (float)
    dist_km : distance en km (float)
    Retourne une string du type "m'ss/km" ou "" si dist=0
    """
    if dist_km == 0 or pd.isna(dist_km) or pd.isna(time_h):
        return ""
    pace_min = (time_h * 60) / dist_km
    minutes = int(pace_min)
    seconds = int((pace_min - minutes) * 60)
    return f"{minutes}'{seconds:02d}/km"


def format_dataframe(df,target_time):
    print(df.columns[:10])
    col_temps_secteur = f"temps_secteur_{target_time}"
    col_temps_secteur_med = f"temps_secteur_med_{target_time}"
    col_temps_total = f"temps_cumule_med_{target_time}"
    col_heure_passage = f"heure_passage_{target_time}"

    if col_temps_secteur_med in df.columns:
        df["Allure secteur"] = df.apply(
            lambda row: format_pace(row[col_temps_secteur_med], row["dist_secteur"]),
            axis=1
        )
        df_display = df[[
            "checkpoint",
            "dist_total",
            "dist_secteur",
            "dplus_secteur",
            "dmoins_secteur",
            col_temps_total,
            col_temps_secteur,
            "Allure secteur",
            col_heure_passage
        ]]
        column_config={ 
                    "dist_total": st.column_config.NumberColumn("Km total", format="%.1f"),
                    "dist_secteur": st.column_config.NumberColumn("Km secteur", format="%.1f"),
                    "dplus_secteur": st.column_config.NumberColumn("D+ secteur", format="%d"),
                    "dmoins_secteur": st.column_config.NumberColumn("D- secteur", format="%d"),
                    col_temps_secteur: st.column_config.TextColumn("Temps secteur"),
                    "Allure secteur": st.column_config.TextColumn("Allure secteur"),
                    col_temps_total: st.column_config.TextColumn("Temps cumulé cible"),
                    col_heure_passage: st.column_config.TextColumn("Heure passage"),
                    "barriere_horaire_hhmm" : st.column_config.TextColumn('Barrière horaire')
                }
        if "barriere_horaire" in df.columns:
            print(df["barriere_horaire"])
            df_display["barriere_horaire_hhmm"] = df["barriere_horaire"].dropna().map(decimal_to_hhmm)
            column_config["barriere_horaire_hhmm"] = st.column_config.TextColumn("Barrière horaire")
        elif "fermeture" in df.columns:
            print(df["fermeture"])
            df_display["barriere_horaire_hhmm"] = df["fermeture"].dropna()
            column_config["barriere_horaire_hhmm"] = st.column_config.TextColumn("Barrière horaire")     
    return(df_display, column_config)

def normalize_ckpts(df, col, mapping, drop_ckpts=None):
    """
    Harmonise les noms de checkpoints + supprime ceux à ignorer.
    """
    # Harmoniser les noms
    df[col] = df[col].replace(mapping)

    # Supprimer les checkpoints non souhaités
    if drop_ckpts is not None:
        df = df.loc[~df[col].isin(drop_ckpts)]

    return df


