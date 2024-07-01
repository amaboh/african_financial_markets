# African Financial Markets
This repository implements a data pipeline for African Financial Market data.

## 1. Overview
The objective of this project is to provide data to equity analysts and investment professionals focusing on African Capital Markets. This project implements an ELT pipeline by scraping data using Scrapy and uploading it to Google Cloud Platform. Analysts can then perform high-level transformations and analysis in BigQuery using dbt and visualize the data using Tableau.

The data is scraped from [african-markets](https://african-markets.com/).

### 1.1 Motivation
This project is motivated by my experience as a treasury analyst, which involved analyzing investment instruments on the African markets where treasury reserves could be invested for high ROI with low risk. Additionally, as a freelancer on Upwork, I was assigned to a gig as a Research/Investment Analyst, which necessitated access to financial data behind paywalls.

## 2. Project Overview 
This project demonstrates the implementation of a highly scalable and containerized web crawler using Scrapy to scrape data at regular intervals and upload the data to Google Cloud. The scraped data is first loaded into PostgreSQL, then queried and uploaded to Google Cloud Storage, and subsequently to BigQuery.

## Architecture

![Architecture Diagram](https://github.com/amaboh/african_financial_markets/assets/85511496/5cb48d62-e1ea-4ba1-82e9-da470a403b10)

### 2.1 Tech Stack 
1. **Terraform**: Used to provision the cloud infrastructure, specifically Google Cloud Storage and BigQuery. Cloud Composer could also be provisioned instead of using Airflow, but Airflow is more cost-effective.
2. **Scrapy**: Used to scrape the website and manage the scraping process.
3. **Airflow**: Orchestrates the workflow from data collection to loading data into BigQuery. The Google alternative is Cloud Composer.
4. **Docker**: Containerizes the data pipeline to ensure portability and consistency.
5. **PGAdmin**: Manages the PostgreSQL database.
6. **Google Cloud Resources**:
    - **Google Cloud Storage**: Google's immutable object storage for unstructured data.
    - **BigQuery**: Google's cloud data warehouse.

## Usage Instructions

### 1. Create Project Directory & Clone Repository
```bash
mkdir African_Markets_data
cd African_Markets_data
git clone git@github.com:amaboh/african_financial_markets.git
cd african_financial_markets
```

### 1.1 Project Structure 
```
African_Markets_data/
|-- airflow/
|   |-- dags/
|   |   |-- __init__.py
|   |   |-- market_data_dag.py
|   |   |-- market_data/
|   |       |-- __init__.py
|   |       |-- items.py
|   |       |-- pipelines.py
|   |       |-- settings.py
|   |       |-- middlewares.py
|   |       |-- extract_to_json.py  # Script for extracting data to JSON
|   |       |-- spiders/
|   |           |-- __init__.py
|   |           |-- companyspider.py
|   |           |-- marketspider.py
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- docker-compose.yml
|-- db/
|   |-- Dockerfile
|   |-- custom-entrypoint.sh
|   |-- jobs.sql
|-- terraform/
|   |-- main.tf
|   |-- variables.tf
|   |-- keys/
|       |-- gcp-creds.json
```

### 2. Provision Cloud Resources with Terraform

#### 2.1 Creating Cloud Project and Access Key
1. Go to Google Cloud Console and create a New Project.
2. Go to IAM and create a Service Account Key with Cloud Storage Admin and BigQuery Admin privileges.
3. Move the downloaded key to `terraform/keys/` and rename it to `gcp-creds.json` (this path is included in the `.gitignore` file).

#### 2.2 Provisioning Resources with Terraform
1. Go to `terraform/variables.tf`, copy the Project ID from the console, replace "african-indices-420410", and update your region.
```hcl
variable "project" {
  description = "project"
  default     = "african-indices-420410"
}
```
2. Provision resources:
```bash
cd terraform/
terraform init
terraform plan
terraform apply
```
Choose yes and verify resources (Cloud Storage GCS and BigQuery) in the console.

### 3. Running Pipeline Locally with Docker
1. Adjust the docker-compose.yaml file to reference Google service keys on your local machine:
```yaml
x-airflow-common: &airflow-common
  build: .
  environment: &airflow-common-env
    GOOGLE_APPLICATIONS_CREDENTIALS: /opt/airflow/keys/gcp-creds.json  # Ensure this path is correct
  volumes:
    - /full/path/to/terraform/keys:/opt/airflow/keys  # Replace with the full path on your machine
```
2. Build and run the Docker containers:
```bash
docker-compose build
docker-compose up -d
```

### 4. Orchestrating Pipeline with Airflow

#### 4.1 Configure Access Connections from Airflow to Postgres
1. Go to `localhost:8080` in your web browser; use `user: airflow` and `password: airflow`.
2. Go to Admin > Connections > + (add new record) and enter the details:
```json
{
  "Connection Id": "ingest_db_conn_id",
  "Connection Type": "Postgres",
  "Host": "postgres",
  "Database": "ingest_db",
  "Login": "airflow",
  "Password": "airflow"
}
```
![Postgres Connection](https://github.com/amaboh/african_financial_markets/assets/85511496/5e56c1ab-9c33-4bc2-ae42-e5e840443bc2)

#### 4.2 Configure Access for Airflow to Google Service Account Keys 
1. Go to Admin > Connections > + (add new record) and enter the details:
```json
{
  "Connection Id": "google_cloud_default",
  "Project Id": "african-indices-420410",
  "Keyfile Path": "/opt/airflow/keys/gcp-creds.json"
}
```
![Google Cloud Connection](https://github.com/amaboh/african_financial_markets/assets/85511496/fa463cee-c0e3-4b2c-ada4-ec09ef824976)

### 5. Trigger DAG 
1. From the Airflow UI, trigger the DAG with the Play Button and ensure all processes complete successfully.

![Airflow DAG Run](https://github.com/amaboh/african_financial_markets/assets/85511496/174d874a-f11a-4579-83a7-cd75ba7ca24e)

![Airflow DAG Success](https://github.com/amaboh/african_financial_markets/assets/85511496/97c5887d-8c93-49d8-90de-2e3486bd73b4)

### Tables in BigQuery 

![BigQuery Tables](https://github.com/amaboh/african_financial_markets/assets/85511496/83d3a424-0c09-46af-ab3e-e2d7f9112e00)

### SQL Query in BigQuery 
![BigQuery SQL](https://github.com/amaboh/african_financial_markets/assets/85511496/cebefa13-d422-4753-bebd-fa4241bff6ae)

