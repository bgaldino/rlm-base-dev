#!/usr/bin/env python3
"""Run the LWC Jest suites for pr_gate.py, with the gate's exit contract.

0 = every suite passed · 1 = a test failed · 2 = Jest could not run (tool error).

A Python wrapper rather than an `npm test` argv because the gate's argv whitelist admits only
an interpreter and paths (tests/test_pr_gate.py, CMD_WORDS): a command built from free words
is how a check becomes a no-op that exits 0. The wrapper also refuses the quiet greens Jest
itself allows: no suite found, no test passed, and skipped or todo tests.

Usage: python scripts/ai/run_lwc_jest.py
"""
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JEST = os.path.join(REPO_ROOT, "node_modules", ".bin", "sfdx-lwc-jest")


def main():
    if not os.path.exists(JEST):
        print(f"sfdx-lwc-jest is not installed ({JEST}); run `npm ci`.", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        report = os.path.join(tmp, "jest.json")
        try:
            proc = subprocess.run([JEST, "--", "--ci", "--json", f"--outputFile={report}"],
                                  cwd=REPO_ROOT, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            # A hang is a property of the change under test, so a failure, as pr_gate.run() rules.
            print("sfdx-lwc-jest timed out after 600s.", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"could not run sfdx-lwc-jest: {exc}", file=sys.stderr)
            return 2
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        try:
            with open(report) as fh:
                result = json.load(fh)
        except (OSError, ValueError):
            print("Jest wrote no result report, so it did not run its suites.", file=sys.stderr)
            return 2
    code, message = verdict(result, proc.returncode)
    print(message, file=sys.stderr if code else sys.stdout)
    return code


def verdict(result, returncode):
    """(exit code, message) for a Jest JSON report and Jest's own exit code.

    numTotalTests counts skipped tests, so a suite of `describe.skip` reads as 13 tests and
    Jest calls it a success. So a pass needs at least one passed test and no skipped or todo
    one: a skipped test is coverage quietly withdrawn.
    """
    passed = result.get("numPassedTests", 0)
    skipped = result.get("numPendingTests", 0) + result.get("numTodoTests", 0)
    failed = result.get("numFailedTests", 0) + result.get("numFailedTestSuites", 0)
    summary = (f"LWC Jest: {result.get('numTotalTestSuites', 0)} suite(s), {passed} passed, "
               f"{result.get('numFailedTests', 0)} failed, {skipped} skipped or todo.")
    if passed == 0:
        return 1, summary + " No LWC test passed. A green run with nothing in it is not a pass."
    if skipped:
        return 1, summary + " Skipped or todo tests: remove the .skip/.todo or the test."
    if failed or returncode != 0 or not result.get("success", False):
        return 1, summary
    return 0, summary

if __name__ == "__main__":
    sys.exit(main())
