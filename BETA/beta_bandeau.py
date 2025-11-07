import streamlit as st

def show_beta_banner():
    html_code = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            ..beta-banner {
                width: 95%;
                background: #e3f2fd; /* bleu clair uniforme */
                border: 1px solid #90caf9;
                padding: 25px 25px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                border-radius: 12px;
                margin-bottom: 15px;
                min-height: 180px;
            }
            
            .beta-banner-left {
                display: flex;
                align-items: center;
                gap: 15px;
                flex: 1;
            }
            
            .beta-banner-content {
                flex: 1;
            }
            
            .beta-banner-title {
                font-size: 20px;
                font-weight: 700;
                color: #0d47a1;
                margin-bottom: 6px;
            }
            
            .beta-banner-subtitle {
                font-size: 14px;
                color: #1e3a8a;
                line-height: 1.6;
            }

            .beta-email-link {
                color: #1565c0;
                text-decoration: none;
                font-weight: 600;
            }

            .beta-email-link:hover {
                text-decoration: underline;
            }

            @media (max-width: 768px) {
                .beta-banner {
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }
                .beta-banner-title {
                    font-size: 18px;
                }
                .beta-banner-subtitle {
                    font-size: 13px;
                }
            }
        </style>
    </head>
    <body>
        <div class="beta-banner">
            <div class="beta-banner-left">
                <div class="beta-banner-content">
                    <h2 class="beta-banner-title">  Merci de participer à la version BETA de TrailPacer !</h2>
                    <p class="beta-banner-subtitle">
                        Vos retours sont essentiels pour améliorer l’outil. Pour toute remarque ou suggestion, écrivez-nous à <a class="email-link" href="mailto:trailpacer.ia@gmail.com">trailpacer.ia@gmail.com</a> ou utilisez l’espace commentaire ci-dessous.
                    </p>
                    <p class="beta-banner-subtitle">
                        Vous pouvez également appareiller votre compte Garmin ou Strava afin que nous récupérions vos données
                        pour mettre en place de nouveaux modèles et analyses qui arriveront par la suite. Merci de votre aide.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    st.markdown(html_code, unsafe_allow_html=True)
