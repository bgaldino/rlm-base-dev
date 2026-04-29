from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from scripts.build_harness.harness.io import load_json, load_jsonl, now_utc, write_json


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
            sig = str(event.get("failure_signature") or "").strip()
            if sig:
                row["failure_signatures"].append(sig)

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
