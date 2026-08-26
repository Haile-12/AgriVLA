from enum import Enum

class Collections(str, Enum):
    USERS = "users"
    SESSIONS = "sessions"
    AGENT_SESSIONS = "agent_sessions"
    AGENT_STATES = "agent_states"
    OBSERVATIONS = "observations"
    PERCEPTIONS = "perceptions"
    ACTIONS = "actions"
    ACTION_VALIDATIONS = "action_validations"
    ENVIRONMENT_TRANSITIONS = "environment_transitions"
    FEEDBACK = "feedback"
    KNOWLEDGE_RETRIEVALS = "knowledge_retrievals"
    TRAJECTORIES = "trajectories"
    EVALUATION_RUNS = "evaluation_runs"
    EVALUATION_RESULTS = "evaluation_results"
