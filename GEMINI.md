# GEMINI.md

## Project Overview

**Luminate Backend** is an AI-powered platform designed for persona-based chat and document analysis. It enables users to interact with AI agents that mimic specific celebrity personalities by blending static personality profiles with real-time data from social media. Additionally, it provides a document analysis workflow for querying uploaded files (PDF, DOCX).

### Core Technologies
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python)
- **Agent Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) (Stateful, multi-node agents)
- **LLM**: [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index) (Mistral, Llama, and other models)
- **Database**: [Neon DB](https://neon.tech/) (PostgreSQL)
- **Data Scraping**: [Apify](https://apify.com/) (Twitter/X scraping)
- **Document Processing**: PyPDF, python-docx, LangChain Text Splitters

### Key Components
- **Persona Agent**: A LangGraph agent that fetches celebrity profiles from the database and fresh tweets from Apify, then generates a response in the celebrity's voice using a Hugging Face LLM.
- **Document Agent**: Handles file uploads and provides a specialized chat interface for document-based Q&A.
- **Services**: Modular services for LLM interactions (`llm_service.py`), database operations (`session_service.py`), tweet fetching (`tweet_service.py`), and document management (`document_service.py`).

---

## Building and Running

### Prerequisites
- Python 3.10+
- A [Neon DB](https://neon.tech/) PostgreSQL instance
- A [Hugging Face](https://huggingface.co/) API key
- An [Apify](https://apify.com/) API key (for real-time tweets)

### Setup
1. **Clone and Install**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file based on `.env.example`:
   ```env
   DATABASE_URL=postgresql://...
   HUGGINGFACE_API_KEY=hf_...
   HUGGINGFACE_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
   APIFY_API_KEY=apify_api_...
   APP_ENV=development
   ```

3. **Database Schema**:
   Run the SQL commands in `schema.sql` against your Neon DB instance to set up the necessary tables.

### Execution
- **Start the Server**:
  ```bash
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Access API Docs**:
  Navigate to `http://localhost:8000/docs` for the interactive Swagger documentation.

### Testing
The project includes several verification scripts:
- `test_full_flow.py`: Tests the complete persona agent workflow including tweet scraping.
- `test_document_agent.py`: Tests document upload and analysis.
- `test_dynamic_doc_flow.py`: Interactive test for document-based chat.
- `test_health.py`: Simple health check for the API.

---

## Development Conventions

### Agent Development (LangGraph)
- **State Management**: Agents use a `TypedDict` (e.g., `AgentState`) to pass context between nodes.
- **Node Design**: Each step in an agent's logic (fetching data, generating LLM response, saving to DB) should be implemented as an independent async function (node).
- **Graph Definition**: Define and compile the agent graph using `StateGraph` in the `app/agents/` directory.

### Code Style & Patterns
- **Asynchronous First**: All I/O-bound operations (DB, external APIs) must be `async`.
- **Pydantic Models**: Use schemas defined in `app/models/schemas.py` for request validation and response serialization.
- **Service Layer**: Logic should be encapsulated in `app/services/` to keep routers thin and maintainable.
- **Logging**: Use print statements or a logging library (if configured) within agent nodes to track the execution flow, especially during the long-running scraping steps.

### Contribution Guidelines
- **Environment Safety**: Never commit `.env` files or hardcode secrets.
- **Test Before Commit**: Ensure `test_full_flow.py` and `test_health.py` pass before submitting changes.
- **Schema Updates**: If you modify the database structure, update `schema.sql` and `CONFIGURATION_CHANGES.md`.
