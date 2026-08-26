import logging
from typing import Optional
from app.domain.actions import ActionProposal, ActionType, ActionValidationResult, RiskLevel
from app.domain.states import AgentState

logger = logging.getLogger(__name__)

class ActionValidator:
    """
    Deterministic safety-first decision policy.
    The LLM/Planner is NOT the only safety mechanism. This validator enforces hard rules.
    """
    
    def validate(self, action: ActionProposal, state: AgentState) -> ActionValidationResult:
        logger.info(f"Validating proposed action: {action.action_type}")
        
        # Rule 1: Escalation policy for repeated failures
        if state.failure_count >= 3 and action.action_type != ActionType.ESCALATE:
            return ActionValidationResult(
                approved=False,
                reason=f"Safety Policy: Agent has failed {state.failure_count} times in a row. Must escalate.",
                risk_level=RiskLevel.CRITICAL,
                corrective_action=ActionType.ESCALATE
            )
            
        # Rule 2: Low confidence requires more evidence or escalation, not treatment
        if state.confidence < 0.5 and action.action_type in [ActionType.WATER, ActionType.RECOMMEND_TREATMENT, ActionType.CHANGE_TREATMENT]:
            return ActionValidationResult(
                approved=False,
                reason="Safety Policy: Confidence too low (<0.5) to perform consequential action.",
                risk_level=RiskLevel.HIGH,
                corrective_action=ActionType.REQUEST_NEW_IMAGE
            )
            
        # Rule 3: Unknown crop with consequential action
        if (not state.crop or state.crop.lower() == "unknown") and action.action_type in [ActionType.RECOMMEND_TREATMENT]:
            return ActionValidationResult(
                approved=False,
                reason="Safety Policy: Cannot recommend treatment for unknown crop.",
                risk_level=RiskLevel.HIGH,
                corrective_action=ActionType.REQUEST_NEW_IMAGE
            )
            
        # Rule 4: Action space validation
        if not isinstance(action.action_type, ActionType):
            return ActionValidationResult(
                approved=False,
                reason="Safety Policy: Proposed action is not in the allowed ActionSpace.",
                risk_level=RiskLevel.CRITICAL,
                corrective_action=ActionType.ESCALATE
            )
            
        # Rule 5: Treatment requires parameters
        if action.action_type in [ActionType.RECOMMEND_TREATMENT, ActionType.CHANGE_TREATMENT]:
            if not action.parameters.get("treatment"):
                return ActionValidationResult(
                    approved=False,
                    reason="Safety Policy: Treatment action proposed without specifying a treatment parameter.",
                    risk_level=RiskLevel.MEDIUM,
                    corrective_action=ActionType.ESCALATE
                )

        # If all rules pass
        return ActionValidationResult(
            approved=True,
            reason="Action conforms to all safety policies.",
            risk_level=RiskLevel.LOW
        )
