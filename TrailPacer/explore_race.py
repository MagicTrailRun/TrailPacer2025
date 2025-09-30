
import streamlit as st
from pathlib import Path
import traceback
from TrailPacer.race_id import color_pente,altitude_metrics,  create_col_profile,  get_df_for_gpx


def explore_race():

    try :

        event_code=st.session_state["event_code"]
        course_code=st.session_state["course_code"]
        year=st.session_state["year"]
        config=st.session_state["config"]
        df=st.session_state["df"]
        
        df_gpx, has_terrain_type =get_df_for_gpx()


        st.info("Page en cours de construction...")
        st.markdown("## Fiche identité")
        st.markdown(f"#### 📅 Edition du {config['startDate'].strftime('%d/%m/%Y %H:%M')}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:  
            st.metric("Distance totale", f"{df['dist_total'].max():.1f} km")
        with col2:
            st.metric("D+ total", f"{df.dplus_cum_m.max():.0f} m")
        with col3:
            st.metric("D- total", f"{df.dmoins_cum_m.max():.0f} m")
        with col4:
            st.metric("Points de passage", len(df))
        seuil=1500
        pct_above, pct_below = altitude_metrics(df_gpx, seuil=seuil)

        col1, col2,_,_ = st.columns(4)
        with col1 :
            st.metric(f"Parcours au-dessus de {seuil} m", f"{pct_above:.1f} %")
        # with col2 :
        #     st.metric(f"Nombre de participants", 2603)
            
        st.divider()
        st.markdown("## Profil par segment")
        option_seg = st.selectbox(
                "Choisis un segment :",
                [
                    s for s in df.loc[df["dist_secteur"] > 0, "checkpoint"].unique()
                
                ]
            )
        if option_seg : 
            df['distance']=df['distance_cum_m']
            fig, metrics = create_col_profile(df_gpx, df, option_seg,has_terrain_type)
            cols_alt = st.columns(len(metrics[0]))

            for i, (label, val) in enumerate(metrics[0].items()):
                cols_alt[i].metric(label, val)
            cols_slope = st.columns(len(metrics[1]))            
            for i, (label, val) in enumerate(metrics[1].items()):
                color = color_pente(val)
                cols_slope[i].markdown(f"<div style='text-align:left; font-size:20px; color:{color}'>{label}<br>{val:.1f}%</div>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        

        st.divider()

        path_to_html = Path(f"data/TrailPacer/{event_code}/{course_code}/gpx_comparison/compare_{course_code}.html")

        if path_to_html.exists():
            with open(path_to_html, 'r', encoding="utf-8") as f:
                html_data = f.read()

            st.header("Différence de parcours des éditions prédécentes")
            st.components.v1.html(html_data, height=600, scrolling=True)
    


    except Exception as e:
            st.error("Cette page n'est pas encore disponible pour la course selectionnée !")
            # Optionnel : log dans la console pour debug
            print(f"[DEBUG] Erreur explorer_course: {e}")
            traceback.print_exc()

        