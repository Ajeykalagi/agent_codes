# from langchain_openai import ChatOpenAI
# from crewai import Agent, Task, Crew
# import subprocess
# import json

# # Initialize LLM
# llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)

# def classify_query(query):
#     prompt = f"""
#     You are a query classification assistant. Based on the query below, classify it into one of these categories:
    
#     1. Database: For queries related to logs, SQL issues, or database performance.
#     2. Confluence: For queries regarding installations, configuration, documentation, setup guides, or blueprint details.
#     3. ServiceNow: For queries about error messages, operational issues, or troubleshooting solutions.
    
#     For example:
#     - "What are the resources created for the blueprint name EMRServerless?" should be classified as Confluence.
#     - "Show me the logs for the last 24 hours" should be classified as Database.
#     - "Why am I getting an authentication error?" should be classified as ServiceNow.
    
#     Query: "{query}"
    
#     Respond with only the category name exactly as given (Database, Confluence, or ServiceNow).
#     """
    
#     llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
#     response = llm.invoke(prompt)
    
#     category = response.content.strip().lower() if hasattr(response, 'content') else str(response).strip().lower()
    
#     category_map = {"database": "Database", "confluence": "Confluence", "servicenow": "ServiceNow"}
    
#     return category_map.get(category, "Unknown")

# # Define agent scripts
# agent_scripts = {
#     "Database": "req_v9/agentic_main.py",
#     "Confluence": "req_v7/main.py",
#     "ServiceNow": "req_v8/main.py"
# }

# # Path to your virtual environment's Python interpreter
# VENV_PYTHON = r"D:\data\Check\cenv\Scripts\python.exe"  # Update this path if needed

# # Function to execute the appropriate agent
# def call_agent(agent, query):
#     if agent in agent_scripts:
#         try:
#             process = subprocess.run(
#                 [VENV_PYTHON, agent_scripts[agent], query], 
#                 capture_output=True, 
#                 text=True
#             )
#             return process.stdout.strip() or process.stderr.strip()
#         except Exception as e:
#             return f"Error executing {agent} agent: {str(e)}"
#     else:
#         return "Unknown agent category."


# # Define CrewAI Agents
# classify_agent = Agent(
#     role="Query Classifier",
#     goal="Classify the user query into one of the predefined categories.",
#     backstory="This agent specializes in identifying the right agent category for handling user queries.",
#     llm=llm,
#     verbose=True
# )

# execute_agent = Agent(
#     role="Query Executor",
#     goal="Execute the query using the correct agent and return the response.",
#     backstory="This agent runs the required subprocess based on the classified category.",
#     llm=llm,
#     verbose=True
# )

# # Define CrewAI Tasks
# classification_task = Task(
#     description="Classify the user query and return the category name.",
#     agent=classify_agent,
#     expected_output="One of: Database, Confluence, ServiceNow."
# )

# execution_task = Task(
#     description="Execute the appropriate agent and return the response.",
#     agent=execute_agent,
#     expected_output="Processed query response."
# )

# # Define Crew
# crew = Crew(
#     agents=[classify_agent, execute_agent],
#     tasks=[classification_task, execution_task],
#     verbose=True
# )


# if __name__ == "__main__":
#     user_query = input("Enter your query: ")
    
#     # Step 1: Classify Query
#     agent_category = classify_query(user_query)
    
#     if agent_category == "Unknown":
#         print("Error: Could not classify the query into a valid category.")
#     else:
#         print(f"Routing query to: {agent_category} agent\n")
        
#         # Step 2: Execute Agent Task
#         response = call_agent(agent_category, user_query)
        
#         print("Response:", response)


import os
import streamlit as st
import subprocess
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)

# Define agent scripts
agent_scripts = {
    "Database": "req_v9/agentic_main.py",
    "Confluence": "req_v7/main.py",
    "ServiceNow": "req_v8/main.py"
}

# Path to your virtual environment's Python interpreter
VENV_PYTHON = r"D:\data\Check\cenv\Scripts\python.exe"  # Update this path if needed

# Function to classify the query
def classify_query(query):
    prompt = f"""
    You are a query classification assistant. Classify the query into one of these categories:
    - Database: Queries about logs, SQL, or performance.
    - Confluence: Queries about installation, documentation, setup guides, or blueprint details.
    - ServiceNow: Queries about error messages, operational issues, or troubleshooting solutions.
    
    For example:
#     - "What are the resources created for the blueprint name EMRServerless?" should be classified as Confluence.
#     - "Show me the logs for the last 24 hours" should be classified as Database.
#     - "Why am I getting an authentication error?" should be classified as ServiceNow.
    Query: "{query}"
    Respond with only the category name: Database, Confluence, or ServiceNow.
    """
    
    response = llm.invoke(prompt)
    category = response.content.strip().lower() if hasattr(response, 'content') else str(response).strip().lower()
    category_map = {"database": "Database", "confluence": "Confluence", "servicenow": "ServiceNow"}
    return category_map.get(category, "Unknown")

# Function to execute the appropriate agent
def call_agent(agent, query):
    if agent in agent_scripts:
        try:
            process = subprocess.run(
                [VENV_PYTHON, agent_scripts[agent], query], 
                capture_output=True, 
                text=True
            )
            return process.stdout.strip() or process.stderr.strip()
        except Exception as e:
            return f"Error executing {agent} agent: {str(e)}"
    else:
        return "Unknown agent category."

# Streamlit UI
st.title("RAG-Based Query Classifier and Executor")
st.markdown("Enter your query below to classify and process it.")

query_input = st.text_area("Enter your query:")

if st.button("Process Query"):
    if query_input.strip():
        with st.spinner("Classifying query..."):
            category = classify_query(query_input)
            st.success(f"Query classified as: **{category}**")

        if category != "Unknown":
            with st.spinner(f"Executing {category} agent..."):
                response = call_agent(category, query_input)
                st.text_area("Response:", response, height=200)
        else:
            st.error("Could not classify the query into a valid category.")
    else:
        st.warning("Please enter a query before processing.")
