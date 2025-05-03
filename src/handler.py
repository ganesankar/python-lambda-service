import json
import os
from databricks.sql.client import Connection, Cursor

def get_databricks_connection():
    """
    Establish a connection to Databricks using environment variables.
    
    Returns:
        Connection: A Databricks SQL connection
    """
    try:
        connection = Connection(
            server_hostname=os.environ.get('DATABRICKS_HOST'),
            http_path=os.environ.get('DATABRICKS_HTTP_PATH'),
            access_token=os.environ.get('DATABRICKS_TOKEN')
        )
        return connection
    except Exception as e:
        print(f"Error connecting to Databricks: {e}")
        raise

def update_delta_table_schema(event, context):
    """
    Update the schema of a delta table in Databricks.
    
    Args:
        event (dict): Lambda event containing table schema details
        context (object): Lambda context
    
    Returns:
        dict: Response with status and message
    """
    try:
        # Validate input
        if not event or 'table_name' not in event or 'schema_changes' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid input. Requires table_name and schema_changes'
                })
            }
        
        table_name = event['table_name']
        schema_changes = event['schema_changes']
        
        # Establish Databricks connection
        with get_databricks_connection() as connection:
            with connection.cursor() as cursor:
                # Construct ALTER TABLE statement
                alter_statements = []
                for change in schema_changes:
                    operation = change.get('operation')
                    column_name = change.get('column_name')
                    column_type = change.get('column_type', '')
                    
                    if operation == 'add':
                        alter_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    elif operation == 'modify':
                        alter_statements.append(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {column_type}")
                    elif operation == 'drop':
                        alter_statements.append(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                
                # Execute ALTER TABLE statements
                for statement in alter_statements:
                    cursor.execute(statement)
                
                # Commit changes
                connection.commit()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully updated schema for table {table_name}',
                'changes': schema_changes
            })
        }
    
    except Exception as e:
        print(f"Error updating delta table schema: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

