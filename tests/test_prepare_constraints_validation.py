#!/usr/bin/env python3
"""
Invariant: prepare_constraints validates every model it imports.

    python tests/test_prepare_constraints_validation.py

Needs PyYAML; no org and no CumulusCI install required.

Why this file exists
--------------------
Validation must cover both retained model imports before either one runs.
The lifecycle must cycle both versions and must not reference retired models.
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


config = yaml.safe_load((REPO / "cumulusci.yml").read_text(encoding="utf-8"))
steps = config["flows"]["prepare_constraints"]["steps"]
ordered = sorted(steps.items(), key=lambda kv: float(kv[0]))

validate = [(num, s) for num, s in ordered if s.get("task") == "validate_cml"]
imports = [(num, s) for num, s in ordered if s.get("task") == "import_cml"]

print("prepare_constraints validates before it imports")
check("exactly one validate_cml step", len(validate) == 1, repr([n for n, _ in validate]))
check("at least one import_cml step", bool(imports))

if len(validate) == 1 and imports:
    v_num, v_step = validate[0]
    raw = (v_step.get("options") or {}).get("data_dirs") or ""
    validated = {d.strip() for d in raw.split(",") if d.strip()}
    imported = {(s.get("options") or {}).get("data_dir") for _, s in imports}

    check("validate_cml uses data_dirs (each model's own blob and ESC rows)", bool(validated),
          "step has no data_dirs option")
    missing = sorted(d for d in imported - validated if d)
    check("every imported model directory is validated", not missing, f"not validated: {missing}")
    extra = sorted(validated - imported)
    check("validate_cml lists no directory the flow doesn't import", not extra, f"extra: {extra}")
    late = [n for n, _ in imports if float(n) < float(v_num)]
    check("validation runs before every import", not late, f"imports before step {v_num}: {late}")
    same_when = all(s.get("when") == v_step.get("when") for _, s in imports)
    check("validate_cml runs under the same condition as the imports", same_when)

expected_dirs = {"datasets/constraints/qb/Server2", "datasets/constraints/qb/QuantumBitBundle"}
check("only the two retained models are imported", {
    s["options"]["data_dir"] for _, s in imports
} == expected_dirs)
check("only retained model datasets are shipped", {
    p.name for p in (REPO / "datasets/constraints/qb").iterdir() if p.is_dir()
} == {"Server2", "QuantumBitBundle"})
expected_versions = {"Server2_V1", "QuantumBitBundle_V1"}
cycles = [(n, s) for n, s in ordered if s.get("task") == "manage_expression_sets"]
check("one deactivate and one activate step", [s["options"]["operation"] for _, s in cycles]
      == ["deactivate_versions", "activate_versions"])
for n, s in cycles:
    check(f"step {n} cycles only retained models", {
        v.strip() for v in s["options"]["version_full_names"].split(",")
    } == expected_versions)
    check(f"step {n} preserves the import guard", s.get("when") == imports[0][1].get("when"))
check("both lifecycle steps follow the imports", bool(cycles) and bool(imports)
      and min(n for n, _ in cycles) > max(n for n, _ in imports))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): " + "; ".join(FAILURES))
    sys.exit(1)
print("All checks passed.")
