import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import plotly.graph_objects as go
import numpy as np

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
        






# --- Nettoyage des types de terrain ---
def clean_terrain_types(df, known_types=None, default_type='default'):
    if known_types is None:
        known_types = ['T1','T2','T','R','F']
    df = df.copy()
    df['type'] = df['type'].fillna(default_type)
    df.loc[~df['type'].isin(known_types), 'type'] = default_type
    return df

def make_segment_polygon(seg, terrain, terrain_colors, description_type, altitude_min, terrain_added):
    """
    Construit un polygone (Scatter plotly) pour un segment de terrain donné.
    """
    color = terrain_colors.get(terrain, terrain_colors['default'])
    description = description_type.get(terrain, terrain)

    x_coords = seg["distance_km"].tolist()
    y_coords = seg["altitude"].tolist()
    x_poly = x_coords + x_coords[::-1]
    y_poly = y_coords + [altitude_min] * len(x_coords)

    show_legend = terrain not in terrain_added
    if show_legend:
        terrain_added.add(terrain)

    return go.Scatter(
        x=x_poly, y=y_poly,
        fill='toself', fillcolor=color,
        line=dict(width=0),
        name=f'{description}',
        showlegend=show_legend,
        legendgroup=terrain,
        hoverinfo='skip',
        mode='none'
    )
def get_segments_by_terrain(df_col, terrain_colors, description_type, min_length=50):
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
                        make_segment_polygon(seg, current_terrain, terrain_colors, description_type, altitude_min, terrain_added)
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
# --- Ajouter les segments colorés selon la pente ---
def add_gradient_segments(fig, df_col):
    for i in range(len(df_col)-1):
        x_start, x_end = df_col.iloc[i]["distance_km"], df_col.iloc[i+1]["distance_km"]
        y_start, y_end = df_col.iloc[i]["altitude"], df_col.iloc[i+1]["altitude"]
        pente = df_col.iloc[i]["pente"]
        color=color_pente(pente)
        fig.add_trace(go.Scatter(
            x=[x_start, x_end], y=[y_start, y_end],
            mode='lines', line=dict(color=color, width=4),
            showlegend=False,
            hoverinfo='skip',
        ))

# --- Fonction principale ---
def create_col_profile(df_segments, df_track, col_name="Col Ferret"):
    mask = df_track["shortName"] == col_name
    if not mask.any(): return go.Figure(), {}

    distance_end = df_track.loc[mask, "distance"].values[0]
    idx_end = df_track.index[df_track["distance"] == distance_end][0]
    distance_start = 0 if idx_end == 0 else df_track.loc[idx_end-1, "distance"]

    df_col = df_segments[(df_segments["distance"] >= distance_start) & 
                         (df_segments["distance"] <= distance_end)].copy()
    if df_col.empty: return go.Figure(), {}

    df_col['distance_km'] = df_col["distance"] / 1000
    df_col = clean_terrain_types(df_col)

    terrain_colors = {
        'T1': 'rgba(34, 139, 34, 0.6)', 'R': 'rgba(128, 128, 128, 0.6)',
        'F': 'rgba(139, 69, 19, 0.6)', 'T': 'rgba(255, 140, 0, 0.6)',
        'T2': 'rgba(178, 34, 34, 0.6)', 'default': 'rgba(255, 223, 0, 0.5)'
    }
    description_type = {'T1': "Sentier randonnée","R":"Route","F":"Chemin forestier",
                        "T":"Sentier","T2":"Sentier montagne"}

    fig = go.Figure()
    fig.add_traces(get_segments_by_terrain(df_col, terrain_colors, description_type),)

    # Ligne principale
    fig.add_trace(go.Scatter(
        x=df_col["distance_km"], y=df_col["altitude"],
        mode='lines', line=dict(color='white', width=4, shape='spline', smoothing=0.5),
        name='Profil altimétrique',
        showlegend=False,
        hoverinfo='skip'
    ))

    add_gradient_segments(fig, df_col)

    # Points pour hover
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

    altitude_min = df_col['altitude'].min()
    fig.update_layout(
        plot_bgcolor= "#D1D4D8", paper_bgcolor= "#D1D4D8",
        title=dict(text=f"Profil altimétrique - <b>{col_name}</b> ", x=0.5, font=dict(size=24,color='black'),  xanchor="center"),
        xaxis=dict(title="Distance (km)", color='black', showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="Altitude (m)", color='black', showgrid=True, gridcolor="rgba(255,255,255,0.1)",
                   range=[altitude_min-20, df_col["altitude"].max()+20]),
        height=None, width=None,
        margin=dict(l=60,r=60,t=80,b=60),
        legend=dict(font=dict(color='black')), hovermode='x unified'
    )
    
    # Points pour hover
    fig.add_annotation(
        text="<b>Description pente:</b><br>"
             "<span style='color:#00AA00'>■</span> Forte descente (&lt;-5%)<br>"
             "<span style='color:#66FF66'>■</span> Descente (-5% à 0%)<br>"
             "<span style='color:#FFFF00'>■</span> Plat/montée légère (0-5%)<br>"
             "<span style='color:#FF6600'>■</span> Montée modérée (5-10%)<br>"
             "<span style='color:#CC0000'>■</span> Forte montée (&gt;10%)",
        xref="paper", yref="paper",
        x=1.02, y=0.4,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=10, color='black'),
        bordercolor="black",
        borderwidth=1,
        bgcolor="#D1D4D8"
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
