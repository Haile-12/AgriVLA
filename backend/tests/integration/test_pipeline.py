"""
Integration tests for the closed-loop agent pipeline (no real VLM, no DB).
"""
import pytest
import asyncio
from app.domain.environment import EnvironmentState
from app.domain.states import AgentState
from app.domain.observations import PerceptionResult, ObservationQuality, QualityLevel
from app.environment.simulator import AgriculturalEnvironment
from app.environment.transitions import EnvironmentTransitions
from app.planning.planner import ActionPlanner
from app.validation.validator import ActionValidator
from app.execution.executor import ActionExecutor
from app.feedback.evaluator import FeedbackEvaluator
from app.state.tracker import StateTracker
from app.domain.actions import ActionType

def make_env(crop="tomato", disease="early_blight", severity=0.5, health=0.6):
    return AgriculturalEnvironment(
        initial_state=EnvironmentState(crop=crop, disease=disease, disease_severity=severity, health=health)
    )

def make_perception(condition="early_blight", severity=0.5, confidence=0.85):
    return PerceptionResult(
        crop="tomato", condition=condition, severity=severity,
        visible_damage=["lesions"], confidence=confidence,
        observation_quality=ObservationQuality(quality_score=0.9, quality_level=QualityLevel.EXCELLENT, issues=[]),
        reasoning_summary="Test", model_name="sim", inference_time_ms=0.0
    )

class TestPipelineIntegration:

    def setup_method(self):
        self.env = make_env()
        self.planner = ActionPlanner()
        self.validator = ActionValidator()
        self.executor = ActionExecutor(environment=self.env)
        self.evaluator = FeedbackEvaluator()

    def test_full_step_pipeline(self):
        """Tests that a single step updates state correctly."""
        state = StateTracker.initialize_state("agent-1", "Cure blight")
        perception = make_perception()
        state = StateTracker.update_from_observation(state, perception)

        action = self.planner.plan(state, [])
        assert action.action_type in list(ActionType)

        validation = self.validator.validate(action, state)
        execution = self.executor.execute(action, validation)
        state = StateTracker.update_from_action(state, execution)

        env_after = self.env.get_state()
        feedback = self.evaluator.evaluate(state, execution, env_after)
        state = StateTracker.update_from_feedback(state, feedback.model_dump())

        assert state.step_number == 1
        assert len(state.action_history) == 1

    def test_treatment_reduces_severity(self):
        """Correct fungicide on blight should reduce disease severity."""
        state = StateTracker.initialize_state("agent-2", "Cure blight")
        perception = make_perception("early_blight", 0.5, 0.9)
        state = StateTracker.update_from_observation(state, perception)

        from app.domain.actions import ActionProposal, ActionValidationResult, RiskLevel
        action = ActionProposal(
            action_type=ActionType.RECOMMEND_TREATMENT, reason="test", confidence=0.9,
            expected_outcome="recovery", parameters={"treatment": "copper_fungicide_blight"}
        )
        validation = ActionValidationResult(approved=True, reason="ok", risk_level=RiskLevel.LOW)
        self.executor.execute(action, validation)
        env_after = self.env.get_state()
        assert env_after.disease_severity < 0.5

    def test_validator_overrides_low_confidence_action(self):
        """With confidence < 0.5, validator should block treatment."""
        state = StateTracker.initialize_state("agent-3", "Cure blight")
        perception = make_perception("early_blight", 0.5, 0.3)  # very low confidence
        state = StateTracker.update_from_observation(state, perception)

        from app.domain.actions import ActionProposal
        action = ActionProposal(
            action_type=ActionType.RECOMMEND_TREATMENT, reason="risky", confidence=0.3,
            expected_outcome="maybe", parameters={"treatment": "fungicide"}
        )
        result = self.validator.validate(action, state)
        assert not result.approved
        assert result.corrective_action == ActionType.REQUEST_NEW_IMAGE
