#!/usr/bin/env python3
"""Phase 0 live-probe helper (throwaway scaffolding, not the final tool).

Wraps `sf api request rest` so we can exercise the lifecycle endpoints against a
real org and capture exact bodies/responses for CONTRACTS.md. Kept deliberately
small; the real client lives in auth.py once contracts are locked.

Usage:
    python scripts/demo_data/_probe.py query  "SELECT ..."
    python scripts/demo_data/_probe.py get     /services/data/v67.0/...
    python scripts/demo_data/_probe.py post    /services/data/v67.0/...  '<json body>'
    python scripts/demo_data/_probe.py patch    /services/data/v67.0/...  '<json body>'
"""
import json
import subprocess
import sys
import tempfile
import urllib.parse

ALIAS = "rlm-base__jun17_1"
V = "v67.0"


def _run(args, body=None):
    cmd = ["sf", "api", "request", "rest", *args, "--target-org", ALIAS]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        tmp.write(body)
        tmp.flush()
        cmd += ["--body", f"@{tmp.name}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout.strip()
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"_raw": out, "_stderr": proc.stderr.strip(), "_exit": proc.returncode}


def main():
    verb = sys.argv[1]
    if verb == "query":
        soql = urllib.parse.quote(sys.argv[2])
        res = _run([f"/services/data/{V}/query?q={soql}"])
    elif verb == "get":
        res = _run([sys.argv[2]])
    elif verb in ("post", "patch"):
        res = _run([sys.argv[2], "-X", verb.upper(),
                    "-H", "Content-Type: application/json"], body=sys.argv[3])
    else:
        sys.exit(f"unknown verb {verb}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
