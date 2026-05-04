from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from scripts.build_harness.harness.io import write_json


_HARNESS_CLI_PATH = Path(__file__).resolve().parents[2] / "scripts" / "build_harness" / "harness.py"
_HARNESS_CLI_SPEC = importlib.util.spec_from_file_location("build_harness_cli_module", _HARNESS_CLI_PATH)
assert _HARNESS_CLI_SPEC and _HARNESS_CLI_SPEC.loader
harness = importlib.util.module_from_spec(_HARNESS_CLI_SPEC)
_HARNESS_CLI_SPEC.loader.exec_module(harness)


def _resume_args(run_id: str) -> argparse.Namespace:
    return argparse.Namespace(
        run_id=run_id,
        scenario="ent-default",
        scenarios_file="unused.json",
        keep_orgs=False,
        format="json",
    )


def test_resolve_run_dir_rejects_path_traversal(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    output_root.mkdir(parents=True)
    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)

    assert harness._resolve_run_dir("../escape") is None
    assert harness._resolve_run_dir("/tmp/escape") is None


def test_cmd_resume_blocks_when_checkpoint_flags_drift_from_empty_dict(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-1"
    scenario_dir = run_dir / "scenarios" / "ent-default"
    scenario_dir.mkdir(parents=True)
    write_json(
        scenario_dir / "checkpoint.json",
        {
            "failed_step": 7,
            "last_successful_step": 6,
            "org_alias": "harness-ent-default-1",
            "effective_flags": {},
        },
    )

    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(harness, "load_cci", lambda _path: {})
    monkeypatch.setattr(harness, "load_default_flags", lambda _cci: {"commerce": True})
    monkeypatch.setattr(harness, "load_prepare_steps", lambda _cci: [])
    monkeypatch.setattr(harness, "load_scenarios_from_file", lambda _path: [{"scenario_id": "ent-default", "flag_overrides": {}}])
    monkeypatch.setattr(harness, "select_scenarios", lambda items, _selected: items)
    monkeypatch.setattr(harness, "compose_flags", lambda _defaults, _overrides: {"commerce": False})

    exit_code = harness.cmd_resume(_resume_args("run-1"))
    assert exit_code == harness.EXIT_RESUME_BLOCKED


def test_cmd_resume_allows_missing_checkpoint_flags(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-2"
    scenario_dir = run_dir / "scenarios" / "ent-default"
    scenario_dir.mkdir(parents=True)
    write_json(
        scenario_dir / "checkpoint.json",
        {
            "failed_step": 4,
            "last_successful_step": 3,
            "org_alias": "harness-ent-default-2",
        },
    )

    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(harness, "load_cci", lambda _path: {})
    monkeypatch.setattr(harness, "load_default_flags", lambda _cci: {"commerce": True})
    monkeypatch.setattr(harness, "load_prepare_steps", lambda _cci: [])
    monkeypatch.setattr(harness, "load_scenarios_from_file", lambda _path: [{"scenario_id": "ent-default", "flag_overrides": {}}])
    monkeypatch.setattr(harness, "select_scenarios", lambda items, _selected: items)
    monkeypatch.setattr(harness, "compose_flags", lambda _defaults, _overrides: {"commerce": False})
    monkeypatch.setattr(
        harness,
        "run_single_scenario",
        lambda **_kwargs: {"status": "success", "scenario_id": "ent-default"},
    )
    monkeypatch.setattr(harness, "write_analysis_artifacts", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(harness, "write_agent_summary", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(harness, "render_report", lambda *_args, **_kwargs: "ok")

    exit_code = harness.cmd_resume(_resume_args("run-2"))
    assert exit_code == harness.EXIT_SUCCESS
