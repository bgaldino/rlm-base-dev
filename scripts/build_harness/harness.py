#!/usr/bin/env python3
"""Local build profiling harness for prepare_rlm_org.

This runner is intentionally both human-friendly and AI-agent friendly:
- Stable subcommands: run / resume / report
- Deterministic exit codes for automation
- Structured machine-readable outputs per run
- Checkpoint-based resume from last successful top-level prepare_rlm_org step
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# Bootstrap: make the repo root importable so the absolute imports below
# resolve when the CLI is invoked as a script (`python scripts/build_harness/
# harness.py ...`). Script invocation only adds the script's own directory to
# sys.path, not the repo root, so we add it here.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.build_harness.harness.config import (
    CCI_FILE,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_SCENARIOS_FILE,
    ROOT,
    compose_flags,
    load_cci,
    load_default_flags,
    load_prepare_steps,
    load_scenarios as extract_scenarios,
    select_scenarios,
)
from scripts.build_harness.harness.execution import make_run_id
from scripts.build_harness.harness.io import (
    ensure_dir,
    load_json,
    now_utc,
    parse_retention,
    prune_old_runs,
    write_json,
)
from scripts.build_harness.harness.provenance import write_all_build_provenance
from scripts.build_harness.harness.reporting import (
    render_report,
    write_agent_summary,
    write_analysis_artifacts,
)
from scripts.build_harness.harness.scenario_runner import run_single_scenario

EXIT_SUCCESS = 0
EXIT_BUILD_FAILED = 10
EXIT_CONFIG_ERROR = 20
EXIT_RESUME_BLOCKED = 30


def _prepare_steps_signature(steps: List[Any]) -> List[Dict[str, Any]]:
    """Serialize top-level prepare steps for resume-safety drift checks."""
    return [
        {
            "step_number": int(step.step_number),
            "target_type": str(step.target_type),
            "target_name": str(step.target_name),
            "when": step.when,
        }
        for step in steps
    ]


def _resolve_run_dir(run_id: str, *, must_exist: bool = False) -> Optional[Path]:
    """Resolve a run-id path safely under DEFAULT_OUTPUT_ROOT."""
    run_id_clean = run_id.strip()
    if not run_id_clean:
        return None
    output_root = DEFAULT_OUTPUT_ROOT.resolve()
    run_dir = (output_root / run_id_clean).resolve()
    if not run_dir.is_relative_to(output_root):
        return None
    if must_exist and not run_dir.exists():
        return None
    return run_dir


def load_scenarios_from_file(path: Path) -> List[Dict[str, Any]]:
    return extract_scenarios(load_json(path))


def _render_pruned_runs(removed: List[Path], *, quiet: bool = False) -> None:
    if quiet:
        return
    if not removed:
        print("[harness] prune requested; no run directories were removed.")
        return
    print(f"[harness] pruned {len(removed)} run directories:")
    for item in removed:
        print(f"  - {item.name}")


def _maybe_prune_runs(raw_retention: Optional[str], *, quiet: bool = False) -> None:
    if not raw_retention:
        return
    retention = parse_retention(raw_retention)
    removed = prune_old_runs(DEFAULT_OUTPUT_ROOT, retention)
    _render_pruned_runs(removed, quiet=quiet)


def _attach_analysis_artifacts(summary: Dict[str, Any], analysis: Dict[str, Any]) -> None:
    summary["analysis_artifacts"] = {
        "compatibility_summary": "compatibility_summary.json",
        "dependency_summary": "dependency_summary.json",
        "optimization_recommendations": "optimization_recommendations.json",
    }
    summary["optimization_recommendations"] = analysis.get("optimization_recommendations", {})


def cmd_run(args: argparse.Namespace) -> int:
    json_output = args.format == "json"
    _maybe_prune_runs(args.prune_older_than, quiet=json_output)
    run_id = args.run_id or make_run_id()
    if not args.run_id:
        suffix = 2
        while _resolve_run_dir(run_id, must_exist=True) is not None:
            run_id = f"{make_run_id()}-{suffix}"
            suffix += 1
    run_dir = _resolve_run_dir(run_id)
    if run_dir is None:
        print(f"Invalid run id: {run_id}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    if run_dir.exists():
        print(
            f"Run directory already exists for run id '{run_id}'. "
            "Choose a new --run-id or omit it to auto-generate one.",
            file=sys.stderr,
        )
        return EXIT_CONFIG_ERROR
    ensure_dir(run_dir)
    ensure_dir(run_dir / "scenarios")

    cci = load_cci(CCI_FILE)
    default_flags = load_default_flags(cci)
    steps = load_prepare_steps(cci)
    all_scenarios = load_scenarios_from_file(Path(args.scenarios_file))
    selected = select_scenarios(all_scenarios, args.scenario)

    scenarios_file = Path(args.scenarios_file)
    run_manifest = {
        "run_id": run_id,
        "started_at": now_utc(),
        "command": "run",
        "scenarios_file": str(scenarios_file.relative_to(ROOT)) if scenarios_file.is_absolute() and scenarios_file.is_relative_to(ROOT) else str(scenarios_file),
        "selected_scenarios": [item["scenario_id"] for item in selected],
        "git_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True).stdout.strip(),
        "prepare_steps_signature": _prepare_steps_signature(steps),
    }
    write_json(run_dir / "run_manifest.json", run_manifest)

    scenario_results: List[Dict[str, Any]] = []
    overall_status = "success"

    for scenario in selected:
        result = run_single_scenario(
            root=ROOT,
            scenario=scenario,
            run_dir=run_dir,
            prepare_steps=steps,
            default_flags=default_flags,
            base_cci=cci,
            skip_validate=args.skip_validate,
            keep_orgs=args.keep_orgs,
            is_resume=False,
            stream_output=not json_output,
        )
        scenario_results.append(result)
        if result["status"] != "success":
            overall_status = "failed"

    summary = {
        "run_id": run_id,
        "started_at": run_manifest["started_at"],
        "finished_at": now_utc(),
        "status": overall_status,
        "scenario_results": scenario_results,
    }
    analysis = write_analysis_artifacts(run_dir, summary)
    _attach_analysis_artifacts(summary, analysis)
    write_json(run_dir / "run_summary.json", summary)
    write_agent_summary(run_dir, summary)
    (run_dir / "report.md").write_text(render_report(run_dir, summary), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_report(run_dir, summary))

    return EXIT_SUCCESS if overall_status == "success" else EXIT_BUILD_FAILED


def cmd_resume(args: argparse.Namespace) -> int:
    json_output = args.format == "json"
    run_dir = _resolve_run_dir(args.run_id, must_exist=True)
    if run_dir is None:
        print(f"Run id not found: {args.run_id}", file=sys.stderr)
        return EXIT_RESUME_BLOCKED

    cci = load_cci(CCI_FILE)
    default_flags = load_default_flags(cci)
    steps = load_prepare_steps(cci)
    all_scenarios = load_scenarios_from_file(Path(args.scenarios_file))
    selected = select_scenarios(all_scenarios, [args.scenario])
    scenario = selected[0]
    scenario_dir = run_dir / "scenarios" / args.scenario
    checkpoint_path = scenario_dir / "checkpoint.json"
    if not checkpoint_path.exists():
        print(f"Checkpoint not found for scenario {args.scenario}", file=sys.stderr)
        return EXIT_RESUME_BLOCKED

    checkpoint = load_json(checkpoint_path)
    failed_step = checkpoint.get("failed_step")
    last_successful_step = int(checkpoint.get("last_successful_step", 0))
    resume_from = int(failed_step or (last_successful_step + 1))
    org_alias = checkpoint.get("org_alias")
    if not org_alias:
        print("Checkpoint missing org alias", file=sys.stderr)
        return EXIT_RESUME_BLOCKED

    checkpoint_shape = checkpoint.get("org_shape")
    scenario_shape = scenario.get("org_shape")
    if checkpoint_shape and scenario_shape and checkpoint_shape != scenario_shape:
        print(
            "Resume blocked: scenario org shape changed since checkpoint. "
            "Run full scenario instead.",
            file=sys.stderr,
        )
        return EXIT_RESUME_BLOCKED

    scenario_manifest_path = scenario_dir / "scenario_manifest.json"
    if scenario_manifest_path.exists():
        scenario_manifest = load_json(scenario_manifest_path)
        manifest_shape = scenario_manifest.get("org_shape")
        if manifest_shape and scenario_shape and manifest_shape != scenario_shape:
            print(
                "Resume blocked: scenario org shape changed since original run manifest. "
                "Run full scenario instead.",
                file=sys.stderr,
            )
            return EXIT_RESUME_BLOCKED

    run_manifest_path = run_dir / "run_manifest.json"
    if run_manifest_path.exists():
        run_manifest = load_json(run_manifest_path)
        recorded_signature = run_manifest.get("prepare_steps_signature")
        if recorded_signature is not None:
            current_signature = _prepare_steps_signature(steps)
            if current_signature != recorded_signature:
                print(
                    "Resume blocked: prepare_rlm_org step signature changed since run start. "
                    "Run full scenario instead.",
                    file=sys.stderr,
                )
                return EXIT_RESUME_BLOCKED

    # Resume safety: block when scenario flags differ from checkpoint flags.
    effective_from_checkpoint = checkpoint.get("effective_flags")
    effective_current = compose_flags(default_flags, scenario.get("flag_overrides", {}))
    if effective_from_checkpoint is not None and effective_current != effective_from_checkpoint:
        print(
            "Resume blocked: scenario flags changed since checkpoint. "
            "Run full scenario instead.",
            file=sys.stderr,
        )
        return EXIT_RESUME_BLOCKED

    result = run_single_scenario(
        root=ROOT,
        scenario=scenario,
        run_dir=run_dir,
        prepare_steps=steps,
        default_flags=default_flags,
        base_cci=cci,
        skip_validate=True,
        keep_orgs=args.keep_orgs,
        is_resume=True,
        resume_from_step=resume_from,
        existing_alias=org_alias,
        stream_output=not json_output,
    )

    summary_path = run_dir / "run_summary.json"
    summary = load_json(summary_path) if summary_path.exists() else {"run_id": args.run_id, "scenario_results": []}
    if "started_at" not in summary:
        manifest_path = run_dir / "run_manifest.json"
        if manifest_path.exists():
            manifest = load_json(manifest_path)
            summary["started_at"] = manifest.get("started_at", now_utc())
        else:
            summary["started_at"] = now_utc()
    replaced = False
    for idx, item in enumerate(summary["scenario_results"]):
        if item.get("scenario_id") == args.scenario:
            summary["scenario_results"][idx] = result
            replaced = True
            break
    if not replaced:
        summary["scenario_results"].append(result)

    summary["finished_at"] = now_utc()
    summary["status"] = "success" if all(s.get("status") == "success" for s in summary["scenario_results"]) else "failed"
    analysis = write_analysis_artifacts(run_dir, summary)
    _attach_analysis_artifacts(summary, analysis)
    write_json(summary_path, summary)
    write_agent_summary(run_dir, summary)
    (run_dir / "report.md").write_text(render_report(run_dir, summary), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_report(run_dir, summary))

    if result["status"] == "resume_blocked":
        return EXIT_RESUME_BLOCKED
    if result["status"] != "success":
        return EXIT_BUILD_FAILED
    return EXIT_SUCCESS


def cmd_report(args: argparse.Namespace) -> int:
    json_output = args.format == "json"
    _maybe_prune_runs(args.prune_older_than, quiet=json_output)
    run_dir = _resolve_run_dir(args.run_id, must_exist=True)
    if run_dir is None:
        print(f"run_summary.json not found for run_id {args.run_id}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    summary_path = run_dir / "run_summary.json"
    if not summary_path.exists():
        print(f"run_summary.json not found for run_id {args.run_id}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    summary = load_json(summary_path)
    write_all_build_provenance(run_dir, summary)
    analysis = write_analysis_artifacts(run_dir, summary)
    _attach_analysis_artifacts(summary, analysis)
    write_json(summary_path, summary)
    report = render_report(run_dir, summary)
    write_agent_summary(run_dir, summary)
    (run_dir / "report.md").write_text(report, encoding="utf-8")
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(report)
    return EXIT_SUCCESS


def cmd_prune(args: argparse.Namespace) -> int:
    retention = parse_retention(args.prune_older_than)
    removed = prune_old_runs(DEFAULT_OUTPUT_ROOT, retention)
    _render_pruned_runs(removed, quiet=args.format == "json")
    payload = {
        "output_root": str(DEFAULT_OUTPUT_ROOT),
        "retention": args.prune_older_than,
        "removed_count": len(removed),
        "removed": [item.name for item in removed],
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    return EXIT_SUCCESS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build profiling harness for dev/ent org shapes.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run scenarios from manifest.")
    run.add_argument("--run-id", help="Optional run id. Defaults to timestamped id.")
    run.add_argument(
        "--scenarios-file",
        default=str(DEFAULT_SCENARIOS_FILE),
        help="Path to scenario manifest JSON.",
    )
    run.add_argument(
        "--scenario",
        action="append",
        help="Scenario id to run (can pass multiple). Defaults to all scenarios.",
    )
    run.add_argument("--skip-validate", action="store_true", help="Skip validate_setup preflight.")
    run.add_argument("--keep-orgs", action="store_true", help="Keep orgs after success (default is delete on success).")
    run.add_argument(
        "--prune-older-than",
        help="Optional retention window for pruning old .harness/runs dirs (e.g. 7d, 24h).",
    )
    run.add_argument("--format", choices=("markdown", "json"), default="markdown")
    run.set_defaults(func=cmd_run)

    resume = sub.add_parser("resume", help="Resume a failed scenario from checkpoint.")
    resume.add_argument("--run-id", required=True, help="Existing run id.")
    resume.add_argument("--scenario", required=True, help="Scenario id to resume.")
    resume.add_argument(
        "--scenarios-file",
        default=str(DEFAULT_SCENARIOS_FILE),
        help="Path to scenario manifest JSON.",
    )
    resume.add_argument("--keep-orgs", action="store_true", help="Keep org after successful resume.")
    resume.add_argument("--format", choices=("markdown", "json"), default="markdown")
    resume.set_defaults(func=cmd_resume)

    report = sub.add_parser("report", help="Render report for a completed run id.")
    report.add_argument("--run-id", required=True, help="Existing run id.")
    report.add_argument(
        "--prune-older-than",
        help="Optional retention window for pruning old .harness/runs dirs (e.g. 7d, 24h).",
    )
    report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    report.set_defaults(func=cmd_report)

    prune = sub.add_parser("prune", help="Delete old run directories under .harness/runs.")
    prune.add_argument(
        "--prune-older-than",
        default="7d",
        help="Retention window (default: 7d). Use values like 7d, 24h, 30m.",
    )
    prune.add_argument("--format", choices=("markdown", "json"), default="markdown")
    prune.set_defaults(func=cmd_prune)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FileNotFoundError as exc:
        print(f"Missing file: {exc}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return EXIT_CONFIG_ERROR


if __name__ == "__main__":
    sys.exit(main())
