# AgriVLA

**Closed-Loop Vision-Language Agent for Adaptive Agricultural Decision Making**

---

## Architecture Overview

```
Image Input
    │
    ▼
┌─────────────────┐
│ QualityAssessor │  ← Deterministic: checks resolution, brightness
└────────┬────────┘
         │
    ┌────▼────┐
    │ Gemini API│  ← Cloud Vision-Language Model
    └────┬────┘
         │ PerceptionResult
    ┌────▼────┐
    │StateTracker│ ← Tracks observation history, trends, failures
    └────┬────┘
         │ AgentState
    ┌────▼─────┐
    │RAGRetriever│ ← Qdrant + SentenceTransformers
    └────┬─────┘
         │ Evidence
    ┌────▼──────┐
    │ActionPlanner│ ← Closed action space heuristics
    └────┬──────┘
         │ ActionProposal
    ┌────▼─────────┐
    │ActionValidator│ ← Hard safety rules (independent of planner)
    └────┬─────────┘
         │ Validated/Overridden Action
    ┌────▼────────┐
    │ActionExecutor│ ← Applies to AgriculturalEnvironment
    └────┬────────┘
         │ EnvironmentState
    ┌────▼──────────┐
    │FeedbackEvaluator│ ← Reward + result classification
    └────┬──────────┘
         │ FeedbackResult
    ┌────▼───────┐
    │StateTracker│ ← Updates trend, failure_count, step_number
    └────┬───────┘
         │ Updated AgentState
    ┌────▼──────────────────┐
    │TrajectoryRepository   │ ← Persists full auditable step to MongoDB
    └───────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ (for frontend)
- No local GPU required (Uses Gemini Cloud API for vision processing)
- **Infrastructure Services (MUST BE RUNNING FIRST):**
  - **MongoDB** (running on port 27017)
  - **Redis** (running on port 6379)
  - **Qdrant Vector DB** (running on port 6333)

### 1. Start Infrastructure
Make sure your infrastructure services are running before proceeding. 
If you are using Docker, you can start MongoDB and Redis from the root directory:
```powershell
cd C:\Users\Hailsha\.gemini\antigravity-ide\scratch\agrivla
docker compose up -d
```
*Note: Make sure your Qdrant server (`qdrant.exe`) is running in the background as well!*

### 2. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -e .

# Ingest agricultural knowledge into Qdrant
python scripts/ingest_knowledge.py

# Initialize MongoDB indexes
python -m app.persistence.mongodb.initialize

# Start API server
uvicorn app.main:app --reload
```
API will be available at `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

### 3. Frontend Setup
```powershell
# Open a new terminal
cd C:\Users\Hailsha\.gemini\antigravity-ide\scratch\agrivla\frontend
npm install
npm run dev
```
App will be available at `http://localhost:5173`

### 4. Run Tests
```powershell
cd backend
# Unit + Integration + Security tests
python -m pytest tests/ -v

# Evaluation harness (no VLM needed, uses simulated perception)
python -m evaluation.harness

# Ablation study (4 conditions)
python -m evaluation.ablation
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create account |
| `POST` | `/api/v1/auth/login` | Authenticate, receive JWT |
| `GET` | `/api/v1/auth/me` | Get current user |
| `POST` | `/api/v1/auth/logout` | Revoke session |
| `POST` | `/api/v1/agents` | Create agent session |
| `GET` | `/api/v1/agents` | List all user sessions |
| `GET` | `/api/v1/agents/{id}` | Get session info |
| `GET` | `/api/v1/agents/{id}/state` | Get latest agent state |
| `GET` | `/api/v1/agents/{id}/trajectory` | Full auditable trajectory |
| `POST` | `/api/v1/agents/{id}/step` | Execute one agent step (multipart image) |
| `GET` | `/health` | Health check |
| `GET` | `/ready` | Readiness check (DB ping) |

---

## Configuration

Copy `.env.example` to `.env` and set your values:

```env
MODEL_NAME=gemini-3.6-flash
GEMINI_API_KEY=your_api_key
MODEL_DEVICE=cuda          # or "cpu"
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<secure-random-string>
```

---

## Module Map

| Path | Description |
|------|-------------|
| `app/perception/` | QualityAssessor, Gemini provider, PerceptionEngine |
| `app/state/` | StateTracker — explicit state management |
| `app/knowledge/` | Qdrant RAG retriever, SentenceTransformers embeddings, ingestion |
| `app/planning/` | Heuristic ActionPlanner (closed action space) |
| `app/validation/` | Deterministic safety validator |
| `app/environment/` | Agricultural simulator & transition equations |
| `app/execution/` | ActionExecutor |
| `app/feedback/` | FeedbackEvaluator & RewardFunction |
| `app/orchestration/` | ClosedLoopAgent — master orchestrator |
| `app/api/` | FastAPI routes, schemas, DI dependencies |
| `app/auth/` | JWT, Argon2 password hashing, AuthService |
| `app/persistence/` | MongoDB repositories (User, Session, Agent, Trajectory) |
| `evaluation/` | Harness + Ablation runner |
| `frontend/` | React + TypeScript + Vite SPA |
| `tests/` | Unit, Integration, Security, API tests |
