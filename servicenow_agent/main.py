from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import json
import os
import sys

# Get the absolute path of the JSON file
json_file_path = os.path.join(os.path.dirname(__file__), "sagemaker_faq.json")

if not os.path.exists(json_file_path):
    print(f"⚠️ Error: Missing JSON file {json_file_path}. Please add it to the directory.")
    exit(1)

# Load JSON data
with open(json_file_path, "r") as f:
    faq_data = json.load(f)

llm = ChatOpenAI(model="gpt-4", temperature=0.2)

# Function to search FAQ JSON
def search_faq(question: str) -> str:
    """Searches the FAQ JSON for an answer."""
    for qa in faq_data["faq"]:
        if question.lower() in qa["question"].lower():
            return qa["response"]
    return None  # Return None if no matching response is found

# Agent 1: Response Generator
response_generator = Agent(
    role="Response Generator",
    goal="Find the best possible answer for the user's query using available data or generate a response using OpenAI.",
    backstory="A technical support agent trained on SageMaker Unified Studio, ready to assist users.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Agent 2: Response Verifier
response_verifier = Agent(
    role="Response Verifier",
    goal="Ensure the accuracy and relevance of the response before presenting it to the user.",
    backstory="A senior support engineer reviewing responses for correctness and clarity.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Task 1: Generate Response
generate_response_task = Task(
    description="Search the FAQ database for a response to the user's question. "
                "If a match is found, use it. Otherwise, generate a response using OpenAI.",
    agent=response_generator,
    expected_output="A clear and helpful response to the user's query.",
    inputs=["question"]
)

# Task 2: Verify and Improve Response
verify_response_task = Task(
    description="Review the generated response to ensure accuracy, clarity, and helpfulness. "
                "Refine the response if necessary before finalizing.",
    agent=response_verifier,
    expected_output="A verified and improved response, ensuring correctness and clarity.",
    inputs=["question", "generated_response"]  # ✅ Pass both user question and generated response
)

# Define the Crew (workflow)
support_bot_crew = Crew(
    agents=[response_generator, response_verifier],
    tasks=[generate_response_task, verify_response_task],
    verbose=True
)

# Function to get a response
def get_support_response(question):
    #print(f"User Question: {question}")

    # Step 1: Check if an answer exists in the JSON
    faq_answer = search_faq(question)

    if faq_answer:
        #print("Using FAQ database answer directly.")
        return faq_answer  # Return answer directly if found in JSON

    # Step 2: Otherwise, use AI-powered generation and verification
    result = support_bot_crew.kickoff(inputs={"question": question})
    return result



# Example Usage

if len(sys.argv) > 1:
    user_input = sys.argv[1]
else:
    user_input = input("Enter the question: ")
response = get_support_response(user_input)
print(f"Final Answer: {response}")
