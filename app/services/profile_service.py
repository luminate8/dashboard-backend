"""
Service to get pre-stored celebrity personality data from DB.
This reduces API costs — personality traits are stored once, never expire.
"""
from app.db.database import get_pool


async def get_celebrity_profile(name: str) -> dict | None:
    """Get pre-stored personality data for a celebrity by name."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM celebrity_profiles WHERE LOWER(name) = LOWER($1)",
            name.strip(),
        )
    if not row:
        return None

    return {
        "name": row["name"],
        "personality_traits": row["personality_traits"],
        "speaking_style": row["speaking_style"],
        "common_topics": row["common_topics"],
        "sample_tweets": row["sample_tweets"] if isinstance(row["sample_tweets"], list) else [],
    }


async def get_multiple_celebrity_profiles(names: list[str]) -> list[dict]:
    """Get profiles for multiple celebrities.
    Returns only the ones found in DB.
    """
    profiles = []
    for name in names:
        profile = await get_celebrity_profile(name)
        if profile:
            profiles.append(profile)
    return profiles
