import streamlit as st
import time
from core import generate_response_stream

# --- 1. SİSTEM YAPILANDIRMASI ---
# Ferah ama teknolojik bir ikon seçtik.
st.set_page_config(page_title="16Lab Neural Cloud", page_icon="📡", layout="centered")


# --- 2. GÖRSEL ZIRH (MODERN TECH-UI CSS) ---
def inject_modern_tech_theme():
    modern_css = """
    <style>
    /* Modern, temiz ve okunabilirliği yüksek global font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 1. KÖK ARKA PLAN (Derin ama Mat Grafit / Slate Tonu - Göz yormaz) */
    .stApp {
        background-color: #0F172A; /* Slate 900 - Çok derin lacivert/gri */
        /* Çok hafif, neredeyse görünmez bir teknolojik ızgara dokusu */
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.015) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #E2E8F0; /* Slate 200 - Yumuşak, parlamayan beyaz */
        font-family: 'Inter', sans-serif;
    }

    /* Başlıklar (Siber Camgöbeği Vurgu) */
    h1, h2 {
        color: #00E5FF !important; /* Canlı Siber Camgöbeği */
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* 3. SOHBET KUTULARI (Endüstriyel ve Temiz) */

    /* Global sohbet kutusu ayarları - Yuvarlaklığı azalttık, köşeli tech hissi verdik */
    [data-testid="stChatMessage"] {
        border-radius: 4px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* Kullanıcı Mesajları (Kumandan) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E293B !important; /* Slate 800 - Arka plandan biraz daha açık */
        border-left: 3px solid #00E5FF !important; /* Camgöbeği Sol Vurgu */
        color: #FFFFFF !important;
    }

    /* Asistan Mesajları (T-Doll) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #111827 !important; /* Gray 900 - Koyu ve ciddi */
        border-left: 3px solid #94A3B8 !important; /* Slate 400 - Yumuşak Gri Vurgu */
        color: #E2E8F0 !important;
    }

    /* 4. GİRDİ ALANI (Chat Input - Odaklanmış ve Keskin) */
    [data-testid="stChatInput"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important; /* Slate 700 - Hafif belirgin sınır */
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Girdi alanına odaklanıldığında (focus) siber parlama efekti */
    [data-testid="stChatInput"]:focus-within {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
    }

    /* Spinner (Yükleniyor ikonu) rengini camgöbeği yapalım */
    .stSpinner i {
        color: #00E5FF !important;
    }
    </style>
    """
    st.markdown(modern_css, unsafe_allow_html=True)


inject_modern_tech_theme()

# --- 3. ARAYÜZ BAŞLIKLARI ---
st.title("📡 16Lab Terminali")
st.caption("Project Neural Cloud | Bağlantı Stabil | T-Doll Beklemede...")
st.markdown("---")

# --- 4. KISA SÜRELİ HAFIZA (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. ANA DİYALOG DÖNGÜSÜ ---
user_input = st.chat_input("Kumandan, emrinizi girin...")

if user_input:
    # 1. Kumandanın mesajını kaydet ve ekrana bas
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Gerçek T-Doll Yanıtı (Harf harf akış / Streaming)
    with st.chat_message("assistant"):
        # Beyinden (core.py) cevabı harf harf çek
        stream = generate_response_stream(user_input, st.session_state.messages[:-1])
        # Streamlit'in özel fonksiyonu ile ekrana akıt
        full_response = st.write_stream(stream)

    # 3. T-doll'un tam cevabını hafızaya kaydet
    st.session_state.messages.append({"role": "assistant", "content": full_response})