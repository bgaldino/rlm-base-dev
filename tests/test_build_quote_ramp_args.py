#!/usr/bin/env python3
"""Offline tests for scripts/build_quote_to_asset.py's ramp argument rules (todo 306).

The ramp options are refused before any org call, so a wrong combination can't leave an
Opportunity or Quote behind: the N-year span, single-line quotes, positive values, and a
group ramp's first year without 29 February.

Run:  python tests/test_build_quote_ramp_args.py   (no org, stdlib only)
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "..", "scripts", "build_quote_to_asset.py")
spec = importlib.util.spec_from_file_location("build_quote_to_asset", _PATH)
bq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bq)

_failures = []


def refused(*argv):
    """True if main() exits with an argument error before touching an org."""
    sys.argv = ["build_quote_to_asset.py", "--org", "x", "--accounts", "A", "--sku", "S", *argv]
    # Every sf_* helper goes through _run, so stubbing it too keeps any org call out.
    trip = lambda *a, **k: (_ for _ in ()).throw(AssertionError("reached the org"))
    real_build, bq.build_one = bq.build_one, trip
    real_run, bq._run = bq._run, trip
    stderr, sys.stderr = sys.stderr, open(os.devnull, "w")
    stdout, sys.stdout = sys.stdout, open(os.devnull, "w")
    try:
        bq.main()
    except SystemExit as exc:
        return exc.code == 2
    except AssertionError:
        return False
    finally:
        sys.stderr.close()
        sys.stderr = stderr
        sys.stdout.close()
        sys.stdout = stdout
        bq.build_one = real_build
        bq._run = real_run
    return False


def expect(label, got, want):
    if got != want:
        _failures.append(f"{label}: got {got!r}, want {want!r}")


RAMP = ("--ramp-years", "2", "--ramp-quantities", "1,2")
expect("an end that isn't N years from the start", refused(*RAMP, "--start", "2026-05-01", "--end", "2027-04-30"), True)
expect("extra lines on a ramp", refused(*RAMP, "--start", "2026-05-01", "--end", "2028-04-30", "--with-sku", "X"), True)
expect("a zero quantity", refused("--ramp-years", "2", "--ramp-quantities", "0,2", "--start", "2026-05-01",
                                  "--end", "2028-04-30"), True)
expect("negative ramp years", refused("--ramp-years", "-2", "--start", "2026-05-01", "--end", "2028-04-30"), True)
expect("quantities without a matching count", refused("--ramp-years", "2", "--ramp-quantities", "1",
                                                      "--start", "2026-05-01", "--end", "2028-04-30"), True)
expect("--ramp-kind group without --ramp-years", refused("--ramp-kind", "group", "--start", "2026-05-01"), True)
expect("a group ramp whose year 1 has 29 February",
       refused(*RAMP, "--ramp-kind", "group", "--start", "2027-03-01", "--end", "2029-02-28"), True)
expect("a line ramp across 29 February is fine",
       refused(*RAMP, "--start", "2027-03-01", "--end", "2029-02-28"), False)
expect("a group ramp whose later year has 29 February is fine (measured)",
       refused(*RAMP, "--ramp-kind", "group", "--start", "2026-05-01", "--end", "2028-04-30"), False)

if _failures:
    print("FAIL")
    for f in _failures:
        print(f"  {f}")
    sys.exit(1)
print("PASS test_build_quote_ramp_args")
