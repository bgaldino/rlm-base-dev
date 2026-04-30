"""Tests for scripts.build_harness.tui.runner."""

from __future__ import annotations

from pathlib import Path
from threading import Event
from types import SimpleNamespace
from typing import Any, Dict, List

import yaml

from scripts.build_harness.tui import runner
from scripts.build_harness.tui.state import BuildConfig, OrgShape, RunEvent


def _emit_collector(events: List[RunEvent]):
    def _emit(event: RunEvent) -> None:
        events.append(event)

    return _emit


def _build_config(*, overrides: Dict[str, bool], effective_flags: Dict[str, Any]) -> BuildConfig:
    return BuildConfig(
        org_shape="ent",
        org_alias="ent-a3f9",
        days=30,
        flag_overrides=overrides,
        effective_flags=effective_flags,
    )


def test_run_build_materializes_workspace_with_overrides(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "load_tui_config", lambda: ([OrgShape("ent", "orgs/ent.json", 30)], {}, {}, [], {}))
    base_cci = {"project": {"custom": {"commerce": True, "billing": True}}, "flows": {"prepare_rlm_org": {"steps": {}}}}
    monkeypatch.setattr(runner, "load_cci", lambda _: base_cci)
    monkeypatch.setattr(runner, "load_prepare_steps", lambda _: [])

    observed: Dict[str, Any] = {"project_root": None, "custom": None}

    def _run_command(*args, **kwargs):
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
        effective_flags={"commerce": False, "billing": True},
    )
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 0
    assert observed["project_root"] is not None
    assert observed["custom"] == {"commerce": False, "billing": True}


def test_run_build_cleans_up_workspace_on_success(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "load_tui_config", lambda: ([OrgShape("ent", "orgs/ent.json", 30)], {}, {}, [], {}))
    monkeypatch.setattr(runner, "load_cci", lambda _: {"project": {"custom": {}}, "flows": {"prepare_rlm_org": {"steps": {}}}})
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
    config = _build_config(overrides={}, effective_flags={})
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 0
    assert cleanup_calls["count"] == 1


def test_run_build_cleans_up_workspace_on_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "load_tui_config", lambda: ([OrgShape("ent", "orgs/ent.json", 30)], {}, {}, [], {}))
    monkeypatch.setattr(runner, "load_cci", lambda _: {"project": {"custom": {}}, "flows": {"prepare_rlm_org": {"steps": {}}}})
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
    config = _build_config(overrides={}, effective_flags={})
    code = runner.run_build(config=config, stop_event=Event(), emit=_emit_collector(events))

    assert code == 42
    assert cleanup_calls["count"] == 1
    assert any(event.kind.value == "run_failed" for event in events)
