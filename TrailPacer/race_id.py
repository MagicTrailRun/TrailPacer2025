import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
from pathlib import Path
import streamlit as st
import xml.etree.ElementTree as ET
from math import radians, cos, sin, sqrt, atan2




@st.cache_data
def load_json(pth):

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






def haversine(lat1, lon1, lat2, lon2):
    """Distance en mètres entre 2 lat/lon."""
    R = 6371000  # rayon Terre en m
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@st.cache_data
def gpx_to_df(gpx_file):
    """Lit un GPX et retourne un DataFrame avec lat, lon, altitude, temps, 
    distance cumulée (3D), pente en %, D+ et D- cumulés."""
    ns = {"default": "http://www.topografix.com/GPX/1/1"}
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    pts = []
    for trkpt in root.findall(".//default:trkpt", ns):
        lat = float(trkpt.attrib["lat"])
        lon = float(trkpt.attrib["lon"])
        ele = float(trkpt.find("default:ele", ns).text or 0)
        pts.append((lat, lon, ele))

    df = pd.DataFrame(pts, columns=["lat", "lon", "altitude"])

    # Distances successives
    dist_2d = [0]
    dist_3d = [0]
    dplus = [0]
    dmoins = [0]
    pente = [0]

    for i in range(1, len(df)):
        d2d = haversine(df.loc[i-1, "lat"], df.loc[i-1, "lon"],
                        df.loc[i, "lat"], df.loc[i, "lon"])
        dh = df.loc[i, "altitude"] - df.loc[i-1, "altitude"]

        d3d = np.sqrt(d2d**2 + dh**2)

        dist_2d.append(d2d)
        dist_3d.append(d3d)

        # pente % sur distance horizontale
        pente.append(100 * dh / d2d if d2d > 0 else np.nan)

        # D+ et D-
        dplus.append(dh if dh > 0 else 0)
        dmoins.append(-dh if dh < 0 else 0)

    df["dist_2d_m"] = dist_2d
    df["dist_3d_m"] = dist_3d
    df["distance"] = df["dist_3d_m"].cumsum()
    df["pente"] = pente
    df["dplus"] = dplus
    df["dmoins"] = dmoins
    df["dplus_cum"] = df["dplus"].cumsum()
    df["dmoins_cum"] = df["dmoins"].cumsum()

    return df






@st.cache_data
def get_df_for_gpx(event_code,course_code,year,file_hash=None):
    tracks_dir = Path(f"data/TrailPacer/{event_code}/{course_code}/tracks/")
    track_tile_csv = tracks_dir / f"track_{year}.csv"
    track_file_gpx = tracks_dir / f"gpx_{year}.gpx"
    track_file_json = tracks_dir / f"track_{year}.json"

    if track_file_json.exists():
        df_gpx = load_json(track_file_json)
        has_terrain_type = True
    elif track_tile_csv.exists():
        df_gpx = pd.read_csv(track_tile_csv)
        has_terrain_type = False
    elif track_file_gpx.exists():
        df_gpx = gpx_to_df(track_file_gpx)
        has_terrain_type = False
    else:
        df_gpx = pd.DataFrame()
        has_terrain_type = False
    return df_gpx, has_terrain_type



@st.cache_data
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

def color_pente(val: float) -> str:
    """Retourne une couleur hex en fonction de la pente (%)"""
    if val < -30:
        return '#000000'  # Noir - descente extrême
    elif val < -20:
        return '#8B0000'  # Rouge foncé descente
    elif val < -15:
        return '#FF6347'  # Rouge clair descente
    elif val < -10:
        return "#67DAE9"
    elif val < -5:
        return '#006400'  # Vert foncé descente
    elif val < 5:
        return '#90EE90'  # Jaune plat / légère montée
    elif val < 10:
        return '#006400' # Orange montée modérée
    elif val < 15:
        return "#67DAE9"
    elif val < 20:
        return '#FF6347'  # Rouge forte montée
    elif val < 30:
        return '#8B0000'  # Rouge très forte montée
    else:
        return '#000000'  # Noir mur infranchissable




# --- Nettoyage des types de terrain ---
def clean_terrain_types(df, known_types=None, default_type='default'):
    if known_types is None:
        known_types = ['T1','T2','T','R','F']
    df = df.copy()
    df['type'] = df['type'].fillna(default_type)
    df.loc[~df['type'].isin(known_types), 'type'] = default_type
    return df

def make_segment_polygon(seg, terrain,  altitude_min,mode,terrain_colors= None, description_type=None,terrain_added=None):
    """
    Construit un polygone (Scatter plotly) pour un segment de terrain donné.
    """
    if mode == "terrain":
        color = terrain_colors.get(terrain, terrain_colors["default"])
        description = description_type.get(terrain, terrain)
        show_legend = terrain not in terrain_added
        if show_legend:
            terrain_added.add(terrain)

    elif mode == "slope":
       
        color = terrain
        description=''
        show_legend=False


    x_coords = seg["distance_km"].tolist()
    y_coords = seg["altitude"].tolist()
    x_poly = x_coords + x_coords[::-1]
    y_poly = y_coords + [altitude_min] * len(x_coords)

    
    return go.Scatter(
        x=x_poly, y=y_poly,
        fill='toself', fillcolor=color,
        line=dict(width=0),
        name=f'{description}',
        showlegend=show_legend,
        #legendgroup=terrain,
        hoverinfo='skip',
        mode='none'
    )
def get_segments_by_terrain(df_col, terrain_colors, description_type, min_length=60):
    """
    Découpe le tracé GPX par type de terrain et crée les polygones de remplissage.
    Les segments trop courts (< min_length) sont considérés comme parasites
    et fusionnés avec le terrain précédent.
    """
    current_terrain = None
    segment_start_idx = 0
    terrain_added = set()
    traces = []

    altitude_min = df_col['altitude'].min()

    for i in range(len(df_col) + 1):
        if i == len(df_col) or df_col.iloc[i]['type'] != current_terrain:
            # Fin de segment
            if current_terrain is not None and i > segment_start_idx:
                seg = df_col.iloc[segment_start_idx:i+1]
                seg_length = seg['distance'].iloc[-1] - seg['distance'].iloc[0]

                if seg_length >= min_length:
                    # vrai segment → on le garde
                    traces.append(
                        make_segment_polygon(seg, current_terrain, altitude_min, mode='terrain', terrain_colors=terrain_colors, description_type=description_type,terrain_added=terrain_added)
                    )
                    # on passe au prochain type
                    if i < len(df_col):
                        current_terrain = df_col.iloc[i]['type']
                        segment_start_idx = i 
                else:
                    # parasite → on l’ignore et on reste dans le terrain précédent
                    if i < len(df_col):
                        # on ne change pas de terrain, on recule le "curseur"
                        continue
            else:
                # tout début du premier segment
                if i < len(df_col):
                    current_terrain = df_col.iloc[i]['type']
                    segment_start_idx = i

    return traces


def get_segments_by_slope(df, min_length=10):
    """
    Version simplifiée qui se contente de grouper par pente sans fusion complexe.
    Plus lisible et plus facilement testable.
    """
    if df.empty:
        return []
    
    df_work = df.copy()
    df_work['slope_color'] = df_work['pente'].apply(color_pente)
    altitude_min = df_work['altitude'].min()
    polygons = []
    current_color = df_work.iloc[0]['slope_color']
    segment_start = 0
    
    for i in range(len(df_work) + 1):
        # Changement de couleur ou fin du DataFrame
        if i == len(df_work) or (df_work.iloc[i]['slope_color'] != current_color):
            if current_color is not None:
                segment = df_work.iloc[segment_start:i+1]
                segment_length = (segment['distance'].iloc[-1] - 
                                segment['distance'].iloc[0])
                
                # Ne garder que les segments assez longs
                if segment_length >= min_length:
                    polygon = make_segment_polygon(
                        segment, current_color, altitude_min, mode='slope'
                    )
                    polygons.append(polygon)
                else :
                    continue
            
            # Préparer le prochain segment
            if i < len(df_work):
                
                current_color = df_work.iloc[i]['slope_color']
                segment_start = i
    
    return polygons
# --- Ajouter les segments colorés selon la pente ---


def add_gradient_segments(fig, df_col,terrain_colors,description_type,terrain_added = set()):
    for i in range(len(df_col)-1):
        x_start, x_end = df_col.iloc[i]["distance_km"], df_col.iloc[i+1]["distance_km"]
        y_start, y_end = df_col.iloc[i]["altitude"], df_col.iloc[i+1]["altitude"]
        terrain = df_col.iloc[i]["type"]
        color=color = terrain_colors.get(terrain, terrain_colors["default"])
        description = description_type.get(terrain, terrain)
        show_legend = terrain not in terrain_added
        if show_legend:
            terrain_added.add(terrain)
        fig.add_trace(go.Scatter(
            x=[x_start, x_end], y=[y_start, y_end],
            mode='lines', line=dict(color=color, width=4),
            showlegend=show_legend,
            hoverinfo='skip',
            name=f'{description}',
            legendgroup=terrain
        ))


def create_col_profile(df_track,df_segments, col_name, has_terrain_type=False):
    mask = df_segments["checkpoint"] == col_name
    if not mask.any():
        return go.Figure(), {}
    distance_end = df_segments.loc[mask, "distance"].values[0]
    idx_end = df_segments.index[df_segments["distance"] == distance_end][0]
    distance_start = 0 if idx_end == 0 else df_segments.loc[idx_end-1, "distance"]
    df_col = df_track[(df_track["distance"] >= distance_start) & 
                         (df_track["distance"] <= distance_end)].copy().reset_index()
    
    if df_col.empty:
        return go.Figure(), {}

    df_col['distance_km'] = df_col["distance"] / 1000


    # Couleurs terrains
    terrain_colors = {
        'T1': 'rgba(34, 139, 34, 1)', 'R': 'rgba(128, 128, 128, 1)',
        'F': 'rgba(139, 69, 19, 1)', 'T': 'rgba(255, 140, 0, 1)',
        'T2': 'rgba(178, 34, 34, 1)', 'default': 'rgba(255, 223, 0, 1)'
    }
    description_type = {
        'T1': "Sentier randonnée","R":"Route","F":"Chemin forestier",
        "T":"Sentier","T2":"Sentier montagne"
    }

    


    fig = go.Figure()
    traces=get_segments_by_slope(df_col)
    df_clean = df_col.copy() #drop(unused_index)
    fig.add_traces(traces)
    # Intervalles et couleurs correspondant à color_pente
    pente_intervals = [
        ("pente < -30%", "#000000"),
        ("-30% <= pente < -20%", "#8B0000"),
        ("-20% <= pente < -15%", "#FF6347"),
        ("-15% <= pente < -10%", "#67DAE9"),
        ("-10% <= pente < -5%", "#006400"),
        ("-5% <= pente < 5%", "#90EE90"),
        ("5% <= pente < 10%", "#006400"),
        ("10% <= pente < 15%","#67DAE9"),
        ("15% <= pente < 20%", "#FF6600"),
        ("20% <= pente < 25%", "#CC0000"),
        ("25% <= pente < 30%", "#8B0000"),
        ("pente >= 30%", "#000000")
    ]

    # Ajouter des traces invisibles juste pour la légende
    for label, color in pente_intervals:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=color),
            showlegend=True,
            name=label
        ))



    # Ajuster layout pour que le graphe laisse de la place
    fig.update_layout(margin=dict(r=120))  # marges droite pour la légende


    if has_terrain_type:
        df_col = clean_terrain_types(df_col)
        add_gradient_segments(fig, df_col,terrain_colors,description_type)
         # === Points pour hover ===
        fig.add_trace(go.Scatter(
            x=df_col["distance_km"], y=df_col["altitude"], mode='markers',
            marker=dict(size=4, color='black', opacity=0),
            name='Points', showlegend=False,
            hovertemplate='<b>Distance:</b> %{x:.1f} km<br>'
                        '<b>Altitude:</b> %{y:.0f} m<br>'
                        '<b>Pente:</b> %{customdata[0]:.1f}%<br>'
                        '<b>Terrain:</b> %{customdata[1]}<extra></extra>',
            customdata=[
                [p, description_type.get(t, t)] 
                for p, t in zip(df_col["pente"], df_col["type"])
            ]
        ))

        # Colorée par terrain
       
    else:
        # Ligne blanche uniforme
        fig.add_trace(go.Scatter(
            x=df_col["distance_km"], y=df_col["altitude"],
            mode='lines', line=dict(color='black', width=1, shape='spline', smoothing=0.5),
            name='Profil altimétrique',
            showlegend=False,
            hoverinfo='skip'
        ))
         # === Points pour hover ===
        fig.add_trace(go.Scatter(
            x=df_clean["distance_km"], y=df_clean["altitude"], mode='markers',
            marker=dict(size=4, color='black', opacity=0),
            name='', 
            showlegend=False,
            hovertemplate='<b>Distance:</b> %{x:.1f} km<br>' 
                        '<b>Altitude:</b> %{y:.0f} m<br>'
                        '<b>Pente:</b> %{customdata[0]:.1f}%<br>',
            customdata=[
                [p] 
                for p in (df_clean["pente"])
            ]
        ))

        
   
    # === Mise en forme ===
    altitude_min = df_col['altitude'].min()
    fig.update_layout(
        plot_bgcolor= "#D1D4D8", paper_bgcolor= "#D1D4D8",
        title=dict(text=f"Profil altimétrique - <b>{col_name}</b> ", x=0.5,
                   font=dict(size=24,color='black'), xanchor="center"),
        xaxis=dict(title="Distance (km)", color='black', showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="Altitude (m)", color='black', showgrid=True, gridcolor="rgba(255,255,255,0.1)",
                   range=[altitude_min-20, df_col["altitude"].max()+20]),
        margin=dict(l=60,r=60,t=80,b=60),
        legend=dict(font=dict(color='black')),
        hovermode='x unified'
    )

    # === Métriques ===
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

    metrics = [alt_metrics, pente_metrics]
    return fig, metrics
