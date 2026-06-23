import pytest
from unittest.mock import patch, MagicMock

from stations_list import fetch_lyon_stations, transform_data, save_new_stations


# ==========================================
# FIXTURES (Données de test partagées)
# ==========================================
@pytest.fixture
def mock_stations_raw():
    return [
        {
            "number": 10001,
            "contractName": "lyon",
            "name": "010001 - METRO GERLAND",
            "position": {"latitude": 45.72, "longitude": 4.83}
        }
    ]

@pytest.fixture
def mock_stations_transformed():
    return [
        {
            "number": 10001,
            "city": "lyon",
            "name": "010001 - METRO GERLAND",
            "latitude": 45.72,
            "longitude": 4.83
        }
    ]


# ==========================================
# TESTS : fetch_lyon_stations
# ==========================================
@patch("stations_list.requests.get")
def test_fetch_lyon_stations_success(mock_get, mock_stations_raw):
    """Teste le succès d'un appel API JCDecaux"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_stations_raw
    mock_get.return_value = mock_response

    result = fetch_lyon_stations("fake_api_key")

    assert result == mock_stations_raw
    mock_get.assert_called_once()


@patch("stations_list.requests.get")
def test_fetch_lyon_stations_failure(mock_get):
    """Teste le comportement en cas d'erreur de l'API (ex: 403 Forbidden)"""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response

    result = fetch_lyon_stations("invalid_key")

    assert result is None


# ==========================================
# TESTS : transform_data
# ==========================================
def test_transform_data(mock_stations_raw, mock_stations_transformed):
    """Teste la normalisation des dictionnaires JCDecaux"""
    result = transform_data(mock_stations_raw)
    assert result == mock_stations_transformed


def test_transform_data_missing_fields():
    """Teste la robustesse si un champ 'position' est manquant"""
    raw_data = [{"number": 12, "contractName": "lyon", "name": "Station Test"}]
    
    result = transform_data(raw_data)
    
    assert result[0]["latitude"] is None
    assert result[0]["longitude"] is None


# ==========================================
# TESTS : save_new_stations
# ==========================================
@patch("stations_list.create_engine")  # Modifié ici aussi
def test_save_new_stations_insert(mock_create_engine, mock_stations_transformed):
    """Teste l'insertion en BDD d'une nouvelle station (n'existe pas encore)"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    # On simule que fetchone() renvoie None (la station n'existe pas en BDD)
    mock_conn.execute.return_value.fetchone.return_value = None

    result = save_new_stations(mock_stations_transformed)

    assert result is True
    # 2 appels attendus : 1 select pour vérifier l'existence + 1 insert
    assert mock_conn.execute.call_count == 2


@patch("stations_list.create_engine")
def test_save_new_stations_skip_existing(mock_create_engine, mock_stations_transformed):
    """Teste qu'une station déjà existante en BDD n'est pas ré-insérée"""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    # On simule que la station existe déjà (fetchone renvoie un ID fictif)
    mock_conn.execute.return_value.fetchone.return_value = (1,)

    result = save_new_stations(mock_stations_transformed)

    assert result is True
    # 1 seul appel attendu : le SELECT. L'INSERT doit être sauté.
    assert mock_conn.execute.call_count == 1