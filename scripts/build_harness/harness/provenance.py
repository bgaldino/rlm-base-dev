from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.build_harness.harness.io import load_json, load_jsonl, now_utc, write_json

# Lines from the stamp_git_commit Apex script look like:
#   Stamped org: commit=abc1234 (dirty), branch=main, timestamp=2026-04-29T..., flow=prepare_rlm_org, org=beta
# The keys we care about. Anything outside this set is preserved into
# ``extra`` so future stamp output additions surface in build_provenance.json
# without a regex update.
_STAMP_PREFIX = "Stamped org:"
_KNOWN_STAMP_KEYS = {"commit", "branch", "timestamp", "flow", "org"}
# Match each ``key=value`` pair where ``value`` extends until the next
# ``, key=`` boundary or end of line. Order-independent, tolerates extra
# whitespace, and lets values legitimately contain commas as long as they
# are not followed by ``\s+key=``. The key class is a full identifier
# (letters, digits, underscore) so future stamp fields like ``ciRunId`` or
# ``ci_run_id2`` are captured into ``extra`` rather than silently dropped.
_STAMP_KEY = r"[A-Za-z_][A-Za-z0-9_]*"
_STAMP_KV_PATTERN = re.compile(rf"({_STAMP_KEY})\s*=\s*(.+?)(?=,\s+{_STAMP_KEY}\s*=|$)")


def parse_stamp_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single ``Stamped org: ...`` line into a provenance dict.

    The previous implementation used a single positional regex that required
    the exact field order ``commit, [dirty?], branch, timestamp, flow, org``.
    This version walks the payload as ``key=value`` pairs so that:

    - the order of fields can change without breaking the parser,
    - missing optional fields yield empty strings instead of failing the
      whole line, and
    - new fields added by the Apex stamp script appear in ``extra`` rather
      than silently dropping the entire stamp.

    Returns ``None`` when the line does not start with ``Stamped org:`` or
    when no ``commit=`` value is present (a stamp line without a commit hash
    is not useful as provenance).
    """
    stripped = line.strip()
    if not stripped.startswith(_STAMP_PREFIX):
        return None
    payload = stripped[len(_STAMP_PREFIX):].lstrip()

    pairs: Dict[str, str] = {}
    for match in _STAMP_KV_PATTERN.finditer(payload):
        key = match.group(1)
        value = match.group(2).strip().rstrip(",").strip()
        pairs[key] = value

    # Known keys are matched case-insensitively; unknown keys keep their
    # original casing when surfaced in ``extra``.
    by_lower = {key.lower(): value for key, value in pairs.items()}

    commit_value = by_lower.get("commit")
    if not commit_value:
        return None

    dirty = "(dirty)" in commit_value
    if dirty:
        commit_value = commit_value.replace("(dirty)", "").strip()

    parsed: Dict[str, Any] = {
        "commit_hash_short": commit_value,
        "branch": by_lower.get("branch", ""),
        "build_timestamp": by_lower.get("timestamp", ""),
        "flow_name": by_lower.get("flow", ""),
        "org_definition": by_lower.get("org", ""),
        "dirty_tree": dirty,
    }

    extra = {
        key: value
        for key, value in pairs.items()
        if key.lower() not in _KNOWN_STAMP_KEYS
    }
    if extra:
        parsed["extra"] = extra

    return parsed


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
