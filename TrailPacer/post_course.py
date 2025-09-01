import streamlit as st
import json
import pandas as pd
from TrailPacer.PlotPacer import PacingPlotter
# -----------------------
# CONFIG
# -----------------------
race = "UTMB"
year = 2025
json_file = f"data/TrailPacer/{race}/post_course/{race}_{year}_all.json"
config_df = pd.read_csv(f"data/TrailPacer/{race}/post_course//config_analysis.csv") 
df_ranks=pd.read_csv(f"data/TrailPacer/{race}/post_course/ranks_{race}_{year}.csv")
# -----------------------
# CHARGEMENT DES DONNÉES


# -----------------------
# CHARGEMENT DES DONNÉES
# -----------------------
with open(json_file, "r", encoding="utf-8") as f:
    results = json.load(f)
# -----------------------------
# Conversion heures float -> hh:mm

def float_hours_to_hm(val):
    if pd.isna(val):
        return None
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)  # ou None si tu préfères

    neg = val < 0
    val = abs(val)
    h = int(val)
    m = int(round((val - h) * 60))
    return f"{'-' if neg else ''}{h}h{m:02d}"
# -----------------------------
# Fonction pour colorer écarts
def color_ecart(val):
    if val == "temps non enregistré":
        return "color:gray"
    if str(val).startswith("-"):
        return "color:green"
    else:
        return "color:red"

# -----------------------------
# Fonction pour colorer type de tronçon
def color_troncon(val):
    if "⬆" in val:
        return "background-color: #ffcccc"  # montée
    elif "⬇" in val:
        return "background-color: #ccffcc"  # descente
    else:
        return ""

# -----------------------------
# Fonction tableau post-course
def show_post_course_table(info):

    st.markdown("### Détails du parcours et des écarts")
    st.markdown(
        """
        Ce tableau présente, pour chaque tronçon du parcours :  
        - **Temps coureur** : temps réalisé par le coureur  
        - **Temps peloton autour du coureur** : temps médian du peloton autour du coureur  
        - **Écarts** : différence en valeur absolue et en pourcentage par rapport au peloton et aux élites  
        - **Type de tronçon** : montée ⬆ / descente ⬇  
        - **Peloton** : participants ayant terminé dans ±20% autour du coureur  
        - **Élite** : participants ayant terminé dans ±20% autour du premier coureur et ±20% autour de la première coureuse
        """
    )
    df_splits = pd.DataFrame(info['splits'])
    df_splits["runner_h"] = pd.to_numeric(df_splits["runner_h"], errors="coerce")
    df_splits = df_splits.merge(config_df, left_on="checkpoint", right_on="Checkpoint", how="left")

    # Ajouter flèches pour montée/descente
    df_splits["Tronçon"] = df_splits.apply(
        lambda row: ("⬆ " if row["Type de tronçon"]=="Montée" else
                     "⬇ " if row["Type de tronçon"]=="Descente" else "") + row["portion_name"], axis=1
    )

    # Colonnes principales
    df_table = pd.DataFrame({
        "Tronçon": df_splits["Tronçon"],
        "Temps coureur": df_splits["runner_h"].apply(float_hours_to_hm),
        "Temps peloton autour du coureur": df_splits["median_local_h"].apply(float_hours_to_hm),
        "Ecart peloton": df_splits["écart_local_h"].apply(float_hours_to_hm),
       "Ecart peloton %": df_splits["écart_local_%"].apply(
    lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) and pd.notna(x) else "N/A"),
        "Temps élite": df_splits["median_elite_h"].apply(float_hours_to_hm),
        "Ecart élite": df_splits["écart_elite_h"].apply(float_hours_to_hm),
        "Ecart élite %": df_splits["écart_elite_%"].apply( lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) and pd.notna(x) else "N/A"),
    })

    st.dataframe(
        df_table.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite","Ecart peloton %","Ecart élite %"])
            .map(color_troncon, subset=["Tronçon"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(df_table))+50,
        hide_index=True,
    )

    # -----------------------------
    # -----------------------------
    # Tableau récap Montée / Descente


    st.subheader("Récapitulatif Montée / Descente")
    st.markdown("""
    - **⬆ Montée** : portionsen rouge  dans tronçon (fond rouge clair)
    - **⬇ Descente** :  portions en vert dans tronçon (fond vert clair)
    - Les écarts sont colorés **vert** si le coureur est plus rapide que le peloton/élite et **rouge** si plus lent.
    """)

  
    recap = []
    # Totaux Montée/Descente
    for ttype in ["Montée", "Descente"]:
        mask = df_splits["Type de tronçon"] == ttype
        if mask.any():
            runner_sum = df_splits.loc[mask, "runner_h"].sum()
            median_local_sum = df_splits.loc[mask, "median_local_h"].sum()
            median_elite_sum = df_splits.loc[mask, "median_elite_h"].sum()
            ecart_local = runner_sum - median_local_sum
            ecart_elite = runner_sum - median_elite_sum
            ecart_local_pct = (ecart_local / median_local_sum * 100) if median_local_sum != 0 else None
            ecart_elite_pct = (ecart_elite / median_elite_sum * 100) if median_elite_sum != 0 else None
            recap.append({
                "Catégorie": f"{'⬆ ' if ttype=='Montée' else '⬇ '} {ttype}",
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })
    recap_df = pd.DataFrame(recap)

    st.dataframe(
        recap_df.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite","Ecart peloton %","Ecart élite %"])
            .map(lambda v: "background-color: #ffcccc" if "⬆" in v else "background-color: #ccffcc" if "⬇" in v else "", subset=["Catégorie"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_df))+50,
        hide_index=True,
    )

# -----------------------------
    # Totaux par Quart de course
    st.subheader("Récapitulatif par Quart de course")
    st.markdown("""
        - **Premier quart** : 0 à 47.2 km → Bonhomme
        - **Deuxième quart** : 87 km → Bertone
        - **Troisième quart** : 128.3 km → Champex-Lac
        - **Quatrième quart** : 175.4 km → Chamonix
        """)
    recap = []
    quart_colors = {
        "Premier quart": "#ffe5b4",
        "Deuxième quart": "#ffd699",
        "Troisième quart": "#ffcc80",
        "Quatrième quart": "#ffb366"
    }

    for quart in df_splits["Quart de course"].dropna().unique():
        mask = df_splits["Quart de course"] == quart
        if mask.any():
            runner_sum = df_splits.loc[mask, "runner_h"].sum()
            median_local_sum = df_splits.loc[mask, "median_local_h"].sum()
            median_elite_sum = df_splits.loc[mask, "median_elite_h"].sum()
            ecart_local = runner_sum - median_local_sum
            ecart_elite = runner_sum - median_elite_sum
            ecart_local_pct = (ecart_local / median_local_sum * 100) if median_local_sum != 0 else None
            ecart_elite_pct = (ecart_elite / median_elite_sum * 100) if median_elite_sum != 0 else None
            recap.append({
                "Catégorie": quart,
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })

    recap_df = pd.DataFrame(recap)
    st.dataframe(
        recap_df.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite","Ecart peloton %","Ecart élite %"])
            .map(lambda v: f"background-color: {quart_colors.get(v, '')}", subset=["Catégorie"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_df))+50,
        hide_index=True,
    )
def show_runner_info(info_runner):
    runner = info_runner.iloc[0]

    st.subheader(f"{runner['name']} | Doss. {runner['bib']} | {runner['country']} | FINISHER")
    st.write(f"**Sexe :** {runner['sex']} | **Catégorie :** {runner['category']} | **Club :** {runner['club']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Classement général", runner["rank"])
    col2.metric("Classement catégorie", runner["category_rank"])
    col3.metric("Classement sexe", runner['sex_rank'])

    st.write(f"**Temps final:** { runner["final_time"]}")
    if runner["diff_to_first"]:
        st.write(f"Écart avec 1er : {runner['diff_to_first']}")

# -----------------------------
# Page principale Streamlit
# -----------------------------
def show_post_course():
    st.title("Analyse Post-Course")

    try:
        # Construire liste mixte nom + dossard
        options = [f"{info['name']} (Doss. {bib})" for bib, info in results.items()]
        choice = st.selectbox("Rechercher un coureur", options)

        if not choice:
            st.info("Sélectionnez un coureur pour voir l'analyse.")
            return

        # Extraire le dossard
        bib = int(choice.split("(Doss. ")[1].split(")")[0])
        info = results.get(str(bib))

        if not info:
            st.warning("Coureur non trouvé")
            return

        # Affichage infos générales
      

        if info['status'] == "DNF":
            st.subheader(f"{info['name']} (Doss. {bib}) - {info['status']}")
            st.write(f"Abandon au checkpoint : {info.get('last_checkpoint','inconnu')}")
            return

        # Infos détaillées du coureur
        info_runner = df_ranks[df_ranks["bib"] == bib]
        if info_runner.empty:
            st.warning("Infos détaillées introuvables")
        else:
            show_runner_info(info_runner)
            st.divider()
            # Graphique pacing
            plotter = PacingPlotter(2025, "UTMB", "UTMB", offline=True)
            fig, df_relative = plotter.plot(bib)
            st.pyplot(fig)
            st.divider()
            show_post_course_table(info)

       

    except Exception as e:
        st.error("Oups, une erreur est survenue !")
        # Optionnel : log dans la console pour debug
        print(f"[DEBUG] Erreur show_post_course: {e}")