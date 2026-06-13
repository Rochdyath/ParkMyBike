from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from scripts.stations_infos import fetch_stations_data, transform_data, save_stations_info

default_args = {
    "owner": "parkmybike",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="station_info",
    description="Collecte de les informations dynamiques des stations de vélo de Lyon",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    tags=["stations", "infos"],
) as dag:

    fetch_stations_data = PythonOperator(
        task_id="fetch_station_list",
        python_callable=fetch_stations_data,
        op_args=[Variable.get("JC_DECAUX_API_KEY")]
    )

    transform_data = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_args=[fetch_stations_data.output]
    )

    save_stations_info = PythonOperator(
        task_id="save_stations_info",
        python_callable=save_stations_info,
        op_args=[transform_data.output],
    )

    fetch_stations_data >> transform_data >> save_stations_info
