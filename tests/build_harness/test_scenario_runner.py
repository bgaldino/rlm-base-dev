"""Tests for scripts.build_harness.harness.scenario_runner.

Covers the pure function ``summarize_policy``.
The orchestration function ``run_single_scenario`` is integration-level
(subprocess + filesystem) and not covered here.
"""

from __future__ import annotations

import json

import pytest

from scripts.build_harness.harness.io import write_json
from scripts.build_harness.harness.config import Step
from scripts.build_harness.harness import scenario_runner
from scripts.build_harness.harness.scenario_runner import summarize_policy


class TestSummarizePolicy:
    """Policy dicts flow into agent_summary.md and must have stable keys."""

    REQUIRED_KEYS = {"recommended_action", "operator_message", "confidence"}

    def test_success_returns_none_action(self) -> None:
        policy = summarize_policy(status="success", can_resume=False, failure_class="none", failed_step=None, retry_count=0)
        assert policy["recommended_action"] == "none"
        assert policy["confidence"] == "high"

    def test_transient_failure_with_resume_recommends_resume(self) -> None:
        policy = summarize_policy(status="failed", can_resume=True, failure_class="transient", failed_step=5, retry_count=0)
        assert policy["recommended_action"] == "resume"
        assert "step 5" in policy["operator_message"]

    def test_unknown_failure_with_resume_recommends_resume(self) -> None:
        policy = summarize_policy(status="failed", can_resume=True, failure_class="unknown", failed_step=3, retry_count=1)
        assert policy["recommended_action"] == "resume"

    def test_transient_with_too_many_retries_falls_through(self) -> None:
        policy = summarize_policy(status="failed", can_resume=True, failure_class="transient", failed_step=5, retry_count=2)
        assert policy["recommended_action"] == "resume"
        assert policy["confidence"] == "low"

    def test_deterministic_failure_requires_manual_fix(self) -> None:
        policy = summarize_policy(status="failed", can_resume=True, failure_class="deterministic", failed_step=5, retry_count=0)
        assert policy["recommended_action"] == "manual_fix_required"
        assert policy["confidence"] == "high"

    def test_no_resume_no_deterministic_recommends_rerun_full(self) -> None:
        policy = summarize_policy(status="failed", can_resume=False, failure_class="unknown", failed_step=5, retry_count=3)
        assert policy["recommended_action"] == "rerun_full"

    @pytest.mark.parametrize("status,can_resume,failure_class", [
        ("success", False, "none"),
        ("failed", True, "transient"),
        ("failed", True, "deterministic"),
        ("failed", False, "unknown"),
        ("resume_blocked", False, "deterministic"),
    ])
    def test_all_branches_return_required_keys(self, status: str, can_resume: bool, failure_class: str) -> None:
        policy = summarize_policy(status=status, can_resume=can_resume, failure_class=failure_class, failed_step=1, retry_count=0)
        assert set(policy.keys()) == self.REQUIRED_KEYS


class TestWriteJson:
    """``write_json`` persists scenario progress to disk."""

    def test_writes_valid_json(self, tmp_path) -> None:
        path = tmp_path / "checkpoint.json"
        payload = {"scenario_id": "base", "last_successful_step": 5}
        write_json(path, payload)
        loaded = json.loads(path.read_text())
        assert loaded == payload

    def test_overwrites_existing_checkpoint(self, tmp_path) -> None:
        path = tmp_path / "checkpoint.json"
        write_json(path, {"step": 1})
        write_json(path, {"step": 2})
        loaded = json.loads(path.read_text())
        assert loaded["step"] == 2


def _base_scenario() -> dict:
    return {
        "scenario_id": "ent-default",
        "org_shape": "ent",
        "days": 1,
        "flag_overrides": {},
    }


def test_run_single_scenario_materializes_org_before_prepare(tmp_path, monkeypatch) -> None:
    run_dir = tmp_path / "runs" / "run-1"
    run_dir.mkdir(parents=True)
    scenario_dir = run_dir / "scenarios" / "ent-default"
    project_root = scenario_dir / "cci_project"

    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _defaults, _overrides: {"demo": True})
    monkeypatch.setattr(
        scenario_runner,
        "prepare_scenario_project_root",
        lambda **_kwargs: project_root,
    )
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _root: None)
    monkeypatch.setattr(scenario_runner, "write_build_provenance", lambda **_kwargs: None)
    monkeypatch.setattr(scenario_runner, "evaluate_when", lambda *_args, **_kwargs: True)

    commands = []

    def _run_command(_root, command, *_args, **_kwargs):
        commands.append(list(command))
        return {
            "duration_seconds": 0.1,
            "exit_code": 0,
            "failure_signature": "",
            "failure_class": "none",
            "tail": [],
        }

    monkeypatch.setattr(scenario_runner, "run_command", _run_command)

    result = scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=[Step(step_number=1, target_type="flow", target_name="prepare_core", when=None)],
        default_flags={"demo": True},
        base_cci={},
        skip_validate=True,
        keep_orgs=True,
        is_resume=False,
    )

    assert result["status"] == "success"
    assert commands[:3] == [
        ["cci", "org", "scratch", "ent", "harness-ent-default-1", "--days", "1"],
        ["cci", "org", "info", "harness-ent-default-1"],
        ["cci", "flow", "run", "prepare_core", "--org", "harness-ent-default-1"],
    ]

    step_results_path = run_dir / "scenarios" / "ent-default" / "step_results.jsonl"
    rows = [json.loads(line) for line in step_results_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["phase"] == "org_create"
    assert rows[1]["phase"] == "org_materialize"
    assert rows[2]["phase"] == "prepare_step"


def test_run_single_scenario_returns_deterministic_failure_for_materialize_error(tmp_path, monkeypatch) -> None:
    run_dir = tmp_path / "runs" / "run-2"
    run_dir.mkdir(parents=True)
    scenario_dir = run_dir / "scenarios" / "ent-default"
    project_root = scenario_dir / "cci_project"

    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _defaults, _overrides: {"demo": True})
    monkeypatch.setattr(
        scenario_runner,
        "prepare_scenario_project_root",
        lambda **_kwargs: project_root,
    )
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _root: None)

    call_count = {"n": 0}

    def _run_command(_root, _command, *_args, **_kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return {
                "duration_seconds": 0.1,
                "exit_code": 0,
                "failure_signature": "",
                "failure_class": "none",
                "tail": [],
            }
        return {
            "duration_seconds": 0.1,
            "exit_code": 2,
            "failure_signature": "materialize failed",
            "failure_class": "unknown",
            "tail": [],
        }

    monkeypatch.setattr(scenario_runner, "run_command", _run_command)

    result = scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=[],
        default_flags={"demo": True},
        base_cci={},
        skip_validate=True,
        keep_orgs=True,
        is_resume=False,
    )

    assert result["status"] == "failed"
    assert result["failure_phase"] == "org_materialize"
    assert result["failure_class"] == "deterministic"
    assert result["failed_target"] == "org_materialize:org_info"


def test_run_single_scenario_uses_failed_step_retry_count_for_policy(tmp_path, monkeypatch) -> None:
    run_dir = tmp_path / "runs" / "run-3"
    run_dir.mkdir(parents=True)
    scenario_dir = run_dir / "scenarios" / "ent-default"
    project_root = scenario_dir / "cci_project"

    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _defaults, _overrides: {"demo": True})
    monkeypatch.setattr(
        scenario_runner,
        "prepare_scenario_project_root",
        lambda **_kwargs: project_root,
    )
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _root: None)
    monkeypatch.setattr(scenario_runner, "write_build_provenance", lambda **_kwargs: None)
    monkeypatch.setattr(scenario_runner, "evaluate_when", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(scenario_runner, "org_exists", lambda *_args, **_kwargs: True)

    steps = [
        Step(step_number=1, target_type="task", target_name="first", when=None),
        Step(step_number=2, target_type="task", target_name="second", when=None),
    ]

    calls = {"step1_attempt": 0}

    def _run_command(_root, command, *_args, **_kwargs):
        if command[:3] == ["cci", "org", "scratch"] or command[:3] == ["cci", "org", "info"]:
            return {
                "duration_seconds": 0.1,
                "exit_code": 0,
                "failure_signature": "",
                "failure_class": "none",
                "tail": [],
            }
        if command[:3] == ["cci", "task", "run"] and len(command) >= 4 and command[3] == "first":
            calls["step1_attempt"] += 1
            if calls["step1_attempt"] < 3:
                return {
                    "duration_seconds": 0.1,
                    "exit_code": 1,
                    "failure_signature": "temporary",
                    "failure_class": "transient",
                    "tail": [],
                }
            return {
                "duration_seconds": 0.1,
                "exit_code": 0,
                "failure_signature": "",
                "failure_class": "none",
                "tail": [],
            }
        return {
            "duration_seconds": 0.1,
            "exit_code": 2,
            "failure_signature": "fresh failure",
            "failure_class": "unknown",
            "tail": [],
        }

    monkeypatch.setattr(scenario_runner, "run_command", _run_command)
    monkeypatch.setattr(scenario_runner.time, "sleep", lambda _seconds: None)

    result = scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=steps,
        default_flags={"demo": True},
        base_cci={},
        skip_validate=True,
        keep_orgs=True,
        is_resume=False,
    )

    assert result["status"] == "failed"
    assert result["retry_count"] == 0
    assert result["total_retry_count"] == 2
    assert result["policy"]["recommended_action"] == "resume"
    assert result["policy"]["confidence"] == "medium"
