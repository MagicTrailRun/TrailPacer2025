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
                background: #e3f2fd; /* bleu clair uniforme */
                border: 1px solid #90caf9;
                padding: 18px 25px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                margin-bottom: 15px;
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
                font-size: 20px;
                font-weight: 700;
                color: #0d47a1;
                margin-bottom: 6px;
            }
            
            .banner-subtitle {
                font-size: 14px;
                color: #1e3a8a;
                line-height: 1.6;
            }

            .email-link {
                color: #1565c0;
                text-decoration: none;
                font-weight: 600;
            }

            .email-link:hover {
                text-decoration: underline;
            }

            @media (max-width: 768px) {
                .banner {
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }
                .banner-title {
                    font-size: 18px;
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
                    <h2 class="banner-title">  Merci de participer à la version BETA de TrailPacer !</h2>
                    <p class="banner-subtitle">
                        Vos retours sont essentiels pour améliorer l’outil. Pour toute remarque ou suggestion, écrivez-nous à <a class="email-link" href="mailto:trailpacer.ia@gmail.com">trailpacer.ia@gmail.com</a> ou utilisez l’espace commentaire ci-dessous.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    st.components.v1.html(html_code)