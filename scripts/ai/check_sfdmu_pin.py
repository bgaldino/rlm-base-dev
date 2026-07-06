#!/usr/bin/env python3
"""Stale-pin watch for the SFDMU plugin version.

This repo tracks the SFDMU plugin version in two places, deliberately:

  1. **CI pin** — `.github/workflows/prepare-rlm-org.yml` installs an exact
     (or, historically, a bare-major) version via `sf plugins install
     sfdmu@<spec>`. CI is the one place that should be pinned exactly, so a
     new SFDMU release can't silently change CI behavior between runs.
  2. **Floor everywhere else** — `tasks/rlm_validate_setup.py` declares
     `MIN_SFDMU_DEFAULT`, the minimum version `validate_setup` requires of a
     developer's local plugin install. This is a floor, not a pin: local envs
     are allowed to run anything at or above it.

Those two numbers drift apart over time (upstream ships a new SFDMU release,
a Docker image gets rebuilt, someone bumps one file but not the other) and
nothing currently catches that automatically. This script is the "stale-pin
watch": it reads both values plus the latest version published to npm, and
reports whether the pin is exact, whether the floor is still <= the pin,
and whether either has fallen behind upstream latest.

It is meant to be run by a human (`python scripts/ai/check_sfdmu_pin.py`) and
by a weekly automated report session — hence the `--json` mode and the
warn-only default exit code (network/npm flakiness should never break an
unattended run; use `--fail-if-stale` when you want a hard gate).

Usage:
    python scripts/ai/check_sfdmu_pin.py
    python scripts/ai/check_sfdmu_pin.py --json
    python scripts/ai/check_sfdmu_pin.py --fail-if-stale
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CI_WORKFLOW = os.path.join(REPO_ROOT, ".github", "workflows", "prepare-rlm-org.yml")
VALIDATE_SETUP = os.path.join(REPO_ROOT, "tasks", "rlm_validate_setup.py")

# Matches `sf plugins install sfdmu@<spec>` or a bare `sf plugins install sfdmu`
# (no @ at all). Captures the spec (may be absent, a bare major like "5", or an
# exact version like "5.8.0").
CI_PIN_RE = re.compile(r"sf\s+plugins\s+install\s+sfdmu(?:@(\S+))?")

# Matches `MIN_SFDMU_DEFAULT: str = "5.6.4"`, tolerating a missing type
# annotation (`MIN_SFDMU_DEFAULT = "5.6.4"`).
FLOOR_RE = re.compile(r'MIN_SFDMU_DEFAULT\s*(?::\s*str\s*)?=\s*"([^"]+)"')

NPM_TIMEOUT_SECS = 15


def parse_version(spec: str) -> Optional[Tuple[int, ...]]:
    """Parse a dotted numeric version string into a tuple for comparison.

    Returns None if `spec` isn't a plain dotted-numeric version, or if it's a
    bare single component (e.g. a major tag like "5") — callers should treat
    None as "not exact / not comparable" rather than crash. A real semantic
    version needs at least major.minor (e.g. "5.0"), so a lone "5" is
    deliberately rejected here even though it matches the digits-only shape —
    that's exactly the "not exact-pinned" case this script exists to flag.
    """
    if not spec or not re.fullmatch(r"\d+(\.\d+)+", spec):
        return None
    return tuple(int(p) for p in spec.split("."))


def read_ci_pin() -> Tuple[Optional[str], str]:
    """Return (spec, note) for the CI install spec.

    spec is the raw string captured after `sfdmu@` (or None if the line/spec
    itself is missing). note explains what was found for human-readable output.
    """
    if not os.path.isfile(CI_WORKFLOW):
        return None, f"CI workflow not found: {os.path.relpath(CI_WORKFLOW, REPO_ROOT)}"

    with open(CI_WORKFLOW, encoding="utf-8") as fh:
        text = fh.read()

    match = CI_PIN_RE.search(text)
    if not match:
        return None, "no `sf plugins install sfdmu[@...]` line found in CI workflow"

    spec = match.group(1)
    if spec is None:
        return None, "CI installs bare `sfdmu` with no @version — not exact-pinned"
    if parse_version(spec) is None:
        return spec, f"CI installs `sfdmu@{spec}` — not exact-pinned (major tag or non-numeric spec)"
    return spec, f"CI pins `sfdmu@{spec}`"


def read_floor() -> Tuple[Optional[str], str]:
    """Return (version, note) for MIN_SFDMU_DEFAULT in tasks/rlm_validate_setup.py."""
    if not os.path.isfile(VALIDATE_SETUP):
        return None, f"validate_setup task not found: {os.path.relpath(VALIDATE_SETUP, REPO_ROOT)}"

    with open(VALIDATE_SETUP, encoding="utf-8") as fh:
        text = fh.read()

    match = FLOOR_RE.search(text)
    if not match:
        return None, "MIN_SFDMU_DEFAULT not found in tasks/rlm_validate_setup.py"

    floor = match.group(1)
    return floor, f"floor (MIN_SFDMU_DEFAULT) = {floor}"


def read_upstream_latest() -> Tuple[Optional[str], str]:
    """Return (version, note) for the latest version published to npm.

    Degrades gracefully when npm is missing, offline, or times out: returns
    (None, "...unavailable (offline)...") rather than raising, so this check
    never breaks unattended automation on a flaky network.
    """
    try:
        proc = subprocess.run(
            ["npm", "view", "sfdmu", "version"],
            capture_output=True,
            text=True,
            timeout=NPM_TIMEOUT_SECS,
        )
    except FileNotFoundError:
        return None, "latest: unavailable (offline) — npm not found on PATH"
    except subprocess.TimeoutExpired:
        return None, f"latest: unavailable (offline) — npm view timed out after {NPM_TIMEOUT_SECS}s"
    except Exception as e:  # pragma: no cover - defensive catch-all
        return None, f"latest: unavailable (offline) — npm view failed: {type(e).__name__}: {e}"

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip().splitlines()[:1]
        detail = f" ({stderr[0]})" if stderr else ""
        return None, f"latest: unavailable (offline) — npm view exited {proc.returncode}{detail}"

    latest = proc.stdout.strip()
    if parse_version(latest) is None:
        return None, f"latest: unavailable — npm view returned unparseable output: {latest!r}"

    return latest, f"latest published to npm = {latest}"


def build_report() -> dict:
    """Gather pin/floor/latest and run the staleness checks. Returns a dict
    suitable for both human-readable printing and --json output."""
    pin_spec, pin_note = read_ci_pin()
    floor_str, floor_note = read_floor()
    latest_str, latest_note = read_upstream_latest()

    pin_version = parse_version(pin_spec) if pin_spec else None
    floor_version = parse_version(floor_str) if floor_str else None
    latest_version = parse_version(latest_str) if latest_str else None

    pin_is_exact = pin_version is not None

    checks = []

    # (a) floor <= pin, only meaningful when the pin is exact.
    if floor_version is not None and pin_version is not None:
        ok = floor_version <= pin_version
        checks.append({
            "name": "floor_le_pin",
            "ok": ok,
            "message": (
                f"floor {floor_str} <= pin {pin_spec}" if ok
                else f"floor {floor_str} is AHEAD of pin {pin_spec} (floor should never exceed the CI pin)"
            ),
        })
    else:
        checks.append({
            "name": "floor_le_pin",
            "ok": None,
            "message": "skipped — pin is not exact, so floor-vs-pin isn't comparable",
        })

    # (b) pin == latest, only meaningful when both are known.
    if pin_version is not None and latest_version is not None:
        ok = pin_version == latest_version
        checks.append({
            "name": "pin_eq_latest",
            "ok": ok,
            "message": (
                f"pin {pin_spec} matches latest {latest_str}" if ok
                else f"pin {pin_spec} is BEHIND latest {latest_str}"
            ),
        })
    else:
        reason = "pin is not exact" if pin_version is None else "latest is unavailable"
        checks.append({
            "name": "pin_eq_latest",
            "ok": None,
            "message": f"skipped — {reason}",
        })

    # (c) floor <= latest, only meaningful when both are known.
    if floor_version is not None and latest_version is not None:
        ok = floor_version <= latest_version
        checks.append({
            "name": "floor_le_latest",
            "ok": ok,
            "message": (
                f"floor {floor_str} <= latest {latest_str}" if ok
                else f"floor {floor_str} is AHEAD of latest {latest_str} (should never happen)"
            ),
        })
    else:
        checks.append({
            "name": "floor_le_latest",
            "ok": None,
            "message": "skipped — latest is unavailable",
        })

    # Staleness verdict: only "stale" if we positively found a problem. Unknown
    # (None) results never count as stale — that's the "can't determine" case.
    failing = [c for c in checks if c["ok"] is False]
    unknown = [c for c in checks if c["ok"] is None]
    stale = bool(failing) or not pin_is_exact

    return {
        "ci_workflow": os.path.relpath(CI_WORKFLOW, REPO_ROOT),
        "validate_setup": os.path.relpath(VALIDATE_SETUP, REPO_ROOT),
        "pin_spec": pin_spec,
        "pin_is_exact": pin_is_exact,
        "pin_note": pin_note,
        "floor": floor_str,
        "floor_note": floor_note,
        "latest": latest_str,
        "latest_note": latest_note,
        "checks": checks,
        "stale": stale,
        "determinable": not unknown or bool(failing),
    }


def print_human(report: dict) -> None:
    print("SFDMU pin/floor stale-pin watch")
    print("=" * 60)
    print(f"CI workflow      : {report['ci_workflow']}")
    print(f"  {report['pin_note']}")
    print(f"validate_setup   : {report['validate_setup']}")
    print(f"  {report['floor_note']}")
    print(f"  {report['latest_note']}")
    print()
    print("Checks:")
    for check in report["checks"]:
        status = "OK" if check["ok"] else ("SKIP" if check["ok"] is None else "FAIL")
        print(f"  [{status:4}] {check['message']}")

    print()
    if report["stale"]:
        if not report["pin_is_exact"]:
            print("VERDICT: STALE-PIN WATCH — CI is not exact-pinned (bare major tag or missing @version).")
        else:
            print("VERDICT: STALE-PIN WATCH — pin and/or floor have drifted behind upstream. See FAIL checks above.")
    else:
        unresolved = [c for c in report["checks"] if c["ok"] is None]
        if unresolved:
            print("VERDICT: OK (with gaps) — no drift detected in the checks we could run, "
                  "but some checks were skipped (see SKIP above).")
        else:
            print("VERDICT: OK — pin is exact, floor <= pin <= latest.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect when the SFDMU CI pin / floor go stale vs upstream npm.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON object instead of human-readable text.",
    )
    parser.add_argument(
        "--fail-if-stale",
        action="store_true",
        help=(
            "Exit 1 when the pin is behind latest or the floor exceeds the pin. "
            "Default is warn-only (always exits 0). Never fails solely because "
            "upstream/npm was unreachable — that case is reported but not treated "
            "as failure."
        ),
    )
    args = parser.parse_args()

    report = build_report()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)

    if args.fail_if_stale and report["stale"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
