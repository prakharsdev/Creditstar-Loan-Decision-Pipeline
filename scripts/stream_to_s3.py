import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/opt/airflow/.env")

# Fetch env vars
FILE_PATH = os.path.join(os.getenv("PROCESSED_DATA_PATH"), "client_features.parquet")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_KEY = "client_features.parquet"


def upload_to_s3():
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT"),
        region_name=os.getenv("S3_REGION"),
    )

    # Upload the file
    s3.upload_file(FILE_PATH, S3_BUCKET, S3_KEY)
    print(f"Uploaded {S3_KEY} to s3://{S3_BUCKET}/")


if __name__ == "__main__":
    upload_to_s3()
