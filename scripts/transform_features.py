import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="/opt/airflow/.env")


def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )


def calculate_features(conn):
    # Subquery to find the latest loan creation date
    latest_date_query = "SELECT MAX(created_on) FROM loan;"
    latest_created_on = pd.read_sql_query(latest_date_query, conn).iloc[0, 0]

    queries = {
        "paid_loans": """
            SELECT client_id, COUNT(*) AS paid_loans
            FROM loan
            WHERE status = 'paid'
            GROUP BY client_id;
        """,
        "days_since_last_late_payment": """
            SELECT l.client_id,
                   DATE_PART('day', NOW() - MAX(p.created_on)) AS days_since_late
            FROM loan l
            JOIN payment p ON l.id = p.loan_id
            WHERE p.status = 'late'
            GROUP BY l.client_id;
        """,
        "profit_rate_90d": f"""
            SELECT l.client_id,
                   SUM(p.interest) / NULLIF(SUM(l.amount), 0) AS profit_rate_90d
            FROM loan l
            JOIN payment p ON l.id = p.loan_id
            WHERE l.created_on >= TIMESTAMP '{latest_created_on}' - INTERVAL '90 days'
            GROUP BY l.client_id;
        """,
    }

    features = {}
    for name, query in queries.items():
        features[name] = pd.read_sql_query(query, conn)

    # Merge all features on client_id
    df = features["paid_loans"]
    df = df.merge(features["days_since_last_late_payment"], on="client_id", how="left")
    df = df.merge(features["profit_rate_90d"], on="client_id", how="left")

    # Decision logic
    df["decision"] = df.apply(
        lambda row: "ACCEPT"
        if (
            row["paid_loans"] >= 3
            and (row["profit_rate_90d"] if pd.notnull(row["profit_rate_90d"]) else 0)
            > 0.1
            and (row["days_since_late"] if pd.notnull(row["days_since_late"]) else 9999)
            > 30
        )
        else "REJECT",
        axis=1,
    )

    return df


if __name__ == "__main__":
    conn = get_connection()
    df = calculate_features(conn)

    # Ensure output directory exists
    output_dir = os.getenv("PROCESSED_DATA_PATH")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "client_features.parquet")
    df.to_parquet(output_path, index=False)
    print(f"Features with decisions saved to {output_path}")
