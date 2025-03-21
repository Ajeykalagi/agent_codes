import os
import faiss  
import numpy as np
from crewai import Agent
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Initialize LLM and Embeddings
llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
embedding = OpenAIEmbeddings()

# Define embedding folder path
embedding_folder_path = os.path.join(os.path.dirname(__file__), "embedding_file")

# Ensure the folder exists
if not os.path.isdir(embedding_folder_path):
    print(f" Error: Missing folder {embedding_folder_path}. Please create it.")
    exit(1)

class RAGProcessingAgent(Agent):
    def __init__(self):
        """Initialize the agent"""
        super().__init__(
            role="Main RAG Agent",
            goal="Extract PDFs, generate embeddings, retrieve context, and return relevant text.",
            backstory="A knowledge-processing AI that handles document ingestion and Q&A.",
            verbose=True,
        )

    def ingest_and_embed(self, pdf_path):
        """Extracts text from PDF, generates embeddings, and saves to FAISS index file"""
        pdf_filename = os.path.basename(pdf_path)
        faiss_index_file = os.path.join(embedding_folder_path, pdf_filename.replace(".pdf", ".faiss"))

        if os.path.exists(faiss_index_file):
            # ✅ Load FAISS index from file
            #print(f" Loading FAISS index from {faiss_index_file}...")
            vector_store = FAISS.load_local(faiss_index_file, embedding, allow_dangerous_deserialization=True)
        else:
            # Process and store embeddings
            print(f"Processing and embedding PDF: {pdf_filename}...")
            loader = PyMuPDFLoader(pdf_path)
            docs = loader.load()
            vector_store = FAISS.from_documents(docs, embedding)

            # ✅ Save FAISS index properly
            vector_store.save_local(faiss_index_file)
            print(f"Saved FAISS index to {faiss_index_file}")

        return vector_store

    def retrieve_and_generate(self, pdf_path, query):
        """Retrieves relevant document section and generates a response."""
        vector_store = self.ingest_and_embed(pdf_path)  # Load FAISS index
        retriever = vector_store.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(query)

        retrieved_text = retrieved_docs[0].page_content if retrieved_docs else "No relevant information found in the document."

        # ✅ Define Chain
        prompt_template = """Given the following document context, answer the user query:
        Context: {context}
        User Query: {question}
        Provide a concise and informative response."""

        prompt = ChatPromptTemplate.from_template(prompt_template)
        sql_chain = prompt | llm | StrOutputParser()
        
        # ✅ Invoke Chain
        final_response = sql_chain.invoke({"context": retrieved_text, "question": query})

        return final_response
