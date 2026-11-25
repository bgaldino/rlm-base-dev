#!/usr/bin/env python3
"""Offline checks for tasks/rlm_clm_clause_sets.py (todo 346).

    python tests/test_clm_clause_sets.py

No org and no CumulusCI install needed: the pure helpers are tested; the org is not.
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("_clm_clause_sets", REPO / "tasks" / "rlm_clm_clause_sets.py")
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

failures = []


def check(label, got, want):
    if got != want:
        failures.append(f"{label}: got {got!r}, want {want!r}")


check("category value is the 15 character Id", mod.category_value("0zMWt0000001L5dMAE"), "0zMWt0000001L5d")

cats = {"Contract": "0zMWt0000001L5dMAE", "Retail": "0zMWt0000001L5eMAE"}
rows = [("A", "Contract", "en_US"), ("B", "Retail", "en_US")]
check("missing rows carry the portable Category",
      mod.missing_rows(rows, cats, set()),
      [{"Name": "A", "DefaultLanguage": "en_US", "Category": "0zMWt0000001L5d"},
       {"Name": "B", "DefaultLanguage": "en_US", "Category": "0zMWt0000001L5e"}])
check("an existing row is skipped", [r["Name"] for r in mod.missing_rows(rows, cats, {("A", "0zMWt0000001L5d")})], ["B"])
check("the same name under another category is not skipped",
      [r["Name"] for r in mod.missing_rows(rows, cats, {("A", "0zMWt0000001L5e")})], ["A", "B"])
try:
    mod.missing_rows([("A", "Nope", "en_US")], cats, set())
    failures.append("an unknown category must raise")
except Exception as exc:
    check("unknown category names the row", "'A'" in str(exc) and "'Nope'" in str(exc), True)

plan = mod.plan_rows(str(REPO / mod.DEFAULT_CSV))
check("the plan CSV has 20 rows", len(plan), 20)
check("every plan category is loaded by the plan",
      {c for _, c, _ in plan} <= {"Contract", "Retail"}, True)
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "x.csv"
    p.write_text("Name,DefaultLanguage\nA,en_US\n")
    try:
        mod.plan_rows(str(p))
        failures.append("a CSV without the category column must raise")
    except Exception:
        pass

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("OK")
