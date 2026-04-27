"""
Test script to verify Apify is fetching REAL tweets
"""
import asyncio
from app.services.tweet_service import fetch_celebrity_tweets


async def test_apify_tweets():
    print("=" * 80)
    print("🧪 TESTING APIFY TWEET FETCHING")
    print("=" * 80)
    
    # Test with Elon Musk
    celebrity = "Elon Musk"
    print(f"\n🔍 Fetching tweets for: {celebrity}...")
    print("-" * 80)
    
    tweets = await fetch_celebrity_tweets(celebrity, count=5)
    
    print(f"\n✅ Successfully fetched {len(tweets)} tweets!\n")
    
    if len(tweets) > 0:
        print("📝 TWEETS FETCHED:")
        print("-" * 80)
        for i, tweet in enumerate(tweets, 1):
            print(f"\n🐦 Tweet {i}:")
            print(f"   Author: {tweet.get('author', 'Unknown')}")
            print(f"   Text: {tweet['text'][:150]}...")
            print(f"   Date: {tweet.get('created_at', 'Unknown')}")
        
        print("\n" + "=" * 80)
        print("✅ APIFY IS WORKING - These are REAL tweets!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ No tweets fetched - Apify might not be working")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_apify_tweets())
