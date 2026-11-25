#!/usr/bin/env python3
"""Drop a plan's conditional DRO steps from a load when the target org lacks their dependency.

Some Dynamic Revenue Orchestrator steps call out to a target the repo cannot ship: the qb-dro
`Stage New Tenant for Provisioning - Platform` Callout posts to `callout:RLM/...`, a Named
Credential that exists only on an org someone configured. On an org without it the step runs at
activation, fails at once and stalls every step that depends on it (todo 419). The tracked CSVs
keep the step and its dependencies, and a load writes a TEMP COPY of the plan without them when
the requirement is absent, so the plan stays whole for an org that has the credential.

A plan opts in with a `conditional_steps.json` next to its `export.json`:

    {
      "steps": [{
        "name": "Stage New Tenant for Provisioning - Platform",
        "requires": {"namedCredential": "RLM"}
      }]
    }

For each step whose requirement is missing on the target org:

* its row is removed from `FulfillmentStepDefinition.csv`;
* every row of `FulfillmentStepDependencyDef.csv` that names it, as predecessor or dependent, is
  removed. A step that depended only on it becomes a root (it runs when the plan starts), and a
  step that also depends on others keeps those dependencies.

The load never deletes: an org that already holds the step keeps it (an Upsert plan only adds and
updates), so `apply_conditions` reports that and the operator removes it. Dependency-free (no
cumulusci): the caller supplies `query`, a function that runs SOQL on the target org and returns
the records, so the task and the tests share this code.
"""

import csv
import json
import os
from typing import Callable, Dict, List, Tuple

CONDITIONS_FILENAME = "conditional_steps.json"
DEFINITION_CSV = "FulfillmentStepDefinition.csv"
DEPENDENCY_CSV = "FulfillmentStepDependencyDef.csv"
DEFINITION_NAME_COLUMN = "Name"
DEPENDENCY_COLUMNS = ("DependsOnStepDefinition.Name", "FulfillmentStepDefinition.Name")
SUPPORTED_REQUIREMENTS = ("namedCredential",)


class ConditionalStepError(Exception):
    """The conditions file or the plan's CSVs are not usable; the message says which and why."""


def load_conditions(plan_dir: str) -> List[dict]:
    """The plan's conditional steps, or [] when the plan has no `conditional_steps.json`."""
    path = os.path.join(plan_dir, CONDITIONS_FILENAME)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    steps = spec.get("steps") if isinstance(spec, dict) else None
    if not isinstance(steps, list) or not steps:
        raise ConditionalStepError(f"{path}: expected a non-empty 'steps' list")
    for item in steps:
        if not isinstance(item, dict) or not item.get("name"):
            raise ConditionalStepError(f"{path}: step is missing 'name': {item!r}")
        requires = item.get("requires")
        if not isinstance(requires, dict) or not requires:
            raise ConditionalStepError(f"{path}: step {item['name']!r} is missing 'requires'")
        for key, value in requires.items():
            if key not in SUPPORTED_REQUIREMENTS:
                raise ConditionalStepError(
                    f"{path}: step {item['name']!r} requires {key!r}; supported: "
                    f"{', '.join(SUPPORTED_REQUIREMENTS)}")
            if not isinstance(value, str) or not value or "'" in value or "\\" in value:
                raise ConditionalStepError(
                    f"{path}: step {item['name']!r}: {key} must be a plain developer name, got {value!r}")
    return steps


def _read_csv(path: str) -> Tuple[List[str], List[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_csv(path: str, header: List[str], rows: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def requirement_met(requires: Dict[str, str], query: Callable[[str], List[dict]]) -> Tuple[bool, str]:
    """`(met, description of what was checked)`. Every listed requirement must exist."""
    for key, value in requires.items():
        if key == "namedCredential":
            found = query(f"SELECT DeveloperName FROM NamedCredential WHERE DeveloperName = '{value}'")
            if not found:
                return False, f"Named Credential {value!r} does not exist on the target org"
    return True, ", ".join(f"{k} {v!r}" for k, v in requires.items())


def apply_conditions(plan_dir: str, query: Callable[[str], List[dict]],
                     log: Callable[[str], None] = print) -> List[str]:
    """Remove the steps whose requirement is missing, IN PLACE (call it on a temp copy).
    Returns the removed step names; raises `ConditionalStepError` when a step the file names is
    not in the plan, so a rename cannot silently turn the guard into a no-op."""
    conditions = load_conditions(plan_dir)
    if not conditions:
        return []
    definition_path = os.path.join(plan_dir, DEFINITION_CSV)
    dependency_path = os.path.join(plan_dir, DEPENDENCY_CSV)
    for path in (definition_path, dependency_path):
        if not os.path.isfile(path):
            raise ConditionalStepError(f"{path} not found; {CONDITIONS_FILENAME} needs it")
    def_header, def_rows = _read_csv(definition_path)
    dep_header, dep_rows = _read_csv(dependency_path)
    if DEFINITION_NAME_COLUMN not in def_header:
        raise ConditionalStepError(f"{definition_path}: no {DEFINITION_NAME_COLUMN} column")
    for column in DEPENDENCY_COLUMNS:
        if column not in dep_header:
            raise ConditionalStepError(f"{dependency_path}: no {column} column")

    removed: List[str] = []
    for item in conditions:
        name = item["name"]
        if not any(row[DEFINITION_NAME_COLUMN] == name for row in def_rows):
            raise ConditionalStepError(
                f"{CONDITIONS_FILENAME} names step {name!r}, which is not in {DEFINITION_CSV}")
        met, what = requirement_met(item["requires"], query)
        if met:
            log(f"Conditional step kept: {name!r} ({what})")
            continue
        def_rows = [row for row in def_rows if row[DEFINITION_NAME_COLUMN] != name]
        kept, dropped = [], []
        for row in dep_rows:
            (dropped if name in (row[c] for c in DEPENDENCY_COLUMNS) else kept).append(row)
        dep_rows = kept
        dependents = sorted({row["FulfillmentStepDefinition.Name"] for row in dropped
                             if row["DependsOnStepDefinition.Name"] == name})
        still = {row["FulfillmentStepDefinition.Name"] for row in dep_rows}
        roots = [d for d in dependents if d not in still]
        gated = [d for d in dependents if d in still]
        note = f"; still gated by other steps: {', '.join(gated)}" if gated else ""
        log(f"Conditional step dropped: {name!r} ({what}). Removed {len(dropped)} dependency row(s); "
            f"now without a predecessor: {', '.join(roots) or 'none'}{note}.")
        quoted = name.replace("\\", "\\\\").replace("'", "\\'")
        if query(f"SELECT Id FROM FulfillmentStepDefinition WHERE Name = '{quoted}'"):
            log(f"WARNING: {name!r} already exists on the target org and this load does not delete "
                f"it, so it will still run. Remove it (and its dependency rows) to match this load.")
        removed.append(name)
    if removed:
        _write_csv(definition_path, def_header, def_rows)
        _write_csv(dependency_path, dep_header, dep_rows)
    return removed
