import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
from openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import tempfile
from uuid import uuid4

# Environment setup for LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = ""

def initialize_session_state():
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'document_count' not in st.session_state:
        st.session_state.document_count = 0

def load_db(file):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name
    
    try:
        # Load documents using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)

        # Define embedding
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

        # Create vector database using FAISS
        db = FAISS.from_documents(docs, embeddings)
        
        # Store the document count
        st.session_state.document_count = len(docs)
        
        return db
    
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

def main():
    st.title("PDF Question Answering System")
    
    # Initialize session state
    initialize_session_state()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
    
    # Check if a new file was uploaded
    if uploaded_file is not None and uploaded_file != st.session_state.current_file:
        try:
            # Initialize or load the vector database
            st.session_state.db = load_db(uploaded_file)
            st.session_state.current_file = uploaded_file
            st.success("File successfully loaded!")
        except Exception as e:
            st.error(f"An error occurred while loading the file: {str(e)}")
    
    if st.session_state.db is not None:
        try:
            # Initialize the ChatOpenAI model
            llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-4"
            )
            
            # Create the QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=st.session_state.db.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # Question input
            question = st.text_input("Ask a question about your PDF:")
            
            if question:
                with st.spinner("Generating answer..."):
                    # Get the answer
                    result = qa_chain({"query": question})
                    
                    # Display document count
                    st.write("### Document Count")
                    st.write(st.session_state.document_count)
                    
                    # Display the answer
                    st.write("### Answer:")
                    st.write(result["result"])
                    
                    # Display source documents
                    st.write("### Sources:")
                    for i, doc in enumerate(result["source_documents"]):
                        st.write(f"Source {i+1}:")
                        st.write(doc.page_content)
                        st.write("---")
                        
        except Exception as e:
            st.error(f"An error occurred during question answering: {str(e)}")

if __name__ == "__main__":
    main()
