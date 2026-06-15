"""Tests for scripts.build_harness.harness.reporting.

Covers ``estimate_optimization_heuristics`` and ``build_run_analysis``.
"""

from __future__ import annotations

import json

import pytest

from scripts.build_harness.harness.reporting import (
    build_run_analysis,
    estimate_optimization_heuristics,
)


class TestEstimateOptimizationHeuristics:
    """Impact/effort labels drive the optimization_recommendations artifact."""

    @pytest.mark.parametrize(
        "seconds, expected_impact",
        [
            (600, "high"),
            (900, "high"),
            (180, "medium"),
            (300, "medium"),
            (179, "low"),
            (0, "low"),
        ],
    )
    def test_impact_thresholds(self, seconds: float, expected_impact: str) -> None:
        result = estimate_optimization_heuristics("task", "some_task", seconds)
        assert result["impact"] == expected_impact

    def test_flow_target_type_is_high_effort(self) -> None:
        result = estimate_optimization_heuristics("flow", "prepare_billing", 10)
        assert result["effort"] == "high"

    @pytest.mark.parametrize("name", ["deploy_full", "assemble_and_deploy_ux", "insert_qb_data", "extract_pricing", "refresh_decision_tables"])
    def test_data_deploy_tasks_are_medium_effort(self, name: str) -> None:
        result = estimate_optimization_heuristics("task", name, 10)
        assert result["effort"] == "medium"

    def test_simple_task_is_low_effort(self) -> None:
        result = estimate_optimization_heuristics("task", "validate_setup", 10)
        assert result["effort"] == "low"

    def test_note_includes_runtime_and_target(self) -> None:
        result = estimate_optimization_heuristics("task", "deploy_full", 123.456)
        assert "123.46" in result["note"]
        assert "task:deploy_full" in result["note"]

    def test_returns_all_required_keys(self) -> None:
        result = estimate_optimization_heuristics("task", "x", 0)
        assert set(result.keys()) == {"impact", "effort", "note"}


class TestBuildRunAnalysis:
    """``build_run_analysis`` aggregates step events into analysis artifacts."""

    def _make_run_dir(self, tmp_path, scenario_results, step_events_by_scenario=None, manifests_by_scenario=None):
        run_dir = tmp_path / "run-test"
        run_dir.mkdir()
        for sr in scenario_results:
            sid = sr["scenario_id"]
            sdir = run_dir / "scenarios" / str(sid)
            sdir.mkdir(parents=True)
            manifest = (manifests_by_scenario or {}).get(sid, {})
            (sdir / "scenario_manifest.json").write_text(json.dumps(manifest))
            events = (step_events_by_scenario or {}).get(sid, [])
            lines = [json.dumps(e) for e in events]
            (sdir / "step_results.jsonl").write_text("\n".join(lines))
        return run_dir

    def test_empty_run_returns_zero_counts(self, tmp_path) -> None:
        run_dir = self._make_run_dir(tmp_path, [])
        result = build_run_analysis(run_dir, {"scenario_results": []})
        assert result["compatibility_summary"]["total_scenarios"] == 0
        assert result["compatibility_summary"]["passed_scenarios"] == 0
        assert result["compatibility_summary"]["failed_scenarios"] == 0

    def test_success_scenario_counted(self, tmp_path) -> None:
        sr = [{"scenario_id": "s1", "status": "success", "failed_step": None, "failed_target": None, "failure_signature": "", "failure_class": "none", "org_alias": "a1"}]
        run_dir = self._make_run_dir(tmp_path, sr)
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        assert result["compatibility_summary"]["passed_scenarios"] == 1
        assert result["compatibility_summary"]["failed_scenarios"] == 0

    def test_failed_scenario_populates_signature_index(self, tmp_path) -> None:
        sr = [{"scenario_id": "s1", "status": "failed", "failed_step": 5, "failed_target": "task:deploy_full", "failure_signature": "DEPLOY_FAILED", "failure_class": "deterministic", "org_alias": "a1"}]
        events = [{"phase": "prepare_step", "status": "failed", "step_number": 5, "target_type": "task", "target_name": "deploy_full", "duration_seconds": 30, "failure_signature": "DEPLOY_FAILED"}]
        run_dir = self._make_run_dir(tmp_path, sr, step_events_by_scenario={"s1": events})
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        sigs = result["compatibility_summary"]["failed_step_signatures"]
        assert len(sigs) == 1
        assert sigs[0]["signature"] == "DEPLOY_FAILED"

    def test_flag_overrides_tracked(self, tmp_path) -> None:
        sr = [{"scenario_id": "s1", "status": "success", "failed_step": None, "failed_target": None, "failure_signature": "", "failure_class": "none", "org_alias": "a1"}]
        manifests = {"s1": {"flag_overrides": {"billing": True, "clm": False}}}
        run_dir = self._make_run_dir(tmp_path, sr, manifests_by_scenario=manifests)
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        flags = {f["flag"]: f for f in result["compatibility_summary"]["flag_involvement"]}
        assert "billing" in flags
        assert flags["billing"]["values"]["true"] == 1

    def test_top_slowest_steps_limited_to_five(self, tmp_path) -> None:
        events = [
            {"phase": "prepare_step", "status": "success", "step_number": i, "target_type": "task", "target_name": f"step_{i}", "duration_seconds": i * 10, "failure_signature": ""}
            for i in range(1, 8)
        ]
        sr = [{"scenario_id": "s1", "status": "success", "failed_step": None, "failed_target": None, "failure_signature": "", "failure_class": "none", "org_alias": "a1"}]
        run_dir = self._make_run_dir(tmp_path, sr, step_events_by_scenario={"s1": events})
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        assert len(result["optimization_recommendations"]["top_slowest_steps"]) == 5

    def test_analysis_contains_all_three_sections(self, tmp_path) -> None:
        run_dir = self._make_run_dir(tmp_path, [])
        result = build_run_analysis(run_dir, {"scenario_results": []})
        assert "compatibility_summary" in result
        assert "dependency_summary" in result
        assert "optimization_recommendations" in result

    def test_skipped_steps_do_not_count_as_timing_samples(self, tmp_path) -> None:
        sr = [{"scenario_id": "s1", "status": "success", "failed_step": None, "failed_target": None, "failure_signature": "", "failure_class": "none", "org_alias": "a1"}]
        events = [
            {"phase": "prepare_step", "status": "skipped", "step_number": 1, "target_type": "task", "target_name": "demo", "duration_seconds": 0, "failure_signature": ""},
            {"phase": "prepare_step", "status": "success", "step_number": 1, "target_type": "task", "target_name": "demo", "duration_seconds": 10, "failure_signature": ""},
        ]
        run_dir = self._make_run_dir(tmp_path, sr, step_events_by_scenario={"s1": events})
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        step_row = result["dependency_summary"]["step_outcomes"][0]
        assert step_row["target"] == "task:demo"
        assert step_row["samples"] == 1
        assert step_row["total_duration_seconds"] == 10

    def test_successful_resume_does_not_emit_failure_dependency_hint(self, tmp_path) -> None:
        sr = [{"scenario_id": "s1", "status": "success", "failed_step": None, "failed_target": None, "failure_signature": "", "failure_class": "none", "org_alias": "a1"}]
        events = [
            {"phase": "prepare_step", "status": "failed", "step_number": 3, "target_type": "task", "target_name": "deploy", "duration_seconds": 20, "failure_signature": "old failure"},
            {"phase": "prepare_step", "status": "success", "step_number": 3, "target_type": "task", "target_name": "deploy", "duration_seconds": 12, "failure_signature": ""},
        ]
        run_dir = self._make_run_dir(tmp_path, sr, step_events_by_scenario={"s1": events})
        result = build_run_analysis(run_dir, {"scenario_results": sr})
        assert result["dependency_summary"]["failure_dependencies"] == []
