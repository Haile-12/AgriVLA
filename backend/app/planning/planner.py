import logging
from typing import List, Dict, Any
from app.domain.states import AgentState
from app.domain.actions import ActionProposal, ActionType

logger = logging.getLogger(__name__)

class ActionPlanner:
    """
    Determines the next action based on current state, history, and retrieved knowledge.
    This MVP implementation uses deterministic heuristics mapping to the closed action space.
    A future iteration could use an LLM for complex reasoning before selecting the constrained action.
    """
    
    def __init__(self, high_conf_thresh: float = 0.75, max_failures: int = 3):
        self.high_conf_thresh = high_conf_thresh
        self.max_failures = max_failures

    def plan(self, state: AgentState, evidence: List[Dict[str, Any]]) -> ActionProposal:
        logger.info(f"Planning next action for agent {state.agent_id} (Step {state.step_number})")
        
        # 1. Check for immediate escalation triggers
        if state.failure_count >= self.max_failures:
            return ActionProposal(
                action_type=ActionType.ESCALATE,
                reason=f"Repeated action failures ({state.failure_count}). System cannot safely proceed.",
                confidence=1.0,
                expected_outcome="Human review required.",
                requires_follow_up_observation=False
            )
            
        # 2. Check observation quality and confidence
        if state.confidence < self.high_conf_thresh or (state.observation_quality and state.observation_quality.quality_score < 0.6):
            return ActionProposal(
                action_type=ActionType.REQUEST_NEW_IMAGE,
                reason="Insufficient visual evidence or low confidence in diagnosis.",
                confidence=1.0,
                expected_outcome="Obtain a clearer observation to make a safe decision.",
                requires_follow_up_observation=True
            )
            
        # 3. Goal checking (simple heuristic for MVP)
        if state.trend == "IMPROVING" and state.severity < 0.1:
            return ActionProposal(
                action_type=ActionType.STOP,
                reason="Crop condition has significantly improved and stabilized.",
                confidence=0.9,
                expected_outcome="Agent terminates successfully.",
                requires_follow_up_observation=False
            )

        # 4. Healthy crop
        if state.condition and state.condition.lower() == "healthy":
            return ActionProposal(
                action_type=ActionType.MONITOR,
                target=state.crop,
                reason="Crop appears healthy. No intervention required.",
                confidence=state.confidence,
                expected_outcome="Maintain current state.",
                requires_follow_up_observation=True,
                parameters={"interval_days": 7}
            )

        # 5. Treatment Logic based on Trend and Condition
        if state.condition and state.condition.lower() != "healthy" and state.condition.lower() != "unknown":
            
            # If we recently tried a treatment and it failed/stagnated
            if state.trend in ["DETERIORATING", "STAGNANT"] and state.previous_action and state.previous_action.get("action_type") == ActionType.RECOMMEND_TREATMENT.value:
                return ActionProposal(
                    action_type=ActionType.CHANGE_TREATMENT,
                    target=state.condition,
                    reason=f"Previous treatment for {state.condition} was ineffective. Attempting alternative.",
                    confidence=0.8,
                    expected_outcome="Disease severity reduction using new treatment.",
                    requires_follow_up_observation=True,
                    parameters={"disease": state.condition, "previous_treatment": state.previous_action.get("parameters", {}).get("treatment")}
                )
                
            # Initial treatment recommendation
            # (In a real system, we would parse `evidence` here to select the exact chemical/treatment)
            treatment_name = "standard_fungicide" if "blight" in state.condition.lower() else "general_treatment"
            if evidence:
                # Naive MVP evidence extraction
                treatment_name = evidence[0].get("metadata", {}).get("recommended_treatment", treatment_name)
                
            return ActionProposal(
                action_type=ActionType.RECOMMEND_TREATMENT,
                target=state.condition,
                reason=f"Identified {state.condition} with {state.severity} severity.",
                confidence=state.confidence,
                expected_outcome="Disease severity should decrease.",
                requires_follow_up_observation=True,
                parameters={"disease": state.condition, "treatment": treatment_name}
            )
            
        # Fallback
        return ActionProposal(
            action_type=ActionType.ESCALATE,
            reason="Planner could not determine a safe valid action based on current state.",
            confidence=1.0,
            expected_outcome="Human review required.",
            requires_follow_up_observation=False
        )
