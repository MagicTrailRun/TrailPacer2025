import streamlit as st
import json
import pandas as pd
from TrailPacer.PlotPacer import PacingPlotter
from TrailPacer.text import explication_tab_post_course
import traceback





# -----------------------
# CONFIG
# -----------------------
race = "UTMB"
year = 2025
json_file = f"data/TrailPacer/{race}/post_course/{race}_{year}_all.json"
config_df = pd.read_csv(f"data/TrailPacer/{race}/post_course//config_analysis.csv") 
df_ranks=pd.read_csv(f"data/TrailPacer/{race}/post_course/ranks_{race}_{year}.csv")
df_best=pd.read_csv(f'data/TrailPacer/{race}/post_course/best_perf.csv')
df_cv=pd.read_csv(f"data/TrailPacer/{race}/post_course/variation_coefficient_{race}_{year}.csv")
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
    m = int((val - h) * 60)
    s = int(round((val - h - m/60) * 3600))

    return f"{'-' if neg else ''}{h:02d}:{m:02d}:{s:02d}"


# -----------------------
# COLLECT GLOBAL INFO

first_female_time = df_ranks[
    (df_ranks['sex'] == 'FEMALE') & (df_ranks['sex_rank'] == 1)
]['final_time'].iloc[0]
first_male_time = df_ranks[
    (df_ranks['sex'] == 'MALE') & (df_ranks['sex_rank'] == 1)
]['final_time'].iloc[0]

# best_by_sector = {}

# for runner_id, runner_info in results.items():
#     for split in runner_info["splits"]:
#         portion = split["portion_name"]
#         time_h = split["runner_h"]
#         if  time_h =='temps non enregistré':
#             continue
#         # Si on n'a pas encore ce secteur, on l'initialise
#         elif  portion not in best_by_sector:
#             best_by_sector[portion] = {"time_h": time_h, "name": runner_info["name"]}
#         else:
#             # On garde le meilleur temps (le plus petit)
#             if float(time_h) < float(best_by_sector[portion]["time_h"]):
#                 best_by_sector[portion] = {"time_h": time_h, "name": runner_info["name"]}
# df_best = pd.DataFrame([
#         {"portion_name": k, "Meilleure perf": f"{v['name']} ({float_hours_to_hm(v['time_h'])})"}
#         for k, v in best_by_sector.items()
#     ])

# df_best.to_csv(f'data/TrailPacer/{race}/post_course//best_perf.csv', index=False)

 #     # Sépare les hommes et les femmes
        #     df_ranks['final_time_sec'] = df_ranks['final_time'].apply(time_to_seconds)
        #     first_female_time_sec=time_to_seconds(first_female_time)
        #     first_male_time_sec=time_to_seconds(first_male_time)

        #    # Détermine les élites
        #     df_ranks['is_elite'] = df_ranks.apply(
        #         lambda row: row['final_time_sec'] <= 1.2 * (first_female_time_sec if row['sex'] == 'FEMALE' else first_male_time_sec),
        #         axis=1
        #     )

        #     # Nombre d’élites
        #     num_elites = df_ranks.groupby("sex")['is_elite'].sum()
        #     print(f"Nombre de coureurs élites : {num_elites}")

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


def post_course_detail(df_splits,df_best) :
# Colonnes principales
    df_splits["Tronçon"] = df_splits.apply(
        lambda row: ("⬆ " if row["Type de tronçon"]=="Montée" else
                     "⬇ " if row["Type de tronçon"]=="Descente" else "") + row["portion_name"], axis=1
    )
    df_splits = df_splits.merge(df_best, on="portion_name", how="left")
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
    "Meilleure perf" : df_splits['Meilleure perf']
    })
    
   
   
    st.dataframe(
        df_table.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite","Ecart peloton %","Ecart élite %"])
            .map(color_troncon, subset=["Tronçon"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(df_table))+50,
        hide_index=True,
    )


def post_course_pente(df_splits):
    recap_pente = []
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
            recap_pente.append({
                "Catégorie": f"{'⬆ ' if ttype=='Montée' else '⬇ '} {ttype}",
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })
    recap_pente_df = pd.DataFrame(recap_pente)
    st.dataframe(
        recap_pente_df.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite","Ecart peloton %","Ecart élite %"])
            .map(lambda v: "background-color: #ffcccc" if "⬆" in v else "background-color: #ccffcc" if "⬇" in v else "", subset=["Catégorie"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_pente_df))+50,
        hide_index=True,
    )

def post_course_quarts(df_splits):
    recap_quart = []
    
    # Mapping des quarts avec détails
    quart_details = {
        "Premier quart": "0–47.2 km | Chamonix → Bonhomme",
        "Deuxième quart": "47.2–87 km | Bonhomme → Bertone",
        "Troisième quart": "87–128.3 km | Bertone → Champex-Lac",
        "Quatrième quart": "128.3–175.4 km | Champex-Lac → Chamonix",
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

            recap_quart.append({
                "Quart (Détails)": f"{quart} ({quart_details.get(quart, '')})",
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })
    
    recap_quart_df = pd.DataFrame(recap_quart)
    st.dataframe(
        recap_quart_df.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite", "Ecart peloton %", "Ecart élite %"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_quart_df))+50,
        hide_index=True,
    )



def show_coefficient_variation(df_cv, bib):
    # Sélection du coureur
    df_cv_runner = df_cv[df_cv["Doss."] == bib].copy()
    
    # Renommer les colonnes avec des labels clairs
    rename_dict = {
        "variation_coefficient": "Coeff. variation",
        "vitesse_moy": "Vitesse moy. (km/h)",
        "cv_median_peers": "Coeff. médian (peloton)",
        "ecart_cv_peers": "Écart peloton",
        "cv_median_elite": "Coeff. médian (élite)",
        "ecart_cv_elite": "Écart élite",
    }
    
    df_cv_runner = df_cv_runner.rename(columns=rename_dict)
    df_cv_runner = df_cv_runner[list(rename_dict.values())]

    # Configuration des colonnes pour Streamlit
    column_config = {
        "Coeff. variation": st.column_config.NumberColumn("Coeff. variation (%)", format="%.2f"),
        "Vitesse moy. (km/h)": st.column_config.NumberColumn("Vitesse moy. (km/h)", format="%.2f"),
        "Coeff. médian (peloton)": st.column_config.NumberColumn("Coeff. peloton médian (%)", format="%.2f"),
        "Écart peloton": st.column_config.NumberColumn("Écart peloton", format="%.2f"),
        "Coeff. médian (élite)": st.column_config.NumberColumn("Coeff. élite médian (%)", format="%.2f"),
        "Écart élite": st.column_config.NumberColumn("Écart élite", format="%.2f"),
    }

    # Affichage Streamlit
    st.dataframe(
        df_cv_runner.style
            .map(color_ecart, subset=["Écart peloton", "Écart élite"])
            .set_table_attributes('style="width:100%"'),
        #height=(35 * len(df_cv_runner)) + 50,
        hide_index=True,
        column_config=column_config
    )


# -----------------------------
# Fonction tableau post-course
def show_post_course_table(info,df_best,df_cv,bib):
    
    st.header("Temps de passage et écarts : où avez-vous gagné ou perdu du temps?")
    st.markdown(
    """
    **Les différents tableaux ci-dessous comparent vos performances :**

    - aux coureurs ayant terminé dans un temps similaire au votre (+/- 5 %),  c'est-à-dire le peloton autour de vous,

    - et aux coureurs élites (temps de référence des meilleurs ~ top 30 au classement).

    Le meilleur temps par secteur est également présenté.
        

    **Les écarts sont exprimés :**

    - en valeur absolue (heures : minutes : secondes , avance ou retard),

    - et en valeur relative (écart en %).
 
""")
    st.success('La comparaison avec les coureurs d’un temps similaire illustre votre gestion de course par rapport à vos pairs, tandis que la comparaison avec les élites sert de repère de performance maximale.')
    
    st.markdown(
    """
 
    **Trois tableaux sont à dispositions pour analyser vos performances selon :**

    1) le profil du terrain (montées / descentes),

    2) la dynamique de course (par quart),

    3) le détail complet (secteur par secteur).
    """
    )

    df_splits = pd.DataFrame(info['splits'])
    df_splits["runner_h"] = pd.to_numeric(df_splits["runner_h"], errors="coerce")
    df_splits = df_splits.merge(config_df, left_on="checkpoint", right_on="Checkpoint", how="left")

 
    st.subheader('Récapitulatif montée / descente : où avez-vous fait la différence ? ')
    st.write(
    """
                
    Une vue d’ensemble de vos performances selon le profil du terrain : en rouge, les portions en montée (sur l’ensemble du parcours) ; en vert, les portions en descente.

    Pour savoir quels secteurs sont classés en montée ou en descente, référez-vous au tableau détaillé (codes couleur des secteurs).
                
    """)

    post_course_pente(df_splits)

    # Totaux par Quart de course
    st.subheader('Analyse par quart de course : comment votre rythme a évolué ?')
    st.write("""
    Un découpage en 4 parties égales pour observer votre dynamique de pacing.
            """)
    

    post_course_quarts(df_splits)



    st.subheader('Coefficient de variation : avez-vous été régulier ?')
    st.write("""

    Le coefficient de variation mesure la dispersion de vos allures entre les différents secteurs.

    - Un CV faible traduit une course régulière et bien maîtrisée.

    - Un CV élevé indique des variations importantes de rythme (accélérations, ralentissements, coups de moins bien).""")

    show_coefficient_variation(df_cv,bib)
    # Details secteur
    st.subheader('Analyse secteur par secteur : où avez-vous gagné ou perdu du temps ? ')
    st.write('Le détail complet de vos passages.')

    post_course_detail(df_splits,df_best)






def show_runner_info(info_runner):
    runner = info_runner.iloc[0]

    st.subheader(f"{runner['name']} | Doss. {runner['bib']} | {runner['country']} | FINISHER")
    st.write(f"**Sexe :** {runner['sex']} | **Catégorie :** {runner['category']} | **Club :** {runner['club']}")
    if runner["diff_to_first"] and  runner["rank"]!=1:
        st.markdown(f"#### Temps final: { runner["final_time"]} | Écart avec 1er : {runner['diff_to_first']}")
    else :
        st.markdown(f"#### Temps final: { runner["final_time"]}")
 

    col1, col2, col3 = st.columns(3)
    col1.metric("Classement général", runner["rank"])
    col2.metric("Classement catégorie", runner["category_rank"])
    col3.metric("Classement sexe", runner['sex_rank'])



def time_to_seconds(t):
    h, m, s = map(int, t.split(':'))
    return h*3600 + m*60 + s



def compare_course_detail(df1, df2,nom1,nom2):

    df = df1.merge(df2, on="portion_name", suffixes=("_c1", "_c2"))

    df["Tronçon"] = df.apply(
        lambda row: ("⬆ " if row["Type de tronçon_c1"]=="Montée" else
                     "⬇ " if row["Type de tronçon_c1"]=="Descente" else "") + row["portion_name"], axis=1
    )

    df_table = pd.DataFrame({
        "Tronçon": df["Tronçon"],
        f"{nom1}": df["runner_h_c1"].apply(float_hours_to_hm),
        f"{nom2}": df["runner_h_c2"].apply(float_hours_to_hm),
        "Écart": (df["runner_h_c1"] - df["runner_h_c2"]).apply(float_hours_to_hm),
        "Écart %": ((df["runner_h_c1"] - df["runner_h_c2"]) / df["runner_h_c1"] * 100).apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )
    })

    st.dataframe(
        df_table.style
            .map(color_troncon, subset=["Tronçon"])
            .map(color_ecart, subset=["Écart","Écart %"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(df_table))+50,
        hide_index=True,
    )


def compare_course_pente(df1, df2,nom1,nom2):
    recap_pente = []
    for ttype in ["Montée", "Descente"]:
        mask1 = df1["Type de tronçon"] == ttype
        mask2 = df2["Type de tronçon"] == ttype
        if mask1.any() and mask2.any():
            sum1 = df1.loc[mask1, "runner_h"].sum()
            sum2 = df2.loc[mask2, "runner_h"].sum()
            ecart = sum1-sum2
            ecart_pct = (ecart / sum1 * 100) if sum1 != 0 else None
            recap_pente.append({
                "Catégorie": f"{'⬆ ' if ttype=='Montée' else '⬇ '} {ttype}",
                 f"{nom1}": float_hours_to_hm(sum1),
                 f"{nom2}": float_hours_to_hm(sum2),
                "Écart": float_hours_to_hm(ecart),
                "Écart %": f"{ecart_pct:.1f}%" if ecart_pct is not None else "N/A"
            })
    recap_pente_df = pd.DataFrame(recap_pente)
    st.dataframe(
        recap_pente_df.style
            .map(lambda v: "background-color: #ffcccc" if "⬆" in v else "background-color: #ccffcc" if "⬇" in v else "", subset=["Catégorie"])
            .map(color_ecart, subset=["Écart","Écart %"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_pente_df))+50,
        hide_index=True,
    )


def compare_course_quarts(df1, df2,nom1,nom2):
    recap_quart = []
    quart_details = {
        "Premier quart": "0–47.2 km | Chamonix → Bonhomme",
        "Deuxième quart": "47.2–87 km | Bonhomme → Bertone",
        "Troisième quart": "87–128.3 km | Bertone → Champex-Lac",
        "Quatrième quart": "128.3–175.4 km | Champex-Lac → Chamonix",
    }

    for quart in df1["Quart de course"].dropna().unique():
        mask1 = df1["Quart de course"] == quart
        mask2 = df2["Quart de course"] == quart
        if mask1.any() and mask2.any():
            sum1 = df1.loc[mask1, "runner_h"].sum()
            sum2 = df2.loc[mask2, "runner_h"].sum()
            ecart = sum1 - sum2
            ecart_pct = (ecart / sum1 * 100) if sum1 != 0 else None
            recap_quart.append({
                "Quart (Détails)": f"{quart} ({quart_details.get(quart, '')})",
                 f"{nom1}": float_hours_to_hm(sum1),
                 f"{nom2}": float_hours_to_hm(sum2),
                "Écart": float_hours_to_hm(ecart),
                "Écart %": f"{ecart_pct:.1f}%" if ecart_pct is not None else "N/A"
            })

    recap_quart_df = pd.DataFrame(recap_quart)
    st.dataframe(
        recap_quart_df.style
            .map(color_ecart, subset=["Écart","Écart %"])
            .set_table_attributes('style="width:100%"'),
        height=(35*len(recap_quart_df))+50,
        hide_index=True,
    )



def compare_coefficient_variation(df_cv, nom1, nom2, bib1, bib2):
    # Extraire les valeurs pour chaque coureur
    runner1 = df_cv.loc[df_cv["Doss."] == bib1, ["variation_coefficient", "vitesse_moy"]].values
    runner2 = df_cv.loc[df_cv["Doss."] == bib2, ["variation_coefficient", "vitesse_moy"]].values

    if len(runner1) == 0 or len(runner2) == 0:
        st.warning("Impossible de trouver les données pour un ou les deux coureurs.")
        return

    cv1, speed1 = runner1[0]
    cv2, speed2 = runner2[0]

    # Construire DataFrame comparatif
    df_comp = pd.DataFrame([{
        f"Coeff. variation {nom1}": round(cv1, 2),
        f"Coeff. variation {nom2}": round(cv2, 2),
        f"Vitesse moy. {nom1} (km/h)": round(speed1, 2),
        f"Vitesse moy. {nom2} (km/h)": round(speed2, 2),
        "Écart coeff.": round(cv1 - cv2, 2),
        "Écart vitesse (km/h)": round(speed1 - speed2, 2)
    }])

    # Configuration colonnes Streamlit (optionnel mais pour un rendu pro)
    column_config = {
        f"Coeff. variation {nom1}": st.column_config.NumberColumn(f"Coeff. variation {nom1} (%)", format="%.2f"),
        f"Coeff. variation {nom2}": st.column_config.NumberColumn(f"Coeff. variation {nom2} (%)", format="%.2f"),
        f"Vitesse moy. {nom1} (km/h)": st.column_config.NumberColumn(f"Vitesse moy. {nom1} (km/h)", format="%.2f"),
        f"Vitesse moy. {nom2} (km/h)": st.column_config.NumberColumn(f"Vitesse moy. {nom2} (km/h)", format="%.2f"),
        "Écart coeff.": st.column_config.NumberColumn("Écart coeff. (%)", format="%.2f"),
        "Écart vitesse (km/h)": st.column_config.NumberColumn("Écart vitesse (km/h)", format="%.2f")
    }

    # Affichage
    st.dataframe(
        df_comp.style
            .map(color_ecart, subset=["Écart coeff.", "Écart vitesse (km/h)"])
            .set_table_attributes('style="width:100%"'),
        hide_index=True,
        column_config=column_config
    )
def compare_runners():
    try : 
        st.header('Comparaison de deux coureurs')

        options = [f"{info['name']} (Doss. {bib})" for bib, info in results.items()]
        selected = st.multiselect("Sélectionnez deux coureurs", options, max_selections=2)

        if len(selected) != 2:
            st.info("Veuillez sélectionner exactement deux coureurs pour la comparaison.")
            return

        bib1 = int(selected[0].split("(Doss. ")[1].split(")")[0])
        bib2 = int(selected[1].split("(Doss. ")[1].split(")")[0])

        info1 = results[str(bib1)]
        info2 = results[str(bib2)]
        if not info1 or not info2:
            st.warning("Coureur non trouvé")
            return

        # Affichage infos générales
        for info in [info1, info2]: 
            if info['status'] == "DNF":
                st.subheader(f"{info['name']} - {info['status']}")
                st.write(f"Abandon au checkpoint : {info.get('last_checkpoint','inconnu')}")
                st.error('La comparaison ne se fait que pour les finishers')
                return


        col1, col_sep, col2 = st.columns([3,1,3])  # la colonne du milieu est très fine

        for (bib, info, col) in [(bib1, info1, col1), (bib2, info2, col2)]:
            with col:
                info_runner = df_ranks[df_ranks["bib"] == bib]
                if info_runner.empty:
                    st.warning("Infos détaillées introuvables")
                else:
                    show_runner_info(info_runner)

        # Ajout d'une ligne verticale de séparation
        with col_sep:
            st.markdown(" ")
            st.markdown(
                "### VS")


        st.divider()
        nom1=info1['name']
        nom2=info2['name']
        plotter = PacingPlotter(2025, "UTMB", "UTMB", is_elite=False, offline=True)
        fig, df_relative = plotter.plot([bib1,bib2])
        st.pyplot(fig)
        # Afficher tableau de variation de coefficient côte à côte
        df1 = pd.DataFrame(info1["splits"])
        
        df1["runner_h"] = pd.to_numeric(df1["runner_h"], errors="coerce")
        df1 = df1.merge(config_df, left_on="checkpoint", right_on="Checkpoint", how="left")

        df2 = pd.DataFrame(info2["splits"])
        df2["runner_h"] = pd.to_numeric(df2["runner_h"], errors="coerce")
        df2 = df2.merge(config_df, left_on="checkpoint", right_on="Checkpoint", how="left")

        st.subheader('Récapitulatif montée / descente : où avez-vous fait la différence ? ')

        compare_course_pente(df1, df2,nom1, nom2)

        st.subheader('Analyse par quart de course : comment votre rythme a évolué ?')
        st.write("""
        Un découpage en 4 parties égales pour observer votre dynamique de pacing.
            """)
        compare_course_quarts(df1, df2,nom1, nom2)

        st.subheader('Coefficient de variation : avez-vous été régulier ?')
        st.write("""

    Le coefficient de variation mesure la dispersion de vos allures entre les différents secteurs.

    - Un CV faible traduit une course régulière et bien maîtrisée.

    - Un CV élevé indique des variations importantes de rythme (accélérations, ralentissements, coups de moins bien).""")
        
        compare_coefficient_variation(df_cv, nom1, nom2,bib1, bib2)
        st.subheader('Analyse secteur par secteur : où avez-vous gagné ou perdu du temps ? ')
        st.write('Le détail complet de vos passages.')

        compare_course_detail(df1, df2,nom1, nom2)

    except Exception as e:
        st.error("Oups, une erreur est survenue !")
        # Optionnel : log dans la console pour debug
        print(f"[DEBUG] Erreur show_post_course: {e}")
        traceback.print_exc()



def post_course_indiv():
   
    st.header('Analyse détaillée')
    try:
        
        # Construire liste mixte nom + dossard
        options =["--"]+ [f"{info['name']} (Doss. {bib})" for bib, info in results.items()]
        choice = st.selectbox("Choisissez un coureur pour lancer l’analyse", options)

        if not choice or choice =='--' :
            st.info("Sélectionnez un coureur pour lancer l'analyse.")
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
        runner = info_runner.iloc[0]
        if info_runner.empty:
            st.warning("Infos détaillées introuvables")
        else:

            if runner['sex'] == "FEMALE" :
                first_time=first_female_time
            else :
                first_time=first_male_time
            
            

            runner_time_sec = time_to_seconds(runner['final_time'])
            first_time_sec = time_to_seconds(first_time)
            is_elite = runner_time_sec <= 1.2 * first_time_sec

       
            show_runner_info(info_runner)
            st.divider()
            # Graphique pacing

            plotter = PacingPlotter(2025, "UTMB", "UTMB", is_elite=is_elite, offline=True)
            fig, df_relative = plotter.plot(bib)
            st.pyplot(fig)
            explication_tab_post_course()
            
            st.divider()
            show_post_course_table(info,df_best, df_cv, bib)

       

    except Exception as e:
        st.error("Oups, une erreur est survenue !")
        # Optionnel : log dans la console pour debug
        print(f"[DEBUG] Erreur show_post_course: {e}")
        traceback.print_exc()




def show_post_course():
    st.title("Analyse post-course UTMB 2025")

    st.markdown(
        """
        <div style="padding:12px; border-radius:12px; background-color:#f0f2f6; margin-bottom:20px;">
            Sélectionnez le mode d'analyse souhaité ci-dessous pour explorer les performances :
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(" Analyse individuelle", use_container_width=True):
            st.session_state["analyse_type"] = "individuelle"

    with col2:
        if st.button(" Comparer 2 coureurs", use_container_width=True):
            st.session_state["analyse_type"] = "comparaison"


    if "analyse_type" not in st.session_state:
        st.info("👉 Veuillez choisir un mode d'analyse ci-dessus pour commencer.")
        return
    
    # Affichage en fonction du choix
    if st.session_state["analyse_type"] == "individuelle":

        post_course_indiv()

    elif st.session_state["analyse_type"] == "comparaison":

        compare_runners()
