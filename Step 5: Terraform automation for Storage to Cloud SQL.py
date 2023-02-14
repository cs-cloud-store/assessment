# Configure provider
provider "google" {
  project = "hale-brook-377621"
  region  = "your-region"
  zone    = "your-zone"
}

# Configure storage bucket
resource "google_storage_bucket" "data_bucket" {
  name = "your-bucket-name"
}

# Configure Cloud SQL instance
resource "google_sql_database_instance" "db_instance" {
  name             = "your-instance-name"
  region           = "your-region"
  database_version = "MYSQL_5_7"
  settings {
    tier = "db-f1-micro"
  }
}

# Configure Cloud SQL database and user
resource "google_sql_database" "db" {
  name     = "your-db-name"
  instance = google_sql_database_instance.db_instance.name
}

resource "google_sql_user" "db_user" {
  name     = "your-db-user"
  password = "your-db-password"
  instance = google_sql_database_instance.db_instance.name
  host     = "%"
}

# Configure Cloud Function to run ETL code
resource "google_cloudfunctions_function" "etl_function" {
  name        = "your-function-name"
  description = "ETL function that ingests, transforms, and loads data from GCS to Cloud SQL"

  source_archive_bucket = google_storage_bucket.data_bucket.name
  source_archive_object = "etl_function.zip"

  entry_point = "main"

  runtime = "python37"

  environment_variables = {
    SQL_USER     = google_sql_user.db_user.name
    SQL_PASSWORD = google_sql_user.db_user.password
    SQL_HOST     = google_sql_database_instance.db_instance.ip_address
    SQL_DATABASE = google_sql_database.db.name
    GCS_BUCKET   = google_storage_bucket.data_bucket.name
  }

  timeout    = "180s"
  available_memory_mb = 256

  trigger_http = true
}

# Configure Cloud Scheduler job to run Cloud Function daily
resource "google_cloud_scheduler_job" "etl_job" {
  name        = "your-job-name"
  description = "Schedule ETL function to run daily at 7AM"

  schedule = "0 7 * * *"

  target_type = "google_cloudfunctions_function"
  target_http_method = "POST"
  target_uri = google_cloudfunctions_function.etl_function.https_trigger_url
}
