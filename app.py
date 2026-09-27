import streamlit as st

from core import generate_response_stream


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RAG Research Assistant",
    page_icon="🔎",
    layout="centered",
)


# --- CUSTOM INTERFACE THEME ---
def inject_modern_tech_theme():
    modern_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Main application background */
    .stApp {
        background-color: #0F172A;
        background-image:
            linear-gradient(rgba(0, 229, 255, 0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.015) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }

    /* Headings */
    h1, h2 {
        color: #00E5FF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Chat message containers */
    [data-testid="stChatMessage"] {
        border-radius: 4px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* User messages */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E293B !important;
        border-left: 3px solid #00E5FF !important;
        color: #FFFFFF !important;
    }

    /* Assistant messages */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #111827 !important;
        border-left: 3px solid #94A3B8 !important;
        color: #E2E8F0 !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        box-shadow:
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
    }

    /* Loading spinner */
    .stSpinner i {
        color: #00E5FF !important;
    }
    </style>
    """

    st.markdown(modern_css, unsafe_allow_html=True)


inject_modern_tech_theme()


# --- HEADER ---
st.title("🔎 RAG Research Assistant")
st.caption(
    "Semantic retrieval, document search, and context-grounded response generation"
)
st.markdown("---")


# --- CONVERSATION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# Render previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- MAIN CHAT LOOP ---
user_input = st.chat_input("Ask a question...")

if user_input:
    # Store and display the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and stream the assistant response
    with st.chat_message("assistant"):
        stream = generate_response_stream(
            user_input,
            st.session_state.messages[:-1],
        )

        full_response = st.write_stream(stream)

    # Store the complete assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )