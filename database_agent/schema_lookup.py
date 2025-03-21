from config import get_snowflake_connection

def get_available_columns(table_name, creds):
    try:
        conn = get_snowflake_connection(creds)
        cur = conn.cursor()
        query = f"""
        SELECT COLUMN_NAME FROM {creds["database"]}.INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = '{creds["schema"]}' AND TABLE_NAME = '{table_name}'
        """
        cur.execute(query)
        return [row[0] for row in cur.fetchall()] or ["No columns found"]

    except Exception as e:
        return [f"Error fetching columns: {str(e)}"]
from config import get_snowflake_connection

def get_available_columns(table_name, creds):
    try:
        conn = get_snowflake_connection(creds)
        cur = conn.cursor()
        query = f"""
        SELECT COLUMN_NAME FROM {creds["database"]}.INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = '{creds["schema"]}' AND TABLE_NAME = '{table_name}'
        """
        cur.execute(query)
        return [row[0] for row in cur.fetchall()] or ["No columns found"]

    except Exception as e:
        return [f"Error fetching columns: {str(e)}"]
