# PDF Question Answering App

This application allows you to upload PDFs and ask questions about their content using GPT-4.

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

## Security Note
- Never share your `.env` file or API key
- The `.env` file is listed in `.gitignore` to prevent accidental commits
- Each user must use their own OpenAI API key

## Usage
1. Upload a PDF file on the main page
2. Navigate to the Question Answering page to ask questions about the PDF
3. View your chat history in the Chat History page
