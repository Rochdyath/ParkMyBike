"""
Fichier de configuration global – ParkMyBike
"""

# JCDecaux
CITY = "Lyon"
BASE_URL = "https://api.jcdecaux.com/vls/v3/stations"

# Météo
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_LAT = 45.7485
WEATHER_LON = 4.8467

# DB
DB_URI = "postgresql+psycopg2://airflow:airflow@postgres:5432/bike_station"