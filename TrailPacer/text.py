
from config.airtableapi import email_form, commentaire_form
import streamlit as st
import streamlit as st
from TrailPacer.formatting import get_base64_image
def pacing():
    st.header("Le pacing selon Trail Pacer")

    # Qu'est-ce que le pacing
    st.subheader("1. Qu’est-ce que le pacing ?")
    st.markdown(
        """
        Le **pacing** désigne l’art de gérer son effort et son allure au cours d’une performance sportive.  
        Autrement dit, c’est la stratégie par laquelle un athlète répartit son énergie pour atteindre un objectif 
        (performance, régularité, finisher…), en tenant compte de la durée, de l’intensité et des contraintes 
        environnementales et techniques.
        """
    )

    st.markdown(
        """
        Un pacing efficace repose sur un équilibre subtil :
        - Trop rapide au départ → risque d’épuisement prématuré, baisse de performance, voire abandon.  
        - Trop prudent → arrivée avec des réserves inutilisées et un résultat en deçà de son potentiel.  
        
        👉 Le pacing est donc une **dynamique d’ajustement continu**, influencée à la fois par les sensations, 
        l’expérience et des facteurs objectifs (dénivelé, météo, technicité du parcours…).
        """
    )

    st.divider()

    st.subheader("2. Le pacing en course sur route")
    st.markdown(
    """
    En course sur route (10 km, semi-marathon, marathon), le pacing est relativement bien étudié car les parcours sont standardisés, avec peu de variations liées au terrain.  
    Cela permet une analyse fine des stratégies d’allure et une comparaison directe entre athlètes et compétitions.  

    Un bon pacing consiste généralement à maintenir une allure régulière.  
    Par exemple, un coureur visant un marathon en 3 heures cherchera à parcourir chaque kilomètre en environ **4 min 16 s**.  

    Une stratégie plus avancée, fréquemment utilisée par les élites, est le *negative split*, qui consiste à courir la seconde moitié de la course légèrement plus rapidement que la première.  
    Cette approche demande une gestion précise de l’effort : partir légèrement en deçà de son allure cible, économiser de l’énergie, puis accélérer dans la seconde moitié.
    """
)

    st.info(
    "Un exemple marquant est la performance historique de **Kelvin Kiptum** le 8 octobre 2023 lors du marathon de Chicago. "
    "Il devient le premier athlète à descendre sous les 2 h 1 min avec un temps de **2 h 00 min 35 s**, améliorant de 34 secondes le précédent record du monde. "
    "Après un passage au semi-marathon en 1 h 00 min 48 s, il couvre la deuxième moitié de course en **59 min 47 s**, illustrant parfaitement la stratégie de *negative split* à haut niveau."
)

    st.divider()
    # Trail
    st.subheader("3. Le pacing en trail et ultratrail")
    st.markdown(
        """
        En trail, impossible de maintenir une allure stable :  
        - profils très différents,  
        - D+ et D-,  
        - technicité du terrain,  
        - météo, altitude, nuit…  

        👉 Ici, le pacing consiste à **limiter les variations d’intensité** plutôt qu’à garder une vitesse fixe.  
        """
    )
    st.markdown(
        "Un indicateur clé est le **coefficient de variation de l’allure** : "
        "plus il est faible, plus l’allure est régulière et efficace."
    )
    st.warning(
        "Pour aller plus loin : consultez [l’article de **Cyril Forestier**](https://courir-mieux.fr/gerer-allure-trail/) "
        "sur son blog **Courir Mieux**."
    )

    st.divider()

    # Pourquoi Trail Pacer
    st.subheader("Pourquoi Trail Pacer ?")
    st.markdown(
        """
    Traditionnellement, lorsqu’on prépare un plan de course, on s’appuie sur les résultats des éditions précédentes. On ouvre un tableur Excel, on examine les temps de passage des coureurs proches de son objectif ou ayant une côte similaire, puis on construit son propre plan en conséquence.
    
    Le problème de cette méthode, c’est qu’elle conduit souvent à reproduire les erreurs du peloton : départ trop rapide, forte variabilité du pacing, et ralentissement marqué, voire effondrement, au fil des kilomètres.
    
    C’est pour répondre à ce constat qu’a été développé Trail Pacer.

        """
    )


    ralentissementUTMB = "TrailPacer/image/ralentissement_utmb.png"
    st.image(ralentissementUTMB, caption="Ralentissement UTMB", use_container_width=False)
    #ralentissementDDf="TrailPacer/image/ralentissement_ddf.png"
    
    #st.image(ralentissementDDf, caption="Ralentissement Diagonale des Fous", use_container_width=False)
    
    st.divider()

    # Méthode
    st.subheader("La méthode Trail Pacer")
    st.markdown(
        """
    Notre approche consiste à déterminer un pacing « optimal » en s’appuyant sur celui des meilleurs coureurs : ceux qui présentent une variation d’allure limitée et un ralentissement bien moins marqué tout au long du parcours.

    Concrètement, pour chaque course, nous exploitons les résultats historiques des éditions précédentes afin de construire un modèle statistique Trailpacer. Celui-ci estime le temps (et donc la vitesse) des coureurs sur chaque secteur en fonction de différents paramètres : dénivelé positif, dénivelé négatif, distance depuis le départ, profil global de la course…

    Le modèle se fonde sur les performances des meilleurs finishers, hommes et femmes, dont nous calculons l’allure de référence. Cette allure est ensuite transposée aux autres profils de coureurs : on applique le même schéma de variation, en multipliant par le temps supplémentaire qu’ils mettent par rapport aux meilleurs.
    
    👉 Ainsi, par rapport à une personne qui termine l’UTMB en 20 heures, un coureur visant 40 heures sera conseillé de mettre environ deux fois plus de temps sur chaque secteur.
    

        """
    )
    ralentissementUTMB = "TrailPacer/image/ralentissement_utmb_allure_trail_pacer.png"
    st.image(ralentissementUTMB, use_container_width=False)
    st.markdown(
        """
    Bien que perfectible, cette approche présente deux avantages majeurs :

•	elle propose un pacing plus régulier, plus prudent et donc optimisé ;

•	elle fournit des temps de passage même sur les nouvelles portions de parcours ou en cas de modifications d’itinéraire.
"""
    )
    st.divider()

#     # Exemple graphique
#     st.subheader("Exemple : pacing médian – UTMB 2024")
#     medUTMB = "TrailPacer/image/med_pacing_utmb_2024.png"
#     st.image(medUTMB, use_container_width=False)
#     st.markdown(
#         """
# Ce graphique illustre le pacing médian des coureurs sur l'UTMB 2024 :

# •	La ligne horizontale violette correspond au plan de course proposé (ici pour 40h30).

# •	La courbe jaune représente le pacing du coureur médian, avec les écarts au pacing de référence Trail Pacer.

# •	La zone bleue montre la dispersion (=où se situent les coureurs) du peloton autour du temps médian.

# On observe un schéma classique de pacing :

# •	Début de course trop rapide : les coureurs passent en avance par rapport au plan.

# •	Milieu de course : ralentissement progressif, accumulation de retard et perte de places.

# •	Fin de course : arrivée autour de 40 h, soit plus lent que l’objectif initial de 38 h.

# ➡️ Cette courbe illustre un constat fondamental : la plupart des coureurs partent trop vite et subissent ensuite un ralentissement marqué.

# Trail Pacer propose au contraire un plan de course plus régulier et réaliste, afin de limiter les variations d’intensité et d’augmenter les chances de terminer proche de l’objectif fixé.

#         """
#     )


#     st.divider()

#     # Exemples concrets
#     st.subheader("Exemples concrets de pacing")
#     st.markdown("""
                
# Dans la suite, nous présentons deux exemples parlants de pacing : les très belles performances d’Émilie Maroteaux et d’Alexandre Boucheix sur les dernières éditions de la Diagonale des Fous.
                
# Vous pouvez d’ailleurs explorer vous-même les analyses post-course dans l’onglet « Analyse post-course » TrailPacer.""")
    
#     st.markdown("""**2021 – Émilie Maroteaux** :
                
# Lors de sa victoire, elle a montré un pacing remarquable : elle est restée très proche du plan de course optimal proposé par TrailPacer, toujours à moins de 20 minutes d’écart sur l’ensemble de la course. L’aire bleue représente les coureurs ayant terminé autour de 30 h. On voit qu’elle est partie plus prudemment que les coureurs qui finissent dans le même temps, ce qui illustre parfaitement l’efficacité de sa stratégie.
# """)
#     em2021 = "TrailPacer/image/EM_DDF_2021.png"
#     st.image(em2021, use_container_width=False)

#     st.markdown("""**2023 – Émilie Maroteaux** : départ un peu trop rapide, finit 30h30.

# Sur cette édition, elle a probablement commencé un peu vite, avec une première partie de course alignée sur un plan de 29 h 30, pour finalement terminer en 30 h 30. L’aire bleue montre que dans la première moitié de course, elle était plus rapide que les autres coureurs ayant terminé autour de 30 h 30.
# """)
#     em2023 = "TrailPacer/image/EM_DDF_2023.png"
#     st.image(em2023, use_container_width=False)

#     st.markdown("Alexandre Boucheix (Casquette Verte) a montré une nette progression sur lors des éditions 2021, 2022 et 2023 de la Diagonale des Fous.")
    
#     st.markdown("""**2021 – Casquette Verte** :2021 – Alexandre Boucheix (Casquette Verte)
# Il parcourt les 50 premiers kilomètres sur les allures correspondant à un plan de moins de 25 h. Il ralentit ensuite progressivement jusqu’au km 140 et termine finalement en 28 h
#                 """)
#     ab2021 = "TrailPacer/image/AB_DDF_2021.png"
#     st.image(ab2021, use_container_width=False)

#     st.markdown("""**2022 – Casquette Verte** :
#     Il part sur un plan de 26 h jusqu’au km 50, mais une chute entraîne un ralentissement brutal. Il effectue une grande partie de la course sur des allures proches d’un plan de 35 h. 
# Son pacing général est totalement décorrélé de celui proposé par TrailPacer ou du pacing des autres coureurs ayant fini autour de 35 h. C’est un exemple typique d’un pacing perturbé par une défaillance majeure.
#                 """)
    
#     ab2022 = "TrailPacer/image/AB_DDF_2022.png"
#     st.image(ab2022, use_container_width=False)

#     st.markdown("""**2023 – Casquette Verte** : 
#     Il réalise une course exemplaire en suivant quasiment à la perfection l’allure optimale proposée par TrailPacer pour un objectif de 27 h. L’écart est resté inférieur à 10 minutes tout au long de la course… au point qu’Alexandre n’a presque plus besoin de notre appli !
#                 """)
#     ab2023 = "TrailPacer/image/AB_DDF_2023.png"
#     st.image(ab2023, use_container_width=False)

#     st.divider()

    # Importance
    st.subheader(" Importance du pacing")
    st.markdown(
        """

•	Optimisation des ressources énergétiques : un pacing adapté permet de mieux utiliser vos réserves de glycogène et de lipides, pour maintenir un effort efficace sur la durée.

•	Optimisation de la performance : un effort régulier et lissé est généralement associé à de meilleurs résultats.

•	Réduction du risque de blessure et d’abandon : un pacing maîtrisé limite les défaillances et protège des blessures liées à une mauvaise gestion de l’effort.

•	Impact mental positif : en partant prudemment, vous rattrapez progressivement des coureurs, ce qui renforce le moral et la confiance.

•	Plaisir accru : une course bien gérée est plus agréable et valorisante qu’une course subie.

•	Évitement des erreurs courantes : Trail Pacer aide à ne pas reproduire les erreurs classiques du peloton (départ trop rapide, effondrement final).
 

        """
    )




def quisommesnous():
    st.header("Qui sommes-nous?")
    txt = """
<div style="font-family: 'Segoe UI', sans-serif; color:#333; line-height:1.5;">

<p><b>Trail Pacer</b>, c'est une équipe passionnée de trail et de science, réunissant des compétences en data science, médecine et recherche. 
Cet outil a vu le jour grâce à l’expertise complémentaire de  :
<hr style="border:0; border-top:1px solid #ccc;">

<h3 style="font-size:18px; color:#222;">Matthieu Oliver</h3>
<p><b>Ingénieur en science des données | Passionné de trail</b></p>
<p>Matthieu a commencé à créer ses propres tableaux de temps de passage pour le <b>Trail de Bourbon</b> (Grand Raid) en 2022 et 2023 afin de mieux gérer ses courses. 
Devant l’intérêt suscité auprès d’autres coureurs, il a choisi de transformer ses outils personnels en une ressource partagée avec la communauté.</p>
<hr style="border:0; border-top:1px solid #ccc;">

<h3 style="font-size:18px; color:#222;">Nicolas Bouscaren</h3>
<p><b>Médecin de santé publique & Médecin du sport | CHU La Réunion | Doctorant LIBM (Pr Guillaume Millet) à l’université de Saint Etienne </b></p>
<p>Médecin-chercheur passionné de trail, de données et de physiologie de l’effort, Nicolas avance avec curiosité et un esprit bouillonnant d’idées. C’est à la fois son moteur et parfois son talon d’Achille, mais aussi ce qui le pousse à relier recherche académique, nouvelles technologies et pratique du terrain. Spécialiste de la thermorégulation en ultra-endurance et de l’épidémiologie du sport, il est à l’origine de plusieurs études sur les impacts du trail running sur la santé.</p>
<hr style="border:0; border-top:1px solid #ccc;">

<h3 style="font-size:18px; color:#222;">Maelle Nicolas</h3>
<p><b>Data Scientist | CHU La Réunion</b></p>
<p>Maelle reprend les travaux de Matthieu et les applique à de nouvelles courses. Elle contribue à modéliser les données pour exploiter pleinement leur potentiel. Curieuse et rigoureuse, elle explore les liens entre innovation technologique, modélisation et applications terrain pour améliorer la compréhension du trail.</p>
<hr style="border:0; border-top:1px solid #ccc;">

<h3 style="font-size:18px; color:#222;">Tanguy Legrand</h3>
<p><b>Data Scientist | CHU La Réunion</b></p>
<p>Tanguy travaille pour l’instant dans l’ombre… mais pas pour longtemps ! En binôme avec Maelle, il développe les prochaines fonctionnalités du projet, bientôt disponibles dans l’application. Spécialiste du traitement et de la modélisation de données sportives, il explore les leviers numériques pour mieux comprendre la performance en trail et prédire le risque de blessures.</p>
</div>
"""
    return st.markdown(txt, unsafe_allow_html=True)




def votreavis():

    st.header("📢 Votre avis nous intéresse !")

   
    st.subheader("Dites-nous ce que vous aimeriez voir")
    st.markdown(
        """
        - **Statistiques souhaitées** : analyses individuelles et collectives post-course, fiches d’identité des courses, statistiques détaillées sur le profil, la technicité ou encore les conditions météo ?  
        - **Courses prioritaires** : sur quelles prochaines épreuves aimeriez-vous que nous concentrions nos efforts ?  
        - **Fonctionnalités utiles** : quelles options seraient les plus pratiques pour préparer vos courses ?  
        - **Améliorations** : toutes vos suggestions sont les bienvenues !
        """
    )

    st.divider()

    st.markdown(
        "Votre retour est précieux pour faire évoluer Trail Pacer et construire, ensemble, "
        "l’outil le plus utile possible pour la communauté des traileurs."
    )

    col1, col2 = st.columns(2)
    with col1 : 
        commentaire_form(key="commentaire_projet")

    st.markdown("📩 Vous pouvez aussi nous écrire directement à **trailpacer.ia@gmail.com**. ")
    st.divider()
    st.markdown(
        "🚀 Trail Pacer n’est qu’une première étape : le projet s’intégrera bientôt dans une initiative "
        "scientifique et communautaire beaucoup plus large... restez connectés !"
    )

    st.markdown(
        """
        Vous souhaitez suivre nos actualités et découvrir en avant-première les nouveautés de **Trail Pacer** ?  
        Laissez-nous votre adresse email pour rester informé :
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1 : 
        email_form(key="avis_email_form")

    st.markdown(
    """
    <small>
    En laissant votre adresse email, vous acceptez de recevoir les actualités de Trail Pacer.  
    Vos données sont utilisées uniquement à cette fin et pourront, avec votre accord, être sollicitées pour des projets de recherche.  
    Elles ne seront jamais partagées à des tiers.  
    Vous pouvez à tout moment demander la modification ou la suppression de vos informations en écrivant à 
    <a href="mailto:trailpacer.ia@gmail.com">trailpacer.ia@gmail.com</a>.
    </small>
    """,
    unsafe_allow_html=True
)

    
    
  

import streamlit as st

def cnil():
    st.header("Politique de confidentialité – Trail Pacer")

    st.subheader(" Responsable du traitement")
    st.markdown(
        """
        Les données collectées via l’application **Trail Pacer** sont traitées par :  
        **Trail Pacer – Projet de recherche et d’innovation en trail running**  
        📩 Contact : [trailpacer.ia@gmail.com](mailto:trailpacer.ia@gmail.com)
        """
    )

    st.divider()

    st.subheader(" Finalités du traitement")
    st.markdown(
        """
        Les informations recueillies (adresses email) sont utilisées pour :  
        - vous envoyer les **actualités et nouveautés** de Trail Pacer,  
        - vous proposer en avant-première de **tester de nouvelles fonctionnalités**,  
        - et, avec votre accord, vous solliciter dans le cadre de **projets de recherche scientifique** (questionnaires, enquêtes, études).
        """
    )

    st.divider()

    st.subheader("Destinataires des données")
    st.markdown(
        """
        Les données sont destinées **exclusivement** à l’équipe Trail Pacer.  
        Elles **ne seront jamais communiquées** à des tiers.
        """
    )

    st.divider()

    st.subheader(" Durée de conservation")
    st.markdown(
        """
        Vos données sont conservées :  
        - jusqu’à ce que vous en demandiez la suppression,  
        - ou **au maximum 5 ans** après la dernière interaction avec Trail Pacer.
        """
    )

    st.divider()

    st.subheader("Vos droits (RGPD)")
    st.markdown(
        """
        Vous disposez des droits suivants concernant vos données :  
        - droit d’accès, de rectification et de suppression,  
        - droit de limitation du traitement,  
        - droit de retrait de votre consentement à tout moment,  
        - droit d’opposition au traitement.  

        👉 Pour exercer vos droits ou poser une question, contactez-nous :  
        **[trailpacer.ia@gmail.com](mailto:trailpacer.ia@gmail.com)**
        """
    )

    st.divider()

    st.subheader("Réclamation auprès de la CNIL")
    st.markdown(
        """
        Si vous estimez, après nous avoir contactés, que vos droits *Informatique et Libertés* ne sont pas respectés,  
        vous pouvez adresser une réclamation à la CNIL : [www.cnil.fr](https://www.cnil.fr)
        """
    )




def explication_tab_post_course():
    with st.expander("📘 Cliquez pour comprendre comment lire ce graphique"):
        st.subheader("Repères de lecture")
        st.markdown("""
        **Légende** :
                    
        - Courbe rouge : votre rythme en course (pacing réel).  
        - Tirets horizontaux : plans de course optimaux TrailPacer (repères servant de comparaison avec votre pacing).  
          L’un d’entre eux est **mis en évidence (gras)** : il correspond à un temps cible ~5% plus rapide que votre résultat final, arrondi à l’heure.  
          Les écarts affichés sont calculés par rapport à ce plan.  
        - Zone bleue : zone de performance des coureurs proches (temps final similaire au vôtre).
        
        **Clés de lecture :**
        - Si la courbe rouge est sous une ligne horizontale → vous êtes plus rapide sur ce secteur.  
        - Si elle est au-dessus → vous êtes plus lent sur ce secteur.  
        - Si la courbe rouge suit une ligne horizontale en pointillés (plan TrailPacer) → votre pacing est comparable à celui recommandé pour terminer dans le temps correspondant.
        """)

        st.success("NB : la comparaison peut se faire par rapport au plan de course optimal TrailPacer, mais aussi à la zone de performance des coureurs proches.")

        st.markdown("""
        **Constat TrailPacer :**  
        La majorité des coureurs partent trop vite en début de course, ce qui entraîne un ralentissement marqué par la suite.  
        Suivre un pacing plus progressif, tel que suggéré par TrailPacer, permet généralement de préserver l’allure et la régularité jusqu’à l’arrivée.
        """)
