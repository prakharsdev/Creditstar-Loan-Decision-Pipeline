FROM apache/airflow:2.7.1-python3.10

USER root
RUN pip install pandas psycopg2-binary boto3 python-dotenv

COPY ./dags /opt/airflow/dags
COPY ./scripts /opt/airflow/scripts
COPY .env /opt/airflow/.env
