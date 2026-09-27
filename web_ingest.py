import hashlib
import os

import chromadb
import requests
from bs4 import BeautifulSoup
from chromadb.utils import embedding_functions
from dotenv import load_dotenv


# --- APPLICATION CONFIGURATION ---

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured. "
        "Create a .env file and add your OpenAI API key."
    )

EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "knowledge_base"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=EMBEDDING_MODEL,
)

knowledge_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef,
)


# --- WEB CONTENT EXTRACTION ---

def fetch_article_text(url: str) -> str | None:
    """
    Fetch a web page and extract readable paragraph text from its HTML.
    """

    print(f"[FETCH] Requesting content from: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = [
            paragraph.get_text(" ", strip=True)
            for paragraph in soup.find_all("p")
        ]

        paragraphs = [
            paragraph
            for paragraph in paragraphs
            if paragraph
        ]

        full_text = "\n".join(paragraphs).strip()

        if not full_text:
            print("[WARNING] No paragraph text could be extracted.")
            return None

        return full_text

    except requests.RequestException as error:
        print(f"[FETCH ERROR] {error}")
        return None


# --- TEXT CHUNKING ---

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks to preserve context
    across chunk boundaries.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be greater than or equal to zero "
            "and smaller than chunk_size."
        )

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


# --- WEB INGESTION ---

def ingest_url(url: str) -> None:
    """
    Fetch a URL, split its text into chunks,
    and store the chunks in ChromaDB.
    """

    article_text = fetch_article_text(url)

    if not article_text:
        print("[WARNING] Ingestion stopped because no text was extracted.")
        return

    print("[INGESTION] Text extracted. Creating chunks...")

    chunks = chunk_text(article_text)

    if not chunks:
        print("[WARNING] No chunks were generated.")
        return

    # A stable hash prevents document-ID collisions between different URLs.
    url_hash = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()[:12]

    for index, chunk in enumerate(chunks):
        document_id = f"web_{url_hash}_chunk_{index}"

        knowledge_collection.upsert(
            ids=[document_id],
            documents=[chunk],
            metadatas=[
                {
                    "source": "web",
                    "url": url,
                    "chunk_index": index,
                }
            ],
        )

    print(
        f"[SUCCESS] {len(chunks)} chunks were stored in ChromaDB."
    )


# --- COMMAND-LINE ENTRY POINT ---

if __name__ == "__main__":
    print("-" * 50)
    print("Web Content Ingestion")
    print("-" * 50)

    target_url = input("Enter a URL to ingest: ").strip()

    if target_url:
        ingest_url(target_url)
    else:
        print("[WARNING] No URL was provided.")

    print("-" * 50)
    print("Ingestion process finished.")