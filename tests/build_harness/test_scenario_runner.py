"""Tests for scripts.build_harness.harness.scenario_runner.

Covers the pure function ``summarize_policy``.
The orchestration function ``run_single_scenario`` is integration-level
(subprocess + filesystem) and not covered here.
"""

from __future__ import annotations

import json

import pytest

from scripts.build_harness.harness.execution import PreflightFailure
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
    monkeypatch.setattr(scenario_runner, "probe_org", lambda *_args, **_kwargs: {"state": "present", "detail": ""})

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


def test_run_single_scenario_accumulates_duration_across_retries(tmp_path, monkeypatch) -> None:
    run_dir = tmp_path / "runs" / "run-4"
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
    monkeypatch.setattr(scenario_runner.time, "sleep", lambda _seconds: None)

    attempt_count = {"prepare": 0}

    def _run_command(_root, command, *_args, **_kwargs):
        if command[:3] == ["cci", "org", "scratch"] or command[:3] == ["cci", "org", "info"]:
            return {
                "duration_seconds": 0.1,
                "exit_code": 0,
                "failure_signature": "",
                "failure_class": "none",
                "tail": [],
            }
        attempt_count["prepare"] += 1
        if attempt_count["prepare"] == 1:
            return {
                "duration_seconds": 2.5,
                "exit_code": 1,
                "failure_signature": "transient",
                "failure_class": "transient",
                "tail": [],
            }
        return {
            "duration_seconds": 3.0,
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
        prepare_steps=[Step(step_number=1, target_type="task", target_name="prepare_core", when=None)],
        default_flags={"demo": True},
        base_cci={},
        skip_validate=True,
        keep_orgs=True,
        is_resume=False,
    )

    assert result["status"] == "success"
    step_results_path = run_dir / "scenarios" / "ent-default" / "step_results.jsonl"
    rows = [json.loads(line) for line in step_results_path.read_text(encoding="utf-8").splitlines()]
    prepare_row = next(row for row in rows if row["phase"] == "prepare_step")
    assert prepare_row["status"] == "success"
    assert prepare_row["duration_seconds"] == pytest.approx(5.5)


def _resume_blocked_result(tmp_path, monkeypatch, probe):
    run_dir = tmp_path / "runs" / "run-9"
    run_dir.mkdir(parents=True)
    project_root = run_dir / "scenarios" / "ent-default" / "cci_project"
    seen = []
    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _d, _o: {"demo": True})
    monkeypatch.setattr(scenario_runner, "prepare_scenario_project_root", lambda **_k: project_root)
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _r: None)
    monkeypatch.setattr(scenario_runner, "write_build_provenance", lambda **_k: None)

    def _probe(_root, sf_alias, **_kwargs):
        seen.append(sf_alias)
        return probe

    monkeypatch.setattr(scenario_runner, "probe_org", _probe)
    result = scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=[Step(step_number=1, target_type="task", target_name="first", when=None)],
        default_flags={"demo": True},
        base_cci={"project": {"name": "proj"}},
        skip_validate=True,
        keep_orgs=True,
        is_resume=True,
        resume_from_step=1,
        existing_alias="demo-org",
    )
    return result, seen


@pytest.mark.parametrize(
    "probe,target,failure_class",
    [
        ({"state": "missing", "detail": "gone"}, "org_missing", "deterministic"),
        ({"state": "timeout", "detail": "slow"}, "org_probe_timeout", "transient"),
        ({"state": "error", "detail": "boom"}, "org_probe_failed", "unknown"),
    ],
)
def test_resume_reports_probe_outcome_distinctly(tmp_path, monkeypatch, probe, target, failure_class) -> None:
    result, seen = _resume_blocked_result(tmp_path, monkeypatch, probe)
    assert seen == ["proj__demo-org"]
    assert result["status"] == "resume_blocked"
    assert result["failed_target"] == target
    assert result["failure_class"] == failure_class
    if target != "org_missing":
        assert "does not exist" not in result["failure_signature"]
        assert "sf org list --all" in result["failure_signature"]
        assert result["can_resume"] is True
        assert result["policy"]["recommended_action"] == "resume"
    else:
        assert result["can_resume"] is False
        assert result["policy"]["recommended_action"] != "resume"


@pytest.mark.parametrize(
    "state,expected",
    [("missing", False), ("timeout", True), ("error", True), ("present", True)],
)
def test_end_of_run_can_resume_follows_probe_state(tmp_path, monkeypatch, state, expected) -> None:
    run_dir = tmp_path / "runs" / "run-11"
    run_dir.mkdir(parents=True)
    project_root = run_dir / "scenarios" / "ent-default" / "cci_project"
    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _d, _o: {"demo": True})
    monkeypatch.setattr(scenario_runner, "prepare_scenario_project_root", lambda **_k: project_root)
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _r: None)
    monkeypatch.setattr(scenario_runner, "write_build_provenance", lambda **_k: None)
    monkeypatch.setattr(scenario_runner, "evaluate_when", lambda *_a, **_k: True)
    monkeypatch.setattr(scenario_runner.time, "sleep", lambda _s: None)
    monkeypatch.setattr(scenario_runner, "probe_org", lambda *_a, **_k: {"state": state, "detail": ""})

    def _run_command(_root, command, *_a, **_k):
        failed = command[:3] == ["cci", "task", "run"]
        return {
            "duration_seconds": 0.1,
            "exit_code": 2 if failed else 0,
            "failure_signature": "boom" if failed else "",
            "failure_class": "deterministic" if failed else "none",
            "tail": [],
        }

    monkeypatch.setattr(scenario_runner, "run_command", _run_command)
    result = scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=[Step(step_number=1, target_type="task", target_name="first", when=None)],
        default_flags={"demo": True},
        base_cci={},
        skip_validate=True,
        keep_orgs=True,
        is_resume=False,
    )
    assert result["status"] == "failed"
    assert result["can_resume"] is expected


def _preflight_failure(tmp_path, monkeypatch, *, is_resume, failure_class="deterministic"):
    run_dir = tmp_path / "runs" / "run-10"
    run_dir.mkdir(parents=True)
    project_root = run_dir / "scenarios" / "ent-default" / "cci_project"
    monkeypatch.setattr(scenario_runner, "compose_flags", lambda _d, _o: {"inapp": True})
    monkeypatch.setattr(scenario_runner, "prepare_scenario_project_root", lambda **_k: project_root)
    monkeypatch.setattr(scenario_runner, "cleanup_scenario_project_root", lambda _r: None)
    monkeypatch.setattr(scenario_runner, "write_build_provenance", lambda **_k: None)
    monkeypatch.setattr(scenario_runner, "verify_project_flags", lambda _root, _flags: PreflightFailure("CCI read inapp=False", failure_class))
    # Neither a CCI command nor the org probe may run when the flags do not reach CCI.
    monkeypatch.setattr(scenario_runner, "run_command", lambda *_a, **_k: pytest.fail("CCI command ran"))
    monkeypatch.setattr(scenario_runner, "probe_org", lambda *_a, **_k: pytest.fail("org probe ran"))
    return scenario_runner.run_single_scenario(
        root=tmp_path,
        scenario=_base_scenario(),
        run_dir=run_dir,
        prepare_steps=[Step(step_number=1, target_type="task", target_name="first", when=None)],
        default_flags={"inapp": False},
        base_cci={},
        skip_validate=False,
        keep_orgs=True,
        is_resume=is_resume,
        resume_from_step=3 if is_resume else None,
        existing_alias="demo-org" if is_resume else None,
    )


def _read_step_results(tmp_path):
    path = tmp_path / "runs" / "run-10" / "scenarios" / "ent-default" / "step_results.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_run_single_scenario_fails_loudly_when_cci_ignores_the_overrides(tmp_path, monkeypatch) -> None:
    result = _preflight_failure(tmp_path, monkeypatch, is_resume=False)
    assert result["status"] == "failed"
    assert result["failed_target"] == "project_root_flags"
    assert result["failure_class"] == "deterministic"
    assert "inapp=False" in result["failure_signature"]
    assert result["can_resume"] is False
    rows = _read_step_results(tmp_path)
    assert len(rows) == 1
    assert rows[0]["phase"] == "preflight" and rows[0]["target_name"] == "project_root_flags"
    assert rows[0]["status"] == "failed" and rows[0]["failure_class"] == "deterministic"


def test_preflight_failure_class_comes_from_the_check(tmp_path, monkeypatch) -> None:
    result = _preflight_failure(tmp_path, monkeypatch, is_resume=False, failure_class="transient")
    assert result["failure_class"] == "transient"
    assert result["can_resume"] is False
    assert _read_step_results(tmp_path)[0]["failure_class"] == "transient"


def test_resume_is_blocked_when_cci_ignores_the_overrides(tmp_path, monkeypatch) -> None:
    result = _preflight_failure(tmp_path, monkeypatch, is_resume=True)
    assert result["status"] == "resume_blocked"
    assert result["failed_step"] == 3
    assert result["failed_target"] == "project_root_flags"
    assert result["can_resume"] is False
    assert result["policy"]["recommended_action"] != "resume"
