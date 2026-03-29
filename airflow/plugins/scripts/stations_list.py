"""
Script de collecte et de transformation des données des stations vélo JCDecaux.

Objectifs :
- Récupérer la liste des stations de la ville de Lyon

Projet : ParkMyBike
"""

import requests
from config import CITY, API_KEY, BASE_URL

def fetch_lyon_stations():
    """
    Récupère la liste des stations de Lyon.

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

def transform_data(stations_raw):
    """
    Récupère les données statiques des stations

    Args:
        stations_raw (list): Données brutes des stations

    Returns:
        list: Données stations normalisées
    """

    transformed_data = []

    for station in stations_raw:
        station_record = {
            "number": station.get("number"),
            "city": station.get("contractName"),
            "name": station.get("name"),
            "latitude": station.get("position", {})
                                     .get("latitude"),
            "longitude": station.get("position", {})
                                     .get("longitude")
        }

        transformed_data.append(station_record)

    return transformed_data

if __name__ == "__main__":

    stations = fetch_lyon_stations()

    if stations:
        final_data = transform_data(stations)
        print(len(final_data))
    else:
        print("Données insuffisantes pour traitement")
