import logging
import time
from typing import Dict, Any, Optional

from app.domain.states import AgentState
from app.domain.actions import ActionType
from app.domain.trajectories import TrajectoryStep

from app.perception.engine import PerceptionEngine
from app.knowledge.retrieval import RAGRetriever
from app.planning.planner import ActionPlanner
from app.validation.validator import ActionValidator
from app.execution.executor import ActionExecutor
from app.feedback.evaluator import FeedbackEvaluator
from app.persistence.mongodb.repositories.trajectories import TrajectoryRepository
from app.state.tracker import StateTracker
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ClosedLoopAgent:
    """
    Orchestrates the entire Closed-Loop Vision-Language Agent pipeline.
    Ensures strict order: Observe -> Perceive -> Track -> Retrieve -> Plan -> Validate -> Act -> Evaluate -> Update.
    """
    
    def __init__(
        self,
        perception_engine: PerceptionEngine,
        rag_retriever: RAGRetriever,
        action_planner: ActionPlanner,
        action_validator: ActionValidator,
        action_executor: ActionExecutor,
        feedback_evaluator: FeedbackEvaluator,
        trajectory_repo: TrajectoryRepository
    ):
        self.perception_engine = perception_engine
        self.rag_retriever = rag_retriever
        self.action_planner = action_planner
        self.action_validator = action_validator
        self.action_executor = action_executor
        self.feedback_evaluator = feedback_evaluator
        self.trajectory_repo = trajectory_repo
        self.max_steps = settings.MAX_AGENT_STEPS

    async def step(self, user_id: str, agent_session_id: str, image_bytes: Optional[bytes] = None, observation_ref: Optional[str] = None) -> AgentState:
        """Executes exactly one step of the closed-loop process."""
        logger.info(f"Agent {agent_session_id} executing step.")
        
        # 1. Load current state — auto-initialize if missing (e.g. old sessions)
        state = await self.trajectory_repo.get_latest_state(user_id, agent_session_id)
        if not state:
            logger.warning(f"No state for {agent_session_id}, auto-initializing from session record.")
            from app.persistence.mongodb.repositories.agents import AgentSessionRepository
            from app.persistence.mongodb.connection import get_database
            db = get_database()
            agent_repo = AgentSessionRepository(db)
            session = await agent_repo.get_by_id(user_id, agent_session_id)
            if not session:
                raise ValueError(f"Agent session {agent_session_id} not found.")
            state = StateTracker.initialize_state(
                agent_id=agent_session_id,
                goal=session.goal,
                scenario_id=session.scenario_id
            )
            await self.trajectory_repo.save_latest_state(user_id, agent_session_id, state)
            
        if state.status in ["COMPLETED", "ESCALATED", "FAILED"] or state.step_number >= self.max_steps:
            logger.warning(f"Agent {agent_session_id} is in terminal state ({state.status}). Cannot step.")
            if state.step_number >= self.max_steps and state.status == "IN_PROGRESS":
                state.status = "FAILED"
                state.termination_reason = "Maximum step count reached."
                await self.trajectory_repo.save_latest_state(user_id, agent_session_id, state)
            return state

        timing = {}
        
        # Snapshot state before action for trajectory record
        state_before_dict = state.model_dump()

        # 2. Perception
        perception_result = None
        if image_bytes:
            t0 = time.time()
            perception_result = await self.perception_engine.observe(image_bytes)
            timing["perception_ms"] = (time.time() - t0) * 1000
            
            # 3. State Update (Observation)
            state = StateTracker.update_from_observation(state, perception_result, observation_ref)

        # 4. Knowledge Retrieval
        t0 = time.time()
        evidence = []
        if state.condition and state.condition != "unknown":
            # Formulate query based on condition
            query = f"Treatment and management for {state.condition} on {state.crop}"
            evidence = self.rag_retriever.retrieve(query, top_k=2)
        timing["retrieval_ms"] = (time.time() - t0) * 1000

        # 5. Action Planning
        t0 = time.time()
        action_proposal = self.action_planner.plan(state, evidence)
        timing["planning_ms"] = (time.time() - t0) * 1000

        # 6. Action Validation
        t0 = time.time()
        validation_result = self.action_validator.validate(action_proposal, state)
        timing["validation_ms"] = (time.time() - t0) * 1000

        # 7. Action Execution
        t0 = time.time()
        execution_result = self.action_executor.execute(action_proposal, validation_result)
        timing["execution_ms"] = (time.time() - t0) * 1000
        
        # 8. State Update (Action)
        state = StateTracker.update_from_action(state, execution_result)

        # 9. Feedback Evaluation (if it was an environment-altering action)
        feedback_result = None
        executed_action = execution_result.get("executed_action")
        
        if executed_action not in [ActionType.OBSERVE, ActionType.REQUEST_NEW_IMAGE]:
            t0 = time.time()
            # Fetch the simulator's true ground truth after execution
            env_state_after = self.action_executor.environment.get_state()
            feedback_result = self.feedback_evaluator.evaluate(state, execution_result, env_state_after)
            timing["feedback_ms"] = (time.time() - t0) * 1000
            
            # 10. State Update (Feedback)
            state = StateTracker.update_from_feedback(state, feedback_result.model_dump())

        # 11. Termination Evaluation
        if executed_action == ActionType.STOP or (feedback_result and feedback_result.result == "SUCCESS"):
            state.status = "COMPLETED"
            state.termination_reason = "Goal achieved or safe stop executed."
        elif executed_action == ActionType.ESCALATE:
            state.status = "ESCALATED"
            state.termination_reason = "Safety rules or planner demanded escalation."

        # 12. Persist Trajectory Step
        trajectory_step = TrajectoryStep(
            agent_session_id=agent_session_id,
            user_id=user_id,
            step_number=state.step_number,
            state_before=state_before_dict,
            observation_ref=observation_ref,
            perception=perception_result.model_dump() if perception_result else None,
            retrieved_knowledge={"evidence": evidence},
            action_proposal=action_proposal.model_dump(),
            validation_result=validation_result.model_dump(),
            environment_result=execution_result,
            feedback=feedback_result.model_dump() if feedback_result else None,
            state_after=state.model_dump(),
            timing_ms=timing
        )
        
        await self.trajectory_repo.save_step(trajectory_step)
        await self.trajectory_repo.save_latest_state(user_id, agent_session_id, state)
        
        logger.info(f"Agent {agent_session_id} step {state.step_number} complete. Status: {state.status}")
        return state
