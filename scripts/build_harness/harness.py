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
import copy
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

EXIT_SUCCESS = 0
EXIT_BUILD_FAILED = 10
EXIT_CONFIG_ERROR = 20
EXIT_RESUME_BLOCKED = 30

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIOS_FILE = ROOT / "scripts" / "build_harness" / "scenarios.json"
DEFAULT_OUTPUT_ROOT = ROOT / ".harness" / "runs"
CCI_FILE = ROOT / "cumulusci.yml"

TRANSIENT_PATTERNS = (
    "timed out",
    "timeout",
    "connection reset",
    "temporarily unavailable",
    "503",
    "502",
    "429",
    "service unavailable",
    "network is unreachable",
    "name or service not known",
)

DETERMINISTIC_PATTERNS = (
    "invalid field",
    "no such column",
    "malformed",
    "yaml",
    "traceback",
    "assertionerror",
    "keyerror",
    "validation error",
    "does not exist",
    "unknown option",
    "not found",
)


@dataclass
class Step:
    step_number: int
    target_type: str  # flow or task
    target_name: str
    when: Optional[str]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def to_cli_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def load_cci() -> Dict[str, Any]:
    with CCI_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_default_flags(cci: Dict[str, Any]) -> Dict[str, Any]:
    custom = cci.get("project", {}).get("custom", {})
    if not isinstance(custom, dict):
        raise ValueError("project.custom missing or invalid in cumulusci.yml")
    return custom


def load_prepare_steps(cci: Dict[str, Any]) -> List[Step]:
    flow = cci.get("flows", {}).get("prepare_rlm_org", {})
    steps = flow.get("steps", {})
    if not isinstance(steps, dict):
        raise ValueError("flows.prepare_rlm_org.steps missing or invalid")

    parsed: List[Step] = []
    for raw_number, raw_step in steps.items():
        if not isinstance(raw_step, dict):
            raise ValueError(f"Invalid step config for {raw_number}: expected object")

        target_type = "flow" if "flow" in raw_step else "task" if "task" in raw_step else None
        if target_type is None:
            raise ValueError(f"Step {raw_number} missing flow/task target")

        step_number = int(raw_number)
        parsed.append(
            Step(
                step_number=step_number,
                target_type=target_type,
                target_name=str(raw_step[target_type]),
                when=raw_step.get("when"),
            )
        )

    return sorted(parsed, key=lambda item: item.step_number)


def evaluate_when(expression: Optional[str], flags: Dict[str, Any], org_name: str, org_is_scratch: bool = True) -> bool:
    if not expression:
        return True

    # CCI-style expression to Python expression with concrete values.
    rendered = expression
    rendered = re.sub(
        r"project_config\.project__custom__([A-Za-z0-9_]+)",
        lambda m: str(bool(flags.get(m.group(1), False))),
        rendered,
    )
    rendered = rendered.replace("org_config.scratch", str(org_is_scratch))
    rendered = rendered.replace("org_config.name", repr(org_name))

    try:
        return bool(eval(rendered, {"__builtins__": {}}, {}))  # noqa: S307 - controlled input domain
    except Exception:
        # Conservative default: execute when expression cannot be interpreted.
        return True


def classify_signature(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in TRANSIENT_PATTERNS):
        return "transient"
    if any(token in lowered for token in DETERMINISTIC_PATTERNS):
        return "deterministic"
    return "unknown"


def run_command(
    command: List[str],
    log_path: Path,
    print_prefix: str = "",
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    start = time.monotonic()
    started_at = now_utc()
    tail = deque(maxlen=250)

    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n[{started_at}] COMMAND: {' '.join(command)}\n")
        log_handle.flush()

        process = subprocess.Popen(
            command,
            cwd=str(cwd or ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        assert process.stdout is not None
        for line in process.stdout:
            tail.append(line.rstrip("\n"))
            log_handle.write(line)
            if print_prefix:
                print(f"{print_prefix}{line}", end="")
            else:
                print(line, end="")

        process.wait()

    duration = round(time.monotonic() - start, 3)
    lines = list(tail)
    signature_line = ""
    for candidate in reversed(lines):
        low = candidate.lower()
        if "cci error --help" in low or "debugging errors" in low:
            continue
        if any(token in low for token in ("error", "exception", "failed", "traceback")):
            signature_line = candidate.strip()
            break
    if not signature_line and lines:
        signature_line = lines[-1].strip()

    return {
        "started_at": started_at,
        "finished_at": now_utc(),
        "duration_seconds": duration,
        "exit_code": int(process.returncode),
        "failure_signature": signature_line,
        "failure_class": classify_signature(signature_line) if process.returncode != 0 else "none",
        "tail": lines[-20:],
    }


def org_exists(alias: str) -> bool:
    result = subprocess.run(
        ["cci", "org", "info", alias],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def make_run_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{stamp}"


def load_scenarios(path: Path) -> List[Dict[str, Any]]:
    payload = load_json(path)
    scenarios = payload.get("scenarios", [])
    if not scenarios:
        raise ValueError("Scenario file contains no scenarios")
    return scenarios


def select_scenarios(all_scenarios: List[Dict[str, Any]], requested: Optional[List[str]]) -> List[Dict[str, Any]]:
    if not requested:
        return all_scenarios
    index = {item["scenario_id"]: item for item in all_scenarios}
    missing = [scenario_id for scenario_id in requested if scenario_id not in index]
    if missing:
        raise ValueError(f"Unknown scenario_id(s): {', '.join(sorted(missing))}")
    return [index[scenario_id] for scenario_id in requested]


def compose_flags(default_flags: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(default_flags)
    merged.update(overrides or {})
    return merged


def alias_for_scenario(scenario: Dict[str, Any], run_id: str) -> str:
    prefix = scenario.get("org_alias_prefix") or f"harness-{scenario['scenario_id']}"
    compact = run_id.replace("run-", "").lower()[-12:]
    return f"{prefix}-{compact}"[:60]


def write_checkpoint(path: Path, payload: Dict[str, Any]) -> None:
    write_json(path, payload)


def prepare_scenario_project_root(
    scenario_dir: Path,
    base_cci: Dict[str, Any],
    effective_flags: Dict[str, Any],
) -> Path:
    """Create a scenario-scoped CCI project root with overridden feature flags.

    We avoid mutating the real repository-level cumulusci.yml while still letting
    CCI evaluate all nested flow/task `when:` expressions against scenario flags.
    """
    project_root = scenario_dir / "cci_project"
    ensure_dir(project_root)

    for item in ROOT.iterdir():
        if item.name == "cumulusci.yml":
            continue
        destination = project_root / item.name
        if destination.exists() or destination.is_symlink():
            continue
        os.symlink(item, destination, target_is_directory=item.is_dir())

    cci_override = copy.deepcopy(base_cci)
    project = cci_override.setdefault("project", {})
    project["custom"] = effective_flags
    with (project_root / "cumulusci.yml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(cci_override, handle, sort_keys=False)

    return project_root


def summarize_policy(
    status: str,
    can_resume: bool,
    failure_class: str,
    failed_step: Optional[int],
    retry_count: int,
) -> Dict[str, Any]:
    if status == "success":
        return {
            "recommended_action": "none",
            "operator_message": "Build completed successfully.",
            "confidence": "high",
        }

    if can_resume and failure_class in ("transient", "unknown") and retry_count < 2:
        return {
            "recommended_action": "resume",
            "operator_message": f"Run `python scripts/build_harness/harness.py resume --run-id <run_id> --scenario <scenario_id>` to continue from step {failed_step}.",
            "confidence": "medium",
        }

    if failure_class == "deterministic":
        return {
            "recommended_action": "manual_fix_required",
            "operator_message": "Failure appears deterministic; apply a config/code fix before rerun.",
            "confidence": "high",
        }

    if can_resume:
        return {
            "recommended_action": "resume",
            "operator_message": f"Resume is available from step {failed_step}.",
            "confidence": "low",
        }

    return {
        "recommended_action": "rerun_full",
        "operator_message": "Resume is blocked; re-run full scenario after addressing blocker.",
        "confidence": "medium",
    }


def run_single_scenario(
    scenario: Dict[str, Any],
    run_dir: Path,
    prepare_steps: List[Step],
    default_flags: Dict[str, Any],
    base_cci: Dict[str, Any],
    skip_validate: bool,
    keep_orgs: bool,
    is_resume: bool,
    resume_from_step: Optional[int] = None,
    existing_alias: Optional[str] = None,
) -> Dict[str, Any]:
    scenario_id = scenario["scenario_id"]
    scenario_dir = run_dir / "scenarios" / scenario_id
    ensure_dir(scenario_dir)

    log_path = scenario_dir / "scenario.log"
    checkpoint_path = scenario_dir / "checkpoint.json"
    step_results_path = scenario_dir / "step_results.jsonl"
    metadata_path = scenario_dir / "scenario_manifest.json"

    flags = compose_flags(default_flags, scenario.get("flag_overrides", {}))
    project_root = prepare_scenario_project_root(
        scenario_dir=scenario_dir,
        base_cci=base_cci,
        effective_flags=flags,
    )
    org_alias = existing_alias or alias_for_scenario(scenario, run_dir.name)
    org_shape = scenario["org_shape"]
    days = int(scenario.get("days", 1))

    scenario_manifest = {
        "scenario_id": scenario_id,
        "org_shape": org_shape,
        "org_alias": org_alias,
        "days": days,
        "flag_overrides": scenario.get("flag_overrides", {}),
        "effective_flags": flags,
        "started_at": now_utc(),
        "mode": "resume" if is_resume else "run",
    }
    write_json(metadata_path, scenario_manifest)

    retry_budget = 2
    scenario_status = "success"
    first_failed_step: Optional[int] = None
    first_failed_target: Optional[str] = None
    last_failure_class = "none"
    last_failure_signature = ""
    total_retries = 0

    def record_event(event: Dict[str, Any]) -> None:
        base = {"scenario_id": scenario_id, "org_alias": org_alias, "recorded_at": now_utc()}
        base.update(event)
        append_jsonl(step_results_path, base)

    if not skip_validate and not is_resume:
        validate_result = run_command(
            ["cci", "task", "run", "validate_setup"],
            log_path,
            print_prefix=f"[{scenario_id}] ",
            cwd=project_root,
        )
        record_event(
            {
                "phase": "preflight",
                "step_number": 0,
                "target_type": "task",
                "target_name": "validate_setup",
                "status": "success" if validate_result["exit_code"] == 0 else "failed",
                "duration_seconds": validate_result["duration_seconds"],
                "exit_code": validate_result["exit_code"],
                "failure_signature": validate_result["failure_signature"],
                "failure_class": validate_result["failure_class"],
                "retries_used": 0,
            }
        )
        if validate_result["exit_code"] != 0:
            return {
                "scenario_id": scenario_id,
                "status": "failed",
                "failed_step": 0,
                "failed_target": "validate_setup",
                "failure_phase": "preflight",
                "failure_signature": validate_result["failure_signature"],
                "failure_class": validate_result["failure_class"],
                "retry_count": 0,
                "can_resume": False,
                "org_alias": org_alias,
            }

    if not is_resume:
        create_cmd = ["cci", "org", "scratch", org_shape, org_alias, "--days", str(days)]
        create_result = run_command(create_cmd, log_path, print_prefix=f"[{scenario_id}] ", cwd=project_root)
        record_event(
            {
                "phase": "org_create",
                "step_number": 0,
                "target_type": "org",
                "target_name": org_shape,
                "status": "success" if create_result["exit_code"] == 0 else "failed",
                "duration_seconds": create_result["duration_seconds"],
                "exit_code": create_result["exit_code"],
                "failure_signature": create_result["failure_signature"],
                "failure_class": create_result["failure_class"],
                "retries_used": 0,
            }
        )
        if create_result["exit_code"] != 0:
            return {
                "scenario_id": scenario_id,
                "status": "failed",
                "failed_step": 0,
                "failed_target": f"org_create:{org_shape}",
                "failure_phase": "org_create",
                "failure_signature": create_result["failure_signature"],
                "failure_class": create_result["failure_class"],
                "retry_count": 0,
                "can_resume": False,
                "org_alias": org_alias,
            }
    else:
        if not org_exists(org_alias):
            return {
                "scenario_id": scenario_id,
                "status": "resume_blocked",
                "failed_step": resume_from_step,
                "failed_target": "org_missing",
                "failure_phase": "resume",
                "failure_signature": f"Org alias `{org_alias}` does not exist.",
                "failure_class": "deterministic",
                "retry_count": 0,
                "can_resume": False,
                "org_alias": org_alias,
            }

    for step in prepare_steps:
        if resume_from_step and step.step_number < resume_from_step:
            continue
        if not evaluate_when(step.when, flags=flags, org_name=org_shape):
            record_event(
                {
                    "phase": "prepare_step",
                    "step_number": step.step_number,
                    "target_type": step.target_type,
                    "target_name": step.target_name,
                    "status": "skipped",
                    "duration_seconds": 0,
                    "exit_code": 0,
                    "failure_signature": "",
                    "failure_class": "none",
                    "retries_used": 0,
                    "when": step.when,
                }
            )
            continue

        base_cmd = ["cci", step.target_type, "run", step.target_name, "--org", org_alias]
        attempt = 0
        step_completed = False
        latest_result: Dict[str, Any] = {}

        while attempt <= retry_budget:
            latest_result = run_command(base_cmd, log_path, print_prefix=f"[{scenario_id}] ", cwd=project_root)
            failure_class = latest_result["failure_class"]
            ok = latest_result["exit_code"] == 0

            if ok:
                step_completed = True
                break

            if failure_class != "transient" or attempt == retry_budget:
                break

            backoff = 30 if attempt == 0 else 90
            total_retries += 1
            print(f"[{scenario_id}] transient failure at step {step.step_number}, retrying in {backoff}s...")
            time.sleep(backoff)
            attempt += 1

        record_event(
            {
                "phase": "prepare_step",
                "step_number": step.step_number,
                "target_type": step.target_type,
                "target_name": step.target_name,
                "status": "success" if step_completed else "failed",
                "duration_seconds": latest_result.get("duration_seconds", 0),
                "exit_code": latest_result.get("exit_code", 1),
                "failure_signature": latest_result.get("failure_signature", ""),
                "failure_class": latest_result.get("failure_class", "unknown"),
                "retries_used": attempt,
                "when": step.when,
            }
        )

        if step_completed:
            write_checkpoint(
                checkpoint_path,
                {
                    "scenario_id": scenario_id,
                    "org_alias": org_alias,
                    "org_shape": org_shape,
                    "effective_flags": flags,
                    "last_successful_step": step.step_number,
                    "last_successful_target": f"{step.target_type}:{step.target_name}",
                    "updated_at": now_utc(),
                },
            )
            continue

        scenario_status = "failed"
        first_failed_step = step.step_number
        first_failed_target = f"{step.target_type}:{step.target_name}"
        last_failure_class = latest_result.get("failure_class", "unknown")
        last_failure_signature = latest_result.get("failure_signature", "")
        write_checkpoint(
            checkpoint_path,
            {
                "scenario_id": scenario_id,
                "org_alias": org_alias,
                "org_shape": org_shape,
                "effective_flags": flags,
                "last_successful_step": step.step_number - 1,
                "failed_step": step.step_number,
                "failed_target": first_failed_target,
                "failure_signature": last_failure_signature,
                "updated_at": now_utc(),
            },
        )
        break

    # Cleanup policy: keep failed orgs by default for resume.
    deleted_org = False
    if scenario_status == "success" and not keep_orgs:
        delete_result = run_command(
            ["cci", "org", "scratch_delete", org_alias],
            log_path,
            print_prefix=f"[{scenario_id}] ",
            cwd=project_root,
        )
        deleted_org = delete_result["exit_code"] == 0
        record_event(
            {
                "phase": "cleanup",
                "step_number": 999,
                "target_type": "org",
                "target_name": "scratch_delete",
                "status": "success" if delete_result["exit_code"] == 0 else "failed",
                "duration_seconds": delete_result["duration_seconds"],
                "exit_code": delete_result["exit_code"],
                "failure_signature": delete_result["failure_signature"],
                "failure_class": delete_result["failure_class"],
                "retries_used": 0,
            }
        )

    can_resume = scenario_status == "failed" and org_exists(org_alias)
    policy = summarize_policy(
        status=scenario_status,
        can_resume=can_resume,
        failure_class=last_failure_class,
        failed_step=first_failed_step,
        retry_count=total_retries,
    )

    return {
        "scenario_id": scenario_id,
        "status": scenario_status,
        "failed_step": first_failed_step,
        "failed_target": first_failed_target,
        "failure_phase": "prepare_step" if scenario_status == "failed" else "none",
        "failure_signature": last_failure_signature,
        "failure_class": last_failure_class if scenario_status == "failed" else "none",
        "retry_count": total_retries,
        "can_resume": can_resume,
        "org_alias": org_alias,
        "org_deleted": deleted_org,
        "policy": policy,
    }


def estimate_optimization_heuristics(target_type: str, target_name: str, avg_seconds: float) -> Dict[str, str]:
    if avg_seconds >= 600:
        impact = "high"
    elif avg_seconds >= 180:
        impact = "medium"
    else:
        impact = "low"

    lowered = target_name.lower()
    if target_type == "flow":
        effort = "high"
    elif any(token in lowered for token in ("deploy", "assemble", "insert_", "extract_", "refresh_")):
        effort = "medium"
    else:
        effort = "low"

    return {
        "impact": impact,
        "effort": effort,
        "note": f"Average runtime {round(avg_seconds, 2)}s for {target_type}:{target_name}.",
    }


def build_run_analysis(run_dir: Path, run_summary: Dict[str, Any]) -> Dict[str, Any]:
    scenario_records: List[Dict[str, Any]] = []
    signature_index: Dict[str, Dict[str, Any]] = {}
    flag_index: Dict[str, Dict[str, Any]] = {}
    step_index: Dict[str, Dict[str, Any]] = {}
    failure_dependencies: List[Dict[str, Any]] = []

    for scenario_result in run_summary.get("scenario_results", []):
        scenario_id = scenario_result.get("scenario_id")
        scenario_dir = run_dir / "scenarios" / str(scenario_id)
        scenario_manifest = load_json(scenario_dir / "scenario_manifest.json") if (scenario_dir / "scenario_manifest.json").exists() else {}
        step_events = load_jsonl(scenario_dir / "step_results.jsonl")

        flag_overrides = scenario_manifest.get("flag_overrides", {}) if isinstance(scenario_manifest, dict) else {}
        failed_events = [e for e in step_events if e.get("status") == "failed" and e.get("phase") == "prepare_step"]
        first_failed = failed_events[0] if failed_events else {}

        scenario_records.append(
            {
                "scenario_id": scenario_id,
                "status": scenario_result.get("status"),
                "org_alias": scenario_result.get("org_alias"),
                "failed_step": scenario_result.get("failed_step"),
                "failed_target": scenario_result.get("failed_target"),
                "failure_signature": scenario_result.get("failure_signature"),
                "flag_overrides": flag_overrides,
                "flags_used_for_run": sorted(flag_overrides.keys()),
            }
        )

        signature = str(scenario_result.get("failure_signature") or "").strip()
        if signature:
            sig_row = signature_index.setdefault(
                signature,
                {"signature": signature, "scenario_ids": [], "targets": [], "failure_classes": []},
            )
            sig_row["scenario_ids"].append(scenario_id)
            if scenario_result.get("failed_target"):
                sig_row["targets"].append(scenario_result["failed_target"])
            if scenario_result.get("failure_class"):
                sig_row["failure_classes"].append(scenario_result["failure_class"])

        for flag_name, override_value in flag_overrides.items():
            flag_row = flag_index.setdefault(
                flag_name,
                {"flag": flag_name, "values": {"true": 0, "false": 0}, "scenario_outcomes": []},
            )
            bool_key = "true" if bool(override_value) else "false"
            flag_row["values"][bool_key] += 1
            flag_row["scenario_outcomes"].append(
                {
                    "scenario_id": scenario_id,
                    "value": bool(override_value),
                    "status": scenario_result.get("status"),
                }
            )

        for event in step_events:
            if event.get("phase") != "prepare_step":
                continue
            target_key = f"{event.get('target_type')}:{event.get('target_name')}"
            row = step_index.setdefault(
                target_key,
                {
                    "target": target_key,
                    "success_count": 0,
                    "failed_count": 0,
                    "skipped_count": 0,
                    "total_duration_seconds": 0.0,
                    "samples": 0,
                    "failure_signatures": [],
                },
            )
            status = event.get("status")
            if status == "success":
                row["success_count"] += 1
            elif status == "failed":
                row["failed_count"] += 1
            elif status == "skipped":
                row["skipped_count"] += 1
            duration = float(event.get("duration_seconds") or 0)
            row["total_duration_seconds"] += duration
            row["samples"] += 1
            signature = str(event.get("failure_signature") or "").strip()
            if signature:
                row["failure_signatures"].append(signature)

        if first_failed:
            previous_success = None
            for event in step_events:
                if event.get("phase") != "prepare_step" or event.get("status") != "success":
                    continue
                if int(event.get("step_number", 0)) < int(first_failed.get("step_number", 0)):
                    previous_success = event
            failure_dependencies.append(
                {
                    "scenario_id": scenario_id,
                    "failed_step_number": first_failed.get("step_number"),
                    "failed_target": f"{first_failed.get('target_type')}:{first_failed.get('target_name')}",
                    "failed_signature": first_failed.get("failure_signature"),
                    "previous_successful_target": (
                        f"{previous_success.get('target_type')}:{previous_success.get('target_name')}" if previous_success else None
                    ),
                    "previous_successful_step_number": previous_success.get("step_number") if previous_success else None,
                    "flag_overrides": flag_overrides,
                }
            )

    step_rows = sorted(step_index.values(), key=lambda row: row["total_duration_seconds"], reverse=True)
    top_slowest_steps: List[Dict[str, Any]] = []
    for row in step_rows[:5]:
        avg = row["total_duration_seconds"] / row["samples"] if row["samples"] else 0.0
        target_type, target_name = row["target"].split(":", 1)
        heuristics = estimate_optimization_heuristics(target_type, target_name, avg)
        top_slowest_steps.append(
            {
                "target": row["target"],
                "total_duration_seconds": round(row["total_duration_seconds"], 3),
                "average_duration_seconds": round(avg, 3),
                "samples": row["samples"],
                "success_count": row["success_count"],
                "failed_count": row["failed_count"],
                "impact": heuristics["impact"],
                "effort": heuristics["effort"],
                "note": heuristics["note"],
            }
        )

    return {
        "compatibility_summary": {
            "generated_at": now_utc(),
            "total_scenarios": len(scenario_records),
            "passed_scenarios": sum(1 for row in scenario_records if row.get("status") == "success"),
            "failed_scenarios": sum(1 for row in scenario_records if row.get("status") != "success"),
            "scenarios": scenario_records,
            "failed_step_signatures": sorted(signature_index.values(), key=lambda row: len(row["scenario_ids"]), reverse=True),
            "flag_involvement": sorted(flag_index.values(), key=lambda row: row["flag"]),
        },
        "dependency_summary": {
            "generated_at": now_utc(),
            "step_outcomes": step_rows,
            "failure_dependencies": failure_dependencies,
        },
        "optimization_recommendations": {
            "generated_at": now_utc(),
            "top_slowest_steps": top_slowest_steps,
        },
    }


def write_analysis_artifacts(run_dir: Path, run_summary: Dict[str, Any]) -> Dict[str, Any]:
    analysis = build_run_analysis(run_dir, run_summary)
    write_json(run_dir / "compatibility_summary.json", analysis["compatibility_summary"])
    write_json(run_dir / "dependency_summary.json", analysis["dependency_summary"])
    write_json(run_dir / "optimization_recommendations.json", analysis["optimization_recommendations"])
    return analysis


def write_agent_summary(run_dir: Path, summary: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Agent Summary")
    lines.append("")
    lines.append(f"- run_id: `{summary['run_id']}`")
    lines.append(f"- status: `{summary['status']}`")
    lines.append("")

    for result in summary["scenario_results"]:
        lines.append(f"## {result['scenario_id']}")
        lines.append(f"- status: `{result['status']}`")
        lines.append(f"- org_alias: `{result['org_alias']}`")
        lines.append(f"- can_resume: `{result['can_resume']}`")
        if result["failed_step"] is not None:
            lines.append(f"- failed_step: `{result['failed_step']}`")
        if result["failure_signature"]:
            lines.append(f"- failure_signature: `{result['failure_signature']}`")
        policy = result.get("policy", {})
        lines.append(f"- recommended_action: `{policy.get('recommended_action', 'none')}`")
        lines.append(f"- confidence: `{policy.get('confidence', 'medium')}`")
        lines.append(f"- operator_message: {policy.get('operator_message', 'n/a')}")
        lines.append("")

    (run_dir / "agent_summary.md").write_text("\n".join(lines), encoding="utf-8")


def render_report(run_dir: Path, run_summary: Dict[str, Any]) -> str:
    started_at = run_summary.get("started_at")
    if not started_at:
        manifest_path = run_dir / "run_manifest.json"
        if manifest_path.exists():
            try:
                started_at = load_json(manifest_path).get("started_at")
            except Exception:
                started_at = None

    lines: List[str] = []
    lines.append("# Build Harness Report")
    lines.append("")
    lines.append(f"- run_id: `{run_summary.get('run_id', run_dir.name)}`")
    lines.append(f"- started_at: `{started_at or 'unknown'}`")
    lines.append(f"- finished_at: `{run_summary.get('finished_at', 'unknown')}`")
    lines.append(f"- status: `{run_summary.get('status', 'unknown')}`")
    lines.append("")
    lines.append("## Scenarios")
    lines.append("")
    for result in run_summary["scenario_results"]:
        lines.append(f"- `{result['scenario_id']}`: `{result['status']}` (org `{result['org_alias']}`)")
        if result["failed_step"] is not None:
            lines.append(f"  - failed_step `{result['failed_step']}` target `{result['failed_target']}`")
        if result["failure_signature"]:
            lines.append(f"  - failure `{result['failure_signature']}`")

    compatibility_path = run_dir / "compatibility_summary.json"
    dependency_path = run_dir / "dependency_summary.json"
    optimization_path = run_dir / "optimization_recommendations.json"

    compatibility = load_json(compatibility_path) if compatibility_path.exists() else {}
    dependency = load_json(dependency_path) if dependency_path.exists() else {}
    optimization = load_json(optimization_path) if optimization_path.exists() else {}

    lines.append("")
    lines.append("## Compatibility and Dependencies")
    lines.append("")
    if compatibility:
        for row in compatibility.get("scenarios", []):
            lines.append(
                f"- `{row.get('scenario_id')}` -> `{row.get('status')}`; "
                f"failed_step=`{row.get('failed_step')}`; flags={row.get('flags_used_for_run', [])}"
            )
            if row.get("failure_signature"):
                lines.append(f"  - signature: `{row.get('failure_signature')}`")
        signatures = compatibility.get("failed_step_signatures", [])
        if signatures:
            lines.append("- Failed signatures observed:")
            for item in signatures:
                lines.append(f"  - `{item.get('signature')}` in scenarios {item.get('scenario_ids')}")
        flag_rows = compatibility.get("flag_involvement", [])
        if flag_rows:
            lines.append("- Flag involvement:")
            for flag in flag_rows:
                values = flag.get("values", {})
                lines.append(
                    f"  - `{flag.get('flag')}` override counts true={values.get('true', 0)} false={values.get('false', 0)}"
                )
    else:
        lines.append("- No compatibility artifact found.")

    if dependency:
        dep_rows = dependency.get("failure_dependencies", [])
        if dep_rows:
            lines.append("- Failure dependency hints:")
            for dep in dep_rows:
                lines.append(
                    f"  - scenario `{dep.get('scenario_id')}` failed at `{dep.get('failed_target')}` "
                    f"after `{dep.get('previous_successful_target')}`"
                )

    lines.append("")
    lines.append("## Optimization Recommendations")
    lines.append("")
    slow_steps = optimization.get("top_slowest_steps", [])
    if not slow_steps:
        lines.append("- No runtime data available yet.")
    else:
        for row in slow_steps:
            lines.append(
                f"- `{row.get('target')}` avg `{row.get('average_duration_seconds')}`s total "
                f"`{row.get('total_duration_seconds')}`s (impact `{row.get('impact')}`, effort `{row.get('effort')}`)"
            )
            lines.append(f"  - {row.get('note')}")

    return "\n".join(lines) + "\n"


def cmd_run(args: argparse.Namespace) -> int:
    run_id = args.run_id or make_run_id()
    run_dir = DEFAULT_OUTPUT_ROOT / run_id
    ensure_dir(run_dir)
    ensure_dir(run_dir / "scenarios")

    cci = load_cci()
    default_flags = load_default_flags(cci)
    steps = load_prepare_steps(cci)
    all_scenarios = load_scenarios(Path(args.scenarios_file))
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

    cci = load_cci()
    default_flags = load_default_flags(cci)
    steps = load_prepare_steps(cci)
    all_scenarios = load_scenarios(Path(args.scenarios_file))
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
