"""
Script de collecte et de transformation des données des stations vélo JCDecaux.

Objectifs :
- Récupérer la liste des stations de la ville de Lyon

Projet : ParkMyBike
"""

import requests
from scripts.config import CITY, BASE_URL, DB_URI
from sqlalchemy import create_engine, Table, Column, Integer, Float, MetaData, insert, String, select

def fetch_lyon_stations(API_KEY):
    """
    Récupère la liste des stations de Lyon.

    Returns:
        list | None : Liste des stations si succès, None sinon
    """

    params = {
        "contract": CITY,
        "apiKey": API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code == 200:
        return response.json()

    print(f"Erreur API stations : {response.status_code}")
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

def save_new_stations(station_list):
    """
    Sauvegarde les données des nouvelles stations dans la base de données

    Args:
        stations_raw (list): Données statiques des stations

    Returns:
        list: None
    """

    engine = create_engine(DB_URI)
    metadata = MetaData()
    
    station_table = Table(
        "station",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("number", Integer),
        Column("name", String),
        Column("city", String),
        Column("latitude", Float),
        Column("longitude", Float),
    )

    with engine.connect() as conn:

        for station in station_list:

            check_stmt = select(station_table.c.id).where(
                station_table.c.number == station["number"] and station_table.c.city == station["city"]
            )

            exists = conn.execute(check_stmt).fetchone()

            if exists:
                continue

            insert_stmt = insert(station_table).values(
                number=station["number"],
                name=station["name"],
                city=station["city"],
                latitude=station["latitude"],
                longitude=station["longitude"]
            )
            conn.execute(insert_stmt)

    return True
