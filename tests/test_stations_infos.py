import pytest
from unittest.mock import patch, MagicMock
import requests

# L'import fonctionne grâce au conftest.py configuré sur airflow/plugins
from stations_infos import fetch_stations_data, transform_data, save_stations_info


# ==========================================
# FIXTURES
# ==========================================
@pytest.fixture
def mock_jcd_raw():
    """Simule les données dynamiques renvoyées par JCDecaux"""
    return [
        {
            "number": 10001,
            "contractName": "lyon",
            "status": "OPEN",
            "totalStands": {
                "capacity": 20,
                "availabilities": {
                    "stands": 15,
                    "bikes": 5
                }
            },
            "lastUpdate": "2026-06-23T12:00:00"
        }
    ]

@pytest.fixture
def mock_transformed_info():
    """Résultat attendu après transformation et enrichissement"""
    return [
        {
            "station_id": 42,
            "weather_id": 99,
            "is_opened": 1,
            "total_capacity": 20,
            "available_stand": 15,
            "available_bike": 5,
            "status_timestamp": "2026-06-23T12:00:00"
        }
    ]


# ==========================================
# TESTS : fetch_stations_data
# ==========================================
@patch("stations_infos.requests.get")
def test_fetch_stations_data_success(mock_get, mock_jcd_raw):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_jcd_raw
    mock_get.return_value = mock_response

    result = fetch_stations_data("secret_key")
    assert result == mock_jcd_raw


@patch("stations_infos.requests.get")
def test_fetch_stations_data_exception(mock_get):
    # Simule une coupure réseau / erreur de connexion
    mock_get.side_effect = requests.exceptions.ConnectionError("Échec de connexion")
    
    result = fetch_stations_data("secret_key")
    assert result is None


# ==========================================
# TESTS : transform_data
# ==========================================
@patch("stations_infos.create_engine")
def test_transform_data(mock_create_engine, mock_jcd_raw):
    """Vérifie la récupération des IDs (météo et station) et la transformation"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Mock des retours de requêtes fetchone() :
    # Premier appel (météo) renvoie ID 99 -> (99,)
    # Deuxième appel (station) renvoie ID 42 -> (42,)
    mock_conn.execute.return_value.fetchone.side_effect = [(99,), (42,)]

    result = transform_data(mock_jcd_raw)

    assert len(result) == 1
    assert result[0]["station_id"] == 42
    assert result[0]["weather_id"] == 99
    assert result[0]["is_opened"] == 1
    assert result[0]["total_capacity"] == 20
    assert result[0]["available_bike"] == 5


# ==========================================
# TESTS : save_stations_info
# ==========================================
@patch("stations_infos.create_engine")
def test_save_stations_info(mock_create_engine, mock_transformed_info):
    """Vérifie que les enregistrements transformés sont bien insérés"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    save_stations_info(mock_transformed_info)

    # L'exécution de l'insert doit être appelée pour chaque station de la liste
    assert mock_conn.execute.call_count == 1