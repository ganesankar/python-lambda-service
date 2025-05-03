import os
import pandas as pd
import boto3
from databricks import sql

from .handler import get_databricks_connection, update_delta_table_schema

def lambda_handler(event, context):
    # S3 configuration
    s3_bucket = os.environ.get('SOURCE_S3_BUCKET')
    s3_key = os.environ.get('SOURCE_S3_KEY')
    delta_table_name = os.environ.get('DELTA_TABLE_NAME')

    # Read CSV from S3
    s3_client = boto3.client('s3')
    csv_obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    df = pd.read_csv(csv_obj['Body'])

    # Get CSV columns
    csv_columns = list(df.columns)

    # Connect to Databricks
    connection = get_databricks_connection()
    cursor = connection.cursor()

    try:
        # Get existing Delta table columns
        cursor.execute(f'DESCRIBE TABLE {delta_table_name}')
        existing_columns = [row[0] for row in cursor.fetchall()]

        # Find missing columns
        missing_columns = [col for col in csv_columns if col not in existing_columns]

        # Update Delta table schema if needed
        if missing_columns:
            for col in missing_columns:
                update_delta_table_schema(
                    connection, 
                    delta_table_name, 
                    'add', 
                    col, 
                    'STRING'  # Default type, adjust as needed
                )

        # Append data to Delta table
        # Convert DataFrame to list of tuples for insertion
        data_to_insert = df.to_records(index=False).tolist()

        # Construct dynamic INSERT statement
        columns_str = ', '.join(csv_columns)
        placeholders = ', '.join(['?' for _ in csv_columns])
        insert_query = f'INSERT INTO {delta_table_name} ({columns_str}) VALUES ({placeholders})'
        
        cursor.executemany(insert_query, data_to_insert)
        connection.commit()

        return {
            'statusCode': 200,
            'body': f'Successfully processed {len(df)} records from {s3_key}'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error processing data: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()