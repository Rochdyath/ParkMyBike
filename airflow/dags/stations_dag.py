from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from scripts.stations_info import fetch_stations_data, fetch_weather, transform_data

default_args = {
    "owner": "parkmybike",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="stations_5min",
    description="Collecte stations et enrichissement météo",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    tags=["stations"],
) as dag:

    fetch_stations_task = PythonOperator(
        task_id="fetch_stations",
        python_callable=fetch_stations_data,
    )

    load_weather_task = PythonOperator(
        task_id="load_weather_cache",
        python_callable=fetch_weather,
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
        op_args=[
            "{{ ti.xcom_pull(task_ids='fetch_stations') }}",
            "{{ ti.xcom_pull(task_ids='load_weather_cache') }}"
        ],
    )

    fetch_stations_task >> load_weather_task >> transform_task
