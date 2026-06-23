from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from weather import fetch_weather, save_weather

default_args = {
    "owner": "parkmybike",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_hourly",
    description="Collecte et mise en cache des données météo",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["weather"],
) as dag:

    fetch_weather_task = PythonOperator(
        task_id="fetch_weather",
        python_callable=fetch_weather,
    )

    save_weather_task = PythonOperator(
        task_id="save_weather",
        python_callable=save_weather,
        op_args=[fetch_weather_task.output],
    )

    fetch_weather_task >> save_weather_task
