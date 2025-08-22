import pandas as pd
import numpy as np
import json

def load_data(race="UTMB",version="pred_v0_UTMB"):
    """Charge les données CSV"""
    try:
        csv1_path = f"data/TrailPacer/{race}/{version}.csv"
        df = pd.read_csv(csv1_path, delimiter=';')
        return df
    except Exception as e:
        return pd.DataFrame()

def get_config(path, course):
    with open(path, "r", encoding="utf-8") as f:
        dic_config = json.load(f)

    config = dic_config['courses'][course]
    config['start_datetime'] = pd.to_datetime(config['start_datetime'])

    temps_cible = np.arange(config['temps_cible'][0], config['temps_cible'][1], config['step'])
    config['temps_cible'] = temps_cible.astype(int).tolist()

    config['temps_cible_start'] = int(config['temps_cible'][0])
    config['temps_cible_end'] = int(config['temps_cible'][-1])
    config['temps_cible_middle'] = int(np.round((config['temps_cible_start'] + config['temps_cible_end'])/2))

    return config, dic_config['mapping_ckpt']
