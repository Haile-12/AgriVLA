"""
Evaluation Harness for AgriVLA
Runs the closed-loop agent against parameterized scenarios and records metrics.
"""
import asyncio
import json
import uuid
import logging
import time
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field

from app.config.settings import settings
from app.domain.environment import EnvironmentState
from app.domain.states import AgentState
from app.environment.simulator import AgriculturalEnvironment
from app.environment.transitions import EnvironmentTransitions
from app.planning.planner import ActionPlanner
from app.validation.validator import ActionValidator
from app.execution.executor import ActionExecutor
from app.feedback.evaluator import FeedbackEvaluator
from app.state.tracker import StateTracker
from app.knowledge.retrieval import get_rag_retriever
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("evaluation")

@dataclass
class ScenarioConfig:
    scenario_id: str
    name: str
    crop: str
    disease: str
    initial_severity: float
    initial_health: float
    goal: str
    max_steps: int = 10

@dataclass
class EvalMetrics:
    scenario_id: str
    scenario_name: str
    success: bool
    final_severity: float
    final_health: float
    steps_taken: int
    total_reward: float
    avg_action_confidence: float
    safety_violations: int
    termination_reason: str
    timing_ms: Dict[str, float] = field(default_factory=dict)

class EvaluationHarness:
    """
    Runs closed-loop agent episodes without a real VLM, using simulated perception
    to measure planning, validation, and feedback quality in isolation.
    """

    SCENARIOS: List[ScenarioConfig] = [
        ScenarioConfig("scen_001", "Early Blight - Tomato", "tomato", "early_blight", 0.5, 0.6, "Eliminate early blight"),
        ScenarioConfig("scen_002", "Healthy Crop Monitor", "wheat", "healthy", 0.0, 0.95, "Maintain health"),
        ScenarioConfig("scen_003", "Severe Disease - Corn", "corn", "gray_leaf_spot", 0.9, 0.3, "Recover crop"),
        ScenarioConfig("scen_004", "Water Stress - Rice", "rice", "healthy", 0.0, 0.5, "Maintain optimal water", 5),
    ]

    def __init__(self):
        self.planner = ActionPlanner()
        self.validator = ActionValidator()
        self.evaluator = FeedbackEvaluator()

    def _simulated_perception_from_env(self, env_state: EnvironmentState) -> dict:
        """Converts ground-truth environment state into what a VLM would approximately see."""
        from app.domain.observations import ObservationQuality, QualityLevel
        return {
            "crop": env_state.crop,
            "condition": env_state.disease or "healthy",
            "severity": env_state.disease_severity,
            "confidence": 0.85,  # Simulated high confidence
            "visible_damage": [f"Visible {env_state.disease} lesions"] if env_state.disease else [],
            "observation_quality": ObservationQuality(quality_score=0.9, quality_level=QualityLevel.EXCELLENT, issues=[]),
            "reasoning_summary": f"Detected {env_state.disease or 'no disease'} on {env_state.crop}.",
            "model_name": "simulated",
            "inference_time_ms": 0.0
        }

    def run_scenario(self, scenario: ScenarioConfig) -> EvalMetrics:
        from app.domain.observations import PerceptionResult

        env_state = EnvironmentState(
            crop=scenario.crop,
            disease=scenario.disease if scenario.disease != "healthy" else None,
            disease_severity=scenario.initial_severity,
            health=scenario.initial_health
        )
        environment = AgriculturalEnvironment(initial_state=env_state)
        executor = ActionExecutor(environment=environment)

        agent_id = str(uuid.uuid4())
        state = StateTracker.initialize_state(agent_id=agent_id, goal=scenario.goal)

        total_reward = 0.0
        confidences = []
        safety_violations = 0
        termination_reason = "Max steps reached"

        for step in range(scenario.max_steps):
            # Simulate perception from ground truth
            perception_data = self._simulated_perception_from_env(environment.get_state())
            perception = PerceptionResult(**perception_data)

            state = StateTracker.update_from_observation(state, perception)

            # Retrieve knowledge
            evidence = []
            if state.condition and state.condition != "unknown":
                query = f"Treatment for {state.condition} on {state.crop}"
                retriever = get_rag_retriever()
                evidence = retriever.retrieve(query, top_k=2)

            # Plan
            action_proposal = self.planner.plan(state, evidence)
            confidences.append(action_proposal.confidence)

            # Validate
            validation = self.validator.validate(action_proposal, state)
            if not validation.approved:
                safety_violations += 1

            # Execute
            execution_result = executor.execute(action_proposal, validation)
            state = StateTracker.update_from_action(state, execution_result)

            # Feedback
            env_after = environment.get_state()
            feedback = self.evaluator.evaluate(state, execution_result, env_after)
            total_reward += feedback.reward
            state = StateTracker.update_from_feedback(state, feedback.model_dump())

            # Terminal checks
            if environment.is_goal_complete():
                state.status = "COMPLETED"
                termination_reason = "Goal achieved"
                break
            if action_proposal.action_type.value == "ESCALATE":
                state.status = "ESCALATED"
                termination_reason = "Escalated"
                break
            if action_proposal.action_type.value == "STOP":
                state.status = "COMPLETED"
                termination_reason = "Agent issued STOP"
                break

        final_env = environment.get_state()
        return EvalMetrics(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            success=environment.is_goal_complete(),
            final_severity=final_env.disease_severity,
            final_health=final_env.health,
            steps_taken=state.step_number,
            total_reward=round(total_reward, 4),
            avg_action_confidence=round(sum(confidences)/len(confidences), 4) if confidences else 0,
            safety_violations=safety_violations,
            termination_reason=termination_reason
        )

    def run_all(self, output_path: str = "./data/eval_results.json") -> List[EvalMetrics]:
        results = []
        print(f"\n{'='*60}")
        print(f"  AgriVLA Evaluation Harness")
        print(f"{'='*60}")

        for scenario in self.SCENARIOS:
            print(f"\n  Running: {scenario.name} ({scenario.scenario_id})")
            t0 = time.time()
            metrics = self.run_scenario(scenario)
            elapsed = (time.time() - t0) * 1000
            metrics.timing_ms["total_episode_ms"] = round(elapsed, 1)
            results.append(metrics)

            status = "[PASS]" if metrics.success else "[FAIL]"
            print(f"  {status} | Steps: {metrics.steps_taken} | Reward: {metrics.total_reward:.2f} | Health: {metrics.final_health:.2f}")

        # Save results
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        print(f"\n  Results saved to {output_path}")

        # Summary
        success_rate = sum(1 for r in results if r.success) / len(results) * 100
        avg_reward = sum(r.total_reward for r in results) / len(results)
        print(f"\n  Summary: {success_rate:.0f}% success rate | Avg reward: {avg_reward:.2f}")
        print(f"{'='*60}\n")

        return results


if __name__ == "__main__":
    harness = EvaluationHarness()
    harness.run_all()
