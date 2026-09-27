# T-Doll RAG Assistant

A Streamlit-based Retrieval-Augmented Generation (RAG) assistant built with OpenAI models and ChromaDB.

The project explores semantic retrieval, document ingestion, web ingestion, intent routing, and context-grounded response generation.

## Features

- Streamlit chat interface
- OpenAI-powered language model responses
- Structured intent routing with Pydantic
- Retrieval-Augmented Generation (RAG)
- OpenAI embeddings
- Persistent ChromaDB vector database
- Local `.txt` document ingestion
- Web page ingestion
- Overlapping text chunking
- Semantic retrieval
- Streaming responses

## Tech Stack

- Python
- Streamlit
- OpenAI API
- ChromaDB
- Pydantic
- BeautifulSoup
- Requests

## Project Structure

```text
t-doll-rag-assistant/
├── app.py
├── core.py
├── data_ingestion.py
├── web_ingest.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── documents/
    └── README.md
```

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Document Ingestion

Place `.txt` files inside the `documents/` directory and run:

```bash
python data_ingestion.py
```

## Web Ingestion

Run:

```bash
python web_ingest.py
```

Enter a URL when prompted.

## Running the Application

```bash
streamlit run app.py
```

## How It Works

1. The user submits a query through the Streamlit interface.
2. An LLM-based router classifies the query.
3. External-knowledge queries trigger semantic retrieval from ChromaDB.
4. Retrieved context is supplied to the language model.
5. The model generates a streamed response grounded in the retrieved context.

## Current Limitations

- The personal-profile memory route is not yet implemented.
- Web extraction currently focuses mainly on paragraph text.
- Retrieval currently uses a fixed top-k value.
- Retrieval quality evaluation has not yet been implemented.
- The application depends on the OpenAI API.

## Future Work

- Retrieval quality evaluation
- Source citations in generated responses
- Metadata filtering
- Improved chunking strategies
- Conversation-memory improvements
- Support for additional document formats
- Configurable retrieval parameters

## About

This project was developed as a learning project focused on the practical components of modern LLM applications, including embeddings, vector databases, RAG pipelines, structured routing, and prompt-based response control.
