from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from stations_list import fetch_lyon_stations, transform_data, save_new_stations

default_args = {
    "owner": "parkmybike",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="station_list",
    description="Collecte de la liste des stations de vélo de Lyon",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["stations", "list"],
) as dag:

    fetch_station_list = PythonOperator(
        task_id="fetch_station_list",
        python_callable=fetch_lyon_stations,
        op_args=[Variable.get("JC_DECAUX_API_KEY")]
    )

    transform_data = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_args=[fetch_station_list.output]
    )

    save_new_stations = PythonOperator(
        task_id="save_new_stations",
        python_callable=save_new_stations,
        op_args=[transform_data.output],
    )

    fetch_station_list >> transform_data >> save_new_stations