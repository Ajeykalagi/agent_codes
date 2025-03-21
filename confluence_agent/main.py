from rag_pipeline import process_query

if __name__ == "__main__":
    pdf_file = "input_pdf_files/sagemaker-user-guide.pdf"
    user_query = input("Enter the Question: ")
    final_answer = process_query(pdf_file, user_query)
    print(final_answer)
