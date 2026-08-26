from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.dependencies.database import get_db
from app.persistence.mongodb.repositories.agents import AgentSessionRepository
from app.persistence.mongodb.repositories.trajectories import TrajectoryRepository
from app.orchestration.agent import ClosedLoopAgent
from app.perception.engine import PerceptionEngine
from app.perception.providers.gemini import GeminiProvider
from app.knowledge.retrieval import get_rag_retriever
from app.planning.planner import ActionPlanner
from app.validation.validator import ActionValidator
from app.execution.executor import ActionExecutor
from app.feedback.evaluator import FeedbackEvaluator
from app.environment.simulator import AgriculturalEnvironment
from app.domain.environment import EnvironmentState

def get_agent_session_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AgentSessionRepository:
    return AgentSessionRepository(db)

def get_trajectory_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> TrajectoryRepository:
    return TrajectoryRepository(db)

def get_closed_loop_agent(
    trajectory_repo: TrajectoryRepository = Depends(get_trajectory_repository)
) -> ClosedLoopAgent:
    
    # In a production setting with Dependency Injection container, these would be singletons/scoped dependencies.
    # For this MVP, we wire them up here.
    provider = GeminiProvider()
    perception_engine = PerceptionEngine(provider=provider)
    
    planner = ActionPlanner()
    validator = ActionValidator()
    
    # Initialize a dummy environment state. In a real scenario with a dataset, this would load from scenario_id
    initial_env_state = EnvironmentState(crop="tomato", health=0.6, disease="early_blight", disease_severity=0.5)
    environment = AgriculturalEnvironment(initial_state=initial_env_state)
    
    executor = ActionExecutor(environment=environment)
    evaluator = FeedbackEvaluator()
    
    return ClosedLoopAgent(
        perception_engine=perception_engine,
        rag_retriever=get_rag_retriever(),
        action_planner=planner,
        action_validator=validator,
        action_executor=executor,
        feedback_evaluator=evaluator,
        trajectory_repo=trajectory_repo
    )
