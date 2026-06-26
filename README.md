# ParkMyBike
ParkMyBike est une plateforme de data engineering permettant de collecter, transformer et visualiser en temps réel la disponibilité des stations de vélos en libre-service (Vélo'v Lyon, JCDecaux), tout en enrichissant ces données avec les conditions météorologiques locales (Open-Meteo).

---

## Architecture du Projet

Le projet s'appuie sur une architecture conteneurisée gérée par Docker Compose :

* Apache Airflow 2.8.1 : Image personnalisée (nommée pmb-airflow et construite via Dockerfile.airflow) incluant requests, sqlalchemy et psycopg2-binary pour orchestrer les pipelines de données.
* PostgreSQL 13 : Stocke la liste des stations, les données météo, ainsi que l'historique des statuts dynamiques.
* Metabase : Interface de Business Intelligence (BI) connectée à PostgreSQL pour la création de tableaux de bord visuels.
* GitHub Actions : Pipeline CI/CD automatisé pour exécuter les tests unitaires avec pytest à chaque commit.

---

## Orchestration et DAGs (Dossier airflow/dags/)

Le projet est rythmé par 3 DAGs Airflow complémentaires qui alimentent la base de données de manière asynchrone :

1. station_list (@daily) : S'exécute une fois par jour pour récupérer l'ensemble du référentiel des stations de Lyon et enregistrer les nouvelles stations si nécessaire.
2. weather_hourly (@hourly) : Récupère toutes les heures les conditions météo courantes de Lyon et les enregistre dans la table weather afin de maintenir un historique météorologique complet.
3. station_info (*/5 * * * *) : Collecte toutes les 5 minutes l'état dynamique des bornes (vélos et places disponibles), associe chaque station à l'enregistrement météo le plus récent, et stocke le tout dans la table pivot.

---

## Démarrage Rapide

### 1. Prérequis
Assurez-vous d'avoir installé Docker et Docker Compose.

### 2. Configuration des variables d'environnement
Créez un fichier .env à la racine du projet en vous basant sur le fichier env.example pour configurer vos accès de manière sécurisée :

```ini
# Base de données PostgreSQL (Superadmin)
POSTGRES_USER=root_admin
POSTGRES_PASSWORD=super_secret_password

# Mots de passe utilisateurs dédiés
DB_USER_PASSWORD_AIRFLOW=airflow_secure_pass
DB_USER_PASSWORD_METABASE=metabase_secure_pass

# Interface Airflow (Compte initial)
AIRFLOW_UI_USERNAME=admin
AIRFLOW_UI_PASSWORD=secure_admin_password
AIRFLOW_UI_FIRSTNAME=Admin
AIRFLOW_UI_LASTNAME=User
AIRFLOW_UI_EMAIL=admin@example.com

# Clés d'API tierces
JC_DECAUX_API_KEY=votre_cle_api_jcdecaux
```

### 3. Build de l'image Airflow et lancement des conteneurs
Avant de lancer l'orchestration, vous devez construire l'image personnalisée pour Airflow, puis démarrer la pile de conteneurs :

```Bash
# 1. Construction de l'image personnalisée Airflow
docker build -t pmb-airflow -f dockers/Dockerfile.airflow .

# 2. Lancement des conteneurs en arrière-plan
docker compose up -d
```

Une fois le lancement terminé, les différents services sont accessibles localement :
* Airflow Webserver : http://localhost:8082
* Metabase : http://localhost:3000 (La base de données métier est pré-connectée automatiquement)
* PostgreSQL : localhost:5432

---

## Modèle de Données et Initialisation
L'initialisation de la base de données (création des bases, des tables, des index optimisés et des rôles applicatifs isolés en lecture/écriture) est gérée de manière sécurisée au tout premier démarrage de Postgres via le script ./sql/init-databases.sh.

Le script s'appuie sur le modèle relationnel suivant :
* station : Stockage statique des stations (numéro, nom, coordonnées).
* weather : Historique horaire de la météo.
* station_status : Table de faits temporelle liant une station, une météo et les indicateurs dynamiques (vélos/places libres).

---

## Tests et Qualité du Code
Le projet intègre une suite de tests unitaires robustes utilisant pytest et unittest.mock. Les appels réseaux (API JCDecaux et Open-Meteo) ainsi que la tuyauterie SQLAlchemy (moteurs, connexions, transactions) y sont entièrement simulés afin de valider le code de manière isuée sans infrastructure active.

### Lancer les tests en local
```Bash
pip install pytest requests sqlalchemy
pytest tests/
```

Note : Le fichier tests/conftest.py ajuste le contexte d'import Python pour simuler à l'identique le comportement du Scheduler d'Airflow vis-à-vis du dossier plugins/.