"""
Unit tests for ActionValidator (Safety Policy)
"""
import pytest
from app.domain.actions import ActionProposal, ActionType, RiskLevel
from app.domain.states import AgentState
from app.validation.validator import ActionValidator
from app.domain.observations import ObservationQuality, QualityLevel

def make_state(**kwargs):
    defaults = dict(agent_id="test-agent", goal="Test goal", confidence=0.85, condition="early_blight", crop="tomato", severity=0.5)
    defaults.update(kwargs)
    return AgentState(**defaults)

def make_action(action_type=ActionType.RECOMMEND_TREATMENT, **kwargs):
    defaults = dict(
        action_type=action_type,
        reason="test",
        confidence=0.85,
        expected_outcome="recovery",
        parameters={"treatment": "copper_fungicide"}
    )
    defaults.update(kwargs)
    return ActionProposal(**defaults)

@pytest.fixture
def validator():
    return ActionValidator()

class TestSafetyValidator:

    def test_approves_valid_action(self, validator):
        state = make_state()
        action = make_action()
        result = validator.validate(action, state)
        assert result.approved is True
        assert result.risk_level == RiskLevel.LOW

    def test_blocks_treatment_on_low_confidence(self, validator):
        state = make_state(confidence=0.3)
        action = make_action(ActionType.RECOMMEND_TREATMENT)
        result = validator.validate(action, state)
        assert result.approved is False
        assert result.corrective_action == ActionType.REQUEST_NEW_IMAGE

    def test_blocks_treatment_for_unknown_crop(self, validator):
        state = make_state(crop="unknown")
        action = make_action(ActionType.RECOMMEND_TREATMENT)
        result = validator.validate(action, state)
        assert result.approved is False
        assert result.corrective_action == ActionType.REQUEST_NEW_IMAGE

    def test_forces_escalation_on_repeated_failures(self, validator):
        state = make_state(failure_count=3)
        action = make_action(ActionType.RECOMMEND_TREATMENT)
        result = validator.validate(action, state)
        assert result.approved is False
        assert result.corrective_action == ActionType.ESCALATE
        assert result.risk_level == RiskLevel.CRITICAL

    def test_blocks_treatment_without_treatment_param(self, validator):
        state = make_state()
        action = make_action(ActionType.RECOMMEND_TREATMENT, parameters={})
        result = validator.validate(action, state)
        assert result.approved is False

    def test_approves_monitor_on_healthy(self, validator):
        state = make_state(condition="healthy", confidence=0.9)
        action = make_action(ActionType.MONITOR, parameters={})
        result = validator.validate(action, state)
        assert result.approved is True

    def test_approves_escalate_always(self, validator):
        state = make_state(failure_count=5)
        action = make_action(ActionType.ESCALATE, parameters={})
        result = validator.validate(action, state)
        assert result.approved is True
