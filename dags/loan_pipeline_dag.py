from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

# Add scripts directory to import path
sys.path.append('/opt/airflow/scripts')

from transform_features import calculate_features, get_connection
from stream_to_s3 import upload_to_s3

default_args = {
    'owner': 'creditstar',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='loan_feature_pipeline',
    default_args=default_args,
    description='Extract, transform and stream loan application features to S3',
    schedule_interval='@hourly',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['creditstar', 'loan', 'etl'],
) as dag:

    transform_task = PythonOperator(
        task_id='transform_features',
        python_callable=lambda: calculate_features(get_connection()).to_parquet(
            os.path.join(os.getenv("PROCESSED_DATA_PATH"), "client_features.parquet"),
            index=False
        )
    )

    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3
    )

    transform_task >> upload_task
