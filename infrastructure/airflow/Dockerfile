FROM apache/airflow:2.7.1-python3.10

USER airflow

RUN pip install --no-cache-dir \
    pandas \
    psycopg2-binary \
    boto3 \
    python-dotenv \
    pytest

COPY --chown=airflow:airflow ./dags /opt/airflow/dags
COPY --chown=airflow:airflow ./scripts /opt/airflow/scripts
COPY --chown=airflow:airflow .env.docker /opt/airflow/.env
COPY --chown=airflow:airflow ./infrastructure/airflow/entrypoint.sh /opt/airflow/entrypoint.sh

RUN chmod +x /opt/airflow/entrypoint.sh

ENTRYPOINT ["/opt/airflow/entrypoint.sh"]
