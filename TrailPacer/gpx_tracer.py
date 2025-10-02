
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def compute_label_shift(dist, ele, idx, label_positions, amplitude, min_alt, idx_max_cluster=6):
    """
    Calcule le décalage vertical optimal (y_shift) et l'ancrage texte pour une annotation.
    
    Args:
        dist (float): distance du point.
        ele (float): altitude du point.
        idx (int): index de la boucle.
        label_positions (list[dict]): positions précédentes [{"x":..., "y":..., "shift":...}, ...]
        amplitude (float): différence max-min d'altitude.
        min_alt (float): altitude minimale du profil.
        idx_max_cluster (float): seuil de proximité horizontale pour considérer un cluster.
    Returns:
        tuple: (y_shift, text_anchor)
    """
    # --- Détection de conflits ---
    conflict = any(
        abs(dist - lp['x']) < idx_max_cluster and abs(ele - (lp['y'] + lp['shift'])) < amplitude * 0.1
        for lp in label_positions
    )

    # --- Cluster dans la zone ---
    cluster_labels = [lp for lp in label_positions if abs(dist - lp['x']) < idx_max_cluster]
    offset_idx = len(cluster_labels)
    conflicting_shift = label_positions[-1]['shift'] if label_positions else 0

    # --- Cas 1 : Conflit ou cluster => on empile ---
    if conflict or offset_idx > 0:
        base_sign = -1 if conflicting_shift > 0 else 1
        y_shift = base_sign * amplitude * (0.01 + 0.01 * offset_idx)
        text_anchor = "bottom" if y_shift > 0 else "top"
    else:
        # --- Cas 2 : Bas de profil ---
        if ele < (min_alt + amplitude * 0.10):
            y_shift, text_anchor = amplitude * 0.01, "bottom"
        # --- Cas 3 : Haut de profil ---
        elif ele > (min_alt + amplitude * 0.90):
            y_shift, text_anchor = -amplitude * 0.01, "top"
        # --- Cas 4 : Zone moyenne ---
        else:
            text_anchor = "bottom" if idx % 2 == 0 else "top"
            y_shift = amplitude * (0.01 if text_anchor == "bottom" else -0.015)

    return y_shift, text_anchor


def plot_altitude_profile_area(df_gpx, df, affichages=None, target_time=None, show_title=True):
    """
    Profil d'altitude avec checkpoints, D+/D- par secteur et design moderne
    """
    df.reset_index(inplace=True)
    min_alt = (df_gpx["altitude"].min()) - 400
    max_alt = df_gpx["altitude"].max()+200
    df_gpx['distance_km'] = df_gpx['distance'] / 1000

    amplitude=df_gpx["altitude"].max()-df_gpx["altitude"].min()
    # Couleurs modernes et gradients
    colors = {
        'primary': "#FFFFFF",      # Indigo moderne
        'secondary': "#E62F38",    # Rose vibrant  
        'accent': '#10B981',       # Emeraude
        'warning': '#F59E0B',      # Ambre
        'success': '#059669',      # Vert
        'background':  "#ffffff",   # Slate sombre
        'surface':  "#ffffff",      # Slate moyen
        'text': "#0C0C0C"     ,
        'eau' :  "#2A86D1" ,
        'fill' :  "#4D4A4A"
    }
     
    # Création du graphique avec subplot pour plus de contrôle
    fig =go.Figure()
    
 
    # Gradient fill moderne
    fig.add_trace(
        go.Scatter(
            x=df_gpx["distance_km"],
            y=df_gpx["altitude"],
            mode='lines',
            fill='tonexty',
            fillcolor=colors["fill"],
            line=dict(
                color=colors['primary'],
                width=3,
                shape='spline',  # Courbes lisses
                smoothing=0.3
            ),
            name='Profil d\'altitude',
            hovertemplate='<b>Distance:</b> %{x:.1f} km<br><b>Altitude:</b> %{y:.0f} m<extra></extra>',
            showlegend=False,
        ),

    )
    
    # Ligne de base pour le gradient
    fig.add_trace(
        go.Scatter(
            x=df_gpx["distance_km"],
            y=[min_alt] * len(df_gpx),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
            
        ),
 
    )
    
    # # === CALCUL ET AFFICHAGE D+/D- PAR SECTEUR ===
    secteurs_d_plus = [0]
    secteurs_d_moins = [0]
    distances_secteur=[0]
    label_positions = []
    # Calcul par secteur
    for idx, row in df.iterrows():
        #name = mapping_ckpts.get(row["checkpoint"], row["checkpoint"])
        name = row["checkpoint"]
        dist = row.get("dist_total", 0)
        
        if pd.isna(dist):
            continue
            
        # D+/D- pour ce secteur (différence avec le précédent)
        if idx == 0:
            d_plus_secteur = row.get('dplus_cum_m', 0)
            d_moins_secteur = row.get('dmoins_cum_m', 0)

        else:
            d_plus_secteur = row.get('dplus_cum_m')
            d_moins_secteur = row.get('dmoins_cum_m')
        secteurs_d_plus.append(d_plus_secteur)
        secteurs_d_moins.append(-d_moins_secteur)  # Négatif pour l'affichage
        distances_secteur.append(dist)
    
    # Checkpoints 
    idx_high=[]
    altitude=2000
    for idx, row in df.iterrows():
        #name = mapping_ckpts.get(row["checkpoint"], row["checkpoint"])
        name = row["checkpoint"] if pd.notna(row["checkpoint"]) else "Départ"

        dist = row.get("dist_total", None)
        if pd.isna(dist):
            continue
            
        ele = np.interp(dist, df_gpx["distance_km"], df_gpx["altitude"])
        if ele>altitude :
            idx_high.append(idx)
        # Construction du texte avec emojis
        texts_h = []
        if affichages:
            if "Heure de passage" in affichages:
                heure_passage_col = f'heure_passage'
                texts_h.append(f'🕐 {row[heure_passage_col]}')
            if "Temps de course cumulé" in affichages:
                temps_passage_col = f'Temps de course cumulé'
                texts_h.append(f'⏱️ {row[temps_passage_col]}')
            if "D+ Segment" in affichages:
                d_plus_secteur = row['dplus_secteur'] 
                texts_h.append(f'↗️ {d_plus_secteur:.0f}m')
            if "D- Segment" in affichages:
                d_moins_secteur = row['dmoins_secteur'] 
                texts_h.append(f'↘️ {d_moins_secteur:.0f}m')
            if "Distance Segment" in affichages :
                dist_secteur= row['dist_secteur']
                texts_h.append(f'📏{dist_secteur:.2f}km')
        
        label_h = f"<b>{name}</b><br>" + "<br>".join(texts_h) if texts_h else f'📍 {name}'
        
        # Marqueur stylé avec couleur alternée
        if 'ravitaillement' in df.columns:
            is_ravito = row.ravitaillement == 'Oui'
            marker_color = colors['eau'] if is_ravito else colors['warning']
            legend = "Ravitaillement" if is_ravito else "Point de chronométrage"

        else:
            marker_color = colors['secondary'] if idx in idx_high else colors['warning']
            legend = f"Point > {altitude} m d'altitude"
        if idx == 1:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode="markers",
                marker=dict(color=marker_color, size=10, symbol="circle", line=dict(width=1, color='grey')),
                name=legend
            ))
        fig.add_trace(
            go.Scatter(
                x=[dist],y=[ele] ,
                mode="markers",
                marker=dict(color=marker_color,size=10,symbol="circle"),
                showlegend=False,
                 hovertext=label_h
            ),
        )

        y_shift, text_anchor = compute_label_shift(
                dist=dist,
                ele=ele,
                idx=idx,
                label_positions=label_positions,
                amplitude=amplitude,
                min_alt=min_alt
            )

        label_positions.append({"x": dist, "y": ele, "shift": y_shift})
        # --- Enregistre la position pour la suite --
        label_y = ele + y_shift*amplitude
        fig.add_shape(
            type="line",
            x0=dist,
            y0=min(ele,label_y),
            x1=dist, 
            y1=max(ele,label_y),
            line=dict(
                color=marker_color,
                width=1,
                dash="dot"
            ),
            opacity=0.6,
        )
        fig.add_annotation(
            x=dist,
            y=ele,
            text=label_h,
            textangle=0,
            showarrow=False,
            xanchor="auto",
            yanchor=text_anchor,
            font=dict(
                size=8,
                color=colors['text']
            ),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor=marker_color,
            borderwidth=1,
            borderpad=1,
            yshift=y_shift,
           
        )

        
    fig.update_layout(
        height=None,              # format dossard
    width=None,              # format dossard
    autosize=False,
    margin=dict(l=80, r=20, t=50, b=50),  # marge suffisante pour axes/ticks
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['surface'],
    font=dict(
        family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        color=colors['text'], 
        size=10
    ),
    legend=dict(x=0.01, y=0.99, xanchor="left", yanchor="top"),
    title=dict(
        text=f"Profil d'élévation - Objectif {target_time}h" if show_title else '',
        font=dict(color='black', size=15)  # couleur et taille du titre
    )
)
 
    


    # Axes du profil principal
    fig.update_xaxes(
        title_text="Distance (km)",
        gridcolor='rgba(255,255,255,0.1)',
        showgrid=True,
        zeroline=False,
        title_font=dict(color=colors['text']),
        tickfont=dict(color=colors['text']),

    )
    fig.update_yaxes(
        title_text="Altitude (m)",
        range=[min_alt, max_alt+500],
        gridcolor='rgba(255,255,255,0.1)',
        showgrid=True,
        zeroline=False,
        title_font=dict(color=colors['text']),
        tickfont=dict(color=colors['text']),

    )
    
   
    
   
    
    return fig

