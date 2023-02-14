import pandas as pd
import mysql.connector
from google.cloud import bigquery
from google.cloud import storage

# Set up connection to Google Cloud Storage
client = storage.Client()
bucket = client.get_bucket('your-bucket-name')

# Load data from CSV file in GCS into a pandas dataframe
blob = bucket.blob('your-file.csv')
data = blob.download_as_string()
df = pd.read_csv(io.BytesIO(data))

# Transform data (if needed)
# For example, you could concatenate first_name and last_name into a new column called full_name:
df['full_name'] = df['first_name'] + ' ' + df['last_name']

# Set up connection to GCP Cloud SQL
cnx = mysql.connector.connect(user='your-db-user', password='your-db-password',
                              host='your-db-host', database='your-db-name')

# Load data into a pandas dataframe
df = pd.read_sql('SELECT * FROM customers', con=cnx)

# Set up connection to BigQuery
client = bigquery.Client()
table_ref = client.dataset('your_dataset_name').table('your_table_name')

# Create job configuration and load data into BigQuery
job_config = bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
job_config.source_format = bigquery.SourceFormat.CSV
job_config.schema = [
    bigquery.SchemaField('id', 'INTEGER'),
    bigquery.SchemaField('first_name', 'STRING'),
    bigquery.SchemaField('last_name', 'STRING'),
    bigquery.SchemaField('email', 'STRING'),
    bigquery.SchemaField('gender', 'STRING'),
    bigquery.SchemaField('ip_address', 'STRING'),
    bigquery.SchemaField('full_name', 'STRING')
]
job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
job.result()  # Wait for job to complete

# Close connection to GCP Cloud SQL
cnx.close()
