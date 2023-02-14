import pandas as pd
import mysql.connector
from google.cloud import storage

# Set up connection to Google Cloud Storage
client = storage.Client()
bucket = client.get_bucket('your-bucket-name')

# Load data from CSV file in GCS into a pandas dataframe
blob = bucket.blob('your-file.csv')
data = blob.download_as_string()
df = pd.read_csv(io.BytesIO(data))

# Transform data
# For example, you could concatenate first_name and last_name into a new column called full_name:
df['full_name'] = df['first_name'] + ' ' + df['last_name']

# Set up connection to MySQL Cloud SQL
cnx = mysql.connector.connect(user='your-db-user', password='your-db-password',
                              host='your-db-host', database='your-db-name')

# Create cursor and table if not exists
cursor = cnx.cursor()
create_table_query = '''
    CREATE TABLE IF NOT EXISTS customers (
        id INT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(255),
        gender VARCHAR(10),
        ip_address VARCHAR(50),
        full_name VARCHAR(100)
    )
'''
cursor.execute(create_table_query)
cnx.commit()

# Load data into MySQL Cloud SQL
for index, row in df.iterrows():
    insert_query = '''
        INSERT INTO customers (id, first_name, last_name, email, gender, ip_address, full_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    values = (row['id'], row['first_name'], row['last_name'], row['email'], row['gender'], row['ip_address'], row['full_name'])
    cursor.execute(insert_query, values)
    cnx.commit()

# Close cursor and connection
cursor.close()
cnx.close()
