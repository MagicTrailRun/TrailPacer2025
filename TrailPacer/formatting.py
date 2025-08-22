import streamlit as st

def format_time_input_to_seconds(time_str):
    """Convertit une entrée HH:MM en secondes"""
    try:
        if ':' in time_str:
            h, m = map(int, time_str.split(':'))
            return h * 3600 + m * 60
        return int(time_str) * 3600
    except:
        return 0

def seconds_to_time_str(seconds):
    """Convertit des secondes en HHhMM"""
    h, m = divmod(seconds // 60, 60)
    return f"{h:02d}h{m:02d}"


def format_dataframe(df,target_time):
    col_temps_secteur = f"temps_secteur_{target_time}"
    col_temps_secteur_med = f"temps_secteur_med_{target_time}"
    col_temps_total = f"temps_cumule_med_{target_time}"
    col_heure_passage = f"heure_passage_{target_time}"

    if col_temps_secteur_med in df.columns:
        df['Allure secteur'] = (
            df[col_temps_secteur_med].mul(60) / df["dist_secteur"]
        ).apply(lambda x: f"{int(x)}'{int((x-int(x))*60):02d}/km")

        df_display = df[[
            "Point de passage",
            "dist_total",
            "dist_secteur",
            "dp_secteur",
            "dm_secteur",
            col_temps_secteur,
            "Allure secteur",
            col_temps_total,
            col_heure_passage
        ]]

            

        column_config={
                    "dist_total": st.column_config.NumberColumn("km total", format="%.1f"),
                    "dist_secteur": st.column_config.NumberColumn("km secteur", format="%.1f"),
                    "dp_secteur": st.column_config.NumberColumn("D+ secteur", format="%d"),
                    "dm_secteur": st.column_config.NumberColumn("D- secteur", format="%d"),
                    col_temps_secteur: st.column_config.TextColumn("Temps secteur"),
                    "Allure secteur": st.column_config.TextColumn("Allure secteur"),
                    col_temps_total: st.column_config.TextColumn("Temps cumulé"),
                    col_heure_passage: st.column_config.TextColumn("Heure passage"),
                }
        
    return(df_display, column_config)

def normalize_ckpts(df, col, mapping, drop_ckpts=None):
    """
    Harmonise les noms de checkpoints + supprime ceux à ignorer.
    """
    # Harmoniser les noms
    df[col] = df[col].replace(mapping)

    # Supprimer les checkpoints non souhaités
    if drop_ckpts is not None:
        df = df.loc[~df[col].isin(drop_ckpts)]

    return df


