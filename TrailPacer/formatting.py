import streamlit as st
import pandas as pd

import base64 

def image_to_base64(path):
    """Convertit une image locale en base64 pour affichage inline"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

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

def format_dataframe(df, target_time, start_time):
    # --- Calcul des temps ---
    df["temps_secteur_med"] = df["temps_norm_med"] * target_time
    df["temps_cumule_med"] = df["temps_secteur_med"].cumsum()
    df["temps_secteur_low"] = df["temps_norm_low"] * target_time
    df["temps_cumule_low"] = df["temps_secteur_low"].cumsum()
    df["temps_secteur_high"] = df["temps_norm_high"] * target_time
    df["temps_cumule_high"] = df["temps_secteur_high"].cumsum()
        # --- 🛑 Vérification barrière horaire ---
    if "barriere_horaire" in df.columns:
        # Comparer le temps cumulé médian à la barrière
        df["hors_barriere"] = df["temps_cumule_med"] > df["barriere_horaire"]

        # Option : tronquer les temps pour ne jamais dépasser la barrière
        df.loc[df["hors_barriere"], "temps_cumule_med"] = df.loc[df["hors_barriere"], "barriere_horaire"]
        
                # ✅ Calculer le temps restant avant barrière
        df["temps_restant"] = df["barriere_horaire"] - df["temps_cumule_med"]

        # Créer un statut enrichi
        def statut_barriere(row):
            bh=decimal_to_hhmm(row.barriere_horaire)
            if row["temps_restant"] <= 5/60 and bh!='0h00' :  # 5 minutes = 5/60 h
                return f"⚠️ {bh} "
            else:
                return bh
        
        df["Barrière horaire"]=df.apply(statut_barriere, axis=1)




    df["Allure secteur"] = df.apply(lambda r: format_pace(r["temps_secteur_med"], r["dist_secteur"]), axis=1)
    df = get_pacing_temps_cible(df, start_time)

    # --- Arrondis ---
    df['dist_secteur'] = df['dist_secteur'].round(1)
    df['dplus_secteur'] = df['dplus_secteur'].round(1)
    df['dmoins_secteur'] = df['dmoins_secteur'].round(1)

    # --- Colonnes texte ---
    df["Segment (Km – Nom)"] = df.apply(lambda x: f"{x['dist_total']:.1f} km – {x['checkpoint']}", axis=1)
    df["Temps de course au passage (± 5%)"] = df.apply(
        lambda x: f"{x['temps_cumule_med_fmt']} ({x['temps_cumule_low_fmt']}-{x['temps_cumule_high_fmt']})", axis=1
    )
    df["Temps segment (± 5%)"] = df.apply(
        lambda x: f"{x['temps_secteur_med_fmt']} ({x['temps_secteur_low_fmt']}-{x['temps_secteur_high_fmt']})", axis=1
    )


    # --- Table affichage ---
    df_display = df[[
        "Segment (Km – Nom)",
        "dist_secteur",
        "dplus_secteur",
        "dmoins_secteur",
        "heure_passage",
        "Temps de course au passage (± 5%)",
        "Temps segment (± 5%)",
        "Allure secteur",
        "Barrière horaire"
    ]]

    df_display.rename(
        columns={
            "dist_secteur": "Km segment",
            "dplus_secteur": "D+ segment",
            "dmoins_secteur": "D- segment",
            "heure_passage": "Heure de passage estimée",
        },
        inplace=True
    )

    # --- Ajouter colonne barrière horaire si dispo ---



    # --- Config colonnes ---
    column_config = { 
        "Segment (Km – Nom)": st.column_config.TextColumn("Segment (Km – Nom)", pinned=True),
        "Km segment": st.column_config.TextColumn("Km segment", width="small"),
        "D+ segment": st.column_config.TextColumn("D+ segment (m)", width="small"),
        "D- segment": st.column_config.TextColumn("D- segment (m)", width="small"),
        "Heure de passage estimée": st.column_config.TextColumn("Heure de passage estimée", width="small"),
        "Barrière horaire": st.column_config.TextColumn("Barrière horaire", width="small"),
    }

    return df, df_display, column_config




def get_pacing_temps_cible(df_pred, start_time):
    temps_cumule_med = df_pred["temps_cumule_med"]
    heure_passage = (start_time + pd.to_timedelta(temps_cumule_med, unit="h")).round("min")
    # format : Ven. 15h (locale)
    weekdays = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.", "Dim."]
    heure_str = heure_passage.dt.strftime('%H:%M')   # format "15h"
    jour_str = heure_passage.dt.weekday.map(lambda x: weekdays[x])
    df_pred[f"heure_passage"] = jour_str + " " + heure_str

    # cumulé et secteur (fenêtre low-high)
    df_pred[f"temps_secteur_med_fmt"] = df_pred[f"temps_secteur_med"].apply(format_hr_to_time)
    df_pred[f"temps_secteur_low_fmt"]=df_pred[f"temps_secteur_low"].apply(format_hr_to_time)
    df_pred[f"temps_secteur_high_fmt"]=df_pred[f"temps_secteur_high"].apply(format_hr_to_time)

    df_pred[f"temps_cumule_med_fmt"] = df_pred[f"temps_cumule_med"].apply(format_hr_to_time)
    df_pred[f"temps_cumule_low_fmt"]=df_pred[f"temps_cumule_low"].apply(format_hr_to_time)
    df_pred[f"temps_cumule_high_fmt"]=df_pred[f"temps_cumule_high"].apply(format_hr_to_time)

    return df_pred


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



def format_hr_to_time(x):
    x = int(x*60)
    return f'{x//60}h{x%60:02d}'