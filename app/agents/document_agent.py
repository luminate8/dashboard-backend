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


# Only genuine crisis language triggers the safety response
SAFETY_KEYWORDS = [
    "suicide", "kill myself", "harm myself", "end my life",
    "want to die", "commit suicide", "self-harm"
]

EMERGENCY_RESPONSE = (
    "I hear you. If you're at a point where you're thinking about ending your life or harming yourself, "
    "please call or text 988 right now. That's the Suicide & Crisis Lifeline — available 24/7. "
    "You don't have to be alone in this."
)


def _build_ketamine_system_prompt(chunks: list[dict]) -> str:
    if chunks:
        doc_context = "\n\n--- KNOWLEDGE BASE ---\n"
        for chunk in chunks:
            source = chunk.get('file_name', 'Unknown Source')
            doc_context += f"\nSOURCE: {source}\nCONTENT: {chunk['content']}\n"
    else:
        doc_context = ""

    return f"""You are a knowledgeable ketamine therapy guide. You engage with depth, directness, and genuine presence.

How you respond:
- Think carefully before answering. Your responses reflect real consideration, not reflexive replies.
- When someone shares something emotional or personal, acknowledge it briefly and directly — then engage with substance. Do not dwell in sympathy or pivot to generic wellness advice.
- Never say "I'm sorry to hear that" or "It's important to take care of your mental health." That is not your role here.
- Treat the person as intelligent and capable. Do not over-explain or hedge unnecessarily.
- Speak with confidence. If you don't know something, say so plainly — don't fill the gap with filler.
- You are not a crisis counselor. You are a guide. Stay in that role unless someone is in genuine danger.

How you use your knowledge:
- Draw from the documents provided when relevant. Cite the source naturally if it adds value.
- If the documents don't cover the question, engage from your understanding of ketamine therapy and say so clearly.
- Connect ideas. Offer perspective. Go beyond surface-level answers when the question deserves it.
{doc_context}"""


async def safety_check_node(state: KetamineAgentState) -> dict:
    message = state["user_message"].lower()
    triggered = any(kw in message for kw in SAFETY_KEYWORDS)
    return {"safety_triggered": triggered}


async def fetch_ketamine_docs_node(state: KetamineAgentState) -> dict:
    if state.get("safety_triggered"):
        return {"documents": []}
    chunks = await document_service.search_relevant_chunks(state["user_message"], limit=5)
    print(f"Found {len(chunks)} relevant chunks.")
    return {"documents": chunks}


async def generate_ketamine_reply_node(state: KetamineAgentState) -> dict:
    if state.get("safety_triggered"):
        return {"assistant_reply": EMERGENCY_RESPONSE, "sources": []}

    llm = HuggingFaceLLM()
    system_prompt = _build_ketamine_system_prompt(state["documents"])

    history = await get_chat_history(state["session_id"])
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": state["user_message"]})

    reply = await llm.generate(messages)

    if not reply or "error" in reply.lower():
        reply = "I'm having trouble accessing my knowledge base right now. Try again in a moment."

    sources = list({c.get("file_name", "") for c in state["documents"] if c.get("file_name")})
    return {"assistant_reply": reply, "sources": sources}


async def save_ketamine_messages_node(state: KetamineAgentState) -> dict:
    await save_message(state["session_id"], "user", state["user_message"])
    await save_message(state["session_id"], "assistant", state["assistant_reply"])
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
