import json
import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import StrOutputParser
from schema_lookup import get_available_columns
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# ✅ Function to determine which JSON file to use
def get_json_filename(agent_database_connection_id):
    """
    Returns the appropriate JSON filename based on the agent_database_connection_id.
    """
    return f"v{agent_database_connection_id}.json"

# ✅ Function to fetch stored query examples from the correct JSON file
def get_examples_text(agent_database_connection_id):
    json_file = get_json_filename(agent_database_connection_id)

    if not os.path.exists(json_file):
        return "[]"  

    with open(json_file, "r") as file:
        try:
            examples = json.load(file)
            return "\n".join([f"Q: {ex['question']}\nSQL: {ex['query']}" for ex in examples])
        except json.JSONDecodeError:
            return "[]"

# ✅ Function to generate SQL dynamically
def generate_sql_query(user_question, table_name, creds, agent_database_connection_id):
    """
    Generate an SQL query using LLM.

    Parameters:
    - user_question (str): Natural language query from the user.
    - table_name (str): The table to query.
    - creds (dict): Dictionary containing Snowflake connection details.
    - agent_database_connection_id (int): ID of the database connection.

    Returns:
    - str: Generated SQL query.
    """
    
    # ✅ Fetch column details dynamically for the selected table
    columns_info = get_available_columns(table_name, creds)
    columns_text = ", ".join(columns_info) if columns_info else "No columns found"
    examples_text = get_examples_text(agent_database_connection_id)

    # ✅ Define SQL prompt template
    SQL_PROMPT_TEMPLATE = f"""
    You are an AI SQL assistant for Snowflake. Your task is to generate **accurate SQL queries**.

    📌 **Selected Table:** {table_name}
    📌 **Available Columns:**
    {columns_text}

    📌 **Example Queries:**
    {examples_text}

    🎯 **User Question:** {user_question}

    ⚠️ **Guidelines:**
    - Use correct column names.
    - Apply **JOINs** where necessary.
    - Ensure **GROUP BY** for aggregations.
    - Follow **Snowflake SQL syntax**.
    - If the user asks for column names, use:
      ❌ `SELECT * FROM table LIMIT 0;` (Incorrect)
      ✅ `SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';` (Correct)

    ➡️ **Return ONLY the SQL query (no explanations).**
    """

    # ✅ Generate SQL using GPT-4 LLM
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(SQL_PROMPT_TEMPLATE)
    sql_chain = prompt | llm | StrOutputParser()
    sql_query = sql_chain.invoke({})

    # ✅ Check if the response is a valid SQL query
    if not sql_query.strip().lower().startswith("select") and "from" not in sql_query.lower():
        return "⚠️ I could not generate a valid SQL query. Please rephrase your question."

    return sql_query

# ✅ Function to save query examples in the correct JSON file
def save_prompt_example(user_question, sql_query, agent_database_connection_id):
    """
    Saves the user's natural language query and corresponding SQL query.

    Parameters:
    - user_question (str): User's natural language input.
    - sql_query (str): Generated SQL query.
    - agent_database_connection_id (int): ID to determine which JSON file to use.

    Returns:
    - None
    """
    json_file = get_json_filename(agent_database_connection_id)

    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            json.dump([], file)

    with open(json_file, "r") as file:
        try:
            examples = json.load(file)
        except json.JSONDecodeError:
            examples = []

    examples.append({"question": user_question, "query": sql_query})

    with open(json_file, "w") as file:
        json.dump(examples, file, indent=4)

    print(f"\n✅ Query saved successfully in {json_file}!")
