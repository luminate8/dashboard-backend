import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

async def main():
    from app.services.embedding_service import embedding_service
    from app.services.document_service import document_service, _chunk_text
    from app.db.database import get_pool

    content = "Ketamine therapy is used to treat treatment-resistant depression. A typical session lasts 40-60 minutes under medical supervision. Patients may experience mild dissociation during the infusion. The recommended protocol is often 6 infusions over 2-3 weeks."

    chunks = _chunk_text(content)
    print(f"Chunks: {len(chunks)}")

    embeddings = await embedding_service.get_embeddings(chunks)
    print(f"Embeddings: {len(embeddings)}, dims: {len(embeddings[0]) if embeddings else 0}")

    pool = await get_pool()
    async with pool.acquire() as conn:
        # Insert directly
        data = [("test.txt", chunks[i], str(embeddings[i])) for i in range(len(chunks))]
        await conn.executemany(
            "INSERT INTO document_chunks (file_name, content, embedding) VALUES ($1, $2, $3::vector)",
            data
        )
        count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
        print(f"Chunks in DB: {count}")

    results = await document_service.search_relevant_chunks("How long does a typical session last?", limit=3)
    print(f"Search results: {len(results)}")
    for r in results:
        print(f"  dist={r['distance']:.4f} | {r['content'][:80]}")

asyncio.run(main())
