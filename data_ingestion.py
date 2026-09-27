import hashlib
import os

import chromadb
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


# --- DOCUMENT INGESTION ---

def scan_and_ingest(folder_path: str) -> None:
    """
    Read all .txt files in a directory, split them into chunks,
    and store the chunks in ChromaDB.
    """

    if not os.path.isdir(folder_path):
        print(f"[ERROR] Folder not found: {folder_path}")
        return

    text_files = sorted(
        filename
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(".txt")
    )

    if not text_files:
        print(f"[WARNING] No .txt files found in: {folder_path}")
        return

    total_chunks = 0

    for filename in text_files:
        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
        except (OSError, UnicodeError) as error:
            print(f"[FILE ERROR] Could not read '{filename}': {error}")
            continue

        if not content:
            print(f"[WARNING] Skipping empty file: {filename}")
            continue

        chunks = chunk_text(content)

        # Stable filename hash keeps document IDs short and predictable.
        file_hash = hashlib.sha256(
            filename.encode("utf-8")
        ).hexdigest()[:12]

        for index, chunk in enumerate(chunks):
            document_id = f"doc_{file_hash}_chunk_{index}"

            knowledge_collection.upsert(
                ids=[document_id],
                documents=[chunk],
                metadatas=[
                    {
                        "source": "document",
                        "filename": filename,
                        "chunk_index": index,
                    }
                ],
            )

        total_chunks += len(chunks)

        print(
            f"[SUCCESS] '{filename}' -> "
            f"{len(chunks)} chunks stored."
        )

    print(
        f"[COMPLETE] {len(text_files)} files processed, "
        f"{total_chunks} chunks stored in ChromaDB."
    )


# --- COMMAND-LINE ENTRY POINT ---

if __name__ == "__main__":
    documents_folder = "documents"

    print("-" * 50)
    print("Document Ingestion")
    print("-" * 50)

    scan_and_ingest(documents_folder)

    print("-" * 50)
    print("Ingestion process finished.")