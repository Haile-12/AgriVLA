"""
Unit tests for StateTracker
"""
import pytest
from app.domain.states import AgentState
from app.domain.observations import PerceptionResult, ObservationQuality, QualityLevel
from app.state.tracker import StateTracker

@pytest.fixture
def initial_state():
    return StateTracker.initialize_state(agent_id="a1", goal="cure blight")

def make_perception(**kwargs):
    defaults = dict(
        crop="tomato", condition="early_blight", severity=0.5,
        visible_damage=["brown lesions"], confidence=0.88,
        observation_quality=ObservationQuality(quality_score=0.9, quality_level=QualityLevel.EXCELLENT, issues=[]),
        reasoning_summary="Blight detected.", model_name="sim", inference_time_ms=100.0
    )
    defaults.update(kwargs)
    return PerceptionResult(**defaults)

class TestStateTracker:

    def test_initialize_state(self, initial_state):
        assert initial_state.agent_id == "a1"
        assert initial_state.step_number == 0
        assert initial_state.status == "IN_PROGRESS"

    def test_update_from_observation(self, initial_state):
        perception = make_perception()
        updated = StateTracker.update_from_observation(initial_state, perception, "img_ref_1")
        assert updated.crop == "tomato"
        assert updated.condition == "early_blight"
        assert updated.confidence == 0.88
        assert updated.current_observation == "img_ref_1"

    def test_update_from_action(self, initial_state):
        action = {"action_type": "RECOMMEND_TREATMENT", "parameters": {"treatment": "fungicide"}}
        updated = StateTracker.update_from_action(initial_state, action)
        assert len(updated.action_history) == 1
        assert updated.previous_action == action

    def test_update_from_feedback_success(self, initial_state):
        feedback = {"result": "SUCCESS", "reward": 5.0}
        updated = StateTracker.update_from_feedback(initial_state, feedback)
        assert updated.trend == "IMPROVING"
        assert updated.failure_count == 0
        assert updated.step_number == 1

    def test_update_from_feedback_failure(self, initial_state):
        feedback = {"result": "FAILURE", "reward": -2.0}
        updated = StateTracker.update_from_feedback(initial_state, feedback)
        assert updated.trend == "DETERIORATING"
        assert updated.failure_count == 1
        assert updated.step_number == 1

    def test_previous_observation_rolls(self, initial_state):
        p1 = make_perception()
        s1 = StateTracker.update_from_observation(initial_state, p1, "img_1")
        p2 = make_perception(severity=0.3)
        s2 = StateTracker.update_from_observation(s1, p2, "img_2")
        assert s2.current_observation == "img_2"
        assert s2.previous_observation == "img_1"
