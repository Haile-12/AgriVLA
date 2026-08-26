from typing import Dict, Any
import logging
from app.domain.actions import ActionValidationResult, ActionProposal
from app.environment.simulator import AgriculturalEnvironment

logger = logging.getLogger(__name__)

class ActionExecutor:
    """Executes validated actions in the environment."""
    
    def __init__(self, environment: AgriculturalEnvironment):
        self.environment = environment

    def execute(self, action: ActionProposal, validation: ActionValidationResult) -> Dict[str, Any]:
        """
        Takes the proposed action and its validation result.
        If validation failed and provided a corrective action, it executes the corrective action instead.
        Otherwise it executes the proposed action.
        """
        
        action_to_execute = action.action_type
        if not validation.approved and validation.corrective_action:
            logger.warning(f"Executing corrective action {validation.corrective_action} instead of {action.action_type}")
            action_to_execute = validation.corrective_action
            
        logger.info(f"Executing action: {action_to_execute}")
        
        # Apply to environment
        new_env_state = self.environment.apply_action(action_to_execute, action.parameters)
        
        return {
            "executed_action": action_to_execute,
            "parameters": action.parameters if validation.approved else {},
            "environment_state_snapshot": new_env_state.model_dump()
        }
