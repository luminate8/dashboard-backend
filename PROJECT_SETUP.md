# 🚀 Luminate Backend - Project Setup & Configuration

## Project Overview

**Type**: AI Persona Chat Agent + Document Analysis Backend
**Purpose**: Respond like user's chosen celebrities using stored personality data + real-time tweets

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | Async web framework |
| **Agent** | LangGraph | Stateful multi-node AI agents |
| **Database** | Neon DB (PostgreSQL) | Serverless SQL database |
| **LLM** | Hugging Face Inference API | AI language model |
| **Twitter Data** | Apify | Real-time tweet scraping |

---

## Current Configuration ✅

### 1. **Database** - CONFIGURED
```
DATABASE_URL = postgresql://...@neon.tech
Status: ✅ Ready
```

### 2. **Hugging Face LLM** - CONFIGURED
```
HUGGINGFACE_API_KEY = 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
HUGGINGFACE_MODEL = mistralai/Mixtral-8x7B-Instruct-v0.1
Status: ✅ Ready
API Endpoint: https://router.huggingface.co/v1/chat/completions
```

### 3. **Twitter Scraping** - CONFIGURED
```
APIFY_API_KEY = apify_api_ja5hRY0LrXxNKlBK3ntNPO1qWR3UN93cRDTx
TWITTER_SCRAPER_ACTOR_ID = apidojo/twitter-scraper-lite
Status: ✅ Ready (PAID, stable, recommended)
```

---

## Mistral AI Model Options

### Current Model (Recommended for Power)
- **Model**: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Params**: 8x7B mixture-of-experts
- **Cost**: Higher but better quality responses
- **Speed**: Moderate
- **Use Case**: When quality matters more than speed

### Alternative Model (Recommended for Speed/Cost)
- **Model**: `mistralai/Mistral-7B-Instruct-v0.3`
- **Params**: 7B
- **Cost**: Lower, faster
- **Speed**: Fast
- **Use Case**: For faster responses with good quality

### Other HF Options
- `Qwen/Qwen2.5-72B-Instruct` - Very powerful
- `meta-llama/Llama-3.2-3B-Instruct` - Lightweight
- `microsoft/Phi-3-mini-4k-instruct` - Compact

---

## Available Test Scripts

### 1. Full Flow Test (Persona Agent + Real Tweets)
```bash
python test_full_flow.py
```
**Tests**: 
- Session creation
- Persona agent with Apify real tweets
- Chat response generation

**Requirements**:
- Server running (`uvicorn main:app --reload`)
- Apify API key configured
- HF API key configured

**Time**: 30-60 seconds (Apify scraping)

---

### 2. Document Agent Test (File Upload + Analysis)
```bash
python test_document_agent.py
```
**Tests**:
- Session creation
- Document upload
- Document analysis chatbot

**Requirements**:
- Server running
- HF API key configured
- Document upload endpoint working

**Time**: 10-20 seconds

---

### 3. Dynamic Document Test (Interactive)
```bash
python test_dynamic_doc_flow.py
```
**Tests**:
- Interactive file upload
- Multi-turn conversation with documents

**Requirements**:
- Server running
- User provides file path

**Time**: Variable

---

## Setup Steps

### Step 1: Install Dependencies
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure .env
Already configured with:
- ✅ `DATABASE_URL` - Neon DB
- ✅ `HUGGINGFACE_API_KEY` - Your HF token
- ✅ `HUGGINGFACE_MODEL` - Mistral AI
- ✅ `APIFY_API_KEY` - Twitter scraper
- ✅ `APP_ENV` - development

### Step 3: Start Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Step 4: Run Tests
In another terminal:
```bash
# Test 1: Full flow with personas
python test_full_flow.py

# Test 2: Document agent
python test_document_agent.py

# Test 3: Dynamic documents (interactive)
python test_dynamic_doc_flow.py
```

---

## API Endpoints

### Sessions
- `POST /api/session` - Create new session
- `GET /api/session/{id}` - Get session details

### Chat
- `POST /api/chat` - Chat with persona agent

### Documents
- `POST /api/documents/upload` - Upload file
- `GET /api/documents/{session_id}` - List documents
- `DELETE /api/documents/{doc_id}` - Delete document

### Document Chat
- `POST /api/doc-chat` - Chat with document analyst

### Health
- `GET /health` - Health check

---

## Database Schema

### celebrities_profiles
Pre-stored personality data (auto-seeded):
- Elon Musk, Lionel Messi, Cristiano Ronaldo
- Taylor Swift, Oprah Winfrey, Dwayne Johnson
- Stephen Hawking

### sessions
User sessions with selected personas

### messages
Conversation history

### documents
Uploaded files with extracted content

---

## Pre-configured Celebrities

| Celebrity | Style |
|-----------|-------|
| **Elon Musk** | Direct, sarcastic, tech-obsessed, memes |
| **Lionel Messi** | Humble, quiet, family-focused, football |
| **Cristiano Ronaldo** | Confident, disciplined, motivational |
| **Taylor Swift** | Poetic, emotional, storytelling |
| **Oprah Winfrey** | Warm, inspiring, wisdom-focused |
| **Dwayne Johnson** | Upbeat, motivational, gratitude |
| **Stephen Hawking** | Philosophical, curious, science-focused |

---

## Cost Saving Strategy

Why this stack is cheaper than OpenAI:

| Item | OpenAI | This Stack |
|------|--------|-----------|
| LLM | $10-50/month | Your HF plan (prepaid) |
| Personality Data | Every call | Stored in DB (free) |
| Tweet Data | Every call | Only when needed |
| Auth/Overhead | Complex | Minimal |

**Key insight**: Pre-stored profiles + selective API calls = huge savings

---

## Troubleshooting

### HF API not responding
- Check `HUGGINGFACE_API_KEY` is valid
- Verify model name is correct
- Check API rate limits

### Apify scraping fails
- Verify `APIFY_API_KEY` is valid
- Check Apify dashboard for quota
- Fallback to stored personality data (always works)

### Documents not uploading
- Check file permissions
- Verify `DATABASE_URL` is accessible
- Check document size limits

---

## Next Steps

1. ✅ Review configuration
2. ⏳ Run `test_full_flow.py` to test personas
3. ⏳ Run `test_document_agent.py` to test documents
4. ⏳ Integrate with frontend

---

**Status**: 🟢 All systems configured and ready for testing
**Last Updated**: April 17, 2026
