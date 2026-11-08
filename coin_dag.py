from datetime import datetime, timedelta, timezone
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from crypto_etl import run_etl

default_args = {
    "owner": "mayank",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="coin_dag",
    default_args=default_args,
    description="Daily CoinGecko snapshot to CSV",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    extract_load = PythonOperator(
        task_id="run_coin_etl",
        python_callable=run_etl,
    )