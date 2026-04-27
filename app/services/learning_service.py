from typing import List, Optional
from app.db.database import get_pool
from app.models.schemas import FeedbackRequest
from app.services.embedding_service import embedding_service


class LearningService:
    @staticmethod
    async def mark_negative(feedback: FeedbackRequest):
        """Update the existing positive record to negative and queue for admin review."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE learning_queue SET feedback = 'negative', suggested_answer = $1
                   WHERE id = (
                       SELECT id FROM learning_queue
                       WHERE question = $2 AND feedback = 'positive'
                       ORDER BY created_at DESC LIMIT 1
                   )""",
                feedback.suggested_answer, feedback.question
            )

    @staticmethod
    async def add_to_queue(feedback: FeedbackRequest):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO learning_queue (question, ai_answer, feedback, suggested_answer) VALUES ($1, $2, $3, $4)",
                feedback.question, feedback.ai_answer, feedback.feedback, feedback.suggested_answer
            )

    @staticmethod
    async def get_queue(status: str = "pending") -> List[dict]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM learning_queue WHERE status = $1 ORDER BY created_at DESC", status
            )
            return [dict(row) for row in rows]

    @staticmethod
    async def update_status(item_id: str, status: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE learning_queue SET status = $1 WHERE id = $2", status, item_id
            )

    @staticmethod
    async def approve_item(item_id: str, edited_answer: Optional[str] = None):
        """Approve a feedback item, optionally updating the answer, and add to vector DB."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 1. Get the current item
            item = await conn.fetchrow(
                "SELECT question, suggested_answer FROM learning_queue WHERE id = $1", 
                item_id
            )
            if not item:
                return False
            
            # Use edited answer if provided, else use the suggested one from the item
            answer_to_save = edited_answer if edited_answer is not None else item['suggested_answer']
            
            # 2. Embed the answer and update status + embedding in learning_queue
            embedding_value = None
            if answer_to_save:
                print(f"Vectorizing approved answer for item {item_id}...")
                embeddings = await embedding_service.get_embeddings([answer_to_save])
                if embeddings:
                    embedding_value = str(embeddings[0])
                    print(f"Embedding generated successfully.")
                else:
                    print(f"Failed to generate embedding.")

            await conn.execute(
                "UPDATE learning_queue SET status = 'approved', suggested_answer = $1, suggested_answer_embedding = $2::vector WHERE id = $3",
                answer_to_save, embedding_value, item_id
            )
            
            if embedding_value:
                await conn.execute(
                    """INSERT INTO document_chunks (session_id, file_name, content, embedding) 
                       VALUES ($1, $2, $3, $4::vector)""",
                    "00000000-0000-0000-0000-000000000000",
                    "Admin Approved Correction",
                    answer_to_save,
                    embedding_value
                )

            
            return True

    @staticmethod
    async def reject_item(item_id: str):
        """Reject a feedback item."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE learning_queue SET status = 'rejected' WHERE id = $1", 
                item_id
            )
            return True

    @staticmethod
    async def get_accuracy_rate() -> float:
        """Calculate the percentage of positive feedback."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) FILTER (WHERE feedback = 'positive') as positive_count,
                    COUNT(*) as total_count
                FROM learning_queue
                """
            )
            if not row or row['total_count'] == 0:
                return 0.0
            return (row['positive_count'] / row['total_count']) * 100.0


learning_service = LearningService()
