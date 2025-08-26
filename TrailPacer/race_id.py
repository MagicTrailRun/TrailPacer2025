import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
description_type={
    'T1' : "Sentier de randonnée",
    "R" : "Route",
    "F" :"Chemin forestier",
    "T" : "Sentier",
    "T2" : "Sentier de montagne"
}

description_pente = {
    'D4' : (-1000, -20), 
    'D3' : (-20, -10),
    'D2' : (-10, -5),
    'D1' : (-5, 0),
    'M1' : (0, 5),
    'M2' : (5, 10),
    'M3' : (10, 20),
    'M4' : (20, 1000)     
}
pentes= list(description_pente.keys())
terrains=list(description_type.keys())

def load_data_checkpoints(csv_file="utmb_checkpoints.csv"):
    """Charge le CSV et parse les dates"""
    df = pd.read_csv(csv_file, parse_dates=['dateFirstRunners','dateLastRunners'])
    return df

def process_data(df):
    """Traite et nettoie les données"""
    # Convertir les dates
    df['dateFirstRunners'] = pd.to_datetime(df['dateFirstRunners'], errors='coerce')
    df['dateLastRunners'] = pd.to_datetime(df['dateLastRunners'], errors='coerce')
    df['cutoff'] = pd.to_datetime(df['cutoff'], errors='coerce')
    
    # Calculer les durées
    if not df['dateFirstRunners'].isna().all() and not df['dateLastRunners'].isna().all():
        df['duree_passage'] = (df['dateLastRunners'] - df['dateFirstRunners']).dt.total_seconds() / 3600
    
    # Distance en km
    df['distance_km'] = df['distance'] / 1000
    df['distCum_km'] = df['distCum'] / 1000
    
    return df





def plot_segment_analysis(df):
    """
    Analyse segmentaire interactive : D+/km, D-/km
    """
    # Calcul des ratios (en m / km)
    df["D+_per_km"] = df["D+CP"] / (df["distCP"] / 1000)
    df["D-_per_km"] = df["D-CP"] / (df["distCP"] / 1000)

    fig = go.Figure()

    # Barres D+
    fig.add_trace(go.Bar(
        x=df["shortName"],
        y=df["D+_per_km"],
        name="D+ / km",
        marker_color="orange",
        hovertemplate="Segment: %{x}<br>D+/km: %{y:.1f}<extra></extra>"
    ))

    # Barres D-
    fig.add_trace(go.Bar(
        x=df["shortName"],
        y=-df["D-_per_km"],  # négatif pour les descentes
        name="D- / km",
        marker_color="blue",
        hovertemplate="Segment: %{x}<br>D-/km: %{y:.1f}<extra></extra>"
    ))

    fig.update_layout(
        title="Répartition du dénivelé par km (D+/km et D-/km)",
        xaxis_title="Segments",
        yaxis_title="Dénivelé par km (m/km)",
        barmode="relative",
        bargap=0.3,
        template="plotly_white"
    )

    return fig




     



def load_gpx(pth):

    with open(pth, "r", encoding="utf-8") as f:
        data = json.load(f)

    list_segments = data.get("segments", [])
    segments = list_segments[0].get('segment')

    df_segments = pd.DataFrame([
    {
        "distance": seg[0],   # m depuis départ
        "altitude": seg[1],   # m
        "lon": seg[2][0],
        "lat": seg[2][1],
        "D+": seg[3][0],
        "D-": seg[3][1],
        "pente": seg[4],
        "type": seg[5]
    }
    for seg in segments
    ])
    return(df_segments)


def plot_slope_histogram(df_gpx):

    
    # Histogramme avec couleurs selon pente positive ou négative
    df_gpx['slope_type'] = np.where(df_gpx['pente'] >= 0, 'Montée', 'Descente')
    df_gpx['segment_km'] = df_gpx['distance'].diff().fillna(0) / 1000  

    # Histogramme pondéré par la distance des segments
    fig = px.histogram(
        df_gpx,
        x='pente',
        nbins=50,
        color='slope_type',
        color_discrete_map={'Montée': 'green', 'Descente': 'blue'},
        title="Répartition des pentes sur tout le parcours",
        labels={'pente': 'Pente (%)', 'y': 'Distance (km)'},
        histfunc="sum",              # somme des valeurs pondérées
        barnorm=None,
        opacity=0.9,
        marginal=None,
        facet_row=None,
        facet_col=None,
        facet_col_wrap=None,
        barmode="overlay",
        height=500,
        hover_data=['segment_km']
    )

    fig.update_layout(
        xaxis_title="Pente (%)",
        yaxis_title="Distance (km)",
        bargap=0.05
    )

    return fig




def altitude_metrics(df_gpx, seuil=2000):
    """
    Retourne la proportion du parcours au-dessus et en-dessous d'un seuil d'altitude
    """
    df = df_gpx.copy()
    df["delta_dist"] = df["distance"].diff().fillna(0)

    total_dist = df["delta_dist"].sum()
    dist_above = df.loc[df["altitude"] >= seuil, "delta_dist"].sum()
    dist_below = total_dist - dist_above

    pct_above = dist_above / total_dist * 100
    pct_below = dist_below / total_dist * 100

    return pct_above, pct_below


def plot_col_profile_tour_style(df_segments, df_track, col_name="Col Ferret"):
    # Récupérer distance_start et distance_end depuis df_track
    mask = df_track["shortName"] == col_name
    if not mask.any():
        print(f"Col '{col_name}' non trouvé dans df_track")
        return go.Figure()
         
    distance_end = df_track.loc[mask, "distance"].values[0]
    idx_end = df_track.index[df_track["distance"] == distance_end][0]
    distance_start = 0 if idx_end == 0 else df_track.loc[idx_end-1, "distance"]
     
    # Filtrer df_segments
    df_col = df_segments[(df_segments["distance"] >= distance_start) & 
                        (df_segments["distance"] <= distance_end)].copy()
    if df_col.empty:
        print("Aucun point dans df_segments pour ce col")
        return go.Figure()
         
    df_col['distance_km'] = df_col["distance"] / 1000
    
    # Créer la figure principale
    fig = go.Figure()
    
    # 1. Zone de remplissage sous la courbe (jaune/orange comme le Tour)
    fig.add_trace(go.Scatter(
        x=df_col["distance_km"],
        y=df_col["altitude"],
        fill='tozeroy',
        fillcolor='rgba(255, 223, 0, 0.8)',  # Jaune Tour de France
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 2. Ligne de profil principale (rouge/bordeaux)
    fig.add_trace(go.Scatter(
        x=df_col["distance_km"],
        y=df_col["altitude"],
        mode='lines',
        line=dict(color='#CC0000', width=4),  # Rouge Tour de France
        name='Profil d\'altitude',
        hovertemplate='<b>Distance:</b> %{x:.1f} km<br>' +
                     '<b>Altitude:</b> %{y:.0f} m<br>' +
                     '<extra></extra>'
    ))
    
    # 3. Ligne noire pour le contour supérieur
    fig.add_trace(go.Scatter(
        x=df_col["distance_km"],
        y=df_col["altitude"],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 4. Ajouter des marqueurs pour les points d'intérêt (pentes importantes)
    steep_points = df_col[abs(df_col["pente"]) > 8]  # Pentes > 8%
    if not steep_points.empty:
        fig.add_trace(go.Scatter(
            x=steep_points["distance_km"],
            y=steep_points["altitude"],
            mode='markers+text',
            marker=dict(
                size=12,
                color='white',
                line=dict(color='black', width=2)
            ),
            text=[f"{p:.0f}%" for p in steep_points["pente"]],
            textposition="top center",
            textfont=dict(size=10, color='black', family='Arial Black'),
            name='Pentes raides',
            showlegend=False,
            hovertemplate='<b>Pente:</b> %{text}<br>' +
                         '<b>Distance:</b> %{x:.1f} km<br>' +
                         '<b>Altitude:</b> %{y:.0f} m<br>' +
                         '<extra></extra>'
        ))
    
    # 5. Grille verticale (comme sur les profils Tour de France)
    max_alt = df_col["altitude"].max()
    min_alt = df_col["altitude"].min()
    
    # Lignes verticales tous les kilomètres
    for km in range(int(df_col["distance_km"].min()), int(df_col["distance_km"].max()) + 1):
        fig.add_vline(
            x=km,
            line=dict(color="rgba(128, 128, 128, 0.3)", width=1, dash="dot"),
            layer="below"
        )
    
    # 6. Configuration du layout dans le style Tour de France
    fig.update_layout(
        title=dict(
            text=f"<b>{col_name}</b><br><sub>Profil d'altitude - Style Tour de France</sub>",
            x=0.5,
            font=dict(size=24, color='black', family='Arial Black')
        ),
        
        # Axes
        xaxis=dict(
            title="Distance (km)",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.3)",
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=14, color='black', family='Arial'),
            title_font=dict(size=16, color='black', family='Arial Black')
        ),
        
        yaxis=dict(
            title="Altitude (m)",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.3)",
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=14, color='black', family='Arial'),
            title_font=dict(size=16, color='black', family='Arial Black')
        ),
        
        # Style général
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        width=1000,
        
        # Légende
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.02,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=10)
        ),
        
        # Marges
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # 7. Ajouter les informations statistiques en annotations
    total_distance = df_col["distance_km"].max() - df_col["distance_km"].min()
    elevation_gain = max(0, df_col["altitude"].max() - df_col["altitude"].min())
    avg_gradient = (elevation_gain / (total_distance * 1000)) * 100 if total_distance > 0 else 0
    max_gradient = df_col["pente"].max()
    
    # Boîte d'informations
    info_text = (f"<b>Distance:</b> {total_distance:.1f} km<br>"
                f"<b>Dénivelé:</b> +{elevation_gain:.0f} m<br>"
                f"<b>Pente moy.:</b> {avg_gradient:.1f}%<br>"
                f"<b>Pente max:</b> {max_gradient:.1f}%")
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=info_text,
        showarrow=False,
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="black",
        borderwidth=2,
        font=dict(size=12, color='black', family='Arial'),
        align="left",
        xanchor="left",
        yanchor="top"
    )
    
    return fig

# Version alternative avec gradient de couleur selon la pente
# Version avec ligne colorée selon la pente et remplissage correct des terrains
# Version avec ligne colorée selon la pente et remplissage correct des terrains
# Version avec ligne colorée selon la pente et remplissage correct des terrains
def plot_col_profile_tour_gradient(df_segments, df_track, col_name="Col Ferret"):
    # Même début que la fonction précédente...
    mask = df_track["shortName"] == col_name
    if not mask.any():
        print(f"Col '{col_name}' non trouvé dans df_track")
        return go.Figure()
         
    distance_end = df_track.loc[mask, "distance"].values[0]
    idx_end = df_track.index[df_track["distance"] == distance_end][0]
    distance_start = 0 if idx_end == 0 else df_track.loc[idx_end-1, "distance"]
     
    df_col = df_segments[(df_segments["distance"] >= distance_start) & 
                        (df_segments["distance"] <= distance_end)].copy()
    if df_col.empty:
        print("Aucun points dans df_segments pour ce col")
        return go.Figure()
         
    df_col['distance_km'] = df_col["distance"] / 1000
    
    # Trouver l'altitude minimale du tronçon
    altitude_min = df_col["altitude"].min()
    
    fig = go.Figure()
    
    # Définir les couleurs et descriptions pour chaque type de terrain
    description_type = {
        'T1': "Sentier de randonnée",
        "R": "Route",
        "F": "Chemin forestier",
        "T": "Sentier",
        "T2": "Sentier de montagne"
    }
    
    terrain_colors = {
        'T1': 'rgba(34, 139, 34, 0.6)',       # Vert pour sentier de randonnée
        'R': 'rgba(128, 128, 128, 0.6)',      # Gris pour route
        'F': 'rgba(139, 69, 19, 0.6)',        # Marron pour chemin forestier
        'T': 'rgba(255, 140, 0, 0.6)',        # Orange pour sentier
        'T2': 'rgba(178, 34, 34, 0.6)',       # Rouge pour sentier de montagne
        'default': 'rgba(255, 223, 0, 0.5)'   # Jaune par défaut
    }
    
    # Créer le remplissage par type de terrain (SOUS la ligne de profil) - point par point
    # Traiter chaque segment continu du même type de terrain
    current_terrain = None
    segment_start_idx = 0
    terrain_added = set()  # Pour éviter les doublons dans la légende
    
    for i in range(len(df_col) + 1):
        # Déterminer si on change de terrain ou si on arrive à la fin
        if i == len(df_col) or df_col.iloc[i]['type'] != current_terrain:
            # Terminer le segment précédent s'il existe
            if current_terrain is not None and i > segment_start_idx:
                terrain_segment = df_col.iloc[segment_start_idx:i]
                color = terrain_colors.get(current_terrain, terrain_colors['default'])
                description = description_type.get(current_terrain, current_terrain)
                
                # Créer le polygone segment par segment pour éviter les dépassements
                x_coords = terrain_segment["distance_km"].tolist()
                y_coords = terrain_segment["altitude"].tolist()
                
                # Polygone : profil -> base (inverse) -> fermeture
                x_polygon = x_coords + x_coords[::-1]
                y_polygon = y_coords + [altitude_min] * len(x_coords)
                
                # N'afficher dans la légende que la première occurrence de chaque terrain
                show_legend = current_terrain not in terrain_added
                if show_legend:
                    terrain_added.add(current_terrain)
                
                fig.add_trace(go.Scatter(
                    x=x_polygon,
                    y=y_polygon,
                    fill='toself',
                    fillcolor=color,
                    line=dict(width=0),
                    name=f'{description}',
                    showlegend=show_legend,
                    legendgroup=current_terrain,
                    hoverinfo='skip'
                ))
            
            # Commencer un nouveau segment
            if i < len(df_col):
                current_terrain = df_col.iloc[i]['type']
                segment_start_idx = i
    
    # LIGNE COLORÉE SELON LA PENTE - segments individuels
    n_segments = len(df_col) - 1
    
    for i in range(n_segments):
        x_start = df_col.iloc[i]["distance_km"]
        x_end = df_col.iloc[i+1]["distance_km"]
        y_start = df_col.iloc[i]["altitude"]
        y_end = df_col.iloc[i+1]["altitude"]
        pente = df_col.iloc[i]["pente"]
        
        # Déterminer la couleur selon la pente
        if pente < -5:
            color = '#00AA00'  # Vert foncé pour forte descente
        elif pente < 0:
            color = '#66FF66'  # Vert clair pour descente légère
        elif pente < 5:
            color = "#6E6E40"  # Jaune pour plat/montée légère
        elif pente < 10:
            color = '#FF6600'  # Orange pour montée modérée
        else:
            color = '#CC0000'  # Rouge foncé pour forte montée
        
        # Segment de ligne coloré avec hover amélioré
        fig.add_trace(go.Scatter(
            x=[x_start, x_end],
            y=[y_start, y_end],
            mode='lines',
            line=dict(
                color=color,
                width=4
            ),
            showlegend=False,
            hovertemplate=f'<b>Pente:</b> {pente:.1f}%<br>' +
                         f'<b>Distance:</b> {x_start:.1f}-{x_end:.1f} km<br>' +
                         f'<b>Altitude:</b> {y_start:.0f}-{y_end:.0f} m<br>' +
                         f'<b>Terrain:</b> {df_col.iloc[i]["type"]} ({description_type.get(df_col.iloc[i]["type"], df_col.iloc[i]["type"])})<br>' +
                         '<extra></extra>'
        ))
    

    # Points de données pour hover détaillé avec info terrain
    fig.add_trace(go.Scatter(
        x=df_col["distance_km"],
        y=df_col["altitude"],
        mode='markers',
        marker=dict(
            size=4,
            color='black',
            opacity=0
        ),
        name='Points de mesure',
        showlegend=False,
        hovertemplate='<b>Distance:</b> %{x:.1f} km<br>' +
                     '<b>Altitude:</b> %{y:.0f} m<br>' +
                     '<b>Pente:</b> %{customdata[0]:.1f}%<br>' +
                     '<b>Terrain:</b> %{customdata[1]} (%{customdata[2]})<br>' +
                     '<extra></extra>',
        customdata=[[p, t, description_type.get(t, t)] for p, t in zip(df_col["pente"], df_col["type"])]
    ))
    
    # Configuration du layout
    fig.update_layout(
        title=dict(
            text=f"<b>{col_name}</b><br><sub>Profil altimétrique avec gradient de pente</sub>",
            x=0.5,
            font=dict(size=24, color='black', family='Arial Black')
        ),
        xaxis=dict(
            title="Distance (km)",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.3)",
            tickfont=dict(size=14, family='Arial')
        ),
        yaxis=dict(
            title="Altitude (m)",
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.3)",
            tickfont=dict(size=14, family='Arial'),
            range=[altitude_min - 20, df_col["altitude"].max() + 20]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        width=1000,
        margin=dict(l=60, r=60, t=80, b=60),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # Annotation pour le code couleur des pentes
    fig.add_annotation(
        text="<b>Gradient de pente:</b><br>" +
             "<span style='color:#00AA00'>■</span> Forte descente (&lt;-5%)<br>" +
             "<span style='color:#66FF66'>■</span> Descente (-5% à 0%)<br>" +
             "<span style='color:#FFFF00'>■</span> Plat/montée légère (0-5%)<br>" +
             "<span style='color:#FF6600'>■</span> Montée modérée (5-10%)<br>" +
             "<span style='color:#CC0000'>■</span> Forte montée (&gt;10%)",
        xref="paper", yref="paper",
        x=1.02, y=0.4,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=10),
        bordercolor="black",
        borderwidth=1,
        bgcolor="rgba(255,255,255,0.9)"
    )
    alt_metrics = {
    "Altitude min": f"{int(df_col['altitude'].min())} m 🏔️",
    "Altitude médiane": f"{int(df_col['altitude'].median())} m 🏞️",
    "Altitude max": f"{int(df_col['altitude'].max())} m ⛰️",

}

    pente_metrics = {
        "Pente min": df_col['pente'].min(),
        "Pente médiane": df_col['pente'].median(),
        "Pente max": df_col['pente'].max()
    }
    metrics = [alt_metrics,pente_metrics]

    return fig, metrics



import streamlit as st

def color_pente(val):
        if val < -5:
            return '#00AA00'  # Vert foncé pour forte descente
        elif val < 0:
            return '#66FF66'  # Vert clair pour descente légère
        elif val < 5:
           return "#6E6E40"  # Jaune pour plat/montée légère
        elif val < 10:
            return '#FF6600'  # Orange pour montée modérée
        else:
            return '#CC0000'  # Rouge foncé pour forte montée
        