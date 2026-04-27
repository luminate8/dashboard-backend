import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

async def main():
    from app.db.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT column_name, data_type, udt_name FROM information_schema.columns WHERE table_name = 'document_chunks'"
        )
        for r in rows:
            print(dict(r))
        dim = await conn.fetchrow(
            "SELECT atttypmod FROM pg_attribute JOIN pg_class ON attrelid=pg_class.oid WHERE relname='document_chunks' AND attname='embedding'"
        )
        if dim:
            print('Vector dim:', dim['atttypmod'])

asyncio.run(main())
