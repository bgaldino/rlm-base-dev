from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


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


def parse_stamp_line(line: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Stamped org: commit=(?P<commit_hash_short>[^\s,]+)"
        r"(?P<dirty>\s+\(dirty\))?, branch=(?P<branch>[^,]+), "
        r"timestamp=(?P<build_timestamp>[^,]+), flow=(?P<flow_name>[^,]+), org=(?P<org_definition>.+)$"
    )
    match = pattern.search(line.strip())
    if not match:
        return None
    payload = match.groupdict()
    payload["dirty_tree"] = bool(payload.pop("dirty"))
    for key in ("branch", "build_timestamp", "flow_name", "org_definition"):
        payload[key] = payload[key].strip()
    return payload


def parse_stamp_from_lines(lines: List[str]) -> Dict[str, Any]:
    for line in reversed(lines):
        parsed = parse_stamp_line(line)
        if parsed:
            return {"status": "stamped", "values": parsed}
        if "Failed to stamp org (non-fatal):" in line:
            return {
                "status": "non_fatal_failure",
                "details": line.strip(),
            }
    return {"status": "unknown", "details": "stamp output not found"}


def parse_stamp_from_log(log_path: Path) -> Dict[str, Any]:
    if not log_path.exists():
        return {"status": "not_found", "details": "scenario.log missing"}

    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    parsed = parse_stamp_from_lines(lines)
    if parsed.get("status") == "unknown":
        parsed["details"] = "stamp output not found in scenario.log"
    return parsed


def parse_stamp_from_event_tail(stamp_event: Dict[str, Any]) -> Dict[str, Any]:
    tail = stamp_event.get("tail")
    if not isinstance(tail, list):
        return {"status": "not_found", "details": "stamp event has no tail"}
    return parse_stamp_from_lines([str(line) for line in tail])


def write_build_provenance(
    run_dir: Path,
    scenario_dir: Path,
    scenario_id: str,
    org_alias: str,
    org_shape: str,
    effective_flags: Dict[str, Any],
) -> None:
    run_manifest_path = run_dir / "run_manifest.json"
    run_manifest = load_json(run_manifest_path) if run_manifest_path.exists() else {}

    checkpoint_path = scenario_dir / "checkpoint.json"
    checkpoint = load_json(checkpoint_path) if checkpoint_path.exists() else {}

    step_results_path = scenario_dir / "step_results.jsonl"
    step_events = load_jsonl(step_results_path)
    stamp_event = next(
        (
            event
            for event in reversed(step_events)
            if event.get("phase") == "prepare_step" and event.get("target_name") == "stamp_git_commit"
        ),
        None,
    )

    stamp_from_event = parse_stamp_from_event_tail(stamp_event) if stamp_event else {"status": "not_attempted"}
    stamp_from_log = parse_stamp_from_log(scenario_dir / "scenario.log")
    stamp_summary = {
        "attempted": stamp_event is not None,
        "event_status": stamp_event.get("status") if stamp_event else None,
        "duration_seconds": stamp_event.get("duration_seconds") if stamp_event else None,
        "failure_signature": stamp_event.get("failure_signature") if stamp_event else None,
        "failure_class": stamp_event.get("failure_class") if stamp_event else None,
        "recorded_at": stamp_event.get("recorded_at") if stamp_event else None,
        "parsed_from_event_tail": stamp_from_event,
        "parsed_from_logs": stamp_from_log,
    }

    provenance = {
        "generated_at": now_utc(),
        "run_id": run_dir.name,
        "scenario_id": scenario_id,
        "org_alias": org_alias,
        "org_shape": org_shape,
        "run_manifest": {
            "git_sha": run_manifest.get("git_sha"),
            "started_at": run_manifest.get("started_at"),
            "command": run_manifest.get("command"),
            "selected_scenarios": run_manifest.get("selected_scenarios"),
        },
        "effective_flags": effective_flags,
        "checkpoint": {
            "last_successful_step": checkpoint.get("last_successful_step"),
            "last_successful_target": checkpoint.get("last_successful_target"),
            "failed_step": checkpoint.get("failed_step"),
            "failed_target": checkpoint.get("failed_target"),
            "updated_at": checkpoint.get("updated_at"),
        },
        "stamp_git_commit": stamp_summary,
    }
    write_json(scenario_dir / "build_provenance.json", provenance)


def write_all_build_provenance(run_dir: Path, run_summary: Dict[str, Any]) -> None:
    for scenario_result in run_summary.get("scenario_results", []):
        scenario_id = scenario_result.get("scenario_id")
        if not scenario_id:
            continue
        scenario_dir = run_dir / "scenarios" / str(scenario_id)
        if not scenario_dir.exists():
            continue
        scenario_manifest_path = scenario_dir / "scenario_manifest.json"
        scenario_manifest = load_json(scenario_manifest_path) if scenario_manifest_path.exists() else {}
        effective_flags = scenario_manifest.get("effective_flags", {})
        write_build_provenance(
            run_dir=run_dir,
            scenario_dir=scenario_dir,
            scenario_id=str(scenario_id),
            org_alias=scenario_result.get("org_alias", scenario_manifest.get("org_alias", "")),
            org_shape=scenario_manifest.get("org_shape", ""),
            effective_flags=effective_flags if isinstance(effective_flags, dict) else {},
        )
