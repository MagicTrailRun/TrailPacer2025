from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")



supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Retourne une instance isolée du client Supabase pour cet utilisateur."""
    if "supabase_client" not in st.session_state:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]