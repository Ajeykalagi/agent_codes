from agents import RAGProcessingAgent

def process_query(pdf_path, query):
    # Initialize agent
    rag_agent = RAGProcessingAgent()

    # Retrieve and generate response using the chain
    response = rag_agent.retrieve_and_generate(pdf_path, query)
    
    return response
