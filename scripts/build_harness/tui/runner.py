"""Background execution engine for the build manager TUI."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
import re
from threading import Event
from typing import Callable, Dict, Iterable, List, Tuple

from scripts.build_harness.harness.config import (
    CCI_FILE,
    ROOT,
    cleanup_scenario_project_root,
    compose_flags,
    evaluate_when,
    load_cci,
    load_default_flags,
    load_prepare_steps,
    prepare_scenario_project_root,
)
from scripts.build_harness.harness.failure import infer_failure_signature
from scripts.build_harness.harness.execution import run_command_stream
from scripts.build_harness.tui.state import BuildConfig, OrgShape, RunEvent, RunEventKind

EventSink = Callable[[RunEvent], None]


def load_tui_config() -> Tuple[
    List[OrgShape],
    Dict[str, bool],
    Dict[str, object],
    List[Tuple[str, List[str]]],
    Dict[str, str],
]:
    """Load org shapes and boolean flags from cumulusci.yml."""
    cci = load_cci(CCI_FILE)
    scratch = cci.get("orgs", {}).get("scratch", {})
    shapes: List[OrgShape] = []
    for shape_name, shape_config in scratch.items():
        if not isinstance(shape_config, dict):
            continue
        days_value = shape_config.get("days", 1)
        days = int(days_value) if isinstance(days_value, int) else 1
        shapes.append(
            OrgShape(
                name=str(shape_name),
                config_file=str(shape_config.get("config_file", "")),
                days=days,
            )
        )

    default_flags_raw = load_default_flags(cci)
    bool_flags = {
        key: value
        for key, value in default_flags_raw.items()
        if isinstance(value, bool)
    }
    flag_groups, flag_comments = _extract_flag_groups_and_comments(bool_flags)
    return sorted(shapes, key=lambda item: item.name), bool_flags, default_flags_raw, flag_groups, flag_comments


def run_build(config: BuildConfig, stop_event: Event, emit: EventSink) -> int:
    """Run scratch org creation + prepare_rlm_org top-level steps."""
    base_cci = load_cci(CCI_FILE)
    scratch = base_cci.get("orgs", {}).get("scratch", {})
    shape_names = {name for name, cfg in scratch.items() if isinstance(cfg, dict)}
    if config.org_shape not in shape_names:
        emit(
            RunEvent(
                kind=RunEventKind.RUN_FAILED,
                payload={"message": f"Unknown org shape: {config.org_shape}"},
            )
        )
        return 2

    all_default_flags = load_default_flags(base_cci)
    effective_flags = compose_flags(all_default_flags, config.flag_overrides)
    prepare_steps = load_prepare_steps(base_cci)
    total_steps = len(prepare_steps)

    emit(RunEvent(kind=RunEventKind.RUN_STARTED, payload={"total_steps": total_steps}))

    run_stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    alias_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", config.org_alias).strip("-") or "org"
    workspace_dir = ROOT / ".harness" / "tui-runs" / f"tui-workspace-{run_stamp}-{alias_slug}"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    project_root = prepare_scenario_project_root(
        root=ROOT,
        scenario_dir=workspace_dir,
        base_cci=base_cci,
        effective_flags=effective_flags,
    )

    try:
        create_cmd = [
            "cci",
            "org",
            "scratch",
            config.org_shape,
            config.org_alias,
            "--days",
            str(config.days),
        ]
        create_result = _run_command(
            create_cmd,
            stop_event=stop_event,
            emit=emit,
            phase="create_org",
            step_number=0,
            step_label=f"scratch:{config.org_shape}",
            cwd=project_root,
        )
        if create_result["exit_code"] != 0:
            emit(
                RunEvent(
                    kind=RunEventKind.RUN_FAILED,
                    payload={
                        "message": "Scratch org creation failed.",
                        "failure_signature": create_result["failure_signature"],
                        "exit_code": create_result["exit_code"],
                    },
                )
            )
            return int(create_result["exit_code"])

        materialize_step_payload = {
            "step_number": 0,
            "target_type": "org",
            "target_name": "materialize",
            "when": None,
            "completed_steps": 0,
            "total_steps": total_steps,
        }
        emit(RunEvent(kind=RunEventKind.STEP_STARTED, payload=materialize_step_payload))
        materialize_result = _run_command(
            ["cci", "org", "info", config.org_alias],
            stop_event=stop_event,
            emit=emit,
            phase="materialize_org",
            step_number=0,
            step_label=f"org_info:{config.org_alias}",
            cwd=project_root,
        )
        if materialize_result["exit_code"] != 0:
            emit(
                RunEvent(
                    kind=RunEventKind.STEP_FAILED,
                    payload={
                        **materialize_step_payload,
                        "duration_seconds": materialize_result["duration_seconds"],
                        "exit_code": materialize_result["exit_code"],
                        "failure_signature": materialize_result["failure_signature"],
                    },
                )
            )
            emit(
                RunEvent(
                    kind=RunEventKind.RUN_FAILED,
                    payload={
                        "message": "Scratch org materialization failed.",
                        "failure_signature": materialize_result["failure_signature"],
                        "exit_code": materialize_result["exit_code"],
                    },
                )
            )
            return int(materialize_result["exit_code"])
        emit(
            RunEvent(
                kind=RunEventKind.STEP_SUCCEEDED,
                payload={
                    **materialize_step_payload,
                    "duration_seconds": materialize_result["duration_seconds"],
                },
            )
        )

        completed = 0
        for step in prepare_steps:
            if stop_event.is_set():
                emit(RunEvent(kind=RunEventKind.RUN_CANCELLED, payload={"message": "Run cancelled by user."}))
                return 130

            should_run = evaluate_when(
                step.when,
                flags=effective_flags,
                org_name=config.org_shape,
                org_is_scratch=True,
            )
            step_payload = {
                "step_number": step.step_number,
                "target_type": step.target_type,
                "target_name": step.target_name,
                "when": step.when,
                "completed_steps": completed,
                "total_steps": total_steps,
            }

            if not should_run:
                completed += 1
                emit(
                    RunEvent(
                        kind=RunEventKind.STEP_SKIPPED,
                        payload={**step_payload, "completed_steps": completed},
                    )
                )
                continue

            emit(RunEvent(kind=RunEventKind.STEP_STARTED, payload=step_payload))
            step_cmd = ["cci", step.target_type, "run", step.target_name, "--org", config.org_alias]
            result = _run_command(
                step_cmd,
                stop_event=stop_event,
                emit=emit,
                phase="prepare_step",
                step_number=step.step_number,
                step_label=f"{step.target_type}:{step.target_name}",
                cwd=project_root,
            )
            if result["exit_code"] != 0:
                emit(
                    RunEvent(
                        kind=RunEventKind.STEP_FAILED,
                        payload={
                            **step_payload,
                            "duration_seconds": result["duration_seconds"],
                            "exit_code": result["exit_code"],
                            "failure_signature": result["failure_signature"],
                        },
                    )
                )
                emit(
                    RunEvent(
                        kind=RunEventKind.RUN_FAILED,
                        payload={
                            "message": f"prepare_rlm_org failed at step {step.step_number}.",
                            "failure_signature": result["failure_signature"],
                            "exit_code": result["exit_code"],
                        },
                    )
                )
                return int(result["exit_code"])

            completed += 1
            emit(
                RunEvent(
                    kind=RunEventKind.STEP_SUCCEEDED,
                    payload={
                        **step_payload,
                        "completed_steps": completed,
                        "duration_seconds": result["duration_seconds"],
                    },
                )
            )

        emit(
            RunEvent(
                kind=RunEventKind.RUN_SUCCEEDED,
                payload={
                    "completed_steps": completed,
                    "message": "Scratch org created and prepare_rlm_org completed successfully.",
                    "total_steps": total_steps,
                },
            )
        )
        return 0
    finally:
        cleanup_error = cleanup_scenario_project_root(project_root)
        if cleanup_error:
            emit(
                RunEvent(
                    kind=RunEventKind.COMMAND_OUTPUT,
                    payload={
                        "phase": "cleanup",
                        "step_number": -1,
                        "line": f"[harness] {cleanup_error}",
                    },
                )
            )

def _run_command(
    command: Iterable[str],
    stop_event: Event,
    emit: EventSink,
    phase: str,
    step_number: int,
    step_label: str,
    cwd: Path | None = None,
) -> Dict[str, object]:
    command_list = list(command)
    emit(
        RunEvent(
            kind=RunEventKind.COMMAND_STARTED,
            payload={
                "phase": phase,
                "step_number": step_number,
                "step_label": step_label,
                "command": " ".join(command_list),
            },
        )
    )

    def _emit_line(line: str) -> None:
        emit(
            RunEvent(
                kind=RunEventKind.COMMAND_OUTPUT,
                payload={
                    "phase": phase,
                    "step_number": step_number,
                    "line": line,
                },
            )
        )

    result = run_command_stream(
        command_list,
        cwd=(cwd or ROOT),
        stop_event=stop_event,
        on_line=_emit_line,
        on_detached=lambda: _emit_line("[harness] process exited but stdout remained open; continuing."),
    )
    result = {
        "duration_seconds": float(result["duration_seconds"]),
        "exit_code": int(result["exit_code"]),
        "failure_signature": str(result["failure_signature"]),
    }
    emit(
        RunEvent(
            kind=RunEventKind.COMMAND_FINISHED,
            payload={
                "phase": phase,
                "step_number": step_number,
                "step_label": step_label,
                "duration_seconds": result["duration_seconds"],
                "exit_code": result["exit_code"],
                "failure_signature": result["failure_signature"],
            },
        )
    )
    return result


def _extract_flag_groups_and_comments(
    bool_flags: Dict[str, bool]
) -> Tuple[List[Tuple[str, List[str]]], Dict[str, str]]:
    """Parse `project.custom` comments/order from cumulusci.yml into groups + inline descriptions."""
    if not CCI_FILE.exists():
        return [("Flags", list(bool_flags.keys()))], {}

    lines = CCI_FILE.read_text(encoding="utf-8").splitlines()
    in_project = False
    in_custom = False
    project_indent = 0
    custom_indent = 0
    current_group = "Flags"
    grouped: List[Tuple[str, List[str]]] = []
    grouped_index: Dict[str, int] = {}
    flag_comments: Dict[str, str] = {}
    seen = set()

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))

        if not in_project:
            if re.match(r"^\s*project:\s*$", line):
                in_project = True
                project_indent = indent
            continue

        if in_project and not in_custom:
            if indent <= project_indent and stripped and not stripped.startswith("#") and not re.match(r"^\s*project:\s*$", line):
                break
            if re.match(r"^\s*custom:\s*$", line):
                in_custom = True
                custom_indent = indent
            continue

        if in_custom:
            if indent <= custom_indent and stripped and not stripped.startswith("#"):
                break
            if not stripped:
                continue
            if stripped.startswith("#"):
                candidate = _normalize_group_comment(stripped)
                if candidate:
                    current_group = candidate
                continue

            key_match = re.match(r"^\s*([A-Za-z0-9_]+):", line)
            if not key_match:
                continue
            flag = key_match.group(1)
            if flag not in bool_flags or flag in seen:
                continue
            seen.add(flag)
            inline_comment = _extract_inline_comment(line)
            if inline_comment:
                flag_comments[flag] = inline_comment
            if current_group not in grouped_index:
                grouped_index[current_group] = len(grouped)
                grouped.append((current_group, []))
            grouped[grouped_index[current_group]][1].append(flag)

    # Include any bool flags not encountered in parsed section.
    remaining = [flag for flag in bool_flags.keys() if flag not in seen]
    if remaining:
        grouped.append(("Other Flags", remaining))
    return (grouped if grouped else [("Flags", list(bool_flags.keys()))], flag_comments)


def _normalize_group_comment(comment_line: str) -> str:
    """Turn project.custom comment headers into friendly group names."""
    text = comment_line.lstrip("#").strip()
    if not text:
        return ""
    # Remove decorative dash bars while preserving words.
    text = text.strip("─- ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    if re.search(r"[A-Za-z]", text) is None:
        return ""
    return text


def _extract_inline_comment(line: str) -> str:
    """Get inline YAML comment text from a key/value line."""
    if "#" not in line:
        return ""
    comment = line.split("#", 1)[1].strip()
    return re.sub(r"\s+", " ", comment)
