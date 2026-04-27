from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse, FeedbackRequest
from app.agents.document_agent import build_ketamine_agent_graph
from app.services.learning_service import learning_service

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

    # Auto-save as positive by default
    await learning_service.add_to_queue(FeedbackRequest(
        question=request.message,
        ai_answer=result["assistant_reply"],
        feedback="positive",
    ))

    return ChatResponse(
        session_id=request.session_id,
        response=result["assistant_reply"],
        personas=["Ketamine Therapy Assistant"],
        sources=result.get("sources", []),
    )
