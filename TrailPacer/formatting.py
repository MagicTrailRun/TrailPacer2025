import streamlit as st
import pandas as pd
import numpy as np
import base64 

def image_to_base64(path):
    """Convertit une image locale en base64 pour affichage inline"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
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
    df["temps_secteur_high"] = df["temps_norm_high"] * target_time
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




    df["Allure segment"] = df.apply(lambda r: format_pace(r["temps_secteur_med"], r["dist_secteur"]), axis=1)
    df = get_pacing_temps_cible(df, start_time)

    # --- Arrondis ---
    df = df.assign(
    dist_secteur = df["dist_secteur"].round(1),
    dplus_secteur = df["dplus_secteur"].round(1),
    dmoins_secteur = df["dmoins_secteur"].round(1)
    )
    if "ravitaillement" in df.columns:
        df["icon_ravito"] = np.where(df["ravitaillement"] == "Oui", ":material/water_bottle:", "")
    else:
        df["icon_ravito"] = ""
    # --- Colonnes texte ---
    df["Segment (Km – Nom)"] = (
    "**" + df["dist_total"].round(1).astype(str) + " km** – " + df["checkpoint"] + " " + df["icon_ravito"]
)

    df["Temps segment (± 5%)"] = (
        df["temps_secteur_med_fmt"] + " (" + df["temps_secteur_low_fmt"] + "-" + df["temps_secteur_high_fmt"] + ")"
    )


    df.set_index("Segment (Km – Nom)", inplace=True)
    # --- Table affichage ---
    df_display = df[[
       # "Segment (Km – Nom)",
        "dist_secteur",
        "dplus_secteur",
        "dmoins_secteur",
        "Temps segment (± 5%)",
        "Temps de course cumulé",
        "heure_passage",
        "Allure segment",
        "Barrière horaire"
    ]]

    df_display=df_display.copy()
    df_display.rename(
        columns={
            "dist_secteur": "Km segment",
            "dplus_secteur": "D+ segment",
            "dmoins_secteur": "D- segment",
            "heure_passage": "Heure de passage",
        },
        inplace=True
    )
    df_display=df_display.copy()
    # --- Ajouter colonne barrière horaire si dispo ---
    df_display['Km segment'] = df_display['Km segment'].apply(lambda x: f"{x:.1f}")
    df_display['D+ segment'] = df_display['D+ segment'].apply(lambda x: f"{x:.1f}")
    df_display['D- segment'] = df_display['D- segment'].apply(lambda x: f"{x:.1f}")
    #df_display.set_index("Segment (Km – Nom)", inplace=True)
    # --- Config colonnes ---
    
    return df, df_display




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

    df_pred[f"Temps de course cumulé"] = df_pred[f"temps_cumule_med"].apply(format_hr_to_time)

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


def show_hero_banner(event=None, course=None, event_code=None):
    if event is None :
        img_base64=get_base64_image(f"TrailPacer/image/banner_image.png")
    else :
        img_base64 = get_base64_image(f"TrailPacer/image/{event_code.lower()}.png")
    background_style = (
        f"background-image: url('data:image/png;base64,{img_base64}');"
        if img_base64
        else "background: linear-gradient(135deg, #1e3a8a, #3b82f6);"
    )

    st.markdown(
        f"""
        <style>
        .hero {{
            position: relative;
            width: 100%;
            height: 280px;
            {background_style}
            background-size: cover;
            background-position: center;
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 1.5rem;
        }}
        .hero h1 {{
            font-size: clamp(2rem, 4vw, 3.5rem);
            font-weight: 800;
            text-shadow: 2px 2px 10px rgba(0,0,0,0);
            margin: 0;
            color: white;
            font-size: 3em;
            font-weight: bold;
            text-shadow: 2px 2px 8px #000;
        }}
        .hero h2, .hero h3 {{
            font-size: clamp(1.3rem, 2.5vw, 2rem);
            color: white;
            font-size: 2em;
            font-weight: 500;
            text-shadow: 2px 2px 6px #000;
            margin: 0;
        }}
        .hero-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(0,0,0,0);
            border-radius: 16px;
        }}
        </style>

        <div class="hero" role="banner" aria-label="En-tête événement {event} style="margin:0; padding:0;">">
            <div class="hero-overlay"></div>
            <h1>TrailPacer</h1>
            <h2>{event}</h2>
            <h3>{course}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

