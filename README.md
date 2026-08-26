# AgriVLA

**Closed-Loop Vision-Language Agent for Adaptive Agricultural Decision Making**

## 1. Overview
AgriVLA is an end-to-end, closed-loop Vision-Language Agent (VLA) designed to perform adaptive agricultural decision-making. Unlike static disease classifiers, AgriVLA maintains an explicit internal state, queries a vectorized agricultural knowledge base, plans actions with safety constraints, and adapts to environment feedback in a continuous loop.

## 2. Problem Statement
Traditional agricultural AI systems rely on static image classification ("one-shot" prediction). When these systems are deployed in dynamic environments, they fail to adapt if an initial diagnosis is incorrect or a treatment fails, leading to crop loss or unsafe chemical application.

## 3. Research Objective
To design, implement, and evaluate a closed-loop agentic architecture where visual perception acts as just one sensor within a broader decision-making pipeline, enabling failure recovery and adaptive strategy shifts through environmental feedback.

## 4. Why Agriculture
Agriculture represents a high-stakes, dynamic environment where visual symptoms (e.g., leaf blight, water stress) evolve over time and treatments have delayed, measurable consequences, making it the ideal testbed for closed-loop embodied AI.

## 5. Why Vision-Language Models
Vision-Language Models (VLMs) like Gemini Flash provide zero-shot semantic understanding of complex visual scenes without requiring thousands of manually annotated bounding boxes, allowing the agent to extract structured reasoning directly from raw pixels.

## 6. Why an Agent
A static classifier stops at diagnosis. An *agent* can query knowledge bases (RAG), validate safety policies, execute treatments, observe the results, and dynamically correct its own course when a previous intervention fails.

## 7. System Architecture
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
         │ Validated Action
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
    └────────────┘
```

## 8. End-to-End Data Flow
1. **Observe**: Receives visual input.
2. **Perceive**: VLM translates pixels to structured JSON (condition, severity, confidence).
3. **Retrieve**: RAG finds treatments based on condition.
4. **Plan**: Selects action (e.g., `RECOMMEND_TREATMENT`).
5. **Validate**: Safety rules check confidence thresholds.
6. **Execute**: Simulates action impact on environment.
7. **Evaluate**: Calculates reward based on severity reduction.
8. **Adapt**: State updates (trend, failure counts) guide next step.

## 9. Perception Architecture
Implemented via `app/perception/`. A `QualityAssessor` first evaluates image viability. Viable images pass to the `GeminiProvider`, which uses async HTTP requests to the Gemini 1.5 Flash API to extract a `PerceptionResult` (crop, condition, severity, confidence).

## 10. State Representation
Managed by `app/state/tracker.py`. Explicitly tracks:
- `step_number`, `crop`, `condition`, `severity`, `confidence`
- `action_history`, `feedback_history`
- `failure_count`, `trend` (IMPROVING, DETERIORATING, STAGNANT)

## 11. Action Space
Closed, strictly typed space:
- `OBSERVE`, `REQUEST_NEW_IMAGE`, `MONITOR`, `WATER`, `RECOMMEND_TREATMENT`, `CHANGE_TREATMENT`, `ESCALATE`, `STOP`

## 12. Action Validation
Managed by `app/validation/validator.py`. Deterministic rules override the planner. For example, if VLM confidence < 50%, the validator intercepts any treatment action and forces `REQUEST_NEW_IMAGE` or `ESCALATE`.

## 13. Environment Simulator
`app/environment/simulator.py`. Maintains hidden ground truth variables (health, disease_severity). State transitions are deterministic: e.g., correct treatments reduce severity, incorrect treatments increase it.

## 14. Feedback Mechanism
`app/feedback/evaluator.py`. Computes numeric rewards and classifies outcomes as `SUCCESS`, `FAILURE`, or `NO_CHANGE`. Repeated failures trigger the `StateTracker` to mark `DETERIORATING`, forcing the Planner to try alternative actions.

## 15. RAG Architecture
`app/knowledge/retrieval.py`.
- **Embedder**: `fastembed` (SentenceTransformers, ONNX-based, CPU-friendly)
- **Vector Store**: Qdrant Vector DB
- **Retrieval**: `query_points()` matching agent state to agricultural interventions.

## 16. Model Selection
- **Primary VLM**: Google Gemini 1.5 Flash (`gemini-1.5-flash`). Chosen for its superior reasoning quality, native JSON schema support, and async REST speed. (No local GPU required).

## 17. Dataset and Scenario Design
Stored in `backend/data/scenarios/`. Scenarios define initial environment states (e.g., Severe Corn Blight) and hidden ground truths against which the agent's decisions are evaluated.

## 18. Repository Structure
```
agrivla/
├── backend/
│   ├── app/ (api, auth, domain, environment, knowledge, orchestration, etc.)
│   ├── data/ (knowledge JSONs, scenarios)
│   ├── evaluation/ (harness, ablation)
│   └── tests/ (unit, integration, security)
├── frontend/ (React, TypeScript, Vite)
└── docker-compose.yml (Redis, MongoDB, Qdrant)
```

## 19. Requirements
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Gemini API Key

## 20. Installation
```bash
git clone <repo>
cd agrivla
```

## 21. Environment Configuration
Copy `.env.example` to `.env` in `backend/`:
```env
MODEL_NAME=gemini-1.5-flash
GEMINI_API_KEY=your_actual_key
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
VECTOR_STORE_URL=http://localhost:6333
JWT_SECRET_KEY=supersecret
```

## 22. Model Setup
No local weights to download. The system relies entirely on the Gemini API. Ensure your `GEMINI_API_KEY` in `.env` is valid and active.

## 23. Knowledge Base Setup
```bash
cd backend
python scripts/ingest_knowledge.py
```
This chunks and embeds `knowledge_data.json` into the Qdrant DB.

## 24. Database Setup
```bash
docker compose up -d
cd backend
python -m app.persistence.mongodb.initialize
```

## 25. Running Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```
Available at `http://localhost:8000`

## 26. Running Frontend
```bash
cd frontend
npm install
npm run dev
```
Available at `http://localhost:5173`

## 27. Running End-to-End Demo
Use the frontend UI (`http://localhost:5173`) to create an Agent Session, upload a crop image, and click "Run Step" to observe the full closed-loop trajectory live.

## 28. Running Tests
```bash
cd backend
pytest tests/ -v
```

## 29. Running Evaluation
```bash
cd backend
python -m evaluation.harness
```
Outputs measurable performance metrics across scenarios.

## 30. Running Ablation Studies
```bash
cd backend
python -m evaluation.ablation
```
Compares `FULL_SYSTEM` against `NO_VALIDATION`, `NO_RAG`, and `LOW_CONF_THRESHOLD`.

## 31. Interpreting Results
Evaluation results are saved to `backend/data/eval_results.json` and `ablation_summary.json`. Look for:
- **Success Rate**: % of goals achieved safely.
- **SafetyViols**: Number of safety policy violations (should be 0 for FULL_SYSTEM).

## 32. API Documentation
Swagger documentation is automatically generated.
Start the backend and visit: `http://localhost:8000/docs`

## 33. Failure Recovery
The agent demonstrates recovery by explicitly tracking `failure_count`. If a treatment yields a `FAILURE` feedback loop, the Planner uses this state to issue a `CHANGE_TREATMENT` action or `ESCALATE`.

## 34. Safety
Deterministic safety rules override VLM hallucinations. `ActionValidator` unconditionally intercepts low-confidence inferences and unsafe chemical applications.

## 35. Limitations
- **Perception Latency**: Cloud API calls take 2-4 seconds.
- **Simulator Ground Truth**: The environment simulator relies on heuristic transitions, not actual biophysical modeling.
- **Image Dependency**: The agent is bounded by the visual quality of the provided image.

## 36. Reproducibility
Evaluation runs seed all random components. Explicit trajectory tracking ensures every decision can be replayed and audited via the `TrajectoryRepository`.

## 37. Future Work
- Integration with live drone feeds instead of static image uploads.
- Replacing the Cloud VLM with a fine-tuned, localized small Vision Model (e.g., Qwen-VL) to remove network latency.

## 38. License
MIT License.
