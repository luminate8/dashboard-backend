import io
from typing import List
from pypdf import PdfReader
from docx import Document
from app.db.database import get_pool
from app.services.embedding_service import embedding_service


def _chunk_text(text: str, chunk_size: int = 400) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


class DocumentService:
    @staticmethod
    async def process_file(filename: str, file_bytes: bytes) -> str:
        ext = filename.split(".")[-1].lower()
        if ext == "pdf":
            pdf = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext == "docx":
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs)
        else:
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return "Unsupported file format or encoding."

    @staticmethod
    async def save_document(session_id: str, filename: str, content: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            chunks = _chunk_text(content)
            if not chunks:
                return

            print(f"Generating embeddings for {len(chunks)} chunks of '{filename}'...")
            embeddings = await embedding_service.get_embeddings(chunks)

            if embeddings and len(embeddings) == len(chunks):
                data = [
                    (session_id, filename, filename, chunks[i], content if i == 0 else None, str(embeddings[i]))
                    for i in range(len(chunks))
                ]
                await conn.executemany(
                    """INSERT INTO document_chunks
                       (session_id, filename, file_name, content, full_content, embedding)
                       VALUES ($1, $2, $3, $4, $5, $6::vector)""",
                    data
                )
                print(f"Successfully stored {len(chunks)} vector chunks for '{filename}'.")
            else:
                print(f"Failed to generate embeddings for '{filename}'. Chunks not vectorized.")

    @staticmethod
    async def search_relevant_chunks(query: str, limit: int = 3) -> List[dict]:
        query_vector = await embedding_service.get_embeddings([query])
        if not query_vector:
            return []

        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT content, file_name, (embedding <=> $1::vector) as distance
                FROM document_chunks
                WHERE embedding IS NOT NULL
                UNION ALL
                SELECT suggested_answer AS content, 'learning_queue' AS file_name,
                       (suggested_answer_embedding <=> $1::vector) as distance
                FROM learning_queue
                WHERE status = 'approved' AND suggested_answer_embedding IS NOT NULL
                ORDER BY distance
                LIMIT $2
                """,
                str(query_vector[0]), limit
            )
            return [dict(row) for row in rows]

    @staticmethod
    async def get_session_documents(session_id: str) -> List[dict]:
        """Return one row per document (the chunk that holds full_content)."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT ON (filename) id, filename, full_content AS content
                FROM document_chunks
                WHERE session_id = $1 AND full_content IS NOT NULL
                ORDER BY filename, id
                """,
                session_id
            )
            return [dict(row) for row in rows]

    @staticmethod
    async def delete_document(document_id: str):
        """Delete all chunks belonging to the same filename as the given chunk id."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT filename, session_id FROM document_chunks WHERE id = $1", document_id
            )
            if row:
                await conn.execute(
                    "DELETE FROM document_chunks WHERE filename = $1 AND session_id = $2",
                    row["filename"], row["session_id"]
                )

    @staticmethod
    async def reindex_documents() -> dict:
        """Re-generate embeddings for all chunks that have a null embedding."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, content FROM document_chunks WHERE embedding IS NULL"
            )

        if not rows:
            return {"message": "All documents already indexed.", "reindexed": 0}

        texts = [r["content"] for r in rows]
        embeddings = await embedding_service.get_embeddings(texts)

        if not embeddings or len(embeddings) != len(rows):
            return {"message": "Failed to generate embeddings.", "reindexed": 0}

        async with pool.acquire() as conn:
            await conn.executemany(
                "UPDATE document_chunks SET embedding = $1::vector WHERE id = $2",
                [(str(embeddings[i]), rows[i]["id"]) for i in range(len(rows))]
            )

        return {"message": f"Re-indexed {len(rows)} chunks.", "reindexed": len(rows)}


document_service = DocumentService()
