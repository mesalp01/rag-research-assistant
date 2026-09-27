import os
import hashlib
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# --- BAĞLANTI PROTOKOLLERİ ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# ChromaDB ve OpenAI Embedding ayarları
chroma_client = chromadb.PersistentClient(path="./chroma_data")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key,
    model_name="text-embedding-3-small"
)

# T-doll hafıza havuzuna (koleksiyonuna) bağlan
memory_collection = chroma_client.get_or_create_collection(
    name="t_doll_memory",
    embedding_function=openai_ef
)


# --- 1. SIZMA (WEB SCRAPING) ---
# --- 1. SIZMA (WEB SCRAPING) ---
def fetch_article_text(url):
    """Bir web sitesine girer ve HTML etiketlerini, reklamları atıp sadece metni çeker."""
    print(f"[LOG]: Infiltration initiated -> {url}")
    try:
        # T-doll'a sivil bir tarayıcı kimliği (User-Agent) giydiriyoruz
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # İstek atarken bu sahte kimliği kullanıyoruz
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Hata varsa işlemi durdur

        # BeautifulSoup ile HTML kodunu ayrıştır
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tüm paragrafları (<p> etiketlerini) bul ve tek bir metin olarak birleştir
        paragraphs = soup.find_all('p')
        full_text = "\n".join([p.get_text() for p in paragraphs])

        return full_text
    except Exception as e:
        print(f"[ERROR]: Target unreachable. Error details: {e}")
        return None


# --- 2. KESİŞİMLİ PARÇALAMA (OVERLAP CHUNKING) ---
def chunk_text(text, chunk_size=1000, overlap=200):
    """Metni, bağlam kopmaması için kiremit gibi üst üste binen (overlap) parçalara böler."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # Bir sonraki parçaya geçerken tam uçtan değil, overlap (kesişim) kadar geriden başla
        start += (chunk_size - overlap)
    return chunks


# --- 3. HAFIZAYA KAZIMA (INGESTION) ---
def ingest_url(url):
    """Ana Operasyon: URL'yi al, metni çek, parçala ve hafızaya göm."""
    article_text = fetch_article_text(url)

    if not article_text:
        return

    print("[LOG]: Text extracted. Initiating chunking process...")
    chunks = chunk_text(article_text)

    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]

    for i, chunk in enumerate(chunks):
        # Her URL için kararlı ve benzersiz bir ID oluştur
        doc_id = f"web_{url_hash}_chunk_{i}"

        # Parçayı ve kaynağını (metadata) ChromaDB'ye kaydet
        memory_collection.upsert(
            ids=[doc_id],
            documents=[chunk],
            metadatas=[{"source": "web_article", "url": url}]
        )

    print(f"[SUCCESS]: Total of {len(chunks)} chunks successfully embedded into ChromaDB.")


# --- OPERASYON BAŞLATMA (EXECUTION) ---
if __name__ == "__main__":
    print("-" * 50)
    print("T-doll Web Intelligence Ingestion: ONLINE")
    print("-" * 50)

    # İstihbarat toplanacak hedef URL
    target_url = input("Ingest edilecek URL'yi girin: ").strip()

    if target_url:
        ingest_url(target_url)

    print("-" * 50)
    print("Logistics complete. System database updated with web intelligence.")