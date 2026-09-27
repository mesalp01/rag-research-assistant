import os
from enum import Enum

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


# --- APPLICATION CONFIGURATION ---

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured. "
        "Create a .env file and add your OpenAI API key."
    )

CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_PATH = "./chroma_data"
COLLECTION_NAME = "knowledge_base"

client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=EMBEDDING_MODEL,
)

knowledge_collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef,
)


# --- ROUTING SCHEMA ---

class IntentRoute(str, Enum):
    EXTERNAL_KNOWLEDGE = "EXTERNAL_KNOWLEDGE"
    PERSONAL_PROFILE = "PERSONAL_PROFILE"
    CHITCHAT = "CHITCHAT"


class RouterDecision(BaseModel):
    target_route: IntentRoute = Field(
        description="The route that should handle the user's query."
    )

    optimized_search_query: str = Field(
        description=(
            "A concise semantic-search query when EXTERNAL_KNOWLEDGE is selected. "
            "Leave empty for routes that do not require retrieval."
        )
    )


# --- ROUTING ---

def analyze_query_intent(user_input: str) -> RouterDecision:
    """
    Classify the user's message and determine whether retrieval is required.
    """

    system_message = """
You are a routing component for a Retrieval-Augmented Generation application.

Classify the user's message into exactly one of these routes:

EXTERNAL_KNOWLEDGE:
Use this when the user asks for information that should be retrieved from
the application's indexed knowledge base.

PERSONAL_PROFILE:
Use this when the user asks about stored personal preferences, characteristics,
or profile information about themselves.

CHITCHAT:
Use this for greetings, acknowledgements, casual conversation, or messages
that do not require knowledge-base retrieval.

When selecting EXTERNAL_KNOWLEDGE, rewrite the user's request into a concise
semantic-search query.

For PERSONAL_PROFILE and CHITCHAT, return an empty optimized_search_query.
"""

    try:
        response = client.beta.chat.completions.parse(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input},
            ],
            response_format=RouterDecision,
            temperature=0.0,
        )

        return response.choices[0].message.parsed

    except Exception as error:
        print(f"[ROUTER ERROR] {error}")

        # Retrieval is used as a safe fallback so the application
        # does not silently answer from unsupported knowledge.
        return RouterDecision(
            target_route=IntentRoute.EXTERNAL_KNOWLEDGE,
            optimized_search_query=user_input,
        )


# --- VECTOR DATABASE RETRIEVAL ---

def query_knowledge_base(search_query: str) -> list[str]:
    """
    Retrieve the most semantically relevant document chunks from ChromaDB.
    """

    if not search_query.strip():
        return []

    try:
        results = knowledge_collection.query(
            query_texts=[search_query],
            n_results=3,
        )

        documents = results.get("documents")

        if not documents or not documents[0]:
            return []

        return documents[0]

    except Exception as error:
        print(f"[RETRIEVAL ERROR] {error}")
        return []


# --- RESPONSE GENERATION ---

def generate_response_stream(user_input: str, st_messages: list[dict]):
    """
    Route the query, retrieve relevant context when needed,
    and return a streamed language-model response.
    """

    # Keep a small amount of recent conversation context.
    history_lines = []

    for message in st_messages[-4:]:
        role_name = "User" if message["role"] == "user" else "Assistant"
        history_lines.append(f"{role_name}: {message['content']}")

    history_text = "\n".join(history_lines)

    # Determine the appropriate processing route.
    decision = analyze_query_intent(user_input)

    print(
        f"\n[ROUTER] "
        f"Route: {decision.target_route.value} | "
        f"Query: {decision.optimized_search_query}"
    )

    # Prepare context according to the selected route.
    if decision.target_route == IntentRoute.EXTERNAL_KNOWLEDGE:
        retrieved_documents = query_knowledge_base(
            decision.optimized_search_query
        )

        if retrieved_documents:
            context_text = "\n\n".join(retrieved_documents)
        else:
            context_text = (
                "No relevant information was found in the indexed knowledge base."
            )

    elif decision.target_route == IntentRoute.PERSONAL_PROFILE:
        context_text = (
            "Personal-profile memory is not implemented in the current version."
        )

    else:
        context_text = "Knowledge-base retrieval was not required."

    system_prompt = f"""
You are a research assistant integrated with a
Retrieval-Augmented Generation application.

Current route:
{decision.target_route.value}

RETRIEVED CONTEXT:
{context_text}

RECENT CONVERSATION:
{history_text}

RESPONSE RULES:

- If the route is EXTERNAL_KNOWLEDGE, answer using only the retrieved context.
- If the retrieved context does not contain enough information, clearly say so.
- Do not invent facts that are absent from the retrieved context.
- If the route is CHITCHAT, respond naturally and concisely using the recent
  conversation when useful.
- If the route is PERSONAL_PROFILE, explain that personal-profile memory is
  not implemented in the current version.
- Keep answers clear, relevant, and concise.
"""

    stream = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7,
        stream=True,
    )

    return stream