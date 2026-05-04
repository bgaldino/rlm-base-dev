from __future__ import annotations

import ast
import copy
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from scripts.build_harness.harness.io import ensure_dir

# Repo-root anchored paths shared by both the CLI (`harness.py`) and the TUI
# runner. Kept here (rather than in the CLI script) so the TUI can import them
# without depending on the CLI module.
ROOT = Path(__file__).resolve().parents[3]
CCI_FILE = ROOT / "cumulusci.yml"
DEFAULT_SCENARIOS_FILE = ROOT / "scripts" / "build_harness" / "scenarios.json"
DEFAULT_OUTPUT_ROOT = ROOT / ".harness" / "runs"


@dataclass
class Step:
    step_number: int
    target_type: str  # flow or task
    target_name: str
    when: Optional[str]


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


# --- safe evaluator for cumulusci.yml `when:` expressions ---------------------
#
# The ``when:`` mini-language we observe in cumulusci.yml today is small:
#   - flag references:  project_config.project__custom__<flag>
#   - org references:   org_config.scratch, org_config.name
#   - boolean ops:      and, or, not, parens
#   - equality:         == / != against string or boolean literals
#
# We render the references as Python literals (True/False/'name'), then parse
# the result as a Python expression (mode='eval') and walk the AST manually,
# allowing only the node types listed below. Anything else (function calls,
# attribute access, subscripts, lambdas, comprehensions, imports) is rejected
# and ``evaluate_when`` falls back to its defensive default.
#
# This replaces an earlier implementation that used ``eval(rendered, {"__builtins__": {}}, {})``.
# The sandbox there was real but narrow: a hostile string that survived the
# regex substitution stage could still construct ``str.__class__`` chains and
# escape. The AST walker eliminates that path entirely by refusing to evaluate
# anything except the documented grammar.
_ALLOWED_BOOL_OPS = (ast.And, ast.Or)
_ALLOWED_UNARY_OPS = (ast.Not,)
_ALLOWED_COMPARE_OPS = (ast.Eq, ast.NotEq)


def _safe_eval_when(node: ast.AST) -> Any:
    """Walk a ``when:`` AST allowing only the documented expression grammar.

    Raises ``ValueError`` on any unsupported node so the caller can apply the
    defensive ``return True`` default that CCI itself would give an unparseable
    ``when:``.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, _ALLOWED_UNARY_OPS):
        return not _safe_eval_when(node.operand)
    if isinstance(node, ast.BoolOp) and isinstance(node.op, _ALLOWED_BOOL_OPS):
        # We evaluate every operand before all()/any(); unlike Python's lazy
        # and/or, this is safe because the supported when-grammar is side-effect free.
        values = [_safe_eval_when(v) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        return any(values)
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise ValueError("only single-comparison expressions are supported")
        op = node.ops[0]
        if not isinstance(op, _ALLOWED_COMPARE_OPS):
            raise ValueError(f"disallowed compare op: {type(op).__name__}")
        left = _safe_eval_when(node.left)
        right = _safe_eval_when(node.comparators[0])
        return left == right if isinstance(op, ast.Eq) else left != right
    if isinstance(node, ast.Name):
        # Bare names should never reach here: project_config.* and
        # org_config.* are substituted to literals before parsing, and
        # True/False/None are parsed as ast.Constant in Python 3.8+.
        # If we see a Name node it's something we don't intend to allow.
        raise ValueError(f"disallowed name reference: {node.id}")
    raise ValueError(f"disallowed expression node: {type(node).__name__}")


def evaluate_when(
    expression: Optional[str],
    flags: Dict[str, Any],
    org_name: str,
    org_is_scratch: bool = True,
) -> bool:
    """Evaluate a CCI ``when:`` expression against the harness flag/org context.

    Returns ``True`` on the empty expression and on *any* parse or evaluation
    failure so a malformed ``when:`` does not silently skip a step (matches
    CCI's own behavior).
    """
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
        tree = ast.parse(rendered, mode="eval")
        return bool(_safe_eval_when(tree.body))
    except (SyntaxError, ValueError, TypeError):
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


_SCENARIO_CCI_BANNER = (
    "# AUTO-GENERATED by scripts/build_harness — do not edit by hand.\n"
    "#\n"
    "# This file is a per-scenario snapshot of the repo-root cumulusci.yml with\n"
    "# the scenario's flag_overrides applied to project.custom. It is rewritten\n"
    "# on every harness run inside the scenario's .harness/runs/<run-id>/\n"
    "# scenarios/<scenario-id>/cci_project/ workspace and is removed at the end\n"
    "# of the run.\n"
    "#\n"
    "# Differences from the source cumulusci.yml that are EXPECTED:\n"
    "# - YAML anchors (&name / *name) are inlined as their resolved values.\n"
    "# - Comments are stripped.\n"
    "# - project.custom is replaced wholesale with the scenario's effective_flags.\n"
    "# These are parse-time-only effects of regenerating from a Python dict and\n"
    "# do not change the values that CCI loads at runtime. For the source of\n"
    "# truth (with comments and anchors), edit the repo-root cumulusci.yml.\n"
    "#\n"
)


def prepare_scenario_project_root(
    root: Path,
    scenario_dir: Path,
    base_cci: Dict[str, Any],
    effective_flags: Dict[str, Any],
) -> Path:
    """Materialize a per-scenario cci_project workspace.

    Every entry in ``root`` is symlinked into the workspace except for
    ``cumulusci.yml`` (which gets rewritten with this scenario's overrides)
    and ``scripts/`` (which is *copied* — see comment below). The rewritten
    ``cumulusci.yml`` carries a banner header so an operator inspecting the
    file inside ``.harness/runs/.../cci_project/`` knows it is generated and
    where to make permanent changes.
    """
    project_root = scenario_dir / "cci_project"
    ensure_dir(project_root)

    for item in root.iterdir():
        if item.name == "cumulusci.yml":
            continue
        destination = project_root / item.name
        if destination.exists() or destination.is_symlink():
            continue
        if item.name == "scripts" and item.is_dir():
            # Copy scripts into the temp project so path validation for
            # file-based task options (e.g. scripts/apex/*.apex) stays inside
            # the scenario repo_root instead of resolving to the source repo.
            shutil.copytree(item, destination)
            continue
        os.symlink(item, destination, target_is_directory=item.is_dir())

    cci_override = copy.deepcopy(base_cci)
    project = cci_override.setdefault("project", {})
    project["custom"] = effective_flags
    with (project_root / "cumulusci.yml").open("w", encoding="utf-8") as handle:
        handle.write(_SCENARIO_CCI_BANNER)
        yaml.safe_dump(cci_override, handle, sort_keys=False)
    return project_root


def cleanup_scenario_project_root(project_root: Path) -> Optional[str]:
    """Remove per-scenario cci_project workspace after a run."""
    if project_root.name != "cci_project":
        return f"Refusing to clean unexpected directory: {project_root}"
    if not project_root.exists():
        return None
    try:
        shutil.rmtree(project_root)
        return None
    except OSError as exc:
        return f"Failed to remove {project_root}: {exc}"
