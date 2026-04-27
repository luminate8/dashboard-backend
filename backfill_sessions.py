"""
One-time script: links existing NULL user_id sessions to auth_users
by matching the most recent session to each user (best-effort).
Run once: python backfill_sessions.py
"""
import asyncio
import asyncpg
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from app.config import DATABASE_URL


async def backfill():
    conn = await asyncpg.connect(DATABASE_URL)

    # Show current state
    sessions = await conn.fetch("SELECT id, user_id, created_at FROM sessions ORDER BY created_at DESC")
    users = await conn.fetch("SELECT id, email FROM auth_users")

    print(f"Found {len(sessions)} sessions, {len(users)} users")
    print("\nSessions with NULL user_id:")
    for s in sessions:
        if s["user_id"] is None:
            print(f"  {s['id']} — created {s['created_at']}")

    print("\nUsers:")
    for u in users:
        print(f"  {u['id']} — {u['email']}")

    if len(users) == 1 and any(s["user_id"] is None for s in sessions):
        # Single user: link all NULL sessions to them
        user_id = users[0]["id"]
        updated = await conn.execute(
            "UPDATE sessions SET user_id = $1 WHERE user_id IS NULL",
            user_id
        )
        print(f"\nLinked all NULL sessions to {users[0]['email']}: {updated}")
    else:
        print("\nMultiple users found. Provide email to link sessions:")
        email = input("Enter email to link NULL sessions to: ").strip()
        user = await conn.fetchrow("SELECT id FROM auth_users WHERE email = $1", email)
        if not user:
            print("User not found.")
        else:
            updated = await conn.execute(
                "UPDATE sessions SET user_id = $1 WHERE user_id IS NULL",
                user["id"]
            )
            print(f"Linked: {updated}")

    await conn.close()


asyncio.run(backfill())
