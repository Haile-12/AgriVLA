import logging
from typing import Dict, Any
from app.domain.states import AgentState
from app.domain.environment import EnvironmentState
from app.domain.feedback import FeedbackResult, FeedbackResultType
from app.feedback.rewards import RewardFunction

logger = logging.getLogger(__name__)

class FeedbackEvaluator:
    """Evaluates the outcome of an action by comparing before/after states."""
    
    def evaluate(self, state_before: AgentState, action_dict: Dict[str, Any], env_state_after: EnvironmentState) -> FeedbackResult:
        logger.info("Evaluating feedback...")
        
        # Calculate changes (assuming state_before.severity approximated truth)
        severity_change = env_state_after.disease_severity - state_before.severity
        health_change = env_state_after.health - (1.0 if not state_before.severity else (1.0 - state_before.severity))
        
        # Determine result classification
        action_type = action_dict.get("executed_action")
        result = FeedbackResultType.UNCERTAIN
        explanation = ""
        
        if action_type in ["REQUEST_NEW_IMAGE", "MONITOR", "OBSERVE"]:
            result = FeedbackResultType.NO_CHANGE
            explanation = "Action was observational. No physical environment change intended."
        elif action_type == "ESCALATE":
            result = FeedbackResultType.FAILURE
            explanation = "Escalation requested due to unsafe conditions or repeated failure."
        elif severity_change < -0.1:
            result = FeedbackResultType.SUCCESS
            explanation = f"Significant improvement in disease severity ({severity_change:.2f})."
        elif severity_change > 0.1 or env_state_after.environmental_stress > 0.5:
            result = FeedbackResultType.FAILURE
            explanation = "Condition deteriorated after action."
        else:
            result = FeedbackResultType.NO_CHANGE
            explanation = "No significant change in crop health."
            
        reward = RewardFunction.calculate(state_before, action_dict, env_state_after)
        goal_progress = env_state_after.health # Simple proxy
        
        return FeedbackResult(
            result=result,
            reward=reward,
            severity_change=severity_change,
            health_change=health_change,
            goal_progress=goal_progress,
            explanation=explanation,
            recommended_next_step="Continue" if result == FeedbackResultType.SUCCESS else "Re-evaluate"
        )
