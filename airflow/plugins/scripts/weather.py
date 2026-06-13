"""
Module de récupération des données météorologiques.

Objectif :
- Récupérer les conditions météo actuelles pour la ville de Lyon
- Normaliser les données pour un usage analytique

Projet : ParkMyBike
"""

import requests
from sqlalchemy import create_engine, Table, Column, Integer, Boolean, TIMESTAMP, Float, MetaData, insert
from scripts.config import WEATHER_LAT, WEATHER_LON, WEATHER_URL, DB_URI


def fetch_weather():
    """
    Récupère les données météorologiques actuelles via l'API Open-Meteo.

    Returns:
        dict | None : Données météo normalisées si succès, None sinon
    """

    params = {
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "models": "meteofrance_seamless",
        "current": [
            "is_day",
            "temperature_2m",
            "precipitation",
            "rain",
            "snowfall"
        ],
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            return {
                "weather_timestamp": data["current"]["time"],
                "is_day": data["current"]["is_day"],
                "temperature": data["current"]["temperature_2m"],
                "precipitation": data["current"]["precipitation"],
                "rain": data["current"]["rain"],
                "snowfall": data["current"]["snowfall"],
            }

        print(f"Erreur météo API : {response.status_code}")
        return None

    except requests.exceptions.RequestException as e:
        print("Erreur lors de l'appel à l'API météo")
        print(e)
        return None

def save_weather(weather_data: dict):
    """
    Sauvegarde les données météo dans la table meteo.

    Args:
        weather_data (dict): Données météo à sauvegarder

    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """

    if not weather_data:
        raise ValueError("Aucune donnée météo à sauvegarder")

    try:
        print(weather_data)
        engine = create_engine(DB_URI)
        metadata = MetaData()
        
        weather_table = Table(
            "weather",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("is_day", Boolean),
            Column("temperature", Float),
            Column("precipitation", Float),
            Column("rain", Float),
            Column("snowfall", Float),
            Column("weather_timestamp", TIMESTAMP)
        )

        with engine.connect() as conn:
            stmt = insert(weather_table).values(
                is_day=weather_data["is_day"],
                temperature=weather_data["temperature"],
                precipitation=weather_data["precipitation"],
                rain=weather_data["rain"],
                snowfall=weather_data["snowfall"],
                weather_timestamp=weather_data["weather_timestamp"]
            )
            conn.execute(stmt)
        
        print("Donnée insérée avec succès !")

        return True

    except Exception as e:
        print("Erreur lors de l'insertion :", str(e))
        return False
