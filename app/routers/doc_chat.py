from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.agents.document_agent import build_ketamine_agent_graph

router = APIRouter(prefix="/api/doc-chat", tags=["doc-chat"])

ketamine_agent_graph = build_ketamine_agent_graph()


@router.post("")
async def doc_chat(request: ChatRequest):
    result = await ketamine_agent_graph.ainvoke({
        "session_id": str(request.session_id),
        "documents": [],
        "user_message": request.message,
        "assistant_reply": "",
        "safety_triggered": False,
        "sources": [],
    })

    return ChatResponse(
        session_id=request.session_id,
        response=result["assistant_reply"],
        personas=["Ketamine Therapy Assistant"],
        sources=result.get("sources", []),
    )
