-- ======================
-- DATABASES
-- ======================

-- base airflow
CREATE DATABASE airflow;

-- base des stations
CREATE DATABASE bike_station;

-- ======================
-- BIKE_STATION DATABASE
-- ======================

\connect bike_station

-- ======================
-- TABLES
-- ======================

-- table station
CREATE TABLE station (
    id SERIAL PRIMARY KEY,
    number INT UNIQUE,
    name VARCHAR(255),
    city VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- table météo
CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    weather_timestamp TIMESTAMP NOT NULL UNIQUE,
    is_day BOOLEAN,
    temperature FLOAT,
    precipitation FLOAT,
    rain FLOAT,
    snowfall FLOAT
);

-- table station_status
CREATE TABLE station_status (
    id BIGSERIAL PRIMARY KEY,
    station_id INT NOT NULL,
    weather_id INT,
    status_timestamp TIMESTAMP NOT NULL,

    is_opened BOOLEAN,
    total_capacity INT,
    available_bike INT,
    available_stand INT,

    CONSTRAINT fk_station
        FOREIGN KEY (station_id)
        REFERENCES station(id),

    CONSTRAINT fk_weather
        FOREIGN KEY (weather_id)
        REFERENCES weather(id)
);

-- ======================
-- INDEX
-- ======================

CREATE INDEX idx_station_status_station
ON station_status(station_id);

CREATE INDEX idx_station_status_timestamp
ON station_status(status_timestamp);

-- ======================
-- ROLES
-- ======================

CREATE ROLE bike_station_read;
CREATE ROLE bike_station_write;

-- lecture
GRANT SELECT ON station TO bike_station_read;
GRANT SELECT ON weather TO bike_station_read;
GRANT SELECT ON station_status TO bike_station_read;

-- écriture
GRANT INSERT ON station TO bike_station_write;
GRANT INSERT ON weather TO bike_station_write;
GRANT INSERT ON station_status TO bike_station_write;

-- accès aux séquences (SERIAL/BIGSERIAL)
GRANT USAGE, SELECT ON SEQUENCE station_id_seq TO bike_station_write;
GRANT USAGE, SELECT ON SEQUENCE weather_id_seq TO bike_station_write;
GRANT USAGE, SELECT ON SEQUENCE station_status_id_seq TO bike_station_write;

-- ======================
-- UTILISATEUR AIRFLOW
-- ======================

CREATE USER airflow WITH PASSWORD 'airflow';

-- accès à la base bike_station
GRANT CONNECT ON DATABASE bike_station TO airflow;

-- accès au schema public
GRANT USAGE ON SCHEMA public TO airflow;

-- attribuer les rôles
GRANT bike_station_read TO airflow;
GRANT bike_station_write TO airflow;

-- ======================
-- UTILISATEUR METABASE
-- ======================

CREATE USER metabase_user WITH PASSWORD 'metabase_pass';

-- accès à la base bike_station
GRANT CONNECT ON DATABASE bike_station TO metabase_user;

-- accès au schema public
GRANT USAGE ON SCHEMA public TO metabase_user;

-- attribuer les rôles
GRANT bike_station_read TO metabase_user;