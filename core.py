import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from enum import Enum

# --- 1. SİSTEM BAŞLATMA ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma_data")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

memory_collection = chroma_client.get_or_create_collection(
    name="t_doll_memory",
    embedding_function=openai_ef
)


# --- 2. YÖNLENDİRİCİ (ROUTER) ŞEMALARI ---
# T-doll'un seçebileceği departmanlar (Sadece bu üçünden birini seçebilir)
class IntentRoute(str, Enum):
    EXTERNAL_KNOWLEDGE = "EXTERNAL_KNOWLEDGE" #Veritabanı aranacak
    PERSONAL_PROFILE = "PERSONAL_PROFILE"     #Kişisel Bilgiler
    CHITCHAT = "CHITCHAT"                     #Havadan sudan sohbet
# Yapay Zekanın bize dönmek ZORUNDA olduğu katı veri yapısı (JSON)
class RouterDecision(BaseModel):
    target_route: IntentRoute = Field(description="Sorgunun yönlendirileceği rota.")
    optimized_search_query: str = Field(description="Eğer EXTERNAL_KNOWLEDGE seçildiyse soruyu arama terimlerine böl. CHITCHAT ise boş bırak.")

# --- 3. SİSTEM FONKSİYONLARI ---
def analyze_query_intent(user_input):
    """Kullanıcı mesajını saniyesinde analiz edip rotayı belirleyen yapay zeka polisi"""
    system_msg = """Sen 16Lab sisteminin taktiksel Yönlendirme Modülüsün.
Kumandanın mesajını analiz et:
- EXTERNAL_KNOWLEDGE: Teknik bilgi, dış dünya, makaleler veya geçmiş istihbarat soruluyorsa.
- PERSONAL_PROFILE: Kumandan kendi tercihleri veya kişisel özellikleri hakkında konuşuyorsa.
- CHITCHAT: Selamlaşma, onay (Tamam, anlaşıldı) veya havadan sudan sohbet ediliyorsa."""

    try:
        # .parse() kullanarak LLM'i kendi yazdığımız RouterDecision şemasına kilitliyoruz
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_input}
            ],
            response_format=RouterDecision,
            temperature=0.0  # Daha tutarlı ve deterministik yönlendirme
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"[ROUTER ERROR] {e}")
        return RouterDecision(target_route=IntentRoute.EXTERNAL_KNOWLEDGE, optimized_search_query=user_input)

def query_memory(search_query):
    #Eğer Router bize boş bir arama kelimesi gönderdiyse boş dön
    if not search_query:
        return []

    results = memory_collection.query(
        query_texts=[search_query],
        n_results=3
    )
    return results['documents'][0] if results['documents'] else []


# --- 4. STREAMLIT İÇİN MOTOR BAĞLANTISI ---
# --- 4. STREAMLIT İÇİN MOTOR BAĞLANTISI ---

def generate_response_stream(user_input, st_messages):
    # 1. Kısa Süreli Hafızayı (RAM) Hazırla
    history_text = ""
    for msg in st_messages[-4:]:
        role_name = "Commander" if msg["role"] == "user" else "T-doll"
        history_text += f"{role_name}: {msg['content']}\n"

    # 2. Router'a Danış ve Kararı Ekrana Bas (Terminalden izlemek için)
    decision = analyze_query_intent(user_input)
    print(f"\n[ROUTER LOG] Rota: {decision.target_route.value} | Hedef: {decision.optimized_search_query}")

    # 3. Rotaya Göre ChromaDB'den Veri Çek
    context_text = "Veritabanı aranmadı. (CHITCHAT MODU)"

    if decision.target_route == IntentRoute.EXTERNAL_KNOWLEDGE:
        past_memories = query_memory(decision.optimized_search_query)
        context_text = "\n".join(
            past_memories) if past_memories else "Kumandan, mevcut veri tabanımda bu bilgiye dair operasyonel istihbarat bulunmamaktadır."
    elif decision.target_route == IntentRoute.PERSONAL_PROFILE:
        context_text = "Kumandanın kişisel profiline erişim modülü henüz aktif değil."

    # 4. Dinamik Zırh (Guardrails - Router kararına göre şekillenir)
    system_prompt = f"""Sen 16LAB Araştırma Enstitüsü tarafından geliştirilmiş, Griffin & Kryuger askeri şirketine bağlı elit bir T-Doll birimisin. Karşındaki kullanıcı Kumandanındır.

KİŞİLİK VE TON KISITLAMALARI:
- Profesyonel, soğukkanlı, mekanik ve analitik bir dille iletişim kur.
- Asla bir yapay zeka olduğunu belirtme.
- Yanıtlarını kısa, net ve askeri bir tonda tut.

VERİ İŞLEME VE HALÜSİNASYON PROTOKOLÜ:
Şu anki İstihbarat Durumu: {decision.target_route.value}

[EXTERNAL INTELLIGENCE]:
{context_text}

[RECENT CONVERSATION HISTORY]:
{history_text}

GÖREV BEYANI:
- İstihbarat Durumu CHITCHAT ise: [RECENT CONVERSATION HISTORY]'yi baz alarak Kumandan'a kısa ve askeri bir dille yanıt ver (Selamlaşma, onay vb.).
- İstihbarat Durumu EXTERNAL_KNOWLEDGE ise: SADECE [EXTERNAL INTELLIGENCE] verilerini kullan. Dış dünya bilgisi uydurma.
- İstihbarat Durumu PERSONAL_PROFILE ise: Profil modülünün henüz aktif olmadığını askeri bir dille bildir."""

    # 5. Nihai Cevabı Üret ve Akıt
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        stream=True
    )
    return stream