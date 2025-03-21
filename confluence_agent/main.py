import os
import sys
from rag_pipeline import process_query

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
    pdf_file = os.path.join(script_dir, "input_pdf_files", "sagemaker-user-guide.pdf")

    #print(f"Looking for PDF at: {pdf_file}")  # Debugging step

    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found at {pdf_file}. Please check the path.")
        sys.exit(1)

    if len(sys.argv) > 1:
        user_query = sys.argv[1]
    else:
        user_query = input("Enter the question: ")

    try:
        final_answer = process_query(pdf_file, user_query)
        print(f"\n {final_answer}")
    except Exception as e:
        print(f"Error processing query: {e}")
