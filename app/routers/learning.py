from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from app.models.schemas import LearningQueueItem
from app.services.learning_service import learning_service

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/queue", response_model=List[LearningQueueItem])
async def get_learning_queue(status: str = "pending"):
    return await learning_service.get_queue(status)


@router.post("/approve/{item_id}")
async def approve_learning_item(item_id: str, edited_answer: Optional[str] = Body(None, embed=True)):
    success = await learning_service.approve_item(item_id, edited_answer)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "message": "Item approved and vectorized into knowledge base"}


@router.post("/reject/{item_id}")
async def reject_learning_item(item_id: str):
    success = await learning_service.reject_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "message": "Item rejected"}


@router.get("/accuracy")
async def get_accuracy_rate():
    rate = await learning_service.get_accuracy_rate()
    return {"accuracy_rate": rate}


@router.get("/graph-stats")
async def get_graph_stats():
    from app.db.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 1. Conversation trend: last 8 weeks, count distinct sessions with messages
        conv_trend = await conn.fetch("""
            SELECT TO_CHAR(DATE_TRUNC('week', m.created_at), 'Mon DD') AS month,
                   DATE_TRUNC('week', m.created_at) AS month_date,
                   COUNT(DISTINCT m.session_id) AS conversations
            FROM messages m
            WHERE m.created_at >= NOW() - INTERVAL '8 weeks'
            GROUP BY DATE_TRUNC('week', m.created_at)
            ORDER BY month_date ASC
        """)

        # 2. Daily message activity for last 14 days (real dates)
        activity = await conn.fetch("""
            SELECT TO_CHAR(DATE_TRUNC('day', created_at), 'Mon DD') AS day,
                   DATE_TRUNC('day', created_at) AS day_date,
                   COUNT(*) AS active
            FROM messages
            WHERE created_at >= NOW() - INTERVAL '14 days'
            GROUP BY DATE_TRUNC('day', created_at)
            ORDER BY day_date ASC
        """)

        # 3. Approval status
        approved = await conn.fetchval("SELECT COUNT(*) FROM learning_queue WHERE status = 'approved'")
        pending = await conn.fetchval("SELECT COUNT(*) FROM learning_queue WHERE status = 'pending'")

        # 4. Accuracy trend: weekly for last 4 weeks — same formula as get_accuracy_rate
        accuracy_trend = await conn.fetch("""
            SELECT
                DATE_TRUNC('week', created_at) AS week_date,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE feedback = 'positive') /
                    NULLIF(COUNT(*), 0), 1
                ) AS accuracy
            FROM learning_queue
            WHERE created_at >= NOW() - INTERVAL '4 weeks'
            GROUP BY DATE_TRUNC('week', created_at)
            ORDER BY week_date ASC
        """)

    return {
        "conversation_trend": [{"month": r["month"], "conversations": r["conversations"]} for r in conv_trend],
        "user_activity": [{"day": r["day"], "messages": r["active"]} for r in activity],
        "approval_status": [
            {"name": "Approved", "value": approved or 0, "color": "#10b981"},
            {"name": "Pending", "value": pending or 0, "color": "#eab308"},
        ],
        "accuracy_trend": [{"week": r["week_date"].strftime("%b %d"), "accuracy": float(r["accuracy"] or 0)} for r in accuracy_trend],
    }


@router.get("/dashboard-stats")
async def get_dashboard_stats():
    from app.db.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        conv_count = await conn.fetchval("SELECT COUNT(DISTINCT session_id) FROM messages")
        pending_count = await conn.fetchval("SELECT COUNT(*) FROM learning_queue WHERE status = 'pending'")
        approved_count = await conn.fetchval("SELECT COUNT(*) FROM learning_queue WHERE status = 'approved'")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM auth_users WHERE is_verified = TRUE")
        accuracy = await learning_service.get_accuracy_rate()
    return {
        "total_conversations": conv_count or 0,
        "pending_approvals": pending_count or 0,
        "approved_count": approved_count or 0,
        "active_users": user_count or 0,
        "accuracy_rate": accuracy,
    }
