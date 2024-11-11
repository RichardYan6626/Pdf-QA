# PDF Question Answering App

This application allows you to upload PDFs and ask questions about their content using GPT-4.
Notice: When working with PDF of hundreds of pages, the upload will take a few minutes, but the retrieval time
        does not change much.

## Prerequisites
- Docker
- OpenAI API key (https://platform.openai.com/api-keys)

## Setup Instructions

1. Clone this repository:

2. Create a `.env` file in the project root with your OpenAI API key:

3. Build and run the Docker container:
```bash
docker-compose up --build
```

4. Open your browser and go to http://localhost:8501


## Get started
1. Upload a PDF file on the main page. 
2. Navigate to the Question Answering page to ask questions about the PDF
3. View your chat history

## Tips: You can upload multiple files and view chat history for each file.
However, the QA is only for the latest file to have a smaller vectorstore. 

## Update Thoughts:
###
This application is implemented using langchain RetrievalQA, so the user queries are embedded for a semantic search.
i.e. if the user query is "what was mentioned about HuggingGPT?", then the query itself is embedded while it would be better to just embed "HuggingGPT".
Also, RetrievalQA cannot handle summary tasks well due to its architecture and limited context window.
### 
Limited context window can be solved with MemGPT(currently known as Letta) and to make the application capable of handling different tasks,
user query should first be fed into an LLM that categorize the task type and extract necessary information. Then specilized prompt templates can be
used for different tasks.
