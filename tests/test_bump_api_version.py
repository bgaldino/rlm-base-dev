#!/usr/bin/env python3
"""Offline tests for scripts/ai/bump_api_version.py.

Provenance lines (a capture recorded at a past release) must survive a bump, and they
are protected by what the line says, never by its position. A per-line (path, number)
exclusion table used to exist; it drifted the moment a line was inserted above its
target and then shielded an unrelated live pin. These tests keep that class closed:

  * no position-keyed exclusion table exists;
  * the two lines that table used to protect are still spared by PROVENANCE_LINE_RE,
    and stay spared when other lines are inserted above them;
  * `--check` passes on this checkout (every in-scope pin is at the target and every
    rule still matches its own probe).

Usage: python tests/test_bump_api_version.py
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "ai" / "bump_api_version.py"

spec = importlib.util.spec_from_file_location("bump_api_version", SCRIPT)
bump = importlib.util.module_from_spec(spec)
sys.modules["bump_api_version"] = bump
spec.loader.exec_module(bump)

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        failures.append(f"{name} {detail}".strip())


# The formerly position-keyed lines, found by content so this test cannot drift either.
FORMER = {
    "scripts/context_service/examples/contextServiceLifecycle.apex": "dataPath semantics",
    "unpackaged/post_utils/classes/RLM_DecisionTableManagerController.cls": "bindingobjectformula (",
}

print("position-keyed exclusions")
check("EXCLUDED_LINES table is gone", not hasattr(bump, "EXCLUDED_LINES"))
check("validate_excluded_lines is gone", not hasattr(bump, "validate_excluded_lines"))

print("former exclusions are protected by content")
for rel, needle in FORMER.items():
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    hits = [ln for ln in lines if needle in ln and re.search(r"v?[0-9]{2}\.0", ln)]
    check(f"{rel}: version-bearing provenance line exists", len(hits) == 1, f"found {len(hits)}")
    for ln in hits:
        check(f"{rel}: spared by PROVENANCE_LINE_RE", bool(bump.PROVENANCE_LINE_RE.search(ln)), ln.strip())
        # Position independence: the match is a property of the line text alone.
        shifted = ["// unrelated"] * 5 + [ln]
        check(f"{rel}: still spared after lines are inserted above",
              bool(bump.PROVENANCE_LINE_RE.search(shifted[-1])))

print("rule and provenance self-tests")
check("provenance grammar intact", bump.validate_provenance_grammar() == [])
check("every rule matches its probe",
      bump.validate_rules(bump.build_rules(), "68.0") == [])

print("--check on this checkout")
r = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT,
                   capture_output=True, text=True)
check("--check exits 0", r.returncode == 0, (r.stdout[-400:] + r.stderr[-400:]))

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("all passed")
