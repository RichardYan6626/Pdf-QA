import streamlit as st
import openai
import os
import shutil
from PyPDF2 import PdfReader
from openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch, Chroma
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
import tempfile
from uuid import uuid4

# Environment setup for LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"

def initialize_session_state():
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

def load_db(file):
    # Generate a unique collection name based on the file name
    collection_name = f"pdf_qa_{uuid4()}"
    
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name
    
    # Load documents using PyPDFLoader
    loader = PyPDFLoader(temp_file_path)
    documents = loader.load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)

    # Define embedding
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

    # Clear the persist directory if it exists
    persist_directory = "./Chroma"
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    # Create vector database from data
    db = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    # Add documents with unique IDs
    uuids = [str(uuid4()) for _ in range(len(docs))]
    db.add_documents(documents=docs, ids=uuids)
    
    # Clean up temporary file
    os.unlink(temp_file_path)
    
    return db

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
                    
                    # Display collection count
                    st.write("### Collection Count")
                    st.write(st.session_state.db._collection.count())
                    
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
