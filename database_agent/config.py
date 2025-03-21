import snowflake.connector

# ✅ Manually provided credentials to access AGENT_DB and AGENT_SCHEMA
AGENT_DB_CREDENTIALS = {
    "user": "Check",  # 🔹 Replace with actual Snowflake user
    "password": "Check@123456789",  # 🔹 Replace with actual password
    "account":"YEIREGF-MRB21264",  # 🔹 Replace with your Snowflake account identifier
    "warehouse": "check_wh",  # 🔹 Warehouse for agent_db access
    "database": "AGENT_DB",  # 🔹 Database containing connection details
    "schema": "AGENT_SCHEMA"  # 🔹 Schema containing connection details
}

# ✅ Function to fetch credentials dynamically based on AGENTID
def get_snowflake_credentials(agent_id):
    """
    Fetch Snowflake credentials using AGENTID in a single JOIN query.

    Parameters:
    - agent_id (int): The agent's ID.

    Returns:
    - dict: Dictionary containing Snowflake connection details (or None if not found).
    """
    try:
        conn = snowflake.connector.connect(**AGENT_DB_CREDENTIALS)
        cur = conn.cursor()

        # 🔹 Optimized Query Using JOINs
        query = f"""
        SELECT 
            adc.username, 
            adc.password, 
            adc.account,
            adc.warehouse,
            adc.role,
            adc.agent_database_connection_id,
            adt.database_name,
            adt.schema_name,
            adt.table_name
        FROM AGENT_DB.AGENT_SCHEMA.AGENT_DATABASE_CONNECTION adc
        JOIN AGENT_DB.AGENT_SCHEMA.AGENT_DATA_SOURCE ads ON adc.agent_data_source_id = ads.agent_data_source_id
        JOIN AGENT_DB.AGENT_SCHEMA.AGENTS a ON ads.AgentID = a.AgentId
        JOIN AGENT_DB.AGENT_SCHEMA.AGENT_DATABASE_TABLE adt ON adc.agent_database_connection_id = adt.agent_database_connection_id
        WHERE a.AgentId = {agent_id};
        """

        cur.execute(query)
        row = cur.fetchone()

        if not row:
            print("⚠️ No credentials found for the given AGENTID.")
            return None

        # ✅ Extract values from the result
        username, password, account, warehouse, role, agent_database_connection_id, database_name, schema_name, table_name = row

        return {
            "account": account,
            "username": username,
            "password": password,
            "warehouse": warehouse,
            "role": role,
            "agent_database_connection_id": agent_database_connection_id,
            "database": database_name,
            "schema": schema_name,
            "table": table_name
        }

    except Exception as e:
        print(f"❌ Error fetching credentials: {e}")
        return None

# ✅ Function to fetch database, schema, and table dynamically
def get_database_table(agent_database_connection_id):
    """
    Fetch database, schema, and table details from AGENT_DATABASE_TABLE.

    Parameters:
    - agent_database_connection_id (int): ID of the database connection.

    Returns:
    - dict: Dictionary containing database, schema, and table name (or None if not found).
    """
    try:
        conn = snowflake.connector.connect(**AGENT_DB_CREDENTIALS)
        cur = conn.cursor()

        query = f"""
        SELECT DATABASE_NAME, SCHEMA_NAME, TABLE_NAME
        FROM AGENT_DATABASE_TABLE
        WHERE AGENT_DATABASE_CONNECTION_ID = {agent_database_connection_id}
        """
        cur.execute(query)
        row = cur.fetchone()
        
        if row:
            database, schema, table = row
            return {"database": database, "schema": schema, "table": table}
        else:
            print("⚠️ No table found for the given AGENTID.")
            return None

    except Exception as e:
        print(f"❌ Error fetching table details: {e}")
        return None

# ✅ Function to establish a dynamic Snowflake connection
def get_snowflake_connection(creds):
    try:
        return snowflake.connector.connect(
            user=creds["username"],
            password=creds["password"],
            account=creds["account"],
            warehouse=creds["warehouse"],
            database=creds["database"],
            schema=creds["schema"]
        )
    except Exception as e:
        print(f"❌ Snowflake Connection Error: {e}")
        return None
