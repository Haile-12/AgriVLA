from app.domain.states import AgentState
from app.domain.environment import EnvironmentState
from typing import Dict, Any

class RewardFunction:
    
    @staticmethod
    def calculate(state_before: AgentState, action_dict: Dict[str, Any], env_state_after: EnvironmentState) -> float:
        """
        Transparent reward function based on measurable state changes.
        """
        reward = 0.0
        
        # Reward disease reduction
        # (Assuming we have a way to know previous true disease severity, or we approximate using agent state)
        if state_before.severity > env_state_after.disease_severity:
            reward += (state_before.severity - env_state_after.disease_severity) * 10
            
        # Reward health improvement
        if env_state_after.health > 0.8:
            reward += 2.0
            
        # Penalties
        action_type = action_dict.get("executed_action")
        if action_type == "ESCALATE":
            reward -= 5.0 # Penalty for needing human intervention
            
        if env_state_after.health < 0.2:
            reward -= 10.0 # Heavy penalty for near death
            
        return reward
