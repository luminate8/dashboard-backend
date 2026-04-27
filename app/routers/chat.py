from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.agents.persona_agent import build_agent_graph
from app.services import session_service

router = APIRouter(prefix="/api", tags=["chat"])

# Build the agent graph once
agent_graph = build_agent_graph()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message and get a persona-based response."""
    print("\n" + "="*80)
    print("🚀 CHAT ENDPOINT HIT - STARTING AGENT WORKFLOW")
    print("="*80)
    print(f"📝 Session ID: {request.session_id}")
    print(f"💬 User message: {request.message}")
    print("⏳ Fetching session and initializing agent...")
    
    # Get session to know which personas to use
    session = await session_service.get_session(str(request.session_id))
    if not session:
        return {"error": "Session not found"}

    # Build list of personas from session
    personas = []
    if session.get("ideal_person"):
        personas.append(session["ideal_person"])
    if session.get("favourite_celebrity"):
        personas.append(session["favourite_celebrity"])
    if session.get("celebrity_to_talk"):
        personas.append(session["celebrity_to_talk"])

    # Remove duplicates while keeping order
    seen = set()
    personas = [p for p in personas if not (p.lower() in seen or seen.add(p.lower()))]

    if not personas:
        personas = ["Assistant"]
    
    print(f"👤 Active personas: {', '.join(personas)}")
    print("="*80)

    # Run the agent graph
    print("\n⏳ Running LangGraph agent workflow...")
    result = await agent_graph.ainvoke({
        "session_id": str(request.session_id),
        "personas": personas,
        "stored_profiles": [],
        "tweets": [],
        "user_message": request.message,
        "assistant_reply": "",
    })
    
    print("\n" + "="*80)
    print("✅ CHAT WORKFLOW COMPLETED SUCCESSFULLY")
    print(f"📝 Response length: {len(result['assistant_reply'])} characters")
    print("="*80 + "\n")

    return ChatResponse(
        session_id=request.session_id,
        response=result["assistant_reply"],
        personas=personas,
    )
