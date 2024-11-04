# pages/3_📝_Chat_History.py
import streamlit as st
import pandas as pd

def main():
    st.title("Chat History 📝")
    
    if 'chat_history' not in st.session_state or not st.session_state.chat_history:
        st.info("No chat history available yet. Start asking questions in the Question Answering page!")
        return
    
    # Add filters
    st.sidebar.header("Filters")
    
    # Get unique file names
    file_names = list(set(entry["file_name"] for entry in st.session_state.chat_history))
    selected_file = st.sidebar.selectbox("Filter by PDF", ["All"] + file_names)
    
    # Filter chat history
    filtered_history = st.session_state.chat_history
    if selected_file != "All":
        filtered_history = [entry for entry in filtered_history if entry["file_name"] == selected_file]
    
    # Display chat history
    for i, entry in enumerate(reversed(filtered_history)):
        with st.expander(f"Q&A {len(filtered_history)-i}: {entry['timestamp']} - {entry['file_name']}", expanded=True):
            st.write("**Question:**")
            st.write(entry["question"])
            st.write("**Answer:**")
            st.write(entry["answer"])
            st.write("**Sources:**")
            for j, source in enumerate(entry["sources"], 1):
                st.write(f"Source {j}:")
                st.write(source)
                st.write("---")
    
    # Add export functionality
    if st.button("Export Chat History to CSV"):
        df = pd.DataFrame(filtered_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="chat_history.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
