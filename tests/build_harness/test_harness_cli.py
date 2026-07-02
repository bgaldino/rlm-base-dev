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


def _run_args(run_id: str | None, fmt: str = "json") -> argparse.Namespace:
    return argparse.Namespace(
        run_id=run_id,
        scenarios_file="unused.json",
        scenario=None,
        skip_validate=True,
        keep_orgs=False,
        prune_older_than=None,
        format=fmt,
    )


def _report_args(run_id: str, fmt: str = "json") -> argparse.Namespace:
    return argparse.Namespace(
        run_id=run_id,
        prune_older_than=None,
        format=fmt,
    )


def test_resolve_run_dir_rejects_path_traversal(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    output_root.mkdir(parents=True)
    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)

    assert harness._resolve_run_dir("../escape") is None
    assert harness._resolve_run_dir("/tmp/escape") is None


def test_cmd_run_rejects_existing_run_id_directory(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-existing"
    run_dir.mkdir(parents=True)
    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)

    exit_code = harness.cmd_run(_run_args("run-existing"))
    assert exit_code == harness.EXIT_CONFIG_ERROR


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


def test_cmd_resume_blocks_when_org_shape_drifted_from_checkpoint(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-shape-drift"
    scenario_dir = run_dir / "scenarios" / "ent-default"
    scenario_dir.mkdir(parents=True)
    write_json(
        scenario_dir / "checkpoint.json",
        {
            "failed_step": 4,
            "last_successful_step": 3,
            "org_alias": "harness-ent-default-3",
            "org_shape": "dev",
            "effective_flags": {"commerce": True},
        },
    )

    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(harness, "load_cci", lambda _path: {})
    monkeypatch.setattr(harness, "load_default_flags", lambda _cci: {"commerce": True})
    monkeypatch.setattr(harness, "load_prepare_steps", lambda _cci: [])
    monkeypatch.setattr(
        harness,
        "load_scenarios_from_file",
        lambda _path: [{"scenario_id": "ent-default", "org_shape": "ent", "flag_overrides": {}}],
    )
    monkeypatch.setattr(harness, "select_scenarios", lambda items, _selected: items)
    monkeypatch.setattr(harness, "compose_flags", lambda _defaults, _overrides: {"commerce": True})

    exit_code = harness.cmd_resume(_resume_args("run-shape-drift"))
    assert exit_code == harness.EXIT_RESUME_BLOCKED


def test_cmd_resume_blocks_when_prepare_steps_signature_drifted(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-step-drift"
    scenario_dir = run_dir / "scenarios" / "ent-default"
    scenario_dir.mkdir(parents=True)
    write_json(
        scenario_dir / "checkpoint.json",
        {
            "failed_step": 4,
            "last_successful_step": 3,
            "org_alias": "harness-ent-default-4",
            "org_shape": "ent",
            "effective_flags": {"commerce": True},
        },
    )
    write_json(
        run_dir / "run_manifest.json",
        {
            "prepare_steps_signature": [
                {"step_number": 1, "target_type": "flow", "target_name": "prepare_core", "when": None}
            ]
        },
    )

    class _Step:
        def __init__(self, number: int, target_name: str):
            self.step_number = number
            self.target_type = "flow"
            self.target_name = target_name
            self.when = None

    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(harness, "load_cci", lambda _path: {})
    monkeypatch.setattr(harness, "load_default_flags", lambda _cci: {"commerce": True})
    monkeypatch.setattr(harness, "load_prepare_steps", lambda _cci: [_Step(1, "prepare_different")])
    monkeypatch.setattr(
        harness,
        "load_scenarios_from_file",
        lambda _path: [{"scenario_id": "ent-default", "org_shape": "ent", "flag_overrides": {}}],
    )
    monkeypatch.setattr(harness, "select_scenarios", lambda items, _selected: items)
    monkeypatch.setattr(harness, "compose_flags", lambda _defaults, _overrides: {"commerce": True})

    exit_code = harness.cmd_resume(_resume_args("run-step-drift"))
    assert exit_code == harness.EXIT_RESUME_BLOCKED


def test_cmd_report_rewrites_human_readable_artifacts(tmp_path, monkeypatch) -> None:
    output_root = tmp_path / ".harness" / "runs"
    run_dir = output_root / "run-report"
    run_dir.mkdir(parents=True)
    write_json(
        run_dir / "run_summary.json",
        {"run_id": "run-report", "status": "success", "scenario_results": []},
    )

    captured_summary = {}

    def _write_agent_summary(path, summary):
        captured_summary["path"] = path
        captured_summary["summary"] = summary
        (path / "agent_summary.md").write_text("fresh summary", encoding="utf-8")

    monkeypatch.setattr(harness, "DEFAULT_OUTPUT_ROOT", output_root)
    monkeypatch.setattr(harness, "write_all_build_provenance", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(harness, "write_analysis_artifacts", lambda *_args, **_kwargs: {"optimization_recommendations": {}})
    monkeypatch.setattr(harness, "write_agent_summary", _write_agent_summary)
    monkeypatch.setattr(harness, "render_report", lambda *_args, **_kwargs: "fresh report")

    exit_code = harness.cmd_report(_report_args("run-report"))

    assert exit_code == harness.EXIT_SUCCESS
    assert captured_summary["path"] == run_dir
    assert (run_dir / "report.md").read_text(encoding="utf-8") == "fresh report"
    assert (run_dir / "agent_summary.md").read_text(encoding="utf-8") == "fresh summary"
