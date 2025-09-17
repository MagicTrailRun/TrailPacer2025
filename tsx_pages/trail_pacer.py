import streamlit as st
import pandas as pd
import io
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
from TrailPacer.data_loader import load_data, get_config
from TrailPacer.gpx_tracer import plot_altitude_profile_area
from TrailPacer.formatting import format_dataframe,get_base64_image
from TrailPacer.race_id import color_pente,altitude_metrics, process_data, load_data_checkpoints, create_col_profile, load_json,gpx_to_df, get_df_for_gpx
from TrailPacer.text import pacing, quisommesnous, votreavis, cnil
#from TrailPacer.post_course import show_post_course
from config.styles import apply_custom_css
import traceback
from pathlib import Path
import streamlit.components.v1 as components



print("___________________________________________")

st.set_page_config(page_title="TrailPacer", page_icon="🏃‍♂️", layout="wide")

import streamlit.components.v1 as components

def select_event():

    # --- CSS custom pour styliser les selectbox
    st.markdown("""
    <style>
    /* Conteneur général du selectbox */
    div[data-baseweb="select"] {
        background-color: #f9f9f9;      /* fond clair */
        border: 2px solid #e0e0e0;      /* bord fin */
        border-radius: 12px;            /* arrondi */
        padding: 6px 10px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease-in-out;
    }

    /* Hover effect */
    div[data-baseweb="select"]:hover {
        border: 2px solid #007bff;      /* bleu au survol */
        box-shadow: 0 4px 12px rgba(0,123,255,0.25);
    }

    /* Texte */
    div[data-baseweb="select"] span {
        font-size: 1.05em;
        font-weight: 500;
        color: #333;
    }

    /* Label au-dessus du selectbox */
    .css-10trblm, label {
        font-size: 1.1em !important;
        font-weight: bold !important;
        color: #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Définition des events/courses
    EVENT_CONFIG = st.session_state.get("EVENT_CONFIG", {})

    with st.sidebar:

        event = st.selectbox("🎯 Choisir un événement", list(EVENT_CONFIG.keys()))

        course = st.selectbox("🏃 Choisir une course", list(EVENT_CONFIG[event]["races"].keys()))

        year = st.selectbox("📅 Année", EVENT_CONFIG[event]["races"][course]["year"])

        st.success(f"Vous avez choisi **{event} – {course} – {year}**")

        # Sauvegarde en session_state
        st.session_state["event_name"] = event
        st.session_state["course_name"] = course
        st.session_state["year"] = year
        st.session_state["event"] = EVENT_CONFIG[event]['tenant']
        st.session_state["course"] = EVENT_CONFIG[event]['races'][course]["code"]

def show():

    st.set_page_config(layout="wide")

   
    year=st.session_state.get("year",2025)
    event=st.session_state["event"]
    course=st.session_state["course"]
    event_name=st.session_state["event_name"]
    course_name=st.session_state["course_name"]
    apply_custom_css()

    img_base64 = get_base64_image(f"TrailPacer/image/{event.lower()}.png")

    
    st.set_page_config(
        page_title="TrailPacer: Planificateur de temps de passage & Analyses course",
        page_icon="🏃‍♂️",
        layout="wide"
    )

    if img_base64:

        st.markdown(
        f"""
        <style>
        .hero {{
            position: relative;
            width: 100%;
            height: 300px;
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: top;
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
        .hero h3 {{
            position: absolute;
            top: 70%;
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
            <h2>{event_name}  </h2>
            <h3> {course_name}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
 
    
    else :
         st.markdown(
        f"""
        <style>
        .hero {{
            position: relative;
            width: 100%;
            height: 300px;
              background-color: white;
            background-size: cover;
            background-position: top;
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
        .hero h3 {{
            position: absolute;
            top: 70%;
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
            <h2>{event_name}  </h2>
            <h3> {course_name}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )


    #onfig, mapping_ckpts = get_config(f"data/TrailPacer/{event}/{course}/config/config_{year}.json", course)
    
    config = get_config(f"data/TrailPacer/{event}/{course}/config/config_{year}.json", course)
    

    df = load_data(event=event,race=course, year=year)

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
            target_time = st.slider("Sélectionnez le temps cible",
                min_value=config['temps_cible_start'],
                max_value=config['temps_cible_end'],
                value=config['temps_cible_middle'],
                label_visibility="collapsed"

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

        format = st.radio("Télécharger au format :", ["CSV", "Excel"], horizontal=True)

        if format == "CSV":
            data = df_display.to_csv(index=False).encode("utf-8")
            mime = "text/csv"
            fname = "temps_de_passage.csv"
        else:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_display.to_excel(writer, index=False, sheet_name="Temps_de_passage")
            data = output.getvalue()
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            fname = "temps_de_passage.xlsx"

        st.download_button(
            label=f"⬇️ Télécharger ({format})",
            data=data,
            file_name=fname,
            mime=mime,
        )

        st.divider()
        title=f"⛰️ Profil d'élévation - Objectif {target_time}h"
        st.subheader(title)
        affichages = st.multiselect(
            "Choisissez les éléments à afficher",
            ["Heure de passage", "Temps de passage", "D+ Secteur", "D- Secteur","Distance Secteur"],
            default=["Heure de passage","D+ Secteur", "D- Secteur"]
)       

      
        

        try :
            df_gpx, has_terrain_type =get_df_for_gpx(event, course, year)

            if not df_gpx.empty:
                fig = plot_altitude_profile_area(df_gpx, df, affichages, target_time)
                st.plotly_chart(fig, use_container_width=True)

        except:
            st.warning("Tracé GPS bientôt disponible")

        
    with pacing2 : 
        pacing()
 
    with explorer3 : 
        # if course == 'GRR' and year==2025 :
        #     path_to_html = Path("data/TrailPacer/grandraid-reunion-oxybol/GRR/gpx_comparaison/comparaison_GRR_2024_2025.html")

        #     if path_to_html.exists():
        #         with open(path_to_html, 'r', encoding="utf-8") as f:
        #             html_data = f.read()

        #         st.header("Différence de parcours entre 2024 et 2025")
        #         st.components.v1.html(html_data, height=600, scrolling=True)
       
        try :
            df_gpx, has_terrain_type =get_df_for_gpx(event, course, year)


            st.info("Page en cours de construction...")
            st.markdown("### Fiche identité")
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
        except Exception as e:
            st.error("Cette page n'est pas encore disponible pour la course selectionnée !")
            # Optionnel : log dans la console pour debug
            print(f"[DEBUG] Erreur explorer_course: {e}")
            traceback.print_exc()





    with postcourse4:
        try : 
            st.info("page temporairement indisponible")
            #show_post_course(event, race,year)
        except Exception as e:
            st.error("Cette page n'est pas encore disponible pour la course selectionnée !")
            # Optionnel : log dans la console pour debug
            print(f"[DEBUG] Erreur show_post_course: {e}")
            traceback.print_exc()




    with avis5 :

        votreavis()

    with qui6 :
        quisommesnous()

    with cnil7 :
        cnil()

if __name__ == "__main__":
    show()
