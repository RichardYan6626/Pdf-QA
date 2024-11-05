import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import datetime

#initialize QA chain and store in session state
def initialize_qa_chain():
    if 'qa_chain' not in st.session_state:
        llm = ChatOpenAI(
            temperature=0.9,
            model_name="gpt-4"
        )
        
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=st.session_state.db.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
        )



def main():
    st.title("Question Answering ❓")
    
    if 'db' not in st.session_state or st.session_state.db is None:
        st.warning("Please upload a PDF file first in the PDF Upload page.")
        return
        
    try:
        initialize_qa_chain()
        
        question = st.text_input("Ask a question about your PDF:")
        
        if question:
            with st.spinner("Generating answer..."):
                result = st.session_state.qa_chain({"query":question})
                
                # Store information in chat history
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                chat_entry = {
                    "timestamp": timestamp,
                    "question": question,
                    "answer": result["result"],
                    "sources": [doc.page_content[:500] for doc in result["source_documents"]],  # Store only first 500 chars of each source
                    "file_name": st.session_state.current_file.name
                }
                
                # Chat history size limit
                if len(st.session_state.chat_history) > 50: 
                    st.session_state.chat_history.pop(0)
                st.session_state.chat_history.append(chat_entry)
                
                # Display answers
                st.write("### Answer:")
                st.write(result["result"])
                
                # Display source documents
                with st.expander("View Sources"):
                    for i, doc in enumerate(result["source_documents"]):
                        st.write(f"Source {i+1}:")
                        st.write(doc.page_content)
                        st.write("---")
                
    except Exception as e:
        st.error(f"An error occurred during question answering: {str(e)}")

if __name__ == "__main__":
    main()
