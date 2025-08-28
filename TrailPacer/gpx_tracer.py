
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

def plot_altitude_profile_area(df_gpx, df, mapping_ckpts, config, affichages=None, target_time=None, show_title=True):
    """
    Profil d'altitude avec checkpoints, D+/D- par secteur et design moderne
    """
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
        'background': "#D1D4D8",   # Slate sombre
        'surface': "#D1D4D8",      # Slate moyen
        'text': "#0C0C0C"          # Blanc cassé
    }
    
    # Création du graphique avec subplot pour plus de contrôle
    fig =go.Figure()
    
    
    # === PROFIL PRINCIPAL AVEC GRADIENT SEXY ===
    
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
    fig.add_annotation(
                x=0,
                y=0,
                text="Départ",
                showarrow=False,
                font=dict(size=10, color="white"),
                textangle= -45,
                xanchor="center",
                yanchor="bottom",
            )

    # Calcul par secteur
    for idx, row in df.iterrows():
        name = mapping_ckpts.get(row["Point de passage"], row["Point de passage"])
        dist = row.get("dist_total", 0)
        
        if pd.isna(dist):
            continue
            
        # D+/D- pour ce secteur (différence avec le précédent)
        if idx == 0:
            d_plus_secteur = row.get('d_plus_total', 0)
            d_moins_secteur = row.get('d_moins_total', 0)

        else:
            d_plus_secteur = row.get('d_plus_total')
            d_moins_secteur = row.get('d_moins_total')
        secteurs_d_plus.append(d_plus_secteur)
        secteurs_d_moins.append(-d_moins_secteur)  # Négatif pour l'affichage
        distances_secteur.append(dist)
    

        fig.add_annotation(
                x=dist,
                y=0,
                text= name,
                showarrow=False,
                font=dict(size=10, color="white"),
                textangle= -45,
                xanchor="center",
                yanchor="bottom",

            )


    # fig.add_trace(
    #     go.Scatter(
    #         x=distances_secteur,
    #         y=secteurs_d_plus,
    #         mode="lines+markers",
    #         line=dict(color=colors["accent"], width=2, shape="spline", smoothing=0.5),
    #         fill="tozeroy",
    #         fillcolor="rgba(16,185,129,0.3)",  # accent en transparent
    #         name="D+ Secteur",
    #         hovertemplate="Distance: %{x:.1f} km<br>D+ secteur: %{y:.0f} m<extra></extra>"
    #     ),
    #     row=2, col=1
    # )

    # # D- secteur (ligne + area remplie)
    # fig.add_trace(
    #     go.Scatter(
    #         x=distances_secteur,
    #         y=secteurs_d_moins,
    #         mode="lines+markers",
    #         line=dict(color=colors["secondary"], width=2, shape="spline", smoothing=0.5),
    #         fill="tozeroy",
    #         fillcolor="rgba(230,47,56,0.3)",  # secondary en transparent
    #         name="D- Secteur",
    #         hovertemplate="D- secteur: %{y:.0f} m<extra></extra>"
    #     ),
    #     row=2, col=1
    # )
    
    # === CHECKPOINTS ULTRA-STYLÉS ===
    
    # Point de départ avec style
    start_texts = []
    if affichages:
        if "Heure de passage" in affichages:
            start_texts.append(f'🕐{config.get("start_day_hour")}')
        if "Temps de passage" in affichages:
            start_texts.append('⏱️ 0h00')
        if "D+ Secteur" in affichages:
            start_texts.append(f'↗️ 0 m')
        if "D- Secteur" in affichages:
            start_texts.append(f'↘️ 0 m')
        if "Distance Secteur" in affichages :
            start_texts.append(f'📏0km')
    
    start_label =f"<b>{name}</b><br>" +  "<br>".join(start_texts) if start_texts else f'{config["start"]}'
    
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[np.interp(0, df_gpx["distance_km"], df_gpx["altitude"])],
            mode="markers+text",
            marker=dict(
                color=colors['success'],
                size=15,
                symbol="triangle-up",
                line=dict(width=3, color='white')
            ),
            text=[start_label],
            textposition="top center",
            textfont=dict(size=11, color=colors['text']),
            name=config["start"],
            showlegend=False,
            hovertemplate=f'<b>{config["start"]}</b><extra></extra>'
        ),
    )
    
    # Checkpoints avec design moderne
    idx_high=[]
    altitude=2000
    for idx, row in df.iterrows():
        name = mapping_ckpts.get(row["Point de passage"], row["Point de passage"])
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
                heure_passage_col = f'heure_passage_{target_time}'
                texts_h.append(f'🕐 {row[heure_passage_col]}')
            if "Temps de passage" in affichages:
                temps_passage_col = f'temps_cumule_med_{target_time}'
                texts_h.append(f'⏱️ {row[temps_passage_col]}')
            if "D+ Secteur" in affichages:
                d_plus_secteur = row['dp_tot_secteur'] 
                texts_h.append(f'↗️ {d_plus_secteur:.0f}m')
            if "D- Secteur" in affichages:
                d_moins_secteur = row['dm_tot_secteur'] 
                texts_h.append(f'↘️ {d_moins_secteur:.0f}m')
            if "Distance Secteur" in affichages :
                dist_secteur= row['dist_secteur']
                texts_h.append(f'📏{dist_secteur:.2f}km')
        
        label_h = f"<b>{name}</b><br>" + "<br>".join(texts_h) if texts_h else f'📍 {name}'
        
        # Marqueur stylé avec couleur alternée
        marker_color = colors['secondary'] if idx in idx_high  else colors['warning']
        idx_up=[18,4,2,20,22]
        idx_down=[3,11]
        fig.add_trace(
            go.Scatter(
                x=[dist],
                y=[ele],
                mode="markers+text",
                marker=dict(
                    color=marker_color,
                    size=10,
                    symbol="circle",
                    line=dict(width=1, color='grey')
                ),
                text=[label_h],
                textposition="top center" if (idx%2==1 and not idx in idx_down) or idx in idx_up  else "bottom center",
                textfont=dict(size=10, color=colors['text']),
                name=name,
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
                        color=marker_color,
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

