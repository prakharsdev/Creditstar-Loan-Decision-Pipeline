import os
import subprocess
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/airflow/.env")

os.environ["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD")

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DUMP_FILE = "./data/raw/de_test_task_db_plain_text"


def run_command(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


def restore_database():
    print("Resetting PostgreSQL database...")

    terminate_connections = f"""
        psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid();"
    """
    drop_create_cmd = f""" 
        psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "DROP DATABASE IF EXISTS {DB_NAME};" #noqa
        psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "CREATE DATABASE {DB_NAME};" 
    """

    run_command(terminate_connections)
    run_command(drop_create_cmd)

    print(f"Loading data from dump into {DB_NAME}...")
    restore_cmd = (
        f"psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f {DUMP_FILE}"
    )
    run_command(restore_cmd)

    print("Database restored successfully.")


if __name__ == "__main__":
    try:
        restore_database()
    except Exception as e:
        print(f"Database restore failed: {e}")
