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
from scripts.build_harness.harness.io import ensure_dir, load_json, now_utc, write_json
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


def load_scenarios_from_file(path: Path) -> List[Dict[str, Any]]:
    return extract_scenarios(load_json(path))


def cmd_run(args: argparse.Namespace) -> int:
    run_id = args.run_id or make_run_id()
    run_dir = DEFAULT_OUTPUT_ROOT / run_id
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
    summary["analysis_artifacts"] = {
        "compatibility_summary": "compatibility_summary.json",
        "dependency_summary": "dependency_summary.json",
        "optimization_recommendations": "optimization_recommendations.json",
    }
    summary["optimization_recommendations"] = analysis.get("optimization_recommendations", {})
    write_json(run_dir / "run_summary.json", summary)
    write_agent_summary(run_dir, summary)
    (run_dir / "report.md").write_text(render_report(run_dir, summary), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_report(run_dir, summary))

    return EXIT_SUCCESS if overall_status == "success" else EXIT_BUILD_FAILED


def cmd_resume(args: argparse.Namespace) -> int:
    run_dir = DEFAULT_OUTPUT_ROOT / args.run_id
    if not run_dir.exists():
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

    # Resume safety: block when scenario flags differ from checkpoint flags.
    effective_from_checkpoint = checkpoint.get("effective_flags", {})
    effective_current = compose_flags(default_flags, scenario.get("flag_overrides", {}))
    if effective_from_checkpoint and effective_current != effective_from_checkpoint:
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
    summary["analysis_artifacts"] = {
        "compatibility_summary": "compatibility_summary.json",
        "dependency_summary": "dependency_summary.json",
        "optimization_recommendations": "optimization_recommendations.json",
    }
    summary["optimization_recommendations"] = analysis.get("optimization_recommendations", {})
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
    run_dir = DEFAULT_OUTPUT_ROOT / args.run_id
    summary_path = run_dir / "run_summary.json"
    if not summary_path.exists():
        print(f"run_summary.json not found for run_id {args.run_id}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    summary = load_json(summary_path)
    write_all_build_provenance(run_dir, summary)
    analysis = write_analysis_artifacts(run_dir, summary)
    summary["analysis_artifacts"] = {
        "compatibility_summary": "compatibility_summary.json",
        "dependency_summary": "dependency_summary.json",
        "optimization_recommendations": "optimization_recommendations.json",
    }
    summary["optimization_recommendations"] = analysis.get("optimization_recommendations", {})
    write_json(summary_path, summary)
    report = render_report(run_dir, summary)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(report)
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
    report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    report.set_defaults(func=cmd_report)

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
