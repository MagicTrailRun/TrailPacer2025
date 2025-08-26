import re
from dotenv import load_dotenv
import csv 
import os
import streamlit as st
load_dotenv()  # charge les variables du .env

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

import requests

def save_email(email, table_name="email"):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": {
            "email": email,
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(response.text)
        return False
    
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def email_form(key="user_form"):
    with st.form(key=key):
        email = st.text_input("Adresse e-mail")
        submitted = st.form_submit_button("Envoyer")
        if submitted:
            # Vérification que tous les champs sont remplis
            if not email:
                st.error("Veuillez remplir tous les champs.")
                return

            # Vérification de la validité de l'e-mail
            if not is_valid_email(email):
                st.error("Veuillez saisir une adresse e-mail correcte.")
                return

            # Sauvegarde dans Airtable ou autre
            success = save_email( email)
            if success:
                st.success("Merci ! Vos informations ont été enregistrées")
            else:
                st.error("Erreur lors de l'enregistrement.")
    
  