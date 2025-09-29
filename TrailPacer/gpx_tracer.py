
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd



def plot_altitude_profile_area(df_gpx, df, affichages=None, target_time=None, show_title=True):
    """
    Profil d'altitude avec checkpoints, D+/D- par secteur et design moderne
    """
    df.reset_index(inplace=True)
    min_alt = df_gpx["altitude"].min() - 300
    max_alt = df_gpx["altitude"].max() + 100
    df_gpx['distance_km'] = df_gpx['distance'] / 1000
    
    # Couleurs modernes et gradients
    colors = {
        'primary': "#8F8F9E",      # Indigo moderne
        'secondary': "#E62F38",    # Rose vibrant  
        'accent': '#10B981',       # Emeraude
        'warning': '#F59E0B',      # Ambre
        'success': '#059669',      # Vert
        'background':  "#f8f9fa",   # Slate sombre
        'surface':  "#f8f9fa",      # Slate moyen
        'text': "#0C0C0C"          # Blanc cassé
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
            fillcolor=f'rgba(99, 102, 241, 0.3)',
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
        marker_color = colors['secondary'] if idx in idx_high  else colors['warning']

        fig.add_trace(
            go.Scatter(
                x=[dist],
                y=[ele] ,
                mode="markers+text",
                marker=dict(
                    color=marker_color,
                    size=10,
                    symbol="circle",
                    line=dict(width=1, color='grey')
                ),
                text=[label_h],
                textposition="top center" if idx%2==1  else "bottom center",
                textfont=dict(size=10, color=colors['text']),
                #name=name,
                showlegend=False,
                #hovertemplate=f'<b>{name}</b><br>Distance: {dist:.1f}km<br>Altitude: {ele:.0f}m<extra></extra>'
            ),
        )
        # Crée un Scatter invisible avec le même style rouge pour légende
        if idx==1 :
            fig.add_trace(
                go.Scatter(
                    x=[None],  # aucun point visible
                    y=[None],
                    mode="markers",
                    marker=dict(
                        color=colors['secondary'],
                        size=10,
                        symbol="circle",
                        line=dict(width=1, color='grey')
                    ),
                    name=f"Checkpoints > {altitude} m d'altitude"  # apparaît dans la légende
                )
            )
        # Ligne de connexion élégante
        fig.add_shape(
            type="line",
            x0=dist, y0=min_alt,
            x1=dist, y1=ele,
            line=dict(
                color=marker_color,
                width=1,
                dash="dot"
            ),
            opacity=0.3,
        )
    
    # === STYLING ULTRA-MODERNE ===
    
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
    hovermode='x unified',
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

