import logging
from app.domain.environment import EnvironmentState
from app.domain.actions import ActionType
from app.environment.transitions import EnvironmentTransitions
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AgriculturalEnvironment:
    """
    Simulates the true state of the crop/farm.
    Maintains the ground truth which the agent cannot directly see.
    """
    def __init__(self, initial_state: EnvironmentState):
        self.state = initial_state

    def apply_action(self, action_type: ActionType, parameters: Dict[str, Any]) -> EnvironmentState:
        logger.info(f"Environment executing action: {action_type}")
        self.state = EnvironmentTransitions.apply_action(self.state, action_type, parameters)
        return self.state

    def get_state(self) -> EnvironmentState:
        return self.state
        
    def is_goal_complete(self) -> bool:
        """Determines if the environment is in a strictly successful state."""
        return self.state.health >= 0.8 and self.state.disease_severity < 0.1 and self.state.environmental_stress < 0.3
