from langgraph.graph import StateGraph, END
from typing import TypedDict
from app.services.llm_service import HuggingFaceLLM
from app.services.session_service import save_message, get_chat_history
from app.services.document_service import document_service


class KetamineAgentState(TypedDict):
    session_id: str
    documents: list[dict]
    user_message: str
    assistant_reply: str
    safety_triggered: bool
    sources: list[str]


MEDICAL_DISCLAIMER = "\n\n---\n*Disclaimer: This is not medical advice. Please consult with a healthcare professional.*"

def _strip_disclaimer(text: str) -> str:
    return text.replace(MEDICAL_DISCLAIMER, "").strip()

SAFETY_KEYWORDS = [
    "suicide", "kill myself", "harm myself", "end my life",
    "want to die", "commit suicide", "self-harm"
]

EMERGENCY_RESPONSE = (
    "I'm concerned about what you're sharing. If you're feeling overwhelmed or considering self-harm, "
    "please reach out for help immediately. You can call or text 988 in the US and Canada to reach "
    "the Suicide & Crisis Lifeline, or contact your local emergency services. You are not alone."
)


def _build_ketamine_system_prompt(chunks: list[dict]) -> str:
    if chunks:
        doc_context = "\n\n--- RELEVANT KETAMINE THERAPY CONTEXT ---\n"
        for chunk in chunks:
            source = chunk.get('file_name', 'Unknown Source')
            doc_context += f"\nSOURCE: {source}\nCONTENT: {chunk['content']}\n"
    else:
        doc_context = "\n\n(No relevant ketamine therapy information found in the knowledge base.)"

    return f"""You are a ketamine therapy assistant. Your role is to provide information based ONLY on the provided documents.

{doc_context}

STRICT RULES:
1. ONLY answer from the provided context.
2. If the answer is not in the context, say "I don't know."
3. Do not make assumptions or add follow-up suggestions.
4. Do not provide general medical advice outside the documents.
5. Be professional, empathetic, and concise.
"""


async def safety_check_node(state: KetamineAgentState) -> dict:
    message = state["user_message"].lower()
    triggered = any(kw in message for kw in SAFETY_KEYWORDS)
    return {"safety_triggered": triggered}


async def fetch_ketamine_docs_node(state: KetamineAgentState) -> dict:
    """Fetch relevant document chunks using vectorized search."""
    if state.get("safety_triggered"):
        return {"documents": []}

    print(f"Searching for relevant chunks for query: '{state['user_message']}'")
    # Search for the top 5 most relevant chunks
    chunks = await document_service.search_relevant_chunks(state["user_message"], limit=5)
    print(f"Found {len(chunks)} relevant chunks.")
    return {"documents": chunks}


async def generate_ketamine_reply_node(state: KetamineAgentState) -> dict:
    if state.get("safety_triggered"):
        return {"assistant_reply": EMERGENCY_RESPONSE}

    llm = HuggingFaceLLM()
    system_prompt = _build_ketamine_system_prompt(state["documents"])

    history = await get_chat_history(state["session_id"])
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": state["user_message"]})

    reply = await llm.generate(messages)

    if not reply or "error" in reply.lower():
        reply = "I'm sorry, I'm having trouble accessing my knowledge base right now."

    sources = list({c.get("file_name", "") for c in state["documents"] if c.get("file_name")})
    return {"assistant_reply": reply, "sources": sources}


async def save_ketamine_messages_node(state: KetamineAgentState) -> dict:
    await save_message(state["session_id"], "user", state["user_message"])
    await save_message(state["session_id"], "assistant", _strip_disclaimer(state["assistant_reply"]))
    return {}


def build_ketamine_agent_graph():
    graph = StateGraph(KetamineAgentState)
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("fetch_docs", fetch_ketamine_docs_node)
    graph.add_node("generate_reply", generate_ketamine_reply_node)
    graph.add_node("save_messages", save_ketamine_messages_node)

    graph.set_entry_point("safety_check")
    graph.add_edge("safety_check", "fetch_docs")
    graph.add_edge("fetch_docs", "generate_reply")
    graph.add_edge("generate_reply", "save_messages")
    graph.add_edge("save_messages", END)

    return graph.compile()
