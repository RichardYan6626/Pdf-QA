# PDF Question Answering App
This application allows you to ask questions about you PDFs using ChatGPT. I made this to help read papers.

Notice: 1. When working with PDF of hundreds of pages, the upload will take a little bit longer, but the retrieval time
        does not change much. The vectorstore is created on local disk and cleared after the session ends

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
2. Navigate to the Question Answering page and ask questions about the PDF
3. View your chat history

## Tips: You can upload multiple files and view chat history for each file.
However, the QA is only for the latest file to have a smaller vectorstore for faster retrieval. 

## Update Thoughts:
###
This application is implemented using langchain RetrievalQA, so the user queries are embedded for a semantic search.
i.e. if the user query is "what was mentioned about HuggingGPT?", then the query itself is embedded while it would be better to just embed "HuggingGPT".
Also, RetrievalQA cannot handle summary tasks well due to its architecture and limited context window.
Limited context window can be solved with MemGPT(currently known as Letta) and to make the application capable of handling different tasks,
user query should first be fed into an LLM that categorize the task type and extract necessary information. Then specilized prompt templates can be used for different tasks.

## Ongoing Projects and Thoughts:
###
1. To-do list manager: generates priority recommendations in JSON format for the user's to-do list. There is a section
   for reviewing the completed tasks and with each task well done, you get a random, hopefully interesting image as a reward
2. Intuitive explainer: Personally I'm a big fan of Richard Feynman for him explaining everything in an intuitive way.
   I tried asking LLM for intuitive explainations to help me memorize or understand things and found it interesting and useful.
   


