"""
Script de collecte et de transformation des données des stations vélo JCDecaux.

Objectifs :
- Collecter les données temps réel des stations vélo
- Enrichir les données avec la météo
- Préparer les données pour stockage et analyse

Projet : ParkMyBike
"""

import requests
import json
from config import CITY, API_KEY, BASE_URL, WEATHER_CACHE_PATH


def fetch_stations_data():
    """
    Récupère les données des stations vélo pour une ville donnée.

    Returns:
        list | None : Liste des stations si succès, None sinon
    """

    params = {
        "contract": CITY,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        if response.status_code == 200:
            return response.json()

        print(f"Erreur API stations : {response.status_code}")
        return None

    except requests.exceptions.RequestException as e:
        print("Erreur lors de l'appel à l'API stations")
        print(e)
        return None

def fetch_weather():
    """
    Charge les données météo depuis le cache.
    """
    try:
        with open(WEATHER_CACHE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Cache météo introuvable")
        return None

def transform_data(stations_raw, weather_data):
    """
    Transforme les données brutes des stations et les enrichit avec la météo.

    Args:
        stations_raw (list): Données brutes des stations
        weather_data (dict): Données météo

    Returns:
        list: Données stations normalisées et enrichies
    """

    transformed_data = []

    for station in stations_raw:
        station_record = {
            "number": station.get("number"),
            "city": station.get("contractName"),
            "is_opened": 1 if station.get("status") == "OPEN" else 0,
            "total_capacity": station.get("totalStands", {}).get("capacity"),
            "available_stands": station.get("totalStands", {})
                                     .get("availabilities", {})
                                     .get("stands"),
            "last_update": station.get("lastUpdate"),
        }

        # Fusion station + météo
        station_record |= weather_data
        transformed_data.append(station_record)

    return transformed_data


if __name__ == "__main__":

    stations = fetch_stations_data()
    weather = fetch_weather()

    if stations and weather:
        final_data = transform_data(stations, weather)
        print(final_data[0])
    else:
        print("Données insuffisantes pour traitement")
