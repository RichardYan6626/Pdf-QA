import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
from openai import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch, Chroma
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
#from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
import tempfile

"""
1. Enable persist for handling multiple pdf files
2. unable to handle markdown features
3. Select chain type
4. Select chunk_size and chunk_overlap
"""


#Logic for ingesting PDF files
def load_db(file):
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

    # Create vector database from data
    db = Chroma.from_documents(docs, embeddings,persist_directory= "./chroma/",collection_name="example_collection")
    st.write(db._collection.count())

    # Define retriever and memory
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Create a chatbot chain. Memory is managed externally.
    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
        chain_type = "map_reduce",
        retriever=retriever,
    )
    return qa

# Show title and description.
st.title("PDF Chatbot:coffee:")
st.write(
    "Upload a pdf below and ask questions about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    #openai.api_key = openai_api_key
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader("Upload a d.pdf", type="pdf")

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about it!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Process the uploaded file and question.
        qa = load_db(uploaded_file)
        outputs = qa.invoke({"query": question})
        query_text = outputs.get("query", "")
        result_text = outputs.get("result", "")


        # Use st.write_stream to stream the result
        if result_text:
            st.write(result_text)
        else:
            st.write("No result found.")
