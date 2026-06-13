"""
Script de collecte et de transformation des données des stations vélo JCDecaux.

Objectifs :
- Collecter les données temps réel des stations vélo
- Enrichir les données avec la météo
- Préparer les données pour stockage et analyse

Projet : ParkMyBike
"""

import requests
from scripts.config import CITY, BASE_URL, DB_URI
from sqlalchemy import create_engine, Table, Column, Integer, TIMESTAMP, Float, MetaData, insert, String, select, Boolean

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

station_info_table = Table(
    "station_status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("station_id", Integer),
    Column("weather_id", Integer),
    Column("is_opened", Boolean),
    Column("total_capacity", Integer),
    Column("available_bike", Float),
    Column("available_stand", Float),
    Column("status_timestamp", TIMESTAMP)
)

def fetch_stations_data(API_KEY):
    """
    Récupère les données des stations vélo de lyon.

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
    Transforme les données brutes des stations et les enrichit avec la météo.

    Args:
        stations_raw (list): Données brutes des stations

    Returns:
        list: Données stations normalisées et enrichies
    """

    engine = create_engine(DB_URI)
    transformed_data = []

    with engine.connect() as conn:
        weather_id_stmt = select(weather_table.c.id).order_by(weather_table.c.weather_timestamp).limit(1)
        weather_id = conn.execute(weather_id_stmt).fetchone()[0]
        for station in stations_raw:
            print(station)
            station_id_stmt = select(station_table.c.id).where(
                station_table.c.number == station["number"] and station_table.c.city == station["city"]
            )
            station_id = conn.execute(station_id_stmt).fetchone()[0]

            station_record = {
                "station_id": station_id,
                "weather_id": weather_id,
                "is_opened": 1 if station.get("status") == "OPEN" else 0,
                "total_capacity": station.get("totalStands", {}).get("capacity"),
                "available_stand": station.get("totalStands", {}).get("availabilities", {}).get("stands"),
                "available_bike": station.get("totalStands", {}).get("availabilities", {}).get("bikes"),
                "status_timestamp": station.get("lastUpdate"),
            }

            transformed_data.append(station_record)

    return transformed_data


def save_stations_info(stations_info):
    engine = create_engine(DB_URI)
    with engine.connect() as conn:
        for station in stations_info:
            insert_stmt = insert(station_info_table).values(
                station_id=station["station_id"],
                weather_id=station["weather_id"],
                is_opened=station["is_opened"],
                total_capacity=station["total_capacity"],
                available_bike=station["available_bike"],
                available_stand=station["available_stand"],
                status_timestamp=station["status_timestamp"]
            )
            conn.execute(insert_stmt)
