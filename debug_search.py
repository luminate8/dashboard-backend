import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

async def main():
    from app.db.database import get_pool
    from app.services.document_service import document_service

    pool = await get_pool()
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks")
        print(f"Total chunks in DB: {count}")
        
        # Check last 3 chunks
        rows = await conn.fetch("SELECT file_name, content, embedding IS NOT NULL as has_emb FROM document_chunks ORDER BY created_at DESC LIMIT 3")
        for r in rows:
            print(f"  file={r['file_name']}, has_emb={r['has_emb']}, content={r['content'][:60]}")

    # Test search
    results = await document_service.search_relevant_chunks("How long does a typical session last?", limit=3)
    print(f"\nSearch results: {len(results)}")
    for r in results:
        print(f"  dist={r.get('distance', '?'):.4f} | {r['content'][:80]}")

asyncio.run(main())
