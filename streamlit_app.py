#pages/1 PDF_Upload
import streamlit as st
import openai
import os
import shutil
import atexit
from openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
import tempfile
from uuid import uuid4
import(‘pysqlite3’)
import sys
sys.modules[‘sqlite3’] = sys.modules.pop(‘pysqlite3’)

#Clean up when a session ends
def cleanup_chroma_directory():
    """Clean up all Chroma directories"""
    try:
        directories = [d for d in os.listdir('.') if d.startswith('Chroma_')]
        for directory in directories:
            shutil.rmtree(directory)
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Register cleanup function to run at exit
atexit.register(cleanup_chroma_directory)

def init_session_state():
    #Initialize session state variables
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        # Generate unique session ID
        st.session_state.session_id = str(uuid4())
    if 'chroma_directory' not in st.session_state:
        st.session_state.chroma_directory = None

#Load PDF file and create vectorstore
def load_db(file, file_name):
    
    # Clear previous QA chain when loading new file
    if 'qa_chain' in st.session_state:
        del st.session_state.qa_chain
    
    # Clean up previous Chroma directory if it exists
    if st.session_state.chroma_directory and os.path.exists(st.session_state.chroma_directory):
        shutil.rmtree(st.session_state.chroma_directory)
        
    # Create new collection name using session ID and file name
    collection_name = f"{st.session_state.session_id}_{file_name}"
    st.session_state.chroma_directory = f"./Chroma_{collection_name}"

    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Save uploaded file
        status_text.text("Saving uploaded file...")
        progress_bar.progress(10)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name
        
        # Load PDF
        status_text.text("Loading PDF...")
        progress_bar.progress(20)
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        # Split documents
        status_text.text("Processing document chunks...")
        progress_bar.progress(40)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)

        # Create embeddings
        status_text.text("Creating embeddings...")
        progress_bar.progress(60)
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

        # Create vector database
        status_text.text("Creating vector database...")
        progress_bar.progress(90)
        db = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=st.session_state.chroma_directory
        )
        
        # Add documents
        uuids = [str(uuid4()) for _ in range(len(docs))]
        db.add_documents(documents=docs, ids=uuids)
        
        # Cleanup
        os.unlink(temp_file_path)
        progress_bar.progress(100)
        status_text.text("Complete!")
        return db

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        raise e

def main():
    st.title("PDF Upload and Processing 📚")
    
    # Initialize session state
    init_session_state()
    
    # Add cleanup function to session state if not already added
    if 'cleanup_done' not in st.session_state:
        cleanup_chroma_directory()  # Clean up any leftover directories from previous sessions
        st.session_state.cleanup_done = True
        
    openai.api_key = st.text_input("Input your openai api")
    os.environ["OPENAI_API_KEY"]=str(openai.api_key)
    uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
    
    if uploaded_file is not None and (st.session_state.current_file is None or 
                                    uploaded_file.name != st.session_state.current_file.name):
        try:
            # First set the current file
            st.session_state.current_file = uploaded_file
            # Then pass both file and file name to load_db
            st.session_state.db = load_db(uploaded_file, uploaded_file.name)
            st.success("File successfully loaded!")
        except Exception as e:
            st.error(f"An error occurred while loading the file: {str(e)}")
    
    if st.session_state.current_file is not None:
        st.info(f"Currently loaded file: {st.session_state.current_file.name}")
        
        # Add a manual cleanup button if needed
        if st.button("Clear Current Session"):
            cleanup_chroma_directory()
            st.session_state.db = None
            st.session_state.current_file = None
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
