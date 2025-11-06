from supabase import create_client, Client
import streamlit as st

def get_supabase_client() -> Client:
    """Retourne une instance isolée du client Supabase pour cet utilisateur."""
    if "supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]