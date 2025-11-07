import streamlit as st

def show_beta_banner():
    html_code = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            .banner {
                width: 100%;
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border: 1px solid #90caf9;
                padding: 20px 25px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-radius: 15px;
            }
            
            .banner-left {
                display: flex;
                align-items: center;
                gap: 15px;
                flex: 1;
            }
            
            .banner-content {
                flex: 1;
            }
            
            .banner-title {
                font-size: 19px;
                font-weight: 700;
                color: #0d47a1;
                margin-bottom: 6px;
            }
            
            .banner-subtitle {
                font-size: 14px;
                color: #1e3a8a;
                line-height: 1.5;
            }

            .email-link {
                color: #1565c0;
                text-decoration: none;
                font-weight: 600;
            }

            .email-link:hover {
                text-decoration: underline;
            }

            .cta-button {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: linear-gradient(135deg, #1565c0 0%, #1e88e5 100%);
                color: white;
                text-decoration: none;
                padding: 12px 22px;
                border-radius: 25px;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 3px 12px rgba(30, 136, 229, 0.3);
                position: relative;
                overflow: hidden;
                flex-shrink: 0;
            }

            .cta-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s ease;
            }

            .cta-button:hover::before {
                left: 100%;
            }

            .cta-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 5px 18px rgba(30, 136, 229, 0.4);
            }

            .pulse {
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.03); }
                100% { transform: scale(1); }
            }

            @media (max-width: 768px) {
                .banner {
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                    padding: 20px;
                }
                
                .banner-left {
                    flex-direction: column;
                    gap: 10px;
                }
                
                .banner-title {
                    font-size: 17px;
                }
                
                .banner-subtitle {
                    font-size: 13px;
                }
            }
        </style>
    </head>
    <body>
        <div class="banner">
            <div class="banner-left">
                <div class="banner-content">
                    <h2 class="banner-title"> Merci de participer à la version BETA de TrailPacer !</h2>
                    <p class="banner-subtitle">
                        Vos retours sont essentiels pour améliorer l’outil. Pour toute remarque ou suggestion, écrivez-nous à 
                        <a class="email-link" href="mailto:trailpacer.ia@gmail.com">trailpacer.ia@gmail.com</a> ou utilisez l’espace commentaire ci-dessous.
                    </p>
                    <p class="banner-subtitle">
                        Vous pouvez également connecter votre compte Garmin ou Strava afin que nous récupérions vos données
                        et développions de nouveaux modèles et analyses à venir. 
                        Merci pour votre aide précieuse 🙏
                    </p>
                </div>
            </div>
            <a href="mailto:trailpacer.ia@gmail.com" class="cta-button pulse">📩 Envoyer un retour</a>
        </div>
    </body>
    </html>
    """
    st.markdown(html_code, unsafe_allow_html=True)
