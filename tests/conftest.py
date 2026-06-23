import sys
import os

# Trouve le chemin absolu vers le dossier airflow/plugins
plugins_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'airflow', 'plugins'))

# Ajoute-le au sys.path local (exactement comme le fait Airflow)
if plugins_path not in sys.path:
    sys.path.insert(0, plugins_path)