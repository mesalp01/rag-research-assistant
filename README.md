# RAG Research Assistant

A lightweight Retrieval-Augmented Generation (RAG) application built with Python, Streamlit, OpenAI, and ChromaDB.

The project combines semantic retrieval, structured intent routing, local document ingestion, and web-content ingestion to generate responses grounded in indexed knowledge.

## Features

- Retrieval-Augmented Generation (RAG)
- Semantic search with OpenAI embeddings
- Persistent vector storage with ChromaDB
- Structured intent routing with Pydantic
- Streaming AI responses
- Local `.txt` document ingestion
- Web-page ingestion and HTML text extraction
- Overlapping text chunking
- Stable document identifiers using SHA-256 hashes
- Streamlit-based chat interface
- Environment-variable-based API key management

## Tech Stack

- Python
- Streamlit
- OpenAI API
- ChromaDB
- Pydantic
- BeautifulSoup
- Requests
- python-dotenv

## Project Structure

- `app.py` — Streamlit user interface
- `core.py` — intent routing, retrieval, and response generation
- `data_ingestion.py` — local text-document ingestion
- `web_ingest.py` — web-page extraction and ingestion
- `requirements.txt` — Python dependencies
- `.env.example` — environment-variable template
- `.gitignore` — Git exclusions
- `documents/`
  - `README.md` — instructions for local documents

Generated files, local environment files, API keys, vector-database data, and user-provided documents are excluded from version control.

## How It Works

The application processes a user query through several stages:

1. The query is analyzed by a structured intent router.
2. The router selects one of three routes:
   - `EXTERNAL_KNOWLEDGE`
   - `PERSONAL_PROFILE`
   - `CHITCHAT`
3. Queries requiring external knowledge are converted into a semantic search query.
4. ChromaDB retrieves the most relevant indexed document chunks.
5. Retrieved context and recent conversation history are passed to the language model.
6. The generated response is streamed to the Streamlit interface.

For external-knowledge queries, the assistant is instructed to answer only from retrieved context and to indicate when the indexed knowledge base does not contain enough information.

## Installation

Clone the repository:

```bash
git clone https://github.com/mesalp01/rag-research-assistant.git
cd rag-research-assistant
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root.

You can use `.env.example` as a template:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit your real API key to version control.

## Local Document Ingestion

Place `.txt` files inside the `documents/` directory.

Then run:

```bash
python data_ingestion.py
```

The script:

- scans the directory for text files,
- splits documents into overlapping chunks,
- generates embeddings,
- and stores the chunks in ChromaDB.

User-provided `.txt` files inside `documents/` are ignored by Git.

## Web Content Ingestion

Run:

```bash
python web_ingest.py
```

Enter a URL when prompted.

The script extracts paragraph text from the page, creates overlapping chunks, and stores them in the same ChromaDB knowledge base.

For example, you can ingest a public article such as:

`https://en.wikipedia.org/wiki/Artificial_intelligence`

## Running the Application

Start the Streamlit interface:

```bash
streamlit run app.py
```

Then open the local Streamlit address shown in the terminal.

## Retrieval Architecture

The application follows this flow:

1. The user submits a query.
2. The intent router classifies the request.
3. If retrieval is required, the query is converted into a semantic-search query.
4. ChromaDB returns the most relevant document chunks.
5. Retrieved context is combined with recent conversation history.
6. The OpenAI model generates a grounded response.
7. The response is streamed back to the Streamlit interface.

## Current Limitations

- Only `.txt` files are supported by the local document-ingestion script.
- Web extraction primarily uses HTML paragraph elements.
- JavaScript-rendered pages may not be extracted correctly.
- Retrieval currently returns a small fixed number of document chunks.
- The personal-profile route is reserved for future development and is not currently implemented.
- The project does not currently include reranking or retrieval-quality evaluation.

## Possible Future Improvements

- PDF and additional document-format support
- Metadata filtering
- Hybrid keyword and vector search
- Retrieval reranking
- Configurable chunking strategies
- Source citations in generated responses
- Retrieval evaluation metrics
- Improved web-content extraction
- User-specific memory
- Automated testing

## Purpose

This project was developed as a practical exploration of Retrieval-Augmented Generation, vector databases, semantic search, structured LLM routing, and document-processing pipelines.

Its main goal is to demonstrate how external information can be indexed, retrieved semantically, and supplied as grounded context to a language model.