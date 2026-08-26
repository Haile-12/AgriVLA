"""
Ablation Runner for AgriVLA
Systematically disables components to measure their contribution to performance.
"""
import json
import time
from typing import Dict, Any, List
from pathlib import Path
from copy import deepcopy
from dataclasses import asdict

from evaluation.harness import EvaluationHarness, EvalMetrics, ScenarioConfig
from app.planning.planner import ActionPlanner
from app.validation.validator import ActionValidator

class AblationRunner:
    """
    Runs the same scenarios under different ablation conditions:
    - FULL: All components active (baseline)
    - NO_VALIDATION: Safety validator bypassed (always approves)
    - NO_RAG: No knowledge retrieved
    - LOW_CONFIDENCE: Confidence threshold set to 0 (always acts)
    """

    def _run_condition(self, name: str, harness: EvaluationHarness) -> Dict[str, Any]:
        print(f"\n  [{name}]")
        results = harness.run_all(output_path=f"./data/ablation_{name.lower().replace(' ', '_')}.json")
        return {
            "condition": name,
            "success_rate": sum(1 for r in results if r.success) / len(results),
            "avg_reward": sum(r.total_reward for r in results) / len(results),
            "avg_steps": sum(r.steps_taken for r in results) / len(results),
            "avg_safety_violations": sum(r.safety_violations for r in results) / len(results),
            "results": [asdict(r) for r in results]
        }

    def run(self, output_path: str = "./data/ablation_summary.json"):
        print(f"\n{'='*60}")
        print(f"  AgriVLA Ablation Study")
        print(f"{'='*60}")
        ablation_results = []

        # --- FULL SYSTEM (Baseline) ---
        harness_full = EvaluationHarness()
        ablation_results.append(self._run_condition("FULL_SYSTEM", harness_full))

        # --- NO_VALIDATION: Replace validator with a passthrough ---
        class NoOpValidator(ActionValidator):
            def validate(self, action, state):
                from app.domain.actions import ActionValidationResult, RiskLevel
                return ActionValidationResult(approved=True, reason="Ablation: no validation", risk_level=RiskLevel.LOW)

        harness_no_val = EvaluationHarness()
        harness_no_val.validator = NoOpValidator()
        ablation_results.append(self._run_condition("NO_VALIDATION", harness_no_val))

        # --- NO_RAG: Skip retrieval entirely by patching the retriever ---
        harness_no_rag = EvaluationHarness()
        # Override the run_scenario to pass empty evidence
        original_run = harness_no_rag.run_scenario
        def no_rag_scenario(scenario):
            import unittest.mock
            with unittest.mock.patch('app.knowledge.retrieval.RAGRetriever.retrieve', return_value=[]):
                return original_run(scenario)
        harness_no_rag.run_scenario = no_rag_scenario
        ablation_results.append(self._run_condition("NO_RAG", harness_no_rag))

        # --- LOW_CONFIDENCE_THRESHOLD: Planner always acts even on low confidence ---
        harness_low_conf = EvaluationHarness()
        harness_low_conf.planner = ActionPlanner(high_conf_thresh=0.0)
        ablation_results.append(self._run_condition("LOW_CONF_THRESHOLD", harness_low_conf))

        # Save summary
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        summary = []
        for r in ablation_results:
            summary.append({
                "condition": r["condition"],
                "success_rate": round(r["success_rate"] * 100, 1),
                "avg_reward": round(r["avg_reward"], 3),
                "avg_steps": round(r["avg_steps"], 1),
                "avg_safety_violations": round(r["avg_safety_violations"], 2)
            })

        with open(output_path, "w") as f:
            json.dump({"summary": summary, "details": ablation_results}, f, indent=2)

        print(f"\n  Ablation Summary:")
        print(f"  {'Condition':<25} {'Success%':>10} {'AvgReward':>12} {'AvgSteps':>10} {'SafetyViols':>12}")
        print(f"  {'-'*70}")
        for r in summary:
            print(f"  {r['condition']:<25} {r['success_rate']:>9.1f}% {r['avg_reward']:>12.3f} {r['avg_steps']:>10.1f} {r['avg_safety_violations']:>12.2f}")
        print(f"\n  Results saved to {output_path}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    runner = AblationRunner()
    runner.run()
