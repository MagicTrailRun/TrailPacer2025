import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from TrailPacer.data_loader import load_data, get_config
from TrailPacer.gpx_tracer import plot_altitude_profile_area
from TrailPacer.formatting import format_dataframe,get_base64_image
from TrailPacer.race_id import color_pente, plot_col_profile_tour_gradient,altitude_metrics, load_gpx, plot_slope_histogram, process_data, load_data_checkpoints, plot_segment_analysis
from TrailPacer.text import pacing, quisommesnous, votreavis, cnil
from config.styles import apply_custom_css


st.set_page_config(page_title="TrailPacer", page_icon="🏃‍♂️", layout="wide")

def show():
    st.set_page_config(layout="wide")
    st.info('Plans de course à venir : Sainté Lyon, Grand Trail des templiers et Grand Raid Réunion...')

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


    plan_course1, pacing2, explorer3, postcourse4, avis5, qui6 , cnil7= st.tabs([
        "Plan de course",
        "Le pacing selon TrailPacer",
        "Explorer les courses",
        "Analyse post-course",
        "Suivre le projet",
        "Qui sommes-nous?",
        "Politique de confidentialité"

    ])
     
    st.markdown("------------")
    with plan_course1:
        st.markdown("### MODE D’EMPLOI ")
        st.write(            
        "1. Choisissez votre temps objectif \n" 
        "2. Trail Pacer calcule vos temps de passage optimisés \n " \
        "3. Téléchargez votre plan ou visualisez-le directement sur le profil de la course.")

        st.markdown("------------")
        st.markdown(" ### Fixez votre objectif de temps pour l’arrivée,  Trail Pacer calcule vos temps de passage.")
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            target_time = st.slider("",
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
            ["Heure de passage", "Temps de passage", "D+ Secteur", "D- Secteur","Distance Secteur"],
            default=["Heure de passage","D+ Secteur", "D- Secteur"]
)       
        title=f"🏃‍♂️ Profil d'élévation - Objectif {target_time}h"
        st.header(title)
        year=2025
        df_gpx=load_gpx(f"data/TrailPacer/{course}/tracks/gpx_{year}.json")
        st.plotly_chart(plot_altitude_profile_area(df_gpx, df, mapping_ckpts, config,affichages,target_time), use_container_width=True)
       
        
        
    with pacing2 :
        pacing()

    with explorer3 : 
                
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

        st.info("Page en cours de construction...")
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
            
        st.divider()

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
        
        # st.divider()

        # st.markdown("## Profil de la course")
        # st.plotly_chart(plot_altitude_profile_area(df_gpx, df, mapping_ckpts, config, show_title=False))
        # st.divider()
        # st.plotly_chart(plot_slope_histogram(df_gpx), use_container_width=True)

        # st.divider()
        # # -----------------------------
        # # 3️⃣ Analyse segmentaire
        # # -----------------------------
       
        # st.plotly_chart(plot_segment_analysis(df_track), use_container_width=True)




    with postcourse4:
       
        st.info("Page en cours de construction...")
        st.markdown(
        """ Visualiser son pacing par rapport au plan Trail Pacer et au peloton.
        Comparaison entre coureurs
        """
        )




    with avis5 :

        votreavis()

    with qui6 :
        st.header("Qui sommes-nous?")
        st.markdown(quisommesnous())

    with cnil7 :
        cnil()

if __name__ == "__main__":
    show()
