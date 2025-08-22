# data/mock_data.py

import pandas as pd
from datetime import datetime, timedelta

class MockDataGenerator:
    """Génère des données factices pour le dashboard"""

    def generate_performance_data(self):
        """Retourne un DataFrame avec des performances simulées"""
        dates = [datetime.today() - timedelta(weeks=i) for i in range(10)][::-1]
        data = {
            "date": dates,
            "vitesse_moyenne": [round(7 + i*0.2 + (-1)**i * 0.5, 2) for i in range(10)]
        }
        return pd.DataFrame(data)

    def get_upcoming_races(self):
        """Retourne une liste de courses simulées à venir"""
        return [
            {"Course": "Trail des Volcans", "Date": "2025-09-15", "Distance": "45 km"},
            {"Course": "Ultra Tour du Mont-Blanc", "Date": "2025-08-30", "Distance": "171 km"},
            {"Course": "Trail de la Réunion", "Date": "2025-10-20", "Distance": "60 km"}
        ]
