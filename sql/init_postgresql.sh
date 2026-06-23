#!/bin/bash
set -e

# 1. INITIALISATION GLOBALE (Bases de données et rôles)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- ======================
    -- DATABASES
    -- ======================
    CREATE DATABASE airflow;
    CREATE DATABASE bike_station;

    -- ======================
    -- ROLES GLOBAUX
    -- ======================
    CREATE ROLE bike_station_read;
    CREATE ROLE bike_station_write;

    -- ======================
    -- UTILISATEURS (Sécurisés via .env)
    -- ======================
    CREATE USER airflow WITH PASSWORD '$DB_USER_PASSWORD_AIRFLOW';
    CREATE USER metabase_user WITH PASSWORD '$DB_USER_PASSWORD_METABASE';

    -- Accès de base à la DB
    GRANT CONNECT ON DATABASE bike_station TO airflow;
    GRANT CONNECT ON DATABASE bike_station TO metabase_user;
EOSQL

# 2. INITIALISATION DANS LA BASE BIKE_STATION
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "bike_station" <<-EOSQL
    -- ======================
    -- TABLES
    -- ======================
    CREATE TABLE station (
        id SERIAL PRIMARY KEY,
        number INT UNIQUE,
        name VARCHAR(255),
        city VARCHAR(100),
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION
    );

    CREATE TABLE weather (
        id SERIAL PRIMARY KEY,
        weather_timestamp TIMESTAMP NOT NULL UNIQUE,
        is_day BOOLEAN,
        temperature FLOAT,
        precipitation FLOAT,
        rain FLOAT,
        snowfall FLOAT
    );

    CREATE TABLE station_status (
        id BIGSERIAL PRIMARY KEY,
        station_id INT NOT NULL,
        weather_id INT,
        status_timestamp TIMESTAMP NOT NULL,
        is_opened BOOLEAN,
        total_capacity INT,
        available_bike INT,
        available_stand INT,
        CONSTRAINT fk_station FOREIGN KEY (station_id) REFERENCES station(id),
        CONSTRAINT fk_weather FOREIGN KEY (weather_id) REFERENCES weather(id)
    );

    -- ======================
    -- INDEX
    -- ======================
    CREATE INDEX idx_station_status_station ON station_status(station_id);
    CREATE INDEX idx_station_status_timestamp ON station_status(status_timestamp);

    -- ======================
    -- PRIVILÈGES DU SCHÉMA PUBLIC
    -- ======================
    GRANT USAGE ON SCHEMA public TO airflow;
    GRANT USAGE ON SCHEMA public TO metabase_user;

    -- Lecture
    GRANT SELECT ON station TO bike_station_read;
    GRANT SELECT ON weather TO bike_station_read;
    GRANT SELECT ON station_status TO bike_station_read;

    -- Écriture
    GRANT INSERT ON station TO bike_station_write;
    GRANT INSERT ON weather TO bike_station_write;
    GRANT INSERT ON station_status TO bike_station_write;

    -- Accès aux séquences
    GRANT USAGE, SELECT ON SEQUENCE station_id_seq TO bike_station_write;
    GRANT USAGE, SELECT ON SEQUENCE weather_id_seq TO bike_station_write;
    GRANT USAGE, SELECT ON SEQUENCE station_status_id_seq TO bike_station_write;

    -- ======================
    -- ATTRIBUTION DES RÔLES
    -- ======================
    GRANT bike_station_read TO airflow;
    GRANT bike_station_write TO airflow;
    GRANT bike_station_read TO metabase_user;
EOSQL