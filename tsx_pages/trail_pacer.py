import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from TrailPacer.data_loader import load_data, get_config
from TrailPacer.gpx_tracer import plot_altitude_profile_area,plot_altitude_profile_area
from TrailPacer.formatting import format_dataframe
from TrailPacer.race_id import color_pente, plot_col_profile_tour_gradient,altitude_metrics, load_gpx, plot_slope_histogram, process_data, load_data_checkpoints, plot_segment_analysis
from TrailPacer.presentation import text_presentation
from TrailPacer.quisommesnous import quisommesnous
from TrailPacer.votreavis import votreavis
import base64

st.set_page_config(page_title="TrailPacer", page_icon="🏃‍♂️", layout="wide")

def show():
  

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    img_base64 = get_base64_image("TrailPacer/image/utmb.png")
    
    st.set_page_config(
        page_title="TrailPacer: Planificateur de temps de passage & Analyses course",
        page_icon="🏃‍♂️",
        layout="wide"
    )

    st.markdown(
    f"""
    <style>
    .hero {{
        position: relative;
        width: 100%;
        height: 300px;
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        border-radius: 15px;
    }}
     .hero h1 {{
        position: absolute;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 3em;
        font-weight: bold;
        text-shadow: 2px 2px 8px #000;
        margin: 0;
    }}
    .hero h2 {{
        position: absolute;
        top: 60%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 2em;
        font-weight: 500;
        text-shadow: 2px 2px 6px #000;
        margin: 0;
    }}
    </style>

    <div class="hero">
        <h1>TrailPacer</h1>
        <h2>UTMB 2025</h2>
    </div>
    """,
    unsafe_allow_html=True
)
 
    # st.header("Choisir une course")
    # col1, col2, col3 = st.columns([1, 1, 1])

    # with col1:
    #     event = st.selectbox("Événement", ["UTMB"], index=0)

    # with col2:
    #     course = st.selectbox("Course", ["UTMB"], index=0)


    event='UTMB'
    course='UTMB'
    config, mapping_ckpts = get_config(f"data/TrailPacer/{event}/config.json", course)
    
   

    df = load_data(race=course)
    if df.empty:
        st.error("Impossible de charger les données")
        return
    st.markdown(
        """
        <style>
        /* Taille et style des labels de tabs */
        div[data-baseweb="tab"] > button p {
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        /* Espace entre les onglets */
        div[data-baseweb="tab-list"] {
            gap: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⏱️ Plan de course",
        "💡 Le pacing selon TrailPacer",
        "EXPLORER LES COURSES",
        "ANALYSE POST-COURSE",
        "VOTRE AVIS NOUS INTERESSE",
        "Qui sommes-nous?"

    ])
     
    st.markdown("------------")
    with tab1:
        st.markdown("### Choisissez votre temps objectif → Trail Pacer calcule vos temps de passage optimisés → téléchargez votre plan ou visualisez-le directement sur le profil de la course.")
        col1, col2, col3 = st.columns([2,1,2])
        
        with col1:
            target_time = st.slider(
                "Fixez votre objectif de temps pour l’arrivée, Trail Pacer calcule vos temps de passage.",
                config['temps_cible_start'],
                config['temps_cible_end'],
                config['temps_cible_middle']
            )
        if not df.empty:
           
            # Tableau principal
            st.subheader(f"📋Plan de course généré pour {target_time} h")
            df_display, column_config=format_dataframe(df,target_time)

            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                height=(35 * len(df_display)) + 50 ,
                column_config=column_config
                
            )

            # Convertir en CSV
            csv = df_display.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name="temps_de_passage.csv",
                mime="text/csv",
)
        affichages = st.multiselect(
            "Choisissez les éléments à afficher",
            ["Heure de passage", "Temps de passage", "D+", "D-"],
            default=["Heure de passage"]
)       
        year=2025
        df_gpx=load_gpx(f"data/TrailPacer/{course}/tracks/gpx_{year}.json")
        st.plotly_chart(plot_altitude_profile_area(df_gpx, df, mapping_ckpts, config,affichages,target_time), use_container_width=False)
        
    with tab2 :
        st.header("Qu'est ce que le pacing?"
                  )
        
        txt="""
1. Qu’est-ce que le pacing ?

Le pacing désigne l’art de gérer son effort et son allure au cours d’une performance sportive. Autrement dit, c’est la stratégie par laquelle un athlète répartit son énergie et ses ressources physiologiques pour atteindre un objectif (performance, régularité, finisher…), en tenant compte de la durée, de l’intensité et des contraintes environnementales et techniques de l’épreuve.

Un pacing efficace repose sur un équilibre subtil :

· Trop rapide au départ, le coureur risque l’épuisement prématuré, une baisse de performance, voire l’abandon.

· Trop prudent, il termine avec des réserves inutilisées et un résultat en deçà de ses capacités.

Le pacing n’est donc pas seulement une question de vitesse moyenne : c’est une dynamique d’ajustement continu, influencée par les sensations, la connaissance de son corps, l’expérience, mais aussi par des facteurs objectifs (dénivelé, conditions météo, technicité du oarcours, concurrence"""
    
        st.markdown(txt)
    with tab3 : 
                
        # Charger les données
        df_track = load_data_checkpoints(f"data/TrailPacer/{course}/tracks/{course}_checkpoints_2025.csv")
        df_track=process_data(df_track)
        df_track_runners=df_track[['name','dateFirstRunners', 'dateLastRunners', 'distCum_km']]
        df_track_runners.loc[df_track.index[0], "name"] = "Départ"
        df_track_runners["name"] = df_track_runners["name"].replace(mapping_ckpts)
        df_track_runners = df_track_runners[~df_track_runners['name'].isin(config['drop_ckpts'])]


        df_timing = df_display[['Point de passage', f'temps_cumule_med_{target_time}']]
        
        df_timing.rename(columns={f'temps_cumule_med_{target_time}': 'Temps cumulé'}, inplace=True)

        df_track_runners=df_track_runners.merge(df_timing, left_on="name", right_on='Point de passage',how='left')

        
        df_gpx=load_gpx(f"data/TrailPacer/{course}/tracks/gpx_{year}.json")
        st.markdown("### Fiche identité")
        st.markdown(f"#### 📅 Prochaine édition {config['start_datetime'].strftime('%d/%m/%Y %H:%M')}")
        col1, col2, col3, col4 = st.columns(4)


        with col1:
            st.metric("Distance totale", f"{df['dist_total'].max():.1f} km")
        with col2:
            st.metric("D+ total", f"{df.d_plus_total.max():.0f} m")
        with col3:
            st.metric("D- total", f"{df.d_moins_total.max():.0f} m")
        with col4:
            st.metric("Points de passage", len(df))
        seuil=1500
        pct_above, pct_below = altitude_metrics(df_gpx, seuil=seuil)

        col1, col2,_,_ = st.columns(4)
        with col1 :
            st.metric(f"Parcours au-dessus de {seuil} m", f"{pct_above:.1f} %")
        with col2 :
            st.metric(f"Nombre de participants", 2603)
            
        
        st.markdown("## Profil de la course")
        st.plotly_chart(plot_altitude_profile_area(df_gpx, df, mapping_ckpts, config, show_title=False))
        st.plotly_chart(plot_slope_histogram(df_gpx), use_container_width=True)

        
        # -----------------------------
        # 3️⃣ Analyse segmentaire
        # -----------------------------
        st.markdown("## Analyse segmentaire : dénivelé et temps")
        st.plotly_chart(plot_segment_analysis(df_track), use_container_width=True)


        st.markdown("## Profil par segment")
        option = st.selectbox("Choisis un segment :", [s for s in df_track.shortName.unique() if s != "Départ"])
        fig, metrics = plot_col_profile_tour_gradient(df_gpx, df_track, col_name=option)
        cols_alt = st.columns(len(metrics[0]))
        
        for i, (label, val) in enumerate(metrics[0].items()):
            cols_alt[i].metric(label, val)
        cols_slope = st.columns(len(metrics[1]))            
        for i, (label, val) in enumerate(metrics[1].items()):
            color = color_pente(val)
            cols_slope[i].markdown(f"<div style='text-align:left; font-size:20px; color:{color}'>{label}<br>{val:.1f}%</div>", unsafe_allow_html=True)
        st.plotly_chart(fig)
        


    with tab4:
       
        
        st.markdown("### Visualiser son pacing par rapport au plan Trail Pacer et au peloton. Comparaison entre coureurs")
        st.write("A venir...")


    with tab5 :
        st.header("Votre avis nous intéresse")
        st.markdown(votreavis())
    with tab6 :
        st.header("Qui sommes-nous?")
        st.markdown(quisommesnous())

if __name__ == "__main__":
    show()
