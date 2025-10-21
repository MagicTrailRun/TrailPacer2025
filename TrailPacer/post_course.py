import streamlit as st
import json
import pandas as pd
from pathlib import Path
import traceback
from TrailPacer.PlotPacer import PacingPlotter
from TrailPacer.text import explication_tab_post_course
import streamlit.components.v1 as components
from TrailPacer.formatting import image_to_base64
import base64
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import os

def get_icon_base64(icon_name: str) -> str:
    """
    Récupère une icône en base64 avec mise en cache.
    
    Args:
        icon_name: Nom de l'icône ('montee' ou 'descente')
    
    Returns:
        str: Code HTML de l'image en base64
    """
    
    try:
        if pd.isna(icon_name):
            return ""
        icon_name = str(icon_name).strip().lower()
        if icon_name == "montée" :
            icon_name= "montee"
        if icon_name == 'non catégorisé':
            return ""
        icon_path = os.path.join("TrailPacer", "image", f"{icon_name}.png")
        base64_str = image_to_base64(icon_path)
        return f'<img src="data:image/png;base64,{base64_str}" width="20" alt="{icon_name}"/>'
    except Exception as e:
        st.warning(f"Impossible de charger l'icône {icon_name}: {e}")
        # Fallback avec des symboles Unicode
        return ""

def show_post_course(course_name,event_code, course_code, year):
    """
    Affiche l'analyse post-course pour un événement donné.
    
    Args:
        event_code (str): Code de l'événement (ex: "UTMB")
        course_code (str): Code de la course (ex: "UTMB") 
        year (int ou str): Année de l'événement
    """
    st.title(f"Analyse post-course {course_name} {year}")
    
    # Conversion en string si nécessaire
    year = str(year)
    
    try:
        # Chargement des données
        data = _load_post_course_data(event_code, course_code, year)
        # Prépare les icônes


        
        if data is None:
            st.error("❌ Page non disponible pour cette course")
            st.info("Les données d'analyse post-course ne sont pas encore disponibles.")
            return
            
        # Extraction des données
        results = data['results']
        config_df = data['config_df']
        df_cv = data['df_cv']

        # Interface utilisateur
        _show_analysis_interface(
            results, config_df,df_cv, 
           event_code, course_code, year,course_name
        )
        
    except Exception as e:
        st.error("❌ Erreur lors du chargement des données")
        st.exception(e)




def _load_post_course_data(event_code, course_code, year):
    """
    Charge toutes les données nécessaires pour l'analyse post-course.
    
    Returns:
        dict: Dictionnaire contenant toutes les données ou None si erreur
    """
    try:
        base_path = Path(f"data/TrailPacer/{event_code}/{course_code}/post_course")
        
        # Vérification de l'existence du dossier
        if not base_path.exists():
            st.warning(f"📁 Dossier non trouvé: {base_path}")
            return None
        
        # Définition des fichiers requis (CORRECTION: underscore manquant)
        files = {
            'results': base_path / f"{course_code}_{year}_all.json",
            'config': base_path / f"df_config_{course_code}_{year}.csv",  # Ajout underscore
            'cv': base_path / f"df_cv_{course_code}_{year}.csv"
        }
        
        # Vérification de l'existence des fichiers
        missing_files = []
        for name, file_path in files.items():
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            st.warning("📄 Fichiers manquants:")
            for file in missing_files:
                st.write(f"- {file}")
            return None
        
        # Chargement des données
        with open(files['results'], "r", encoding="utf-8") as f:
            results = json.load(f)
        
        config_df = pd.read_csv(files['config'])
        df_cv = pd.read_csv(files['cv'])
        
        # Validation des données
        if not results:
            st.warning("⚠️ Aucun résultat trouvé dans les données")
            return None
        
        # Validation structure config_df
        required_config_cols = ['portion_name', 'Type de tronçon', 'Quart de course','secteur_quart']
        if not all(col in config_df.columns for col in required_config_cols):
            st.warning(f"⚠️ Colonnes manquantes dans df_config: {required_config_cols}")
            return None
        
        # Validation structure df_cv
        required_cv_cols = ['bib', 'name', 'variation_coefficient', 'vitesse_moy']
        if not all(col in df_cv.columns for col in required_cv_cols):
            st.warning(f"⚠️ Colonnes manquantes dans df_cv: {required_cv_cols}")
            return None
        
        # Renommer la colonne 'bib' en 'Doss.' pour compatibilité avec le reste du code
        if 'bib' in df_cv.columns:
            df_cv = df_cv.rename(columns={'bib': 'Doss.'})
        
        return {
            'results': results,
            'config_df': config_df,
            'df_cv': df_cv,
        }
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        st.exception(e)
        return None




def _show_analysis_interface(results, config_df, df_cv, 
                            event_code, course_code, year,course_name):
    """
    Affiche l'interface d'analyse post-course.
    """
    
    # Statistiques générales
    total_runners = len(results)
    finishers = len([r for r in results.values() if r.get('status') == 'FINISHER'])
    dnf_rate = ((total_runners - finishers) / total_runners * 100) if total_runners > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total coureurs", total_runners)
    with col2:
        st.metric("Finishers", finishers)
    with col3:
        st.metric("Taux d'abandon", f"{dnf_rate:.1f}%")
    
    st.divider()
    
    # Interface de sélection du mode d'analyse
    st.info("👉 Sélectionnez le mode d'analyse souhaité ci-dessous pour explorer les performances :")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏃 Analyse individuelle", use_container_width=True):
            st.session_state["analyse_type"] = "individuelle"
    
    with col2:
        if st.button("⚖️ Analyse comparée", use_container_width=True):
            st.session_state["analyse_type"] = "comparaison"
    
    # Affichage en fonction du choix
    if st.session_state.get("analyse_type") == "individuelle":
        _show_individual_analysis(results, config_df, df_cv, 
                                event_code, course_code, year,course_name)
    elif st.session_state.get("analyse_type") == "comparaison":
        _show_comparison_analysis(results, config_df, df_cv, 
                                event_code, course_code, year,course_name)





def _show_individual_analysis(results, config_df, df_cv, 
                              event_code, course_code, year,course_name):
    """
    Affiche l'interface d'analyse individuelle.
    """
    st.header('Analyse détaillée')
    try:
        st.info("Sélectionnez un coureur pour lancer l'analyse :")

        options = ["--"] + [
            f"{info.get('rank_scratch','DNF')} - {info.get('name','Inconnu')} (Doss. {bib})"
            for bib, info in sorted(results.items(), key=lambda x: x[1].get("rank_scratch", 9999))
        ]
        choice = st.selectbox("Choisir un coureur :", options, label_visibility="collapsed")

        if not choice or choice == "--":
            return

        bib = int(choice.split("(Doss. ")[1].split(")")[0])
        info = results.get(str(bib))

        if not info:
            st.warning("❌ Coureur non trouvé")
            return

        if info.get('status') == "DNF":
            st.subheader(f"{info.get('name','Inconnu')} (Doss. {bib}) - DNF")
            st.write(f"Statut: Abandon")
            return

        # Affichage info coureur
        col1, col2 = st.columns([2, 1])
        with col1:
            show_runner_info(info,bib)
        # Graphique pacing si disponible
        try:
            is_elite=info.get("is_elite", False)
            plotter = PacingPlotter(year, event_code, course_name, course_code, 
                                   is_elite=is_elite, offline=True)
            fig, _ = plotter.plot(bib)
            st.pyplot(fig)
            explication_tab_post_course()
        except Exception as e:
            st.warning(f"Graphique pacing non disponible: {e}")

        st.divider()
        
        # Tableaux d'analyse
        show_post_course_table(info, config_df, df_cv, bib)

    except Exception as e:
        st.error("Erreur lors de l'analyse individuelle")
        st.exception(e)


def _show_comparison_analysis(results, config_df, df_cv, event_code, course_code, year,course_name):
    try: 
        st.header('Comparaison de deux finishers')
        st.info("Veuillez sélectionner exactement deux dossards pour la comparaison.")

        options = ["--"] + [
            f"{info.get('rank_scratch','DNF')} - {info.get('name','Inconnu')} (Doss. {bib})"
            for bib, info in sorted(results.items(), key=lambda x: x[1].get("rank_scratch", 9999))
        ]
        selected = st.multiselect("Sélection", options, max_selections=2)

        if len(selected) != 2 or "--" in selected:
            return

        def extract_bib(option):
            return int(option.split("(Doss. ")[1].split(")")[0])

        bib1, bib2 = [extract_bib(opt) for opt in selected]
        info1 = results.get(str(bib1))
        info2 = results.get(str(bib2))

        if not info1 or not info2:
            st.warning("❌ Dossard non trouvé")
            return

        # Vérifier statut
        for info in [info1, info2]:
            if info.get('status') != "FINISHER":
                st.error("⚠️ La comparaison n'est possible que pour les finishers")
                return

        # Affichage des infos
        col1, col_sep, col2 = st.columns([3,1,3])  # la colonne du milieu est très fine

        for (bib, info, col) in [(bib1, info1, col1), (bib2, info2, col2)]:
            with col:
                
                show_runner_info(info,bib)
        with col_sep:
            st.markdown(
        "<h3 style='text-align: center;'>VS</h3>",
        unsafe_allow_html=True
    )
        # Graphique pacing
        plotter = PacingPlotter(year, event_code,course_name, course_code, 
                                is_elite=False, offline=True, show_peloton=False)
        fig, _ = plotter.plot([bib1, bib2])
        st.pyplot(fig)
        # Analyse comparative
        df1 = pd.DataFrame(info1["splits"])
        df1["runner_h"] = pd.to_numeric(df1["runner_h"], errors="coerce")
        df1 = df1.merge(config_df, on="portion_name", how="left")

        df2 = pd.DataFrame(info2["splits"])
        df2["runner_h"] = pd.to_numeric(df2["runner_h"], errors="coerce")
        df2 = df2.merge(config_df, on="portion_name", how="left")

        nom1, nom2 = info1.get('name', '?'), info2.get('name', '?')

        st.subheader('Récapitulatif montée / descente')
        compare_course_pente(df1, df2, nom1, nom2)

        st.subheader('Analyse par quart de course')
        compare_course_quarts(df1, df2, nom1, nom2)

        st.subheader('Coefficient de variation')
        compare_coefficient_variation(df_cv, nom1, nom2, bib1, bib2)

        st.subheader('Analyse secteur par secteur')
        compare_course_detail(df1, df2, nom1, nom2)
    except Exception as e:
        st.error("Erreur lors de l'analyse comparative")
        st.exception(e)




# Fonction pour colorer écarts
def color_ecart(val):
    if val == "temps non enregistré":
        return "color:gray"
    if str(val).startswith("-"):
        return "color:green"
    else:
        return "color:red"
def color_ecart_neg(val):
    if val == "temps non enregistré":
        return "color:gray"
    if str(val).startswith("-"):
        return "color:red"
    else:
        return "color:green"

def color_troncon(val):
    """Applique une couleur de fond selon le type de tronçon."""
    val_str = str(val)
    if get_icon_base64('montee') in val_str :
        return "background-color: #ffe5b4"  # orange pâle pour montée
    elif get_icon_base64('descente') in val_str :
        return "background-color: #cce5ff"  # bleu clair pour descente
    return ""



def post_course_detail(df_splits):

    # Ajout de deux colonnes séparées : "Profil" (icône) + "Tronçon" (nom)
    df_splits["Profil"] = df_splits["Type de tronçon"].map(lambda t: get_icon_base64(t))
    df_splits["Tronçon"] = df_splits["portion_name"]


    df_table = pd.DataFrame({
        "Profil": df_splits["Profil"],
        "Tronçon": df_splits["Tronçon"],
        "Temps coureur": df_splits["runner_h"].apply(float_hours_to_hm),
        "Temps peloton autour du coureur": df_splits["median_local_h"].apply(float_hours_to_hm),
        "Ecart peloton": df_splits["écart_local_h"].apply(float_hours_to_hm),
        "Ecart peloton %": df_splits["écart_local_%"].apply(
            lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) and pd.notna(x) else "N/A"
        ),
        "Temps élite": df_splits["median_elite_h"].apply(float_hours_to_hm),
        "Ecart élite": df_splits["écart_elite_h"].apply(float_hours_to_hm),
        "Ecart élite %": df_splits["écart_elite_%"].apply(
            lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) and pd.notna(x) else "N/A"
        ),
        "Meilleure perf": df_splits["Meilleure perf"]
    })

    # Styling
    styled = (
        df_table.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite", "Ecart peloton %", "Ecart élite %"])
            .map(color_troncon, subset=["Profil"])  
            .set_properties(**{"text-align": "center"})
            .set_table_attributes('style="width:100%"')
            .hide(axis="index")
    )

    st.write(styled.to_html(escape=False), unsafe_allow_html=True)


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
                " ":  get_icon_base64(ttype.lower()),
                "Catégorie": ttype,
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })

    df_recap = pd.DataFrame(recap_pente)

    # Styling avec couleurs douces
    styled = (
        df_recap.style
            .map(color_ecart, subset=["Ecart peloton", "Ecart élite", "Ecart peloton %", "Ecart élite %"])
            .map(color_troncon, subset=[" "])   # <-- applique les couleurs aux icônes
            .set_properties(**{"text-align": "center"})
            .set_table_attributes('style="width:100%"')
            .hide(axis="index")
    )

    st.write(styled.to_html(escape=False), unsafe_allow_html=True)




def post_course_quarts(df_splits):
   
    recap_quart = []
    
    # Tri pour garder l'ordre logique
    quarts_order = df_splits["Quart de course"].dropna().unique()
    
    for quart in quarts_order:
        mask = df_splits["Quart de course"] == quart
        if mask.any():
            quart_name = df_splits.loc[mask, 'secteur_quart'].dropna().unique()
            quart_name = quart_name[0] if len(quart_name) > 0 else "N/A"
            runner_sum = df_splits.loc[mask, "runner_h"].sum()
            median_local_sum = df_splits.loc[mask, "median_local_h"].sum()
            median_elite_sum = df_splits.loc[mask, "median_elite_h"].sum()
            ecart_local = runner_sum - median_local_sum
            ecart_elite = runner_sum - median_elite_sum
            ecart_local_pct = (ecart_local / median_local_sum * 100) if median_local_sum != 0 else None
            ecart_elite_pct = (ecart_elite / median_elite_sum * 100) if median_elite_sum != 0 else None

            recap_quart.append({
                "Quart": quart_name,
                "Temps coureur": float_hours_to_hm(runner_sum),
                "Temps peloton": float_hours_to_hm(median_local_sum),
                "Ecart peloton": float_hours_to_hm(ecart_local),
                "Ecart peloton %": f"{ecart_local_pct:.1f}%" if ecart_local_pct is not None else "N/A",
                "Temps élite": float_hours_to_hm(median_elite_sum),
                "Ecart élite": float_hours_to_hm(ecart_elite),
                "Ecart élite %": f"{ecart_elite_pct:.1f}%" if ecart_elite_pct is not None else "N/A",
            })
    
    if not recap_quart:
        st.warning("Aucune donnée de quart de course disponible")
        return
        
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
        "Coeff. variation": st.column_config.NumberColumn("Coeff. variation (%)", format="%.1f"),
        "Vitesse moy. (km/h)": st.column_config.NumberColumn("Vitesse moy. (km/h)", format="%.1f"),
        "Coeff. médian (peloton)": st.column_config.NumberColumn("Coeff. peloton médian (%)", format="%.1f"),
        "Écart peloton": st.column_config.NumberColumn("Écart peloton", format="%.1f"),
        "Coeff. médian (élite)": st.column_config.NumberColumn("Coeff. élite médian (%)", format="%.1f"),
        "Écart élite": st.column_config.NumberColumn("Écart élite", format="%.1f"),
    }

    # Affichage Streamlit
    st.dataframe(
        df_cv_runner.style
            .map(color_ecart, subset=["Écart peloton", "Écart élite"])
            .set_table_attributes('style="width:100%"')
            .set_properties(**{"text-align": "center"}).hide(axis="index"),
        #height=(35 * len(df_cv_runner)) + 50,
        hide_index=True,
        column_config=column_config
    )




def show_post_course_table(info, config_df, df_cv, bib):
    
    st.header("Temps de passage et écarts : où avez-vous gagné ou perdu du temps?")
    with st.expander("📘 Cliquez pour plus d'infos sur les données"):
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
    df_splits = df_splits.merge(config_df, left_on="portion_name", right_on="portion_name", how="left")

 
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
    Un découpage en 4 parties pour observer votre dynamique de pacing.
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

    post_course_detail(df_splits)


    metrics_options = {
        "Écart vs peloton (%)": "écart_local_%",
        "Écart vs élites (%)": "écart_elite_%",
        "Écart vs index (%)": "écart_index_%",
        "Écart vs peloton (h)": "écart_local_h",
        "Écart vs élites (h)": "écart_elite_h",
        "Écart vs index (h)": "écart_index_h",
    }

    # metric_label = st.selectbox(
    #     "📊 Choisir la métrique à afficher :",
    #     list(metrics_options.keys()),
    #     index=0
    # )
    # key = metrics_options[metric_label]
    # plot_spider_pacing(df_splits, bib, info, key=key)  # ou "écart_elite_%"

def show_runner_info(runner,bib, height=230):
    # sécuriser les valeurs
    name = runner.get("name","?")
    sex = runner.get("sex","?")
    category = runner.get("category","?")
    utmb_index = runner.get("utmb_index","?")
    diff = runner.get("diff_to_first","")
    final_time = float_hours_to_hm(runner.get("final_time_h",0))
    rank = int(runner.get("rank_scratch") or 0)
    category_rank = int(runner.get("rank_cat") or 0)
    sex_rank = int(runner.get("rank_sex") or 0)

    # HTML de la carte (tu peux ajuster couleurs/tailles ici)
    html = f"""
    <div style="
        background:#f5f5f5;
        border-radius:12px;
        padding:16px;
        margin:6px 0;
        border:1px solid rgba(49,51,63,0.10);
        font-family: Inter, sans-serif;
    ">
      <div style="margin-bottom:8px;">
        <h3 style="margin:0;font-weight:600;">{name} &nbsp;|&nbsp; Doss. {bib} &nbsp;|&nbsp; FINISHER</h3>
        <div style="color:#444;margin-top:6px;">
          <strong>Sexe :</strong> {sex} &nbsp;|&nbsp;
          <strong>Catégorie :</strong> {category} &nbsp;|&nbsp;
          <strong>UTMB index :</strong> {utmb_index}
        </div>
      </div>
      <div style="margin-top:8px;">
        {"<h4 style='margin:6px 0;'>Temps final : " + str(final_time) + " | Écart avec 1er : " + str(diff) + "</h4>" if diff and rank != 1 else "<h4 style='margin:6px 0;'>Temps final : " + str(final_time) + "</h4>"}
      </div>
      <div style="display:flex;gap:12px;margin-top:12px;">
        <div style="flex:1;padding:10px;background:#ffffff;border-radius:8px;text-align:center;">
          <div style="font-size:12px;color:#666;">Classement général</div>
          <div style="font-size:20px;font-weight:700;margin-top:6px;">{rank}</div>
        </div>
        <div style="flex:1;padding:10px;background:#ffffff;border-radius:8px;text-align:center;">
          <div style="font-size:12px;color:#666;">Classement catégorie</div>
          <div style="font-size:20px;font-weight:700;margin-top:6px;">{category_rank}</div>
        </div>
        <div style="flex:1;padding:10px;background:#ffffff;border-radius:8px;text-align:center;">
          <div style="font-size:12px;color:#666;">Classement sexe</div>
          <div style="font-size:20px;font-weight:700;margin-top:6px;">{sex_rank}</div>
        </div>
      </div>
    </div>
    """

    # render dans Streamlit — ajuster height si nécessaire
    components.html(html, height=height, scrolling=False)



# Fonction utilitaire pour valider les paramètres d'entrée
def validate_post_course_params(event_code, course_code, year):
    """
    Valide les paramètres d'entrée pour show_post_course.
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not event_code or not isinstance(event_code, str):
        return False, "event_code doit être une chaîne non vide"
    
    if not course_code or not isinstance(course_code, str):
        return False, "course_code doit être une chaîne non vide"
    
    try:
        year_int = int(year)
        if year_int < 2000 or year_int > 2030:
            return False, "year doit être entre 2000 et 2030"
    except (ValueError, TypeError):
        return False, "year doit être un nombre valide"
    
    return True, ""


# Exemple d'utilisation avec validation
def safe_show_post_course(event_code, course_code, year):
    """
    Version sécurisée de show_post_course avec validation des paramètres.
    """
    is_valid, error_msg = validate_post_course_params(event_code, course_code, year)
    
    if not is_valid:
        st.error(f"❌ Paramètres invalides: {error_msg}")
        return
    
    show_post_course(event_code, course_code, year)




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



def time_to_seconds(t):
    h, m, s = map(int, t.split(':'))
    return h*3600 + m*60 + s



def compare_course_detail(df1, df2, nom1, nom2):
    df = df1.merge(df2, on="portion_name", suffixes=("_c1", "_c2"))

    df["Profil"] = df["Type de tronçon_c1"].map(
        lambda t: get_icon_base64(t)
    )
    df["Tronçon"] = df["portion_name"]

    df_table = pd.DataFrame({
        " ": df["Profil"],
        "Tronçon": df["Tronçon"],
        f"{nom1}": df["runner_h_c1"].apply(float_hours_to_hm),
        f"{nom2}": df["runner_h_c2"].apply(float_hours_to_hm),
        "Écart": (df["runner_h_c1"] - df["runner_h_c2"]).apply(float_hours_to_hm),
        "Écart %": ((df["runner_h_c1"] - df["runner_h_c2"]) / df["runner_h_c1"] * 100).apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )
    })

    styled = (
        df_table.style
            .map(color_troncon, subset=[" "])
            .map(color_ecart, subset=["Écart", "Écart %"])
            .hide(axis="index")
            .set_table_attributes('style="width:100%"')
    )

    st.write(styled.to_html(escape=False), unsafe_allow_html=True)


def compare_course_pente(df1, df2, nom1, nom2):
    recap_pente = []
    for ttype in ["Montée", "Descente"]:
        mask1 = df1["Type de tronçon"] == ttype
        mask2 = df2["Type de tronçon"] == ttype
        if mask1.any() and mask2.any():
            sum1 = df1.loc[mask1, "runner_h"].sum()
            sum2 = df2.loc[mask2, "runner_h"].sum()
            ecart = sum1 - sum2
            ecart_pct = (ecart / sum1 * 100) if sum1 != 0 else None

            recap_pente.append({
                " ": get_icon_base64(ttype),
                "Catégorie": ttype,
                f"{nom1}": float_hours_to_hm(sum1),
                f"{nom2}": float_hours_to_hm(sum2),
                "Écart": float_hours_to_hm(ecart),
                "Écart %": f"{ecart_pct:.1f}%" if ecart_pct is not None else "N/A"
            })

    recap_pente_df = pd.DataFrame(recap_pente)

    styled = (
        recap_pente_df.style
            .map(color_troncon, subset=[" "])
            .map(color_ecart, subset=["Écart", "Écart %"])
            .hide(axis="index")
            .set_table_attributes('style="width:100%"')
    )

    st.write(styled.to_html(escape=False), unsafe_allow_html=True)
def compare_course_quarts(df1, df2, nom1, nom2):

    recap_quart = []
    quarts_order = df1["Quart de course"].dropna().unique()

    for quart in quarts_order:
        
        mask1 = df1["Quart de course"] == quart
        mask2 = df2["Quart de course"] == quart
        if mask1.any() and mask2.any():
            quart_name = df1.loc[mask1, 'secteur_quart'].dropna().unique()
            quart_name = quart_name[0] if len(quart_name) > 0 else "N/A"
            sum1 = df1.loc[mask1, "runner_h"].sum()
            sum2 = df2.loc[mask2, "runner_h"].sum()
            ecart = sum1 - sum2
            ecart_pct = (ecart / sum1 * 100) if sum1 != 0 else None
            recap_quart.append({
                "Quart": quart_name,
                f"{nom1}": float_hours_to_hm(sum1),
                f"{nom2}": float_hours_to_hm(sum2),
                "Écart": float_hours_to_hm(ecart),
                "Écart %": f"{ecart_pct:.1f}%" if ecart_pct is not None else "N/A"
            })

    if not recap_quart:
        st.warning("Aucune donnée de quart de course disponible")
        return
        
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
        st.warning("Impossible de trouver les données pour un ou les deux dossards.")
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
        f"Coeff. variation {nom1}": st.column_config.NumberColumn(f"Coeff. variation {nom1} (%)", format="%.1f"),
        f"Coeff. variation {nom2}": st.column_config.NumberColumn(f"Coeff. variation {nom2} (%)", format="%.1f"),
        f"Vitesse moy. {nom1} (km/h)": st.column_config.NumberColumn(f"Vitesse moy. {nom1} (km/h)", format="%.1f"),
        f"Vitesse moy. {nom2} (km/h)": st.column_config.NumberColumn(f"Vitesse moy. {nom2} (km/h)", format="%.1f"),
        "Écart coeff.": st.column_config.NumberColumn("Écart coeff. (%)", format="%.1f"),
        "Écart vitesse (km/h)": st.column_config.NumberColumn("Écart vitesse (km/h)", format="%.1f")
    }

    # Affichage
    st.dataframe(
        df_comp.style
            .map(color_ecart, subset=["Écart coeff."])
            .map(color_ecart_neg, subset=["Écart vitesse (km/h)"])
            .set_table_attributes('style="width:100%"'),
        hide_index=True,
        column_config=column_config
    )






def plot_spider_pacing(splits: dict, bib: str, runner: dict, key: str = "écart_local_%"):
    """
    Trace un spider chart (radar) pour visualiser le pacing d'un coureur.
    
    Paramètres
    ----------
    results : dict
        Dictionnaire complet contenant les splits par dossard.
    bib : str
        Dossard du coureur.
    runner : dict
        Détails du coureur (par exemple results[bib]).
    key : str, optionnel
        La métrique utilisée pour le radar ("écart_local_%" ou "écart_elite_%").
    """


    # --- Construire le DataFrame ---
    
 

    df_chart = splits[["portion_name", key]].copy()
    print(splits.columns)
    print(df_chart)
    df_chart["portion_name"] = df_chart["portion_name"].str.replace("→", "→\n")  # lisibilité

    # --- Préparer les données pour le radar ---
    categories = df_chart["portion_name"].tolist()
    values = df_chart[key].tolist()

    # Fermer le cercle
    categories += [categories[0]]
    values += [values[0]]

    # --- Créer le graphique ---
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=f"coureur",
        line=dict(color="royalblue", width=3)
    ))

    # Ligne médiane = 0%
    fig.add_trace(go.Scatterpolar(
        r=[0]*len(categories),
        theta=categories,
        mode='lines',
        name=f'{key}',
        line=dict(color="gray", dash='dash')
    ))

    # --- Mise en forme ---
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[min(values) - 5, max(values) + 5],
                tickformat=".0f",
                title="%"
            )
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
