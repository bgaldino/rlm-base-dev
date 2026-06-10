from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.build_harness.harness.config import (
    Step,
    alias_for_scenario,
    cleanup_scenario_project_root,
    compose_flags,
    evaluate_when,
    prepare_scenario_project_root,
)
from scripts.build_harness.harness.execution import org_exists, run_command
from scripts.build_harness.harness.io import append_jsonl, now_utc, write_json
from scripts.build_harness.harness.provenance import write_build_provenance


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
    root: Path,
    scenario: Dict[str, Any],
    run_dir: Path,
    prepare_steps: List[Step],
    default_flags: Dict[str, Any],
    base_cci: Dict[str, Any],
    skip_validate: bool,
    keep_orgs: bool,
    is_resume: bool,
    stream_output: bool = True,
    resume_from_step: Optional[int] = None,
    existing_alias: Optional[str] = None,
) -> Dict[str, Any]:
    scenario_id = scenario["scenario_id"]
    scenario_dir = run_dir / "scenarios" / scenario_id
    scenario_dir.mkdir(parents=True, exist_ok=True)

    log_path = scenario_dir / "scenario.log"
    checkpoint_path = scenario_dir / "checkpoint.json"
    step_results_path = scenario_dir / "step_results.jsonl"
    metadata_path = scenario_dir / "scenario_manifest.json"

    flags = compose_flags(default_flags, scenario.get("flag_overrides", {}))
    project_root = prepare_scenario_project_root(
        root=root,
        scenario_dir=scenario_dir,
        base_cci=base_cci,
        effective_flags=flags,
    )
    org_alias = existing_alias or alias_for_scenario(scenario, run_dir.name)
    org_shape = scenario["org_shape"]
    days = int(scenario.get("days", 1))

    write_json(
        metadata_path,
        {
            "scenario_id": scenario_id,
            "org_shape": org_shape,
            "org_alias": org_alias,
            "days": days,
            "flag_overrides": scenario.get("flag_overrides", {}),
            "effective_flags": flags,
            "started_at": now_utc(),
            "mode": "resume" if is_resume else "run",
        },
    )

    retry_budget = 2
    scenario_status = "success"
    cleanup_workspace = True
    first_failed_step: Optional[int] = None
    first_failed_target: Optional[str] = None
    last_failure_class = "none"
    last_failure_signature = ""
    total_retries = 0
    failed_step_retries = 0

    def record_event(event: Dict[str, Any]) -> None:
        base = {"scenario_id": scenario_id, "org_alias": org_alias, "recorded_at": now_utc()}
        base.update(event)
        append_jsonl(step_results_path, base)

    def build_failure_result(
        *,
        status: str,
        failed_step: Optional[int],
        failed_target: Optional[str],
        failure_phase: str,
        failure_signature: str,
        failure_class: str,
        retry_count: int,
        can_resume: bool,
        total_retry_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        if total_retry_count is None:
            total_retry_count = retry_count
        return {
            "scenario_id": scenario_id,
            "status": status,
            "failed_step": failed_step,
            "failed_target": failed_target,
            "failure_phase": failure_phase,
            "failure_signature": failure_signature,
            "failure_class": failure_class,
            "retry_count": retry_count,
            "total_retry_count": total_retry_count,
            "can_resume": can_resume,
            "org_alias": org_alias,
            "policy": summarize_policy(
                status=status,
                can_resume=can_resume,
                failure_class=failure_class,
                failed_step=failed_step,
                retry_count=retry_count,
            ),
        }

    try:
        if not skip_validate and not is_resume:
            validate_result = run_command(
                root,
                ["cci", "task", "run", "validate_setup"],
                log_path,
                print_prefix=f"[{scenario_id}] ",
                cwd=project_root,
                emit_output=stream_output,
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
                cleanup_workspace = False
                return build_failure_result(
                    status="failed",
                    failed_step=0,
                    failed_target="validate_setup",
                    failure_phase="preflight",
                    failure_signature=validate_result["failure_signature"],
                    failure_class=validate_result["failure_class"],
                    retry_count=0,
                    can_resume=False,
                )

        if not is_resume:
            create_cmd = ["cci", "org", "scratch", org_shape, org_alias, "--days", str(days)]
            create_result = run_command(
                root,
                create_cmd,
                log_path,
                print_prefix=f"[{scenario_id}] ",
                cwd=project_root,
                emit_output=stream_output,
            )
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
                cleanup_workspace = False
                return build_failure_result(
                    status="failed",
                    failed_step=0,
                    failed_target=f"org_create:{org_shape}",
                    failure_phase="org_create",
                    failure_signature=create_result["failure_signature"],
                    failure_class=create_result["failure_class"],
                    retry_count=0,
                    can_resume=False,
                )
            materialize_cmd = ["cci", "org", "info", org_alias]
            materialize_result = run_command(
                root,
                materialize_cmd,
                log_path,
                print_prefix=f"[{scenario_id}] ",
                cwd=project_root,
                emit_output=stream_output,
            )
            record_event(
                {
                    "phase": "org_materialize",
                    "step_number": 0,
                    "target_type": "org",
                    "target_name": "org_info",
                    "status": "success" if materialize_result["exit_code"] == 0 else "failed",
                    "duration_seconds": materialize_result["duration_seconds"],
                    "exit_code": materialize_result["exit_code"],
                    "failure_signature": materialize_result["failure_signature"],
                    "failure_class": materialize_result["failure_class"],
                    "retries_used": 0,
                }
            )
            if materialize_result["exit_code"] != 0:
                cleanup_workspace = False
                return build_failure_result(
                    status="failed",
                    failed_step=0,
                    failed_target="org_materialize:org_info",
                    failure_phase="org_materialize",
                    failure_signature=materialize_result["failure_signature"],
                    failure_class="deterministic",
                    retry_count=0,
                    can_resume=False,
                )
        else:
            if not org_exists(root, org_alias):
                cleanup_workspace = False
                return build_failure_result(
                    status="resume_blocked",
                    failed_step=resume_from_step,
                    failed_target="org_missing",
                    failure_phase="resume",
                    failure_signature=f"Org alias `{org_alias}` does not exist.",
                    failure_class="deterministic",
                    retry_count=0,
                    can_resume=False,
                )

        last_completed_step = 0
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
            total_attempt_duration = 0.0
            while attempt <= retry_budget:
                latest_result = run_command(
                    root,
                    base_cmd,
                    log_path,
                    print_prefix=f"[{scenario_id}] ",
                    cwd=project_root,
                    emit_output=stream_output,
                )
                total_attempt_duration += float(latest_result.get("duration_seconds") or 0.0)
                failure_class = latest_result["failure_class"]
                if latest_result["exit_code"] == 0:
                    step_completed = True
                    break
                if failure_class != "transient" or attempt == retry_budget:
                    break
                backoff = 30 if attempt == 0 else 90
                total_retries += 1
                if stream_output:
                    print(f"[{scenario_id}] transient failure at step {step.step_number}, retrying in {backoff}s...")
                time.sleep(backoff)
                attempt += 1

            event_payload = {
                "phase": "prepare_step",
                "step_number": step.step_number,
                "target_type": step.target_type,
                "target_name": step.target_name,
                "status": "success" if step_completed else "failed",
                "duration_seconds": total_attempt_duration,
                "exit_code": latest_result.get("exit_code", 1),
                "failure_signature": latest_result.get("failure_signature", ""),
                "failure_class": latest_result.get("failure_class", "unknown"),
                "retries_used": attempt,
                "when": step.when,
            }
            if step.target_name == "stamp_git_commit":
                event_payload["tail"] = latest_result.get("tail", [])
            record_event(event_payload)

            if step_completed:
                last_completed_step = step.step_number
                write_json(
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
            failed_step_retries = attempt
            write_json(
                checkpoint_path,
                {
                    "scenario_id": scenario_id,
                    "org_alias": org_alias,
                    "org_shape": org_shape,
                    "effective_flags": flags,
                    "last_successful_step": last_completed_step,
                    "failed_step": step.step_number,
                    "failed_target": first_failed_target,
                    "failure_signature": last_failure_signature,
                    "updated_at": now_utc(),
                },
            )
            break

        deleted_org = False
        if scenario_status == "success" and not keep_orgs:
            delete_result = run_command(
                root,
                ["cci", "org", "scratch_delete", org_alias],
                log_path,
                print_prefix=f"[{scenario_id}] ",
                cwd=project_root,
                emit_output=stream_output,
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

        can_resume = scenario_status == "failed" and org_exists(root, org_alias)
        policy = summarize_policy(
            status=scenario_status,
            can_resume=can_resume,
            failure_class=last_failure_class,
            failed_step=first_failed_step,
            retry_count=failed_step_retries,
        )
        write_build_provenance(
            run_dir=run_dir,
            scenario_dir=scenario_dir,
            scenario_id=scenario_id,
            org_alias=org_alias,
            org_shape=org_shape,
            effective_flags=flags,
        )
        if scenario_status != "success":
            cleanup_workspace = False
        return {
            "scenario_id": scenario_id,
            "status": scenario_status,
            "failed_step": first_failed_step,
            "failed_target": first_failed_target,
            "failure_phase": "prepare_step" if scenario_status == "failed" else "none",
            "failure_signature": last_failure_signature,
            "failure_class": last_failure_class if scenario_status == "failed" else "none",
            "retry_count": failed_step_retries,
            "total_retry_count": total_retries,
            "can_resume": can_resume,
            "org_alias": org_alias,
            "org_deleted": deleted_org,
            "policy": policy,
        }
    finally:
        if cleanup_workspace:
            cleanup_error = cleanup_scenario_project_root(project_root)
            if cleanup_error:
                with log_path.open("a", encoding="utf-8") as handle:
                    handle.write(f"\n[{scenario_id}] WARNING workspace cleanup failed: {cleanup_error}\n")
                record_event(
                    {
                        "phase": "workspace_cleanup",
                        "step_number": 1000,
                        "target_type": "workspace",
                        "target_name": "remove_cci_project",
                        "status": "failed",
                        "duration_seconds": 0,
                        "exit_code": 1,
                        "failure_signature": cleanup_error,
                        "failure_class": "deterministic",
                        "retries_used": 0,
                    }
                )
