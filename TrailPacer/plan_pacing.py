import io
import streamlit as st
import pandas as pd
from TrailPacer.gpx_tracer import plot_altitude_profile_area
from TrailPacer.formatting import format_dataframe


def show_intro_section():
    st.header("MODE D’EMPLOI")
    st.write(
        "1. Choisissez votre temps objectif\n"
        "2. Trail Pacer calcule vos temps de passage optimisés\n"
        "3. Téléchargez votre plan ou visualisez-le directement sur le profil de la course."
    )
    st.markdown("---")
    st.markdown("### Fixez votre objectif de temps pour l’arrivée, Trail Pacer calcule vos temps de passage.")


def select_target_time(config):
    col1, _, _ = st.columns([1, 1, 2])
    with col1:
        return st.slider(
            "Sélectionnez le temps cible",
            min_value=config['temps_cible_start'],
            max_value=config['temps_cible_end'],
            value=config['temps_cible_middle'],
            label_visibility="collapsed"
        )


def generate_plan_table(df, target_time, start_time):
    if df.empty:
        st.warning("⚠️ Aucune donnée de course disponible.")
        st.stop()

    df, df_display = format_dataframe(df, target_time, start_time)
    st.subheader(f"📋 Plan de course généré pour {target_time} h")

    st.table(
        df_display.style
        .format(escape='html')
        .set_table_styles([{'selector': 'th', 'props': [('background-color', "#f8f9fa"), ('color', 'black'), ('font-weight', 'bold')]}])
        .set_properties(**{"text-align": "center", "background-color": "#f8f9fa", "color": "black"})
    )
    return df, df_display


def show_nutrition_section(df, df_display, target_time):
    with st.expander("Personnaliser votre plan de course", icon=":material/discover_tune:", expanded=True):

        col_obj, col_col = st.columns([1, 1])
        with col_obj:
            st.markdown("### :material/water_bottle: Ajoutez vos objectifs nutritionnels et d'hydratation")
            glucides = st.number_input("**Glucides (g/h)** _(recommandé : 60–90)_", min_value=0, max_value=100, step=1)
            eau = st.number_input("**Hydratation (mL/h)** _(recommandé : 400–800)_", min_value=0, max_value=2000, step=50)

        with col_col:
            if glucides > 0 or eau > 0:
                st.markdown("### :material/lab_profile: Résumé de votre plan nutritionnel")

            warning = ""
            if glucides > 0 and not (60 <= glucides <= 90):
                warning += "⚠️ Votre apport en glucides est en dehors de la plage recommandée (60–90 g/h).\n\n"
            if eau > 0 and not (400 <= eau <= 800):
                warning += "⚠️ Votre hydratation est en dehors de la plage recommandée (400–800 mL/h)."

            if warning:
                st.warning(warning.strip())

            col_g, col_e = st.columns(2)
            if glucides > 0:
                total_g = (glucides * target_time) / 1000
                col_g.metric("🍌 Total glucides estimés", f"{total_g:.1f} kg")

            if eau > 0:
                total_e = (eau * target_time) / 1000
                col_e.metric("💧 Total hydratation estimée", f"{total_e:.1f} L")

            if glucides > 0 and eau > 0:
                st.info(
                    f"**Sur {target_time:.0f} h :** {glucides} g/h de glucides (~ {total_g:.2f} kg) "
                    f"et {eau} mL/h d’hydratation (~ {total_e:.2f} L)."
                )

        colonnes_obligatoires = ["Heure de passage", "Temps de course cumulé", "Temps segment (± 5%)"]
        if glucides > 0:
            df_display["Glucides secteur (g)"] = (df["temps_secteur_med"] * glucides).apply(lambda x: f"{x:.0f}")
            colonnes_obligatoires.append("Glucides secteur (g)")
        if eau > 0:
            df_display["Hydratation secteur (mL)"] = (df["temps_secteur_med"] * eau).apply(lambda x: f"{x:.0f}")
            colonnes_obligatoires.append("Hydratation secteur (mL)")

        colonnes_selectionnees = st.multiselect(
            "Cochez les colonnes à afficher :",
            options=df_display.columns.tolist(),
            default=colonnes_obligatoires
        )

        colonnes_finales = [c for c in df_display.columns if (c in colonnes_obligatoires) or (c in colonnes_selectionnees)]

        st.table(
            df_display[colonnes_finales].style
            .format(escape='html')
            .set_table_styles([{'selector': 'th', 'props': [('background-color', "#f8f9fa"), ('color', 'black'), ('font-weight', 'bold')]}])
            .set_properties(**{"text-align": "center", "background-color": "#f8f9fa", "color": "black"})
        )

        return df_display[colonnes_finales]


def download_plan(df_display):
    format_type = st.radio("Télécharger au format :", ["CSV", "Excel"], horizontal=True)
    if format_type == "CSV":
        data = df_display.to_csv(index=False).encode("utf-8")
        mime = "text/csv"
        fname = "temps_de_passage.csv"
    else:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_display.to_excel(writer, index=False, sheet_name="temps_de_passage")
        data = output.getvalue()
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        fname = "temps_de_passage.xlsx"

    st.download_button("Télécharger", data=data, file_name=fname, mime=mime, icon=":material/download:")


def show_altitude_profile(df, df_gpx, target_time):
    st.divider()
    st.subheader(f"⛰️ Profil d'élévation - Objectif {target_time}h")
    affichages = st.multiselect(
        "Choisissez les éléments à afficher",
        ["Heure de passage", "Temps de course cumulé", "D+ Segment", "D- Segment", "Distance Segment"],
        default=["Heure de passage", "D+ Segment", "D- Segment"]
    )
    if not df_gpx.empty:
        fig = plot_altitude_profile_area(df_gpx, df, affichages, target_time)
        st.plotly_chart(fig, use_container_width=True, selection_mode='points')
    else:
        st.warning("Tracé GPS bientôt disponible")


def show_plan_pacing():
    config = st.session_state.get("config")
    df = st.session_state.get("df", pd.DataFrame())
    df_gpx = st.session_state.get("df_gpx", pd.DataFrame())

    show_intro_section()
    target_time = select_target_time(config)
    df, df_display = generate_plan_table(df, target_time, config["startDate"])
    df_final = show_nutrition_section(df, df_display, target_time)
    download_plan(df_final)
    show_altitude_profile(df, df_gpx, target_time)
