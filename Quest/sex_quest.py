import streamlit as st
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def show_quest_banner():
    logo_base64 = get_base64_image("Quest/image/chu_reunion.png")

    html_code = f"""
    <style>
        .banner {{
            width: 95%;
            margin: 0 auto 20px auto;
            background: linear-gradient(135deg, #f8f4ff 0%, #f0e6ff 100%);
            border: 1px solid #e8d5ff;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 15px;
        }}
        
        .banner-left {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }}
        
        .logo {{
            width: 60px;
            height: auto;
            max-height: 50px;
            object-fit: contain;
            flex-shrink: 0;
        }}
        
        .banner-content {{
            flex: 1;
        }}
        
        .banner-title {{
            font-size: 18px;
            font-weight: 600;
            color: #c2185b;
            margin-bottom: 4px;
        }}
        
        .banner-subtitle {{
            font-size: 13px;
            color: #666;
            line-height: 1.3;
        }}
        
        .cta-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
            color: white;
            text-decoration: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(233, 30, 99, 0.3);
            position: relative;
            overflow: hidden;
            flex-shrink: 0;
        }}
        
        .cta-button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }}
        
        .cta-button:hover::before {{
            left: 100%;
        }}
        
        .cta-button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 5px 18px rgba(233, 30, 99, 0.4);
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); }}
            100% {{ transform: scale(1); }}
        }}
        
        @media (max-width: 768px) {{
            .banner {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
                padding: 20px;
            }}
            
            .banner-left {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .banner-title {{
                font-size: 16px;
            }}
            
            .banner-subtitle {{
                font-size: 12px;
            }}
        }}
    </style>

    <div class="banner">
        <div class="banner-left">
            <img src="data:image/png;base64,{logo_base64}" alt="CHU La Réunion" class="logo">
            <div class="banner-content">
                <h2 class="banner-title">Étude nationale : Trail & Sexualité</h2>
                <p class="banner-subtitle">
                    Questionnaire sur la sexualité des traileuses et des traileurs.<br>
                    Libido, excitation, récupération, relations : comment le trail influence-t-il la sexualité ?
                    Aidez-nous à mieux comprendre.
                </p>
            </div>
        </div>
        <a href="https://sextrailquest.skezia.io/" target="_blank" class="cta-button pulse">
            📋 Accéder au questionnaire
        </a>
    </div>
    """

    st.markdown(html_code, unsafe_allow_html=True)
