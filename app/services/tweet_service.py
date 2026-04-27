import asyncio
import logging
import httpx
from app.config import TWITTER_API_KEY, USE_TWIKIT, APIFY_API_KEY, TWITTER_SCRAPER_ACTOR_ID

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def fetch_celebrity_tweets(celebrity_name: str, count: int = 20) -> list[dict]:
    """Fetch recent tweets for a given celebrity/person.
    
    Priority:
    1. Apify (PAID - reliable, stable, officially supported)
    2. Twikit (FREE - scrapes X directly) - COMMENTED OUT
    3. TwitterAPI.io (paid, stable) - COMMENTED OUT
    4. Mock data (fallback for testing)
    """
    
    logger.info("=" * 80)
    logger.info("🔄 FETCHING TWEETS STARTED")
    logger.info(f"👤 Celebrity: {celebrity_name}")
    logger.info(f"📊 Requested count: {count}")
    logger.info("=" * 80)
    
    # Try Apify first (RELIABLE option)
    if APIFY_API_KEY and APIFY_API_KEY != "your_apify_api_key_here":
        try:
            logger.info("✅ Using Apify scraper (PAID - reliable)")
            return await _fetch_tweets_apify(celebrity_name, count)
        except Exception as e:
            logger.error(f"❌ Apify failed for {celebrity_name}: {e}")
            logger.info("⚠️  Falling back to mock tweets...")
            return _get_mock_tweets(celebrity_name, count)
    
    # Twikit integration (COMMENTED OUT - using Apify instead)
    # if USE_TWIKIT:
    #     try:
    #         return await _fetch_tweets_twikit(celebrity_name, count)
    #     except Exception as e:
    #         print(f"Twikit failed for {celebrity_name}: {e}")
    #         print("Falling back to mock tweets...")
    #         return _get_mock_tweets(celebrity_name, count)
    
    # TwitterAPI.io integration (COMMENTED OUT - using Apify instead)
    # if not TWITTER_API_KEY:
    #     # Return mock data if no API key (for testing)
    #     return _get_mock_tweets(celebrity_name, count)
    #
    # api_url = "https://twitterapi.io/api/v2/tweets"
    #
    # params = {
    #     "q": f"from:{celebrity_name.replace(' ', '')}",
    #     "count": count,
    # }
    #
    # headers = {
    #     "X-API-Key": TWITTER_API_KEY,
    # }
    #
    # async with httpx.AsyncClient() as client:
    #     try:
    #         response = await client.get(api_url, params=params, headers=headers, timeout=15)
    #         response.raise_for_status()
    #         data = response.json()
    #
    #         tweets = []
    #         for tweet in data.get("tweets", []):
    #             tweets.append({
    #                 "text": tweet.get("text", ""),
    #                 "created_at": tweet.get("created_at", ""),
    #             })
    #
    #         return tweets[:count]
    #     except Exception as e:
    #         print(f"Error fetching tweets for {celebrity_name}: {e}")
    #         return _get_mock_tweets(celebrity_name, count)
    
    # Fallback to mock tweets
    logger.warning("⚠️  No tweet scraper configured, using mock tweets")
    return _get_mock_tweets(celebrity_name, count)


async def _fetch_tweets_twikit(celebrity_name: str, count: int = 20) -> list[dict]:
    """Fetch tweets using Twikit (FREE - scrapes X directly).
    
    Note: This may break if X changes their website. Update as needed.
    
    IMPORTANT: Twikit may require authentication for some features.
    If you see authentication errors, you have two options:
    
    1. Set USE_TWIKIT=false in .env to use mock tweets (for testing)
    2. Add Twikit authentication (see comments below)
    
    To add authentication (optional):
    - Create a Twitter account
    - Use: await client.login(
          auth_info='your_username',
          password='your_password',
          email='your_email'
      )
    - Or use cookies: await client.load_cookies('cookies.json')
    """
    try:
        import twikit
        import random
        import time
        
        # Initialize client with random delay to avoid detection
        client = twikit.Client('en-US')
        
        # Optional: Add random delay (1-3 seconds) to avoid rate limiting
        delay = random.uniform(1.0, 3.0)
        print(f"Waiting {delay:.1f}s before fetching tweets...")
        await asyncio.sleep(delay)
        
        # Search for user by name
        try:
            users = await client.search_user(celebrity_name, count=1)
        except Exception as search_error:
            print(f"Search failed for {celebrity_name}: {search_error}")
            print("This might be due to X's anti-scraping measures.")
            print("Consider:")
            print("  1. Setting USE_TWIKIT=false in .env (uses mock tweets)")
            print("  2. Adding Twikit authentication (see code comments)")
            return _get_mock_tweets(celebrity_name, count)
        
        if not users:
            print(f"No user found for: {celebrity_name}")
            return _get_mock_tweets(celebrity_name, count)
        
        # Get the first user
        user = users[0]
        print(f"Found user: {user.name} (@{user.screen_name})")
        
        # Get user's tweets
        tweets = await client.get_user_tweets(user.id, 'Tweets')
        
        if not tweets:
            print(f"No tweets found for: {celebrity_name}")
            return _get_mock_tweets(celebrity_name, count)
        
        # Format tweets
        result = []
        for tweet in tweets[:count]:
            result.append({
                "text": tweet.text,
                "created_at": str(tweet.created_at) if hasattr(tweet, 'created_at') else "unknown",
            })
        
        print(f"Fetched {len(result)} tweets for {celebrity_name} using Twikit")
        return result
        
    except ImportError:
        print("Twikit not installed. Install with: pip install twikit")
        return _get_mock_tweets(celebrity_name, count)
    except Exception as e:
        print(f"Twikit error: {e}")
        raise


async def _fetch_tweets_apify(celebrity_name: str, count: int = 20) -> list[dict]:
    """Fetch tweets using Apify's apidojo/tweet-scraper (from your other working project).
    
    Actor ID: apidojo/tweet-scraper
    Docs: https://apify.com/apidojo/tweet-scraper
    
    Note: This is the exact same scraper you're using in your other project!
    """
    try:
        from apify_client import ApifyClientAsync
        
        print("\n" + "="*80)
        print("🤖 APIFY TWITTER SCRAPER - RUNNING")
        print("="*80)
        print(f"🔍 Actor: apidojo/tweet-scraper")
        print(f"👤 Searching for: {celebrity_name}")
        print(f"📊 Max tweets requested: {count}")
        print("-"*80)
        
        # Initialize Apify client
        client = ApifyClientAsync(APIFY_API_KEY)
        
        # Prepare input for apidojo/tweet-scraper (matching your other project's format)
        scraper_input = {
            "searchTerms": [celebrity_name],  # Search by celebrity name
            "maxItems": count,
            "sort": "Latest",
        }
        
        print(f"📤 Sending request to Apify API...")
        print(f"   → Search term: {celebrity_name}")
        print(f"   → Sort: Latest")
        print(f"   → Max items: {count}")
        
        # Start the actor and wait for it to finish
        print("\n⏳ Apify actor is RUNNING... (this may take 30-60 seconds)")
        print("   → Scraping tweets from X/Twitter...")
        run = await client.actor(TWITTER_SCRAPER_ACTOR_ID).call(run_input=scraper_input)
        
        print(f"✅ Apify actor COMPLETED!")
        print(f"📊 Dataset ID: {run['defaultDatasetId']}")
        print("📥 Fetching results...\n")
        
        # Fetch results
        tweets = []
        async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            if len(tweets) >= count:
                break
            
            # Extract tweet text (matching your other project's format)
            tweet_text = item.get("text") or item.get("full_text") or ""
            author = item.get("author", {}).get("userName") or "Unknown"
            
            if tweet_text:
                tweets.append({
                    "text": tweet_text,
                    "created_at": item.get("createdAt", "unknown"),
                    "author": author,
                })
        
        print("="*80)
        print(f"✅ APIFY SCRAPING COMPLETED SUCCESSFULLY")
        print(f"👤 Celebrity: {celebrity_name}")
        print(f"📊 Successfully fetched {len(tweets)} tweets")
        print(f"📝 Sample tweets:")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"   {i}. [{tweet['author']}] {tweet['text'][:100]}...")
        print("="*80 + "\n")
        
        return tweets
        
    except ImportError:
        print("\n❌ ERROR: Apify client not installed!")
        print("   Install with: pip install apify-client")
        print("   Falling back to mock tweets...\n")
        return _get_mock_tweets(celebrity_name, count)
    except Exception as e:
        print(f"\n❌ APIFY ERROR: {e}")
        print("   Falling back to mock tweets...\n")
        raise


def _get_mock_tweets(name: str, count: int) -> list[dict]:
    """Mock tweets for testing when no Twitter API key is set."""
    import random

    mock_templates = [
        f"Just had an amazing day working on something new. Big things coming soon! #excited",
        f"Thanks to everyone who supports me. You all mean the world to me. ❤️",
        f"Working hard, staying focused. The grind never stops. 💪",
        f"Life is about pushing boundaries and exploring the unknown.",
        f"Grateful for every moment. Every day is a blessing.",
        f"Always believe in yourself. If I can do it, so can you.",
        f"Big things are happening. Stay tuned. 🔥",
        f"Never give up on your dreams. Keep going no matter what.",
        f"Today was a great day. Met some amazing people and learned a lot.",
        f"The future is bright. Keep moving forward!",
    ]

    return [
        {
            "text": random.choice(mock_templates),
            "created_at": "2026-04-08",
        }
        for _ in range(count)
    ]
