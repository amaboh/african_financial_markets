locals {
  data_lake_bucket = "african_market_data_lake"
}

variable "credentials" {
  description = " my google credentials"
  default     = "./keys/gcp-creds.json"
}

variable "project" {
    description = "ptojrct"
  default = "african-indices-420410"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "europe-west2"
  type        = string
}

variable "storage_class" {
  description = "Storage class type for the bucket"
  default     = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type        = string
  default     = "market_indice"
}
