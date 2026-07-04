#!/usr/bin/env python3
"""List Context Definitions in an org (read-only).

GETs ``connect/context-definitions`` and prints one row per definition:
developerName, active version number, isActive, isUpgradeAvailable.

Auth is delegated to the sf CLI (see _client.py) — no tokens are handled here.

Usage:
    python scripts/context_service/list_contexts.py --target-org rlm-base__beta
    python scripts/context_service/list_contexts.py --target-org rlm-base__beta --json

Note: the exact GET response shape (field names, includeInactive/includeUpgrade
query params) is pinned to Release 262 / API v67.0 and should be re-verified
against a live org — this is a "verify-live" tool for its GET behavior.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _client import (  # noqa: E402
    ContextClientError,
    active_version,
    connect_get,
    definition_developer_name,
    eprint,
    normalize_definition_list,
)


def _row(defn: dict) -> dict:
    version = active_version(defn)
    return {
        "developerName": definition_developer_name(defn),
        "activeVersion": version.get("versionNumber")
        or version.get("contextDefinitionVersionNumber"),
        "isActive": defn.get("isActive")
        if defn.get("isActive") is not None
        else version.get("isActive"),
        "isUpgradeAvailable": defn.get("isUpgradeAvailable"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="List Context Definitions in an org.")
    parser.add_argument(
        "--target-org",
        required=True,
        help="SF CLI alias or username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument(
        "--api-version", default="67.0", help="Salesforce API version (default 67.0)."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )
    args = parser.parse_args(argv)

    # includeInactive/includeUpgrade surface inactive defs + upgrade availability.
    path = "connect/context-definitions?includeInactive=true&includeUpgrade=true"
    try:
        response = connect_get(path, args.target_org, args.api_version)
    except ContextClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    definitions = normalize_definition_list(response)
    rows = [_row(d) for d in definitions]

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    if not rows:
        print("No context definitions returned.")
        return 0

    rows = sorted(rows, key=lambda r: (r["developerName"] or ""))
    name_w = max(len("DeveloperName"), *(len(r["developerName"] or "?") for r in rows))

    def _fmt(v, dash="-"):
        # None means the field was absent from the response (unknown), which is
        # distinct from a genuine False — render it as a dash, not "False".
        if v is None:
            return dash
        if isinstance(v, str):
            return v
        return str(bool(v)) if isinstance(v, bool) else str(v)

    header = f"{'DeveloperName':<{name_w}}  {'ActiveVer':>9}  {'Active':<6} {'Upgrade':<7}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{(row['developerName'] or '?'):<{name_w}}  "
            f"{_fmt(row['activeVersion']):>9}  "
            f"{_fmt(row['isActive']):<6} "
            f"{_fmt(row['isUpgradeAvailable']):<7}"
        )
    print(f"\n{len(rows)} definition(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
