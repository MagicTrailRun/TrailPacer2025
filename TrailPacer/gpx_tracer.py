
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def plot_altitude_profile_area(df_gpx, df,  mapping_ckpts, config,affichages=None,target_time=None,show_title=True):
    """
    Profil d'altitude avec checkpoints et heures de passage
    """
    min_alt=df_gpx["altitude"].min()-100
    df_gpx['distance_km']=df_gpx['distance']/ 1000  
    # profil de base
    fig = px.area(
        df_gpx,
        x="distance_km",   # km
        y="altitude",   # m
        labels={"distance": "Distance (km)", "altitude": "Altitude (m)"}
    )
    fig.update_traces( line=dict(color="#2E86AB", width=2),
        fillcolor="rgba(46,134,171,0.3)")
    fig.update_layout(
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="black"),
        title="Profil d'élévation course avec checkpoints et heures de passage" if show_title else "",
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=40),
        yaxis=dict(range=[min_alt , df_gpx["altitude"].max() + 200])  # marge haute
    )
    ## add start
    start_texts = []
    if affichages:
        if "Heure de passage" in affichages:
            start_texts.append(config.get("start_day_hour", "0h00"))
        if "Temps de passage" in affichages:
            start_texts.append("0h00")
    start_label = "<br>".join(start_texts) if start_texts else config["start"]

    fig.add_trace(go.Scatter(
        x=[0], y=[np.interp(0, df_gpx["distance_km"], df_gpx["altitude"])],
        mode="markers+text",
        marker=dict(color="red", size=8, symbol="triangle-up"),
        text=[start_label],
        textposition="top center",
        name=config["start"]
    ))
    fig.add_annotation(
                x=0,
                y=min_alt, 
                text= config['start'],
                textangle=0,  
                showarrow=False,
                font=dict(size=10, color="black"),
                xanchor="center",
                yanchor="top"
            )
    # --- Ajout des checkpoints ---
    for idx, row in df.iterrows():
        name = mapping_ckpts.get(row["Point de passage"], row["Point de passage"])
        dist = row.get("dist_total", None)
        if pd.isna(dist):
            continue
        ele = np.interp(dist, df_gpx["distance_km"], df_gpx["altitude"])

        # Texte dynamique selon choix utilisateur
        texts_h = []
        if affichages:
            if "Heure de passage" in affichages :
                heure_passage_col = f'heure_passage_{target_time}'
                texts_h.append(str(row[heure_passage_col]))
            if "Temps de passage" in affichages :
                temps_passage_col = f'temps_cumule_med_{target_time}'
                texts_h.append(str(row[temps_passage_col]))
            if "D+" in affichages:
                texts_h.append(f"D+ {row['d_plus_total']} m")
            if "D-" in affichages:
                texts_h.append(f"D- {row['d_moins_total']} m")

        label_h = "<br>".join(texts_h) if texts_h else name
  
     
        # Marqueur sur le profil
        fig.add_trace(go.Scatter(
            x=[dist], y=[ele],
            mode="markers+text",
            marker=dict(color="red", size=8, symbol="0"),
            text=[label_h],
            textposition="top center",
            name=name,
            showlegend=False
        ))

        if idx % 2 == 0:
            y_pos = min_alt * 1   # un peu au-dessus
        else:
            y_pos = min_alt * 1.1  # un peu plus haut

        fig.add_annotation(
            x=dist,
            y=y_pos,
            text=name if label_h!=name else '',
            textangle=0,
            showarrow=False,
            font=dict(size=10, color="black"),
            xanchor="center",
            yanchor="top"
        )

    return fig




