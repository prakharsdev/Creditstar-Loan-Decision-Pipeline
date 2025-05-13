# Creditstar: Automated Loan Decision System

This repository contains a production-grade data pipeline developed for a technical assessment by Creditstar. The goal was to design a scalable, modular, and automated system that extracts data from a PostgreSQL database, transforms it into client-level features, applies rule-based loan decision logic, and stores the results in MinIO as a Parquet file. The solution emphasizes automation, clarity, and extensibility, mirroring patterns used in modern fintech data platforms.

---
## Full Project Demo Video
[![Demo Video](https://github.com/user-attachments/assets/2a8b7be1-d1a2-4149-90c4-fc4af6b4d924)](https://youtu.be/0MIHMGOn7oM)
---
## Business Context

The core objective of this project is to automate decision-making within the loan application process at Credistar. In a high-volume consumer finance environment, manually reviewing every application is neither scalable nor efficient. Therefore, building a data-driven system to assess the reliability of loan applicants helps optimize operational effort, reduce credit risk, and improve turnaround time.

This project simulates a production-grade pipeline that would be part of a broader credit decisioning system. Specifically, it focuses on the transformation of raw transactional and behavioral data (loans and payments) into meaningful features that can power automated decisions such as accepting or rejecting a loan application.

By processing historical loan data, payment behavior, and calculating profitability and delinquency metrics, the system enables a rule-based decision logic that can later be extended into a machine learning model. This modular approach ensures that as business requirements evolve such as the need to support real-time decisions, additional input features, or regulatory reporting, the system can grow without fundamental restructuring.

The decision rules (such as a minimum number of paid loans, positive profit rate, and absence of recent late payments) reflect business risk appetite and are used to flag clients as either “ACCEPT” or “REJECT.” The result is a structured Parquet file ready for consumption by downstream systems, BI dashboards, or ML workflows.

This assignment is a microcosm of how data platforms are used in fintech to make decisions at scale while ensuring traceability, data quality, and operational reproducibility.

---
## What’s Completed

* Full local environment via Docker Compose
* Airflow DAG with feature transformation and upload
* Feature engineering with SQL + pandas
* Loan decision logic added
* Parquet output on MinIO
* Terraform bucket provisioning
* Unit tests for transformation logic using Pytest

---
## Tech Stack

| Component      | Tool/Tech               |
| -------------- | ----------------------- |
| Orchestration  | Apache Airflow          |
| Database       | PostgreSQL              |
| Object Storage | MinIO (S3-compatible)   |
| Scripting      | Python + pandas         |
| Deployment     | Docker + Docker Compose |
| Automation     | Terraform (for S3)      |
| Visualization  | pgAdmin                 |
| Testing        | Pytest                  |

---

## Project Structure

```
Creditstar/
├── dags/                      # Airflow DAG definitions
│   └── loan_pipeline_dag.py
├── scripts/                   # Python ETL scripts
│   ├── restore_db.py          # Load raw SQL dump into PostgreSQL
│   ├── transform_features.py  # SQL + feature engineering + decision logic
│   └── stream_to_s3.py        # Upload to MinIO
├── infrastructure/            # Infra setup files
│   ├── airflow/
│   │   ├── Dockerfile         # Custom Airflow image with required packages
│   │   └── entrypoint.sh
│   └── postgres/init.sql      # Placeholder for DB-level init if needed
├── data/
│   ├── raw/                   # SQL dump: de_test_task_db_plain_text
│   └── processed/             # Generated client_features.parquet
├── terraform/                 # Terraform to provision S3 bucket
│   └── main.tf
├── test/                      # Pytest tests
│   └── test_transformations.py
├── .env.docker                # Environment variables
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── docker-compose.yml         # Service definitions
└── README.md                  # You're reading it :)
```

---
##  How to Run the Project

### 1. Start the infrastructure

```bash
docker-compose up -d --build
```

> This spins up PostgreSQL, pgAdmin, MinIO, and Airflow.

### 2. Restore the database

```bash
docker exec -it creditstar-airflow-1 bash
python scripts/restore_db.py
```

>  This loads the raw SQL dump into the PostgreSQL DB named `creditstar`.

### 3. Trigger the DAG

* Access Airflow UI at: [http://localhost:8080](http://localhost:8080)
* Run `loan_feature_pipeline` manually.

### 4. View the output

* Access MinIO: [http://localhost:9001](http://localhost:9001)
* Bucket: `creditstar-features`
* File: `client_features.parquet`

---
##  .env.docker Configuration

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=creditstar

S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password123
S3_BUCKET_NAME=creditstar-features
S3_REGION=us-east-1

PROCESSED_DATA_PATH=/opt/airflow/data/processed
LOG_LEVEL=INFO
```

---
##  Terraform Usage

I used Terraform to provision the `creditstar-features` bucket in MinIO. It avoids manual steps and ensures reproducibility.

```hcl
provider "minio" {
  minio_server   = "minio:9000"
  minio_user     = "admin"
  minio_password = "password123"
  insecure       = true
}

resource "minio_s3_bucket" "creditstar_features" {
  bucket = "creditstar-features"
  acl    = "private"
}
```

Run via:

```bash
cd terraform
terraform init
terraform apply
```

---
## Automated Tests

To ensure the correctness and reliability of the transformation logic, I added a test suite under `test/test_transformations.py` using Pytest. These tests validate that the output dataframe is not empty, contains expected columns, and includes valid decision outcomes.

### Test Cases

1. **test\_transform\_output\_not\_empty**: Ensures that the transformation does not result in an empty DataFrame.
2. **test\_columns\_exist**: Checks if all required columns (`client_id`, `paid_loans`, `days_since_late`, `profit_rate_90d`) are present.
3. **test\_decision\_values**: Confirms that all values in the `decision` column are either `ACCEPT` or `REJECT`.

### How to Run

```bash
# Enter the running Airflow container
docker exec -it creditstar-airflow-1 bash

# Run tests from within the container
PYTHONPATH=/opt/airflow pytest test/test_transformations.py
```

---

## Code Formatting & Quality (Pre-commit Hooks)

This project includes a `.pre-commit-config.yaml` setup to enforce consistent code style and prevent common mistakes. The following hooks are configured:

* **Black**: Ensures code formatting adheres to the [Black](https://github.com/psf/black) style guide.
* **End-of-File Fixer**: Makes sure files end with a newline.
* **Check for Large Files**: Prevents accidental commits of large files.

These checks are scoped to the `scripts/` directory.

### How to Use

1. Install pre-commit:

   ```bash
   pip install pre-commit
   ```

2. Run checks manually (without committing):

   ```bash
   pre-commit run --all-files
   ```

3. Or limit it to `scripts/`:

   ```bash
   pre-commit run --files scripts/*.py
   ```

These lightweight checks improve code consistency and reduce review friction without requiring full linting or type checking.

---

## Feature Engineering & Decision Logic

The goal of this step is to transform raw transactional data (loans and payments) into meaningful client-level features that can guide automated loan decisions. This is implemented in the `transform_features.py` script and executed as part of the Airflow DAG.

The process is a **hybrid approach**, where data is partially aggregated in SQL (to leverage PostgreSQL's performance) and further processed in pandas for flexibility and final logic application.

### 1. **Paid Loan History**

```sql
SELECT client_id, COUNT(*) AS paid_loans
FROM loan
WHERE status = 'paid'
GROUP BY client_id;
```

### 2. **Days Since Last Late Payment**

```sql
SELECT l.client_id, 
       DATE_PART('day', NOW() - MAX(p.created_on)) AS days_since_late
FROM loan l
JOIN payment p ON l.id = p.loan_id
WHERE p.status = 'late'
GROUP BY l.client_id;
```

### 3. **Profit Rate (Last 90 Days)**

```sql
SELECT l.client_id,
       SUM(p.interest) / NULLIF(SUM(l.amount), 0) AS profit_rate_90d
FROM loan l
JOIN payment p ON l.id = p.loan_id
WHERE l.created_on >= (
    SELECT MAX(created_on) FROM loan
) - INTERVAL '90 days'
GROUP BY l.client_id;
```

### Decision Logic

The following rule-based logic determines whether a client is eligible for a loan based on three key criteria: repayment history, profitability, and recent delinquency. The logic is applied row by row to the feature DataFrame.

```python
row["decision"] = "ACCEPT" if (
    row.paid_loans >= 3 and 
    (row.profit_rate_90d if row.profit_rate_90d is not None else 0) > 0.1 and 
    (row.days_since_late if row.days_since_late is not None else 9999) > 30
) else "REJECT"
```

**Explanation:**

* `paid_loans >= 3`: Ensures the client has a proven history of at least 3 fully repaid loans.
* `profit_rate_90d > 0.1`: Validates that the client’s recent loans are financially profitable. If the value is missing, it's treated as `0`.
* `days_since_late > 30`: Confirms that the client has not made any late payments in the last 30 days. If there's no late payment history, the default is set to `9999` (i.e., very safe).

Only when **all three** conditions are met, the client is marked as `"ACCEPT"`. Otherwise, the decision is `"REJECT"`.


---

## Exploratory Analysis

A Jupyter notebook is included for quick validation and insight generation. It loads the generated Parquet file and confirms that the decision logic matches the final "ACCEPT" flag. This helps ensure logic correctness and supports future ML development.

```bash
notebooks/exploratory_analysis.ipynb
```

---
##  Data Flow Pipeline

The DAG `loan_feature_pipeline` orchestrates the entire process:

```text
┌────────────┐     ┌────────────────────────┐     ┌───────────────┐
│ Raw SQL DB │ →  │ transform_features.py  │ →  │ client_features│
└────────────┘     └────────────────────────┘     └──────┬────────┘
                                                        ↓
                                              Uploaded to MinIO
```

---
### Design Decisions

**Modular Data Pipeline Structure**
The solution is designed with a clear modular architecture, where each component is responsible for a specific part of the data lifecycle. The `restore_db.py` script handles database seeding, `transform_features.py` is responsible for deriving business-relevant features, and `stream_to_s3.py` takes care of persisting results to an object store. This modularity allows for independent testing and maintenance, reducing the cognitive load when updating or debugging the pipeline.

**Environment Variable Management**
To avoid hardcoding credentials and environment-specific settings, all configuration parameters (such as database host, port, credentials, and file paths) are pulled in through environment variables defined in `.env.docker`. This approach ensures the project can be safely deployed across environments by simply swapping environment files, improving both security and maintainability.

**Airflow for Orchestration**
Airflow is used to schedule and orchestrate the ETL process. It allows for visual representation, monitoring, retry mechanisms, and modular DAGs. Tasks such as `transform_features` and `upload_to_s3` are implemented as PythonOperators, enabling granular control and visibility into the DAG’s execution state. The DAG is built for clarity and can easily be extended to include additional steps like email alerts or validation checks.

**MinIO as a Local S3-Compatible Object Store**
Rather than relying on AWS or another cloud provider during development, MinIO is used as a locally hosted, S3-compatible object store. This enables realistic simulation of production object storage systems without incurring cost or requiring credentials. By using MinIO locally, I can test the complete pipeline, including S3 interactions, with minimal infrastructure.

**Decision Logic Co-located with Features**
The decisioning rule—whether to accept or reject a client—is included directly in the transformation logic. This co-location helps improve transparency during development and review, making it easy to validate and iterate on business rules. In a more mature setup, this logic might be abstracted into a scoring engine or business rules service, but for this use case, integrating it with feature engineering keeps the process streamlined and auditable.

**SQL + Pandas Hybrid Approach**
SQL queries are used to extract and aggregate data directly in the database where possible, capitalizing on PostgreSQL’s computation efficiency. Once loaded into memory, pandas is used for joining and applying logic that benefits from Python’s expressiveness. This hybrid model strikes a balance between performance and flexibility, making the best use of both technologies.

**Parquet Format for Downstream Consumption**
The resulting dataset is saved in the Apache Parquet format, which is both storage-efficient and highly performant for analytical workloads. Parquet is columnar and compressed, making it suitable for integration with tools such as Apache Spark, Snowflake, or BI platforms. Using this format enables faster reads and smaller storage footprint compared to alternatives like CSV.

**Containerization and Local Infrastructure**
Docker Compose is used to orchestrate the entire stack—PostgreSQL, Airflow, MinIO, and pgAdmin. This ensures that all services are isolated yet can communicate with one another seamlessly. It also makes the entire system reproducible with a single command, reducing dependency issues and onboarding friction.

**Terraform for Optional Infrastructure-as-Code (IaC)**
Although Docker Compose manages local containers, a lightweight Terraform setup is included to demonstrate how infrastructure such as the MinIO bucket can be declaratively managed. This shows preparedness for scaling the project into a cloud environment where IaC tools like Terraform are standard for provisioning infrastructure reliably and repeatedly.

---
### What Was Out of Scope (By Design)

While the system is architected to support future scaling needs, two key features were intentionally scoped out:

1. **Real-Time Streaming Triggers:**
   The current pipeline is designed as a batch process orchestrated by Airflow. Integrating real-time event streaming (e.g., Kafka + Spark) would require significant changes to the data ingestion model and infrastructure setup. For this assignment, I prioritized reliability, clarity, and modularity over introducing complexity. However, the architecture is designed in a way that streaming components can be integrated later with minimal disruption.

2. **Machine Learning Scoring:**
   A rule-based decision logic was used in place of a machine learning model. This keeps the pipeline interpretable, auditable, and easy to validate during early stages. The current decision logic is built on features that could feed directly into a predictive model in the future. This allows for a smooth transition to ML-based scoring without needing to re-engineer the transformation layer.
---

## Scalability & Performance

The current solution is designed with modularity and extensibility in mind. Each component—data loading, transformation, storage, and orchestration—is containerized and decoupled using Docker and orchestrated via Airflow. This approach offers a solid foundation to scale both horizontally and vertically depending on future demands.

###  Horizontal Scalability

This pipeline can scale out by increasing the number of instances for each service:

* **Airflow:** Additional worker containers can be added to handle more DAGs or larger task volumes in parallel.
* **PostgreSQL:** While this setup uses a single Postgres container, it can be replaced with a managed service (e.g., AWS RDS or Cloud SQL) with built-in replication and read replicas for concurrent processing.
* **MinIO (S3):** MinIO is stateless and can be scaled horizontally using distributed mode with load balancers.
* **Terraform Integration:** Since Terraform provisions the MinIO bucket automatically, this makes it cloud-agnostic and reusable across multiple environments, enabling teams to deploy the exact same infrastructure in development, staging, or production clusters.

###  Vertical Scalability

The pipeline can also be scaled vertically by allocating more CPU or memory to:

* The **Airflow container** to run heavier computations or larger data volume transformations.
* The **Postgres container** to improve read/write throughput or complex query performance.
* The **MinIO server** to store larger datasets or support more concurrent file operations.

In a production environment, resource limits and autoscaling policies can be enforced using Kubernetes or container orchestration tools, making vertical scaling even more flexible.

---

### Pros of This Architecture

* **Reproducible Infrastructure:** With Terraform provisioning the MinIO bucket, the pipeline is infrastructure-as-code compliant and easy to redeploy.
* **Simple Local Setup:** Docker Compose makes it easy to spin up the full environment consistently on any developer machine.
* **Component Isolation:** Each module (ETL, orchestration, storage) can be swapped or scaled independently without reengineering the entire stack.
* **Data Lineage Ready:** Airflow DAGs enable auditability, retry logic, and extendability for future use cases like scheduled model retraining.

---

###  Tradeoffs & Cons

* **Docker Compose is limited** to local development and small-scale testing. For production workloads, Kubernetes or ECS would be more suitable.
* **Manual DAG triggering and DB loading** steps can be automated further using event-driven pipelines or Airflow sensors.
* **Single-node Postgres** may become a bottleneck as data volume grows, but this can be addressed by migrating to a managed and scalable Postgres service.


## Improvements (Next Steps)

While the current implementation meets the core requirements of the assignment and mirrors a real-world data pipeline, there are several opportunities to further improve scalability, automation, and robustness:

### 1. **Automate DAG Triggering on DB Restore**

Currently, the DAG needs to be triggered manually from the Airflow UI after the database is restored. This step can be automated by:

* Adding a DAG sensor to watch for successful DB seeding.
* Triggering the DAG programmatically from the `restore_db.py` script using the Airflow REST API or CLI.
  This would create a smoother, end-to-end automated pipeline.

### 2. **Replace Raw SQL with dbt for Transformations**

Although the current solution uses raw SQL queries and pandas for feature engineering, introducing [dbt](https://www.getdbt.com/) would:

* Enable modular, version-controlled transformations.
* Add lineage tracking and documentation.
* Simplify testing and reusability for larger pipelines.

### 3. **Incorporate CI/CD**

Integrating GitHub Actions (or similar CI/CD tools) would allow:

* Automated testing for each commit or PR.
* Linting, SQL validation, and security checks.
* Deployment of infrastructure (e.g., Terraform apply) in a controlled and auditable way.

### 4. **Expand Unit & Integration Tests**

The current test suite verifies feature transformations. To improve robustness:

* Add integration tests to validate the DAG end-to-end.
* Include data quality assertions (e.g., null checks, value ranges).
* Use tools like `pytest-dag` or `great_expectations`.

### 5. **Scale Beyond Local: Use Cloud-Native Stack**

This project is designed for local development. In a production setting:

* PostgreSQL could be migrated to a managed service like AWS RDS.
* MinIO could be swapped with Amazon S3 or GCP Cloud Storage.
* Airflow could be deployed on Kubernetes or MWAA.
  Terraform modules could then provision all cloud components, not just the object store.

### 6. **Introduce Real-Time Triggers**

If decisioning needs to move closer to real-time:

* Replace batch DAGs with streaming tools (e.g., Kafka + Spark Structured Streaming).
* Integrate with APIs or messaging queues for live scoring.

---
