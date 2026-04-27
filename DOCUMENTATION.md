# Eluminate Backend - Documentation

AI Persona Chat Agent — Responds like user's chosen celebrities using their tweets and pre-stored personality data.

---

## Table of Contents
- [Tech Stack](#tech-stack)
- [Project Flow](#project-flow)
- [How the Agent Works](#how-the-agent-works)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Pre-stored Celebrities](#pre-stored-celebrities)
- [Setup & Run](#setup--run)
- [Environment Variables](#environment-variables)
- [Cost Saving Strategy](#cost-saving-strategy)
- [Project Structure](#project-structure)

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Backend | Python + FastAPI | Async, fast, industry standard |
| Agent Framework | LangGraph | Stateful multi-step AI agents |
| Database | Neon DB (PostgreSQL) | Serverless, cheap, scales well |
| LLM | Hugging Face Inference API | Uses your paid HF plan, no OpenAI costs |
| Twitter Data | TwitterAPI.io (or mock) | Cheap third-party, official X API too expensive |

---

## Project Flow

```
1. Frontend Welcome Screen
   User answers:
   → "Who is your ideal person?"     (e.g., Elon Musk)
   → "Who is your favourite?"        (e.g., Lionel Messi)
   → "Which celebrity to talk to?"   (e.g., Cristiano Ronaldo)

2. POST /api/session
   Backend saves these names to DB → returns session_id

3. User sends a chat message
   POST /api/chat { session_id, message }

4. LangGraph Agent runs (4 nodes):
   Node 1 → Fetch stored personality profiles from DB (free, always available)
   Node 2 → Fetch fresh tweets from Twitter API (optional, real-time)
   Node 3 → Generate reply (combines personality + tweets → calls HuggingFace LLM)
   Node 4 → Save conversation to DB

5. Response sent back to frontend
   AI replies in the exact voice/style of chosen celebrities
```

---

## How the Agent Works

The LangGraph agent combines **two data sources** to generate authentic responses:

### Source 1: Pre-stored Personality Data (Free, Always Available)
Each celebrity has stored:
- **Personality traits**: How they think, what drives them
- **Speaking style**: Sentence structure, tone, word choices, emoji usage
- **Common topics**: What they usually talk about
- **Example quotes**: Things they've actually said

This data **never expires** because personality traits don't change.

### Source 2: Fresh Tweets (Real-time, Costs Money)
- Fetches last 10 tweets per celebrity from Twitter API
- Gives the AI **current events and recent opinions**
- If Twitter API is unavailable, the agent still works using stored data

### Combined Prompt to LLM
```
You are now role-playing as Elon Musk and Lionel Messi.

--- ELON MUSK ---
Personality: Visionary, direct, sarcastic humor, tech-obsessed...
Speaking Style: Short punchy sentences, uses ellipses...
Common Topics: SpaceX, Mars, Tesla, AI, cryptocurrency...
Examples:
  - "Mars is the next giant leap for humanity."
  - "The point of SpaceX is to build a self-sustaining city on Mars."

--- LIONEL MESSI ---
Personality: Humble, quiet, family-oriented, dedicated...
Speaking Style: Humble and grateful, short answers...
Common Topics: Football, World Cup, Argentina, family...
Examples:
  - "The World Cup was the biggest moment of my career."

RECENT TWEETS (fresh data):
[Elon Musk] "Just launched another rocket..."
[Lionel Messi] "Grateful for the fans..."

IMPORTANT RULES:
- Stay completely in character
- Use their stored personality traits AND speaking style
- Blend fresh tweets with stored personality
- Never break character or mention you are an AI

Respond to the user as Elon Musk and Lionel Messi would.
```

---

## API Endpoints

### 1. Create Session (Welcome Screen)
```
POST /api/session
Content-Type: application/json

{
  "ideal_person": "Elon Musk",
  "favourite_celebrity": "Lionel Messi",
  "celebrity_to_talk": null
}

Response (200):
{
  "id": "b2255e4c-df9b-4889-b07c-0b487e638401",
  "ideal_person": "Elon Musk",
  "favourite_celebrity": "Lionel Messi",
  "celebrity_to_talk": null,
  "created_at": "2026-04-08T18:51:51.501111Z"
}
```

### 2. Get Session
```
GET /api/session/{session_id}

Response (200):
{
  "id": "b2255e4c-df9b-4889-b07c-0b487e638401",
  "ideal_person": "Elon Musk",
  "favourite_celebrity": "Lionel Messi",
  "celebrity_to_talk": null,
  "created_at": "2026-04-08T18:51:51.501111Z"
}
```

### 3. Chat with Agent
```
POST /api/chat
Content-Type: application/json

{
  "session_id": "b2255e4c-df9b-4889-b07c-0b487e638401",
  "message": "Hey, what do you think about going to Mars?"
}

Response (200):
{
  "session_id": "b2255e4c-df9b-4889-b07c-0b487e638401",
  "response": "Mars is the future! We have to become a multiplanetary species...",
  "personas": ["Elon Musk", "Lionel Messi"]
}
```

### 4. Health Check
```
GET /health

Response (200):
{
  "status": "ok",
  "message": "Backend is running"
}
```

---

## Database Schema

### `sessions`
Stores user session from welcome screen.
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| ideal_person | TEXT | User's ideal person |
| favourite_celebrity | TEXT | User's favourite celebrity |
| celebrity_to_talk | TEXT | Additional celebrity to talk to |
| created_at | TIMESTAMPTZ | When session was created |
| updated_at | TIMESTAMPTZ | Last updated |

### `celebrity_profiles`
Pre-stored personality data (seeded on startup, one-time).
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| name | TEXT | Celebrity name (unique) |
| personality_traits | TEXT | How they think, what drives them |
| speaking_style | TEXT | Sentence structure, tone, style |
| common_topics | TEXT | What they usually discuss |
| sample_tweets | JSONB | Array of example quotes/tweets |
| last_updated | TIMESTAMPTZ | When profile was last updated |

### `messages`
Stores conversation history.
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| session_id | UUID | References sessions(id) |
| role | TEXT | "user" or "assistant" |
| content | TEXT | Message text |
| created_at | TIMESTAMPTZ | When message was sent |

### `persona_configs`
Stores fetched tweet data for each persona (optional use).
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| session_id | UUID | References sessions(id) |
| persona_name | TEXT | Celebrity name |
| tweets | JSONB | Array of fetched tweets |
| persona_traits | TEXT | Additional traits |
| created_at | TIMESTAMPTZ | When config was created |
| updated_at | TIMESTAMPTZ | Last updated |

---

## Pre-stored Celebrities

These 7 profiles are automatically seeded into the database on startup:

| Celebrity | Style |
|---|---|
| **Elon Musk** | Direct, sarcastic, tech-obsessed, uses memes, talks about Mars/SpaceX/Tesla |
| **Lionel Messi** | Humble, quiet, family-focused, talks about football and World Cup |
| **Cristiano Ronaldo** | Confident, disciplined, motivational, uses "SIUUU", talks about hard work |
| **Taylor Swift** | Poetic, emotional, storytelling, talks about music and memories |
| **Oprah Winfrey** | Warm, inspiring, wise, talks about purpose and self-improvement |
| **Dwayne Johnson** | Upbeat, motivational, talks about hard work and gratitude |
| **Stephen Hawking** | Deep, philosophical, curious, talks about the universe and science |

To add more celebrities, edit `app/utils/celebrity_profiles.py` and add a new entry.

---

## Setup & Run

### Prerequisites
- Python 3.11+
- Neon DB account (free)
- Hugging Face account (you have paid)
- (Optional) TwitterAPI.io account for real tweets

### Step 1: Clone and Setup
```bash
cd eluminate-backend
python -m venv venv
.\venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Step 2: Configure Environment
Copy `.env.example` to `.env` and fill in your keys:
```env
DATABASE_URL=postgresql://user:password@your-neon-db-host.neon.tech/dbname
HUGGINGFACE_API_KEY=hf_your_key_here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.3
TWITTER_API_KEY=your_twitter_api_key_here   # Optional
APP_ENV=development
```

### Step 3: Run Server
```bash
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server starts at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Step 4: Test
```bash
# Health check
curl http://localhost:8000/health

# Create session
curl -X POST http://localhost:8000/api/session \
  -H "Content-Type: application/json" \
  -d '{"ideal_person":"Elon Musk","favourite_celebrity":"Lionel Messi"}'

# Chat (use the session_id from previous response)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"YOUR_SESSION_ID","message":"What do you think about Mars?"}'
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Neon DB connection string |
| `HUGGINGFACE_API_KEY` | Yes | Your HF API key (hf_xxxxx) |
| `HUGGINGFACE_MODEL` | No | Model to use (default: Mistral-7B-Instruct) |
| `TWITTER_API_KEY` | No | Twitter API key (mock tweets if not set) |
| `APP_ENV` | No | `development` or `production` |

---

## Cost Saving Strategy

### How this saves money vs OpenAI:

| Component | OpenAI Cost | This Stack Cost |
|---|---|---|
| LLM | $10-50/month | Your paid HF plan (already paid) |
| Personality Data | Every call needs full context | Stored in DB (free) |
| Tweet Data | Every call = API hit | Only fetched when needed |
| No Auth Needed | Adds complexity | Skipped (not needed) |

### Pre-stored profiles = cheaper:
- Without profiles: AI has no data → needs tweets every time → expensive
- With profiles: Personality always in DB → tweets are bonus → much cheaper
- Even if Twitter API fails, AI still responds in character using stored data

---

## Project Structure

```
eluminate-backend/
│
├── app/
│   ├── agents/
│   │   └── persona_agent.py        # LangGraph agent (4 nodes)
│   │
│   ├── db/
│   │   └── database.py             # Neon DB connection + auto table creation + seeding
│   │
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response models
│   │
│   ├── routers/
│   │   ├── sessions.py             # POST /api/session, GET /api/session/{id}
│   │   └── chat.py                 # POST /api/chat
│   │
│   ├── services/
│   │   ├── llm_service.py          # HuggingFace LLM calls with fallback
│   │   ├── session_service.py      # DB operations (sessions, messages)
│   │   ├── profile_service.py      # Get stored celebrity profiles from DB
│   │   └── tweet_service.py        # Fetch tweets (or mock if no API key)
│   │
│   ├── utils/
│   │   └── celebrity_profiles.py   # Pre-stored personality data for 7 celebrities
│   │
│   └── config.py                   # Environment variable loader
│
├── main.py                         # FastAPI app entry point + CORS + lifespan
├── requirements.txt                # Python dependencies
├── .env                            # Your secrets (not committed to git)
├── .env.example                    # Template for .env
├── schema.sql                      # Reference SQL (for documentation)
└── README.md                       # Quick start guide
```

---

## Adding More Celebrities

Edit `app/utils/celebrity_profiles.py` and add a new entry:

```python
CELEBRITY_PROFILES = {
    # ... existing entries ...
    
    "new celebrity name": {
        "name": "Display Name",
        "personality_traits": "Trait1, trait2, trait3...",
        "speaking_style": "How they speak, sentence structure, tone...",
        "common_topics": "Topic1, topic2, topic3...",
        "sample_tweets": [
            "Quote 1",
            "Quote 2",
            "Quote 3",
            "Quote 4",
            "Quote 5",
            "Quote 6",
            "Quote 7",
        ]
    },
}
```

Restart the server — the new profile auto-seeds into the database.

---

## Deployment

For production deployment:

1. **Change CORS origins** in `main.py` from `["*"]` to your frontend URL
2. **Set APP_ENV=production** in `.env`
3. **Deploy options:**
   - Railway (easiest)
   - Render
   - DigitalOcean App Platform
   - Your own server
4. **Use a dedicated Hugging Face Inference Endpoint** for faster responses (optional, costs $0.60/hr)





mistralai/Voxtral-4B-TTS-2603
Text-to-Speech
•
Updated 17 days ago
•
7.69k
•
744
mistralai/Voxtral-Mini-4B-Realtime-2602
Automatic Speech Recognition
•
4B
•
Updated Mar 11
•
890k
•
826
mistralai/Mistral-7B-Instruct-v0.3
7B
•
Updated Dec 3, 2025
•
2.32M
•
2.53k
dphn/Dolphin-Mistral-24B-Venice-Edition
Text Generation
•
24B
•
Updated 1 day ago
•
85.4k
•
•
491
mistralai/Mixtral-8x7B-Instruct-v0.1
47B
•
Updated Jul 24, 2025
•
589k
•
4.67k
mistralai/Mistral-7B-v0.1
Text Generation
•
7B
•
Updated Jul 24, 2025
•
883k
•
4.08k
mistralai/Mistral-7B-Instruct-v0.2
Text Generation
•
7B
•
Updated Jul 24, 2025
•
2.17M
•
•
3.12k
mistralai/Voxtral-Small-24B-2507
Audio-Text-to-Text
•
24B
•
Updated Dec 21, 2025
•
28.9k
•
484
mistralai/Devstral-Small-2-24B-Instruct-2512
24B
•
Updated Feb 25
•
279k
•
586
mistralai/Mistral-Small-4-119B-2603
119B
•
Updated 23 days ago
•
81.7k
•
355
mistralai/Mistral-Nemo-Instruct-2407
Updated Jul 28, 2025
•
121k
•
1.67k
mistralai/Voxtral-Mini-3B-2507
5B
•
Updated Jul 28, 2025
•
587k
•
641
mistralai/Ministral-3-3B-Instruct-2512
Updated Jan 15
•
151k
•
219
mistralai/Mistral-Small-4-119B-2603-eagle
Updated 9 days ago
•
303
•
46
mistralai/Mistral-7B-Instruct-v0.1
Text Generation
•
Updated Jul 24, 2025
•
403k
•
1.83k
bartowski/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF
Text Generation
•
22B
•
Updated Sep 26, 2024
•
3.35k
•
30
mistralai/Ministral-8B-Instruct-2410
Updated Jul 31, 2025
•
173k
•
578
mistralai/Mistral-Small-3.2-24B-Instruct-2506
Updated Dec 22, 2025
•
1.06M
•
579
unsloth/Mistral-Small-3.2-24B-Instruct-2506
Image-Text-to-Text
•
24B
•
Updated Aug 26, 2025
•
3.13k
•
•
16
mistralai/Devstral-Small-2507
Updated Aug 18, 2025
•
43.4k
•
365
mistralai/Magistral-Small-2509
24B
•
Updated Feb 23
•
17.9k
•
300
mistralai/Ministral-3-3B-Base-2512
4B
•
Updated Jan 15
•
21.8k
•
65
mistralai/Ministral-3-8B-Reasoning-2512
Updated Jan 15
•
16.8k
•
78
mistralai/Ministral-3-14B-Instruct-2512
Updated Jan 15
•
384k
•
274
mistralai/Devstral-2-123B-Instruct-2512
125B
•
Updated Feb 25
•
94.5k
•
315
mistralai/Mistral-Large-3-675B-Instruct-2512
Updated Dec 19, 2025
•
922
•
226
TheBloke/Mistral-7B-v0.1-GGUF
Text Generation
•
7B
•
Updated Sep 29, 2023
•
11k
•
275
teknium/Mistral-Trismegistus-7B
Text Generation
•
Updated Nov 12, 2023
•
1.33k
•
238
Bilic/Mistral-7B-LLM-Fraud-Detection
Text Generation
•
Updated Nov 23, 2023
•
604
•
8
TheBloke/Mistral-7B-Instruct-v0.2-GGUF