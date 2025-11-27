
import streamlit as st
from pathlib import Path
import traceback
import pandas as pd 
from TrailPacer.race_id import color_pente,altitude_metrics,  create_col_profile


def explore_race():

    try :

        event_code=st.session_state["event_code"]
        course_code=st.session_state["course_code"]
        year=st.session_state["year"]
        config=st.session_state["config"]
        df=st.session_state["df"]
        
        df_gpx, has_terrain_type = st.session_state["df_gpx"], st.session_state["has_terrain_type"]

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
        st.header("Profil par segment")
        event_code = st.session_state["event_code"]
        course_code = st.session_state["course_code"]

        # --- Charger le CSV ---
        path_stats = Path(f"data/TrailPacer/{event_code}/{course_code}/stats/{course_code}_top12_par_secteur_all_time.csv")
        if path_stats.exists() :
            df_stats = pd.read_csv(path_stats)
            option_seg = st.selectbox(
                "Choisis un segment :",
                df_stats["secteur"].unique()
            )
  
            if option_seg : 
                # --- Filtrer sur le segment sélectionné ---
                df_seg = df_stats[df_stats['secteur'] == option_seg].copy()
                start= df_seg['start_checkpoint'].iloc[0]
                end= df_seg['end_checkpoint'].iloc[0]

            

                profile_altimetirque(df,df_gpx,has_terrain_type, end , start)
                stats_top(option_seg,df_seg)

        path_to_html = Path(f"data/TrailPacer/{event_code}/{course_code}/gpx_comparison/compare_{course_code}.html")

        if path_to_html.exists():
            with open(path_to_html, 'r', encoding="utf-8") as f:
                html_data = f.read()

            st.header("Différence de parcours des éditions prédécentes")
            st.components.v1.html(html_data, height=600, scrolling=True)
    


    except Exception as e:
            st.error("Cette page n'est pas encore disponible pour la course selectionnée !")
            print(f"[DEBUG] Erreur explorer_course: {e}")
            traceback.print_exc()




def profile_altimetirque(df,df_gpx,has_terrain_type,end, start=None):
    
        if end : 
            df['distance']=df['distance_cum_m']
            fig, metrics = create_col_profile(df_gpx, df,end,start,has_terrain_type)
            cols_alt = st.columns(len(metrics[0]))
 
            for i, (label, val) in enumerate(metrics[0].items()):
                cols_alt[i].metric(label, val)
            cols_slope = st.columns(len(metrics[1]))            
            for i, (label, val) in enumerate(metrics[1].items()):
                color = color_pente(val)
                cols_slope[i].markdown(f"<div style='text-align:left; font-size:20px; color:{color}'>{label}<br>{val:.1f}%</div>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        

        st.divider()        
def stats_top(option_seg,df_seg):

        if option_seg : 
            st.subheader("Meilleures performances de tout temps")
            if df_seg.empty:
                st.info(f"Aucun top10 disponible pour le segment {option_seg}.")
                return

            col1, col2 = st.columns(2)

            # --- Séparer hommes et femmes et garder top10 ---
            df_males = df_seg[df_seg['sex'] == 'MALE'].copy().sort_values("segment_time").head(10).reset_index(drop=True)
            df_females = df_seg[df_seg['sex'] == 'FEMALE'].copy().sort_values("segment_time").head(10).reset_index(drop=True)

            # --- Style simple top3 lignes ---
            def style_table(df):
                def color_rows(row):
                    if row.name == 0:
                        return ['background-color: gold; font-weight:bold']*len(row)
                    elif row.name == 1:
                        return ['background-color: silver; font-weight:bold']*len(row)
                    elif row.name == 2:
                        return ['background-color: #cd7f32; font-weight:bold']*len(row)
                    else:
                        return ['']*len(row)
                return df.style.apply(color_rows, axis=1)

            # --- Affichage ---
            with col1:
                st.subheader("Femmes")
                if not df_females.empty:
                    st.dataframe(
                        style_table(df_females[["rank", "name", "segment_time", "year"]]).hide(axis="index"),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Aucune donnée Femmes pour ce segment.")

            with col2:
                st.subheader("Hommes")
                if not df_males.empty:
                    st.dataframe(
                        style_table(df_males[["rank", "name", "segment_time", "year"]]).hide(axis="index"),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Aucune donnée Hommes pour ce segment.")
