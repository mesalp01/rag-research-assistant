import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# 1. BAĞLANTI PROTOKOLLERİ
load_dotenv()

# 2. NEURAL CLOUD BAĞLANTISI
chroma_client = chromadb.PersistentClient(path="./chroma_data")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), 
    model_name="text-embedding-3-small"
)

memory_collection = chroma_client.get_or_create_collection(
    name="t_doll_memory",
    embedding_function=openai_ef
)

def scan_and_ingest(folder_path):
    """Klasördeki .txt dosyalarını otomatik olarak hafızaya yükler."""
    if not os.path.exists(folder_path):
        print(f"[ERROR]: Folder '{folder_path}' not found, Commander.")
        return

    all_files = os.listdir(folder_path)
    
    for filename in all_files:
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            doc_id = f"doc_{filename}"
            memory_collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[{"source": "external_document", "filename": filename}]
            )
            print(f"[SUCCESS]: '{filename}' has been embedded into the Digimind.")

if __name__ == "__main__":
    docs_folder = "documents"
    print("-" * 50)
    print(f"16Lab Tactical Update: Scanning '{docs_folder}'...")
    scan_and_ingest(docs_folder)
    print("-" * 50)
    print("Logistics complete. System database updated.")