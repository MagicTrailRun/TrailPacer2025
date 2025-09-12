import pandas as pd
import numpy as np
import json

def load_data(event,race="UTMB",year=2025, version="vf"):
    """Charge les données CSV"""
    try:
        csv_path = f"data/TrailPacer/{event}/{race}/pred_pacing/pred_{year}_{version}.csv"
        df = pd.read_csv(csv_path)
        
        if "checkpoint" in df.columns:
            df = df.drop_duplicates(subset=["checkpoint"], keep="first")
        return df
    except Exception as e:
        return pd.DataFrame()

def get_config(path, course):
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    #config = dic_config['courses'][course]
    config['startDate'] = pd.to_datetime(config['startDate'])

    temps_cible = np.arange(config['temps_cible'][0], config['temps_cible'][1], config.get('step',1))
    config['temps_cible'] = temps_cible.astype(int).tolist()

    config['temps_cible_start'] = int(config['temps_cible'][0])
    config['temps_cible_end'] = int(config['temps_cible'][-1])
    config['temps_cible_middle'] = int(np.round((config['temps_cible_start'] + config['temps_cible_end'])/2))

    return config #, dic_config['mapping_ckpt']



