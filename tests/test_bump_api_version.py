#!/usr/bin/env python3
"""Offline tests for scripts/ai/bump_api_version.py.

Provenance lines (a capture recorded at a past release) must survive a bump, and they
are protected by what the line says, never by its position. A per-line (path, number)
exclusion table used to exist; it drifted the moment a line was inserted above its
target and then shielded an unrelated live pin. These tests keep that class closed:

  * no position-keyed exclusion table exists;
  * the two lines that table used to protect are still spared by PROVENANCE_LINE_RE;
  * a dry run to the next version never changes a provenance or floor line (the repo-wide
    `--check` is the always-run `api_version_pins` gate check, not repeated here).

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


# The current target, read from the project's own source of truth rather than restated here.
CURRENT = re.search(r'^\s*api_version:\s*"([0-9]{2}\.0)"', (ROOT / "cumulusci.yml").read_text(encoding="utf-8"), re.M).group(1)

# The formerly position-keyed lines, found by content so this test cannot drift either.
FORMER = {
    "scripts/context_service/examples/contextServiceLifecycle.apex": "dataPath semantics",
    "unpackaged/post_utils/classes/RLM_DecisionTableManagerController.cls": "bindingobjectformula (",
}

# Lines that state a floor ("only as of vNN") and would become false if retargeted, found by
# content. Wordings of that shape that no provenance form covers ("baseline", "introduced in",
# "pinned to", "at least") must not sit on a line the bump rewrites: none do today, and the
# dry-run check below fails if one appears.
FLOOR_FILES = {
    "unpackaged/post_mcp_custom/classes/RLM_CloneSalesTransaction.cls": ["ASYNC-CAPABLE", "exist only"],
    "unpackaged/post_mcp_custom/classes/RLM_CloneSalesTransactionTest.cls": ["async-capable ("],
}
UNGUARDED_WORDINGS = ("baseline", "introduced in", "pinned to", "at least", "floor", "only from",
                      "minimum", "since", "gone in", "min_api_version")

print("position-keyed exclusions")
check("EXCLUDED_LINES table is gone", not hasattr(bump, "EXCLUDED_LINES"))
check("validate_excluded_lines is gone", not hasattr(bump, "validate_excluded_lines"))

print("former exclusions and floor lines are protected by content")
for rel, needle in FORMER.items():
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    hits = [ln for ln in lines if needle in ln and re.search(r"v?[0-9]{2}\.0", ln)]
    check(f"{rel}: version-bearing provenance line exists", len(hits) == 1, f"found {len(hits)}")
    for ln in hits:
        check(f"{rel}: spared by PROVENANCE_LINE_RE", bool(bump.PROVENANCE_LINE_RE.search(ln)), ln.strip())

print("rule and provenance self-tests")
check("provenance grammar intact", bump.validate_provenance_grammar() == [])
check("every rule matches its probe",
      bump.validate_rules(bump.build_rules(), CURRENT) == [])

print("provenance regex is word-bounded")
for text in ("alias offset v68.0", "it has offered v68.0", "unobserved at v68.0",
             "unverified on v68.0", "xlive-verified v68.0",
             "foo(MIN_API_VERSION, 'v68.0')", "see MIN_API_VERSION for v68.0",
             'if MIN_API_VERSION == "v68.0":'):
    check(f"does not spare a live pin on {text!r}", not bump.PROVENANCE_LINE_RE.search(text))
for text in ("as of v67.0", "as-of v67.0", "observed at v67.0", "MIN_API_VERSION = \"65.0\"",
             'MIN_API_VERSION: str = "65.0"', "MIN_API_VERSION:str=\"65.0\"",
             "live-verified v67.0", "verified on 262 / v67.0"):
    check(f"spares {text!r}", bool(bump.PROVENANCE_LINE_RE.search(text)))

print("floor lines exist and are spared by content")
for rel, needles in FLOOR_FILES.items():
    lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    for needle in needles:
        hits = [ln for ln in lines if needle in ln and re.search(r"v?[0-9]{2}\.0", ln)]
        check(f"{rel}: {needle!r} line carries a version", bool(hits))
        check(f"{rel}: {needle!r} line spared by PROVENANCE_LINE_RE",
              all(bump.PROVENANCE_LINE_RE.search(ln) for ln in hits), str(hits))

# End to end: a dry run to the next version writes nothing and lists every line it WOULD change.
# Position-independence cannot be shown on one line's text, but it can be shown here: whatever
# the line numbers are today, no changed line may be a provenance or floor statement.
print("dry run to the next version spares provenance and floor lines")
target = bump.next_version(CURRENT)
before = subprocess.run(["git", "diff", "--no-ext-diff"], cwd=ROOT, capture_output=True, text=True).stdout
r = subprocess.run([sys.executable, str(SCRIPT), "--to", target, "--verbose"], cwd=ROOT,
                   capture_output=True, text=True)
check("dry run exits 0", r.returncode == 0, (r.stdout[-300:] + r.stderr[-300:]))
changed: list[tuple[str, str]] = []  # (path, old line)
path = ""
for raw in r.stdout.splitlines():
    m = re.match(r"^    (\S+):\d+$", raw)
    if m:
        path = m.group(1)
    elif raw.startswith("      - "):
        changed.append((path, raw[8:]))
check("dry run found live pins to rewrite", len(changed) > 100, str(len(changed)))
# NOTE: the first assertion below only proves process() still honours PROVENANCE_LINE_RE; it is
# not coverage of the phrase list. Coverage of wordings the list lacks is the second assertion.
forms = [f.lower() for f in bump.PROVENANCE_FORMS]
leaked = [(p, ln.strip()[:80]) for p, ln in changed if any(f in ln.lower() for f in forms)]
check("no changed line carries a provenance phrase (process() guard)", not leaked, str(leaked[:3]))
unguarded = [(p, ln.strip()[:80]) for p, ln in changed
             if any(w in ln.lower() for w in UNGUARDED_WORDINGS)]
check("no changed line uses a floor wording the grammar does not guard", not unguarded,
      str(unguarded[:3]))
marked = list(FORMER.values()) + [n for needles in FLOOR_FILES.values() for n in needles]
rewritten = [(p, ln.strip()[:80]) for p, ln in changed if any(n in ln for n in marked)]
check("no former-exclusion or floor line is rewritten", not rewritten, str(rewritten[:3]))
after = subprocess.run(["git", "diff", "--no-ext-diff"], cwd=ROOT, capture_output=True, text=True).stdout
check("dry run wrote nothing", before == after)

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("all passed")
