# african_financial_markets
This a repository implementing a data pipeline of African Financial Market Data

## 1. Overview
The overall objective of this project is to provide data to equity analyst and investment professionals with a focus on African Capital Markets. This project implements an ELT pipeline by scraping data using scrapy and uploads it to Google Cloud Platform where analyst can perform high level transformation and analyst in Big Query using dbt and visualization using Tableau. 

The data is scraped from ![african-markets](https://african-markets.com/)

### 1.1 Motivation
This project is motivated by my experience as a treasury analyst which involved analyzing investment instruments on the African markets where treasury reserved could be invested for high Return on Investment with low risk. In addition to being a freelancer on Upwork I was was assigned a Geek as a Research/investment Analyst which neccistiated access to financial data behind paywalls. Below is a screen shot of the clients request. 

![image](https://github.com/amaboh/african_financial_markets/assets/85511496/12721e8a-cd49-4335-b92b-a4579c5713b8)

## 2. Project Overview 
This project demonstrates the implementation of highly scalable and containarized web crawler using scrapy to scrape a data at a regualr interval and upload the data to Google Cloud. The scraped data is first laoded to Postgres which is then queried and upload to Google Cloud Storage and subsequently to Big Query. 

## Architecture

![image](https://github.com/amaboh/african_financial_markets/assets/85511496/5cb48d62-e1ea-4ba1-82e9-da470a403b10)

### 2.1 Tech stack 
1. Terraform: Main purpose to provision the cloud infrastructure with various resources needed, and in our case is Google Cloud storag and BigQuery. We could have also provisioned Cloud Composer instead of using Airflow, but AIrflow is better from a cost perspective. 
2. Scrapy: This is used to scrape the website and manage scraping process
3. Airflow: This is used to orchestrate the workflow from data begining to end i.e from scraping to loading data to BigQuery. Google alternative is Cloud Composer. 
4. Docker: This is used to containerized this data pipeline and ensure portability and consistency.
5. PGAdmin: Used to manage the database in Postgres.
6. Google Cloud Resources:
6.1 Google Cloud Storage: Google's immutable object storage store for unstructured data
6.2 BigQuery: Google's Cloud data warehouse

##  Usage Instructions
### 1. Create Project Directory & Git Clone
- In your terminal $ mkdir African_Markets_data
- $ cd African_Markets_data
- $ git clone git@github.com:amaboh/african_financial_markets.git
- cd market_data

1.1 Project Structure 
`African_Markets_data/
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
`

### 2. Provision Cloud Resources with Terraform

#### 2.1 Creating Cloud Project and Access Key
##### 2.1.1 Go to Google Cloud Console and create a New Project in Google Cloud 
##### 2.1.2 Go to IAM and choose Service Keys to create a Service Account Key and grant Cloud Storage Admin and Big Query Admin priviledges
##### 2.1.3 Move downloaded keys to terraform/keys/ and rename downloaded keys to gcp-creds.json (this path has been included in the .gitignore file already) 

#### 2.2 Provisioning resources with Terraform
#### 2.2.1 Go to terraform/variables.tf directory and copy the Project ID from the console copy the project ID and replace "african-inices-420410" and also check your region and replace "europe-west2" (choose a region closer to you). 
example of terraform variable from this project
`variable "project" {
    description = "ptoject"
  default = "african-indices-420410"
}`
#### 2.2.1 Provisioning with Terraform
- $ cd terraform/
- $ terraform init
- $ terraform plan
- $ terraform apply
- choose yes and proceed to check resources(Cloud Storage GCS and Biquery) provisioned in console

### 3 Running Pipeline Locally with Docker
- Referencing Google service keys on local machine to container by making this adjustments in the docker-compose.yaml file
- `x-airflow-common: &airflow-common
  build: .
  environment: &airflow-common-env
      GOOGLE_APPLICATIONS_CREDENTIALS: /opt/airflow/keys/gcp-creds.json  # check this corresponds 
  volumes:
      - /Volumes/AM/Desktop/Projects/african_financial_markets/market_data/terraform/keys:/opt/airflow/keys # copy the full path where your keys are located on your machine to this path on the left:/opt
  `
  - $ docker-compose build
  - $ docker-compose up -d

### 4. Orchestrating Pipeline with Airflow
#### 4.1 Configure Access connections from airflow to Postgres Database
- From your web browers go to localhost:8080; enter user: airflow password: airflow
- Go to Admins > Connections > + (add new record)
- enter the details in the pictures below respectively

`{
    "Connection Id": "ingest_db_conn_id",
    "Connection Type": "Postgres",
    "Host": "postgres",
    "Database": "ingest_db",
    "Login": "airflow",
    "Password": "airflow",
}
`
![image](https://github.com/amaboh/african_financial_markets/assets/85511496/5e56c1ab-9c33-4bc2-ae42-e5e840443bc2)

 #### 4.2 Configure Access for airflow to Google Service Account Keys 
- Go to Admins > Connections > + (add new record)
- enter the details in the pictures below respectively
 `{Connection Id *	: google_cloud_default
 Project Id	: african-indices-420410
 Keyfile Path	: /opt/airflow/keys/gcp-creds.json}`

![image](https://github.com/amaboh/african_financial_markets/assets/85511496/fa463cee-c0e3-4b2c-ada4-ec09ef824976)

### 5 Trigger DAG 
- From the Airflow UI trigger the DAG with the Play Button and haved all processes completed successfully as seen below
  ![image](https://github.com/amaboh/african_financial_markets/assets/85511496/174d874a-f11a-4579-83a7-cd75ba7ca24e)

![image](https://github.com/amaboh/african_financial_markets/assets/85511496/97c5887d-8c93-49d8-90de-2e3486bd73b4)

### Tabels in BigQuery 

![image](https://github.com/amaboh/african_financial_markets/assets/85511496/83d3a424-0c09-46af-ab3e-e2d7f9112e00)

### SQL Query in BigQuery 
![image](https://github.com/amaboh/african_financial_markets/assets/85511496/cebefa13-d422-4753-bebd-fa4241bff6ae)



	
