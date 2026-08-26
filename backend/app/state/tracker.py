from datetime import datetime
from typing import Dict, Any
from app.domain.states import AgentState
from app.domain.observations import PerceptionResult

class StateTracker:
    """Explicitly manages state transitions for the agent."""
    
    @staticmethod
    def initialize_state(agent_id: str, goal: str, scenario_id: str = None) -> AgentState:
        return AgentState(
            agent_id=agent_id,
            goal=goal,
            scenario_id=scenario_id
        )
        
    @staticmethod
    def update_from_observation(state: AgentState, perception: PerceptionResult, observation_ref: str = None) -> AgentState:
        """Updates the agent's understanding based on new visual evidence."""
        state.previous_observation = state.current_observation
        state.current_observation = observation_ref
        
        state.crop = perception.crop
        state.condition = perception.condition
        state.severity = perception.severity
        state.visible_damage = perception.visible_damage
        state.confidence = perception.confidence
        state.observation_quality = perception.observation_quality
        
        state.updated_at = datetime.utcnow()
        return state

    @staticmethod
    def update_from_action(state: AgentState, action: Dict[str, Any]) -> AgentState:
        """Records an executed action."""
        state.previous_action = action
        state.action_history.append(action)
        state.updated_at = datetime.utcnow()
        return state

    @staticmethod
    def update_from_feedback(state: AgentState, feedback: Dict[str, Any]) -> AgentState:
        """Updates statistics and trend based on environment feedback."""
        state.feedback_history.append(feedback)
        
        result = feedback.get("result", "UNKNOWN")
        if result == "SUCCESS":
            state.successful_action_count += 1
            state.trend = "IMPROVING"
            # Reset failure count on success
            state.failure_count = 0 
        elif result == "FAILURE":
            state.failure_count += 1
            state.trend = "DETERIORATING"
        elif result == "NO_CHANGE":
            state.trend = "STAGNANT"
            
        state.step_number += 1
        state.updated_at = datetime.utcnow()
        return state
