from config import get_snowflake_connection
import pandas as pd

def execute_query(query, creds):
    try:
        conn = get_snowflake_connection(creds)
        cursor = conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)

    except Exception as e:
        return f"❌ Snowflake Connection Error: {e}"
