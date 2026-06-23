import pytest
from unittest.mock import patch, MagicMock
import requests

# Grâce au conftest.py déjà créé, cet import fonctionne tout seul
from weather import fetch_weather, save_weather


# ==========================================
# FIXTURES (Fausses données pour les tests)
# ==========================================
@pytest.fixture
def mock_open_meteo_raw():
    """Simule la réponse JSON brute de l'API Open-Meteo"""
    return {
        "current": {
            "time": "2026-06-23T12:00:00",
            "is_day": 1,
            "temperature_2m": 22.5,
            "precipitation": 0.0,
            "rain": 0.0,
            "snowfall": 0.0
        }
    }

@pytest.fixture
def mock_weather_normalized():
    """Simule le dictionnaire dictionnaire propre renvoyé par votre fonction"""
    return {
        "weather_timestamp": "2026-06-23T12:00:00",
        "is_day": 1,
        "temperature": 22.5,
        "precipitation": 0.0,
        "rain": 0.0,
        "snowfall": 0.0
    }


# ==========================================
# TESTS : fetch_weather
# ==========================================

@patch("weather.requests.get")
def test_fetch_weather_success(mock_get, mock_open_meteo_raw, mock_weather_normalized):
    """Vérifie que l'API est appelée et que les données sont bien restructurées"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_open_meteo_raw
    mock_get.return_value = mock_response

    result = fetch_weather()

    assert result == mock_weather_normalized
    mock_get.assert_called_once()


@patch("weather.requests.get")
def test_fetch_weather_api_error(mock_get):
    """Vérifie le comportement si l'API renvoie une erreur HTTP (ex: 500)"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = fetch_weather()

    assert result is None


@patch("weather.requests.get")
def test_fetch_weather_timeout(mock_get):
    """Vérifie que le bloc try/except capture bien une panne réseau (Timeout)"""
    # On force le mock à lever une exception réseau au lieu de renvoyer une réponse
    mock_get.side_effect = requests.exceptions.Timeout("La connexion a expiré")

    result = fetch_weather()

    # Le bloc 'except' a capturé le crash et renvoie proprement None
    assert result is None


# ==========================================
# TESTS : save_weather
# ==========================================

def test_save_weather_value_error():
    """Vérifie que la fonction lève bien une ValueError si le dictionnaire est vide"""
    with pytest.raises(ValueError, match="Aucune donnée météo à sauvegarder"):
        save_weather({})


@patch("weather.create_engine")
def test_save_weather_success(mock_create_engine, mock_weather_normalized):
    """Vérifie l'insertion réussie en base de données"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    result = save_weather(mock_weather_normalized)

    assert result is True
    # L'insert doit être exécuté 1 seule fois
    assert mock_conn.execute.call_count == 1


@patch("weather.create_engine")
def test_save_weather_database_crash(mock_create_engine, mock_weather_normalized):
    """Vérifie que si la DB crash, le 'except' attrape l'erreur et renvoie False"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # On simule une erreur de connexion à la base de données lors du execute()
    mock_conn.execute.side_effect = Exception("Connexion perdue avec Postgres")

    result = save_weather(mock_weather_normalized)

    # Grâce au try/except de votre fonction, l'application ne plante pas, elle renvoie False
    assert result is False