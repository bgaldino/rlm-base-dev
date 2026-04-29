from __future__ import annotations

import copy
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Step:
    step_number: int
    target_type: str  # flow or task
    target_name: str
    when: Optional[str]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_cci(cci_file: Path) -> Dict[str, Any]:
    with cci_file.open("r", encoding="utf-8") as handle:
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

        parsed.append(
            Step(
                step_number=int(raw_number),
                target_type=target_type,
                target_name=str(raw_step[target_type]),
                when=raw_step.get("when"),
            )
        )

    return sorted(parsed, key=lambda item: item.step_number)


def evaluate_when(expression: Optional[str], flags: Dict[str, Any], org_name: str, org_is_scratch: bool = True) -> bool:
    if not expression:
        return True

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
        return True


def load_scenarios(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def prepare_scenario_project_root(
    root: Path,
    scenario_dir: Path,
    base_cci: Dict[str, Any],
    effective_flags: Dict[str, Any],
) -> Path:
    project_root = scenario_dir / "cci_project"
    ensure_dir(project_root)

    for item in root.iterdir():
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
