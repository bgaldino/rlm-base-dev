"""Tests for scripts.build_harness.tui.runner."""

from __future__ import annotations

from pathlib import Path
from threading import Event
from types import SimpleNamespace
from typing import Any, Dict, List

import yaml

from scripts.build_harness.tui import runner
from scripts.build_harness.tui.state import BuildConfig, RunEvent


def _emit_collector(events: List[RunEvent]):
    def _emit(event: RunEvent) -> None:
        events.append(event)

    return _emit


def _build_config(*, overrides: Dict[str, bool]) -> BuildConfig:
    return BuildConfig(
        org_shape="ent",
        org_alias="ent-a3f9",
        days=30,
        flag_overrides=overrides,
    )


def test_run_build_materializes_workspace_with_overrides(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    base_cci = {"project": {"custom": {"commerce": True, "billing": True}}, "flows": {"prepare_rlm_org": {"steps": {}}}, "orgs": {"scratch": {"ent": {"config_file": "orgs/ent.json", "days": 30}}}}
    monkeypatch.setattr(runner, "load_cci", lambda _: base_cci)
    monkeypatch.setattr(runner, "load_prepare_steps", lambda _: [])

    observed: Dict[str, Any] = {"project_root": None, "custom": None, "commands": []}

    def _run_command(*args, **kwargs):
        observed["commands"].append(list(args[0]))
        observed["project_root"] = kwargs.get("cwd")
        return {"duration_seconds": 0.01, "exit_code": 0, "failure_signature": ""}

    def _cleanup(project_root: Path):
        payload = yaml.safe_load((project_root / "cumulusci.yml").read_text(encoding="utf-8"))
        observed["custom"] = payload["project"]["custom"]
        return None

    monkeypatch.setattr(runner, "_run_command", _run_command)
    monkeypatch.setattr(runner, "cleanup_scenario_project_root", _cleanup)

    events: List[RunEvent] = []
    config = _build_config(
        overrides={"commerce": False},
    )
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 0
    assert observed["project_root"] is not None
    assert observed["custom"] == {"commerce": False, "billing": True}
    assert observed["commands"][:2] == [
        ["cci", "org", "scratch", "ent", "ent-a3f9", "--days", "30"],
        ["cci", "org", "info", "ent-a3f9"],
    ]


def test_run_build_cleans_up_workspace_on_success(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "load_cci", lambda _: {"project": {"custom": {}}, "flows": {"prepare_rlm_org": {"steps": {}}}, "orgs": {"scratch": {"ent": {"config_file": "orgs/ent.json", "days": 30}}}})
    monkeypatch.setattr(
        runner,
        "load_prepare_steps",
        lambda _: [SimpleNamespace(step_number=1, target_type="task", target_name="demo", when=None)],
    )

    cleanup_calls = {"count": 0}

    def _cleanup(project_root: Path):
        cleanup_calls["count"] += 1
        return None

    monkeypatch.setattr(runner, "cleanup_scenario_project_root", _cleanup)
    monkeypatch.setattr(runner, "evaluate_when", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        runner,
        "_run_command",
        lambda *_args, **_kwargs: {"duration_seconds": 0.01, "exit_code": 0, "failure_signature": ""},
    )

    events: List[RunEvent] = []
    config = _build_config(overrides={})
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 0
    assert cleanup_calls["count"] == 1
    step_started_numbers = [
        int(event.payload.get("step_number", -1))
        for event in events
        if event.kind.value == "step_started"
    ]
    assert step_started_numbers[:2] == [0, 1]


def test_run_build_cleans_up_workspace_on_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "load_cci", lambda _: {"project": {"custom": {}}, "flows": {"prepare_rlm_org": {"steps": {}}}, "orgs": {"scratch": {"ent": {"config_file": "orgs/ent.json", "days": 30}}}})
    monkeypatch.setattr(runner, "load_prepare_steps", lambda _: [])

    cleanup_calls = {"count": 0}

    def _cleanup(project_root: Path):
        cleanup_calls["count"] += 1
        return None

    monkeypatch.setattr(runner, "cleanup_scenario_project_root", _cleanup)
    monkeypatch.setattr(
        runner,
        "_run_command",
        lambda *_args, **_kwargs: {
            "duration_seconds": 0.02,
            "exit_code": 42,
            "failure_signature": "synthetic failure",
        },
    )

    events: List[RunEvent] = []
    config = _build_config(overrides={})
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 42
    assert cleanup_calls["count"] == 1
    assert any(event.kind.value == "run_failed" for event in events)


def test_run_build_fails_when_org_materialization_fails(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(
        runner,
        "load_cci",
        lambda _: {
            "project": {"custom": {}},
            "flows": {"prepare_rlm_org": {"steps": {}}},
            "orgs": {"scratch": {"ent": {"config_file": "orgs/ent.json", "days": 30}}},
        },
    )
    monkeypatch.setattr(runner, "load_prepare_steps", lambda _: [])
    monkeypatch.setattr(runner, "cleanup_scenario_project_root", lambda _root: None)

    call_state = {"count": 0}

    def _run_command(*_args, **_kwargs):
        call_state["count"] += 1
        if call_state["count"] == 1:
            return {"duration_seconds": 0.02, "exit_code": 0, "failure_signature": ""}
        return {"duration_seconds": 0.02, "exit_code": 9, "failure_signature": "materialize failed"}

    monkeypatch.setattr(runner, "_run_command", _run_command)

    events: List[RunEvent] = []
    config = _build_config(overrides={})
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 9
    assert any(
        event.kind.value == "run_failed"
        and event.payload.get("message") == "Scratch org materialization failed."
        for event in events
    )
    assert any(
        event.kind.value == "step_failed" and int(event.payload.get("step_number", -1)) == 0
        for event in events
    )
