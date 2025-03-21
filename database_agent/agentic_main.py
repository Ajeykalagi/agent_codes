from crewai import Agent, Task, Crew
from query_generator import generate_sql_query, save_prompt_example
from query_executor import execute_query
from config import get_snowflake_credentials, get_database_table
import sys

# CrewAI Agents
query_generator_agent = Agent(
    name="Query Generator",
    role="AI SQL Assistant",
    goal="Generate SQL queries.",
    backstory="An advanced AI designed to convert natural language questions into precise SQL queries for Snowflake databases."
)

query_validator_agent = Agent(
    name="Query Validator",
    role="SQL Validator",
    goal="Validate SQL queries.",
    backstory="A specialized agent that ensures SQL queries are correctly formatted and free of syntax errors before execution."
)

query_executor_agent = Agent(
    name="Query Executor",
    role="Database Executor",
    goal="Execute SQL queries.",
    backstory="An AI-powered agent that securely connects to Snowflake databases and executes validated SQL queries."
)

query_saver_agent = Agent(
    name="Query Saver",
    role="Query Storage Manager",
    goal="Save queries.",
    backstory="Responsible for storing frequently used SQL queries for future reference and quick retrieval."
)

# CrewAI Tasks
query_task = Task(
    description="Generate a SQL query based on user's natural language request.",
    agent=query_generator_agent,
    run=lambda query, table, creds: generate_sql_query(query, table, creds),
    expected_output="A valid SQL query string."
)

validation_task = Task(
    description="Validate the SQL query before execution.",
    agent=query_validator_agent,
    run=lambda sql: sql if sql.strip().endswith(";") else "⚠️ Missing semicolon",
    expected_output="The validated SQL query or an error message if invalid."
)

execution_task = Task(
    description="Execute a validated SQL query on Snowflake.",
    agent=query_executor_agent,
    run=lambda sql, creds: execute_query(sql, creds),
    expected_output="The result of the executed SQL query."
)

query_saving_task = Task(
    description="Save generated SQL queries for future use.",
    agent=query_saver_agent,
    run=lambda query, sql: save_prompt_example(query, sql),
    expected_output="Confirmation that the query has been saved."
)

# Crew Workflow
crew = Crew(
    agents=[query_generator_agent, query_validator_agent, query_executor_agent, query_saver_agent],
    tasks=[query_task, validation_task, execution_task, query_saving_task]
)

def main():
    print("\n Welcome to AI SQL Chatbot (Agentic Version) \n")

    #agent_id = input("Enter AGENTID: ").strip()
    agent_id =1
    # ✅ Fetch connection credentials from Snowflake table
    creds = get_snowflake_credentials(agent_id)
    if not creds:
        print(" Failed to retrieve database credentials.")
        return

    # ✅ Fetch table details using the retrieved AGENT_DATABASE_CONNECTION_ID
    table_details = get_database_table(creds["agent_database_connection_id"])
    if not table_details:
        print("Failed to retrieve table details.")
        return

    creds["database"], creds["schema"], table_name = table_details["database"], table_details["schema"], table_details["table"]

    #while True:
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = input("Enter the question: ")
    #user_input = input("\nEnter your query: ").strip()
    sql_query = generate_sql_query(user_input, table_name, creds, agent_id)

    print("\n **Generated SQL Query:**")
    print(sql_query)

    #if input("\n Execute this query? (yes/no): ").strip().lower() == "yes":
    result = execute_query(sql_query, creds)
    print("\n**Query Execution Result:**")
    print(result)

        # if input("\n ave this query? (yes/no): ").strip().lower() == "yes":
        #     save_prompt_example(user_input, sql_query, agent_id)

        # if input("\n Enter another query? (yes/no): ").strip().lower() != "yes":
        #     break

if __name__ == "__main__":
    main()
