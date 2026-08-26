from app.domain.environment import EnvironmentState
from app.domain.actions import ActionType
from typing import Dict, Any

class EnvironmentTransitions:
    """Explicit deterministic transition equations for the environment."""
    
    @staticmethod
    def apply_action(state: EnvironmentState, action_type: ActionType, parameters: Dict[str, Any]) -> EnvironmentState:
        """Calculates new environment state based on action."""
        
        # Increment time
        state.timestep += 1
        
        if action_type == ActionType.WATER:
            if state.water_level < 0.3:
                state.health = min(1.0, state.health + 0.1)
                state.environmental_stress = max(0.0, state.environmental_stress - 0.2)
            elif state.water_level > 0.8:
                state.environmental_stress = min(1.0, state.environmental_stress + 0.2)
                state.health = max(0.0, state.health - 0.1)
            state.water_level = min(1.0, state.water_level + 0.4)
            
        elif action_type in [ActionType.RECOMMEND_TREATMENT, ActionType.CHANGE_TREATMENT]:
            treatment = parameters.get("treatment", "")
            # Simple simulation heuristic
            if "fungicide" in treatment.lower() and "blight" in (state.disease or "").lower():
                # Correct treatment
                state.disease_severity = max(0.0, state.disease_severity - 0.3)
                state.treatment_status = treatment
                if state.disease_severity == 0.0:
                    state.disease = None
            else:
                # Incorrect treatment or general treatment
                state.disease_severity = min(1.0, state.disease_severity + 0.1)
                state.health = max(0.0, state.health - 0.1)
                
        elif action_type == ActionType.MONITOR:
            # Natural evolution
            if state.disease and state.disease_severity > 0:
                state.disease_severity = min(1.0, state.disease_severity + 0.05)
                state.health = max(0.0, state.health - 0.05)
            # Natural drying
            state.water_level = max(0.0, state.water_level - 0.1)
            if state.water_level < 0.2:
                state.environmental_stress = min(1.0, state.environmental_stress + 0.1)
                
        # REQUEST_NEW_IMAGE, ESCALATE, STOP don't advance physical time in this simulation
        
        return state
