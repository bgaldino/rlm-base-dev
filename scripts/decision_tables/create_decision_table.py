#!/usr/bin/env python3
"""Create a BRE Decision Table from a canonical spec (MUTATING).

Reads an author-facing **canonical spec** (JSON — see ``_schema.py`` for the
shape and ``validate_spec`` for the rules), validates it offline, then creates
the table via one of three authoring paths:

* ``--path metadata`` (default) — generate a ``.decisionTable-meta.xml`` and
  deploy it via a **temp SFDX project outside the repo** (``sf project deploy
  start --ignore-conflicts``, cleaned up after — no generated churn in
  ``git status``). ``--generate-only <path>`` skips the deploy and instead writes
  the XML to an explicit path you choose (+ prints deploy instructions); only that
  mode leaves a file behind, at a location you name.
* ``--path tooling`` — Tooling ``DecisionTable`` POST (``{"FullName","Metadata"}``).
* ``--path connect`` — Connect Definitions POST (flat body; ``setupName`` +
  ``status`` required — the translator defaults ``status`` to ``Draft``).

**Preview by default.** Without ``--confirm`` the tool validates the spec and logs
the planned write (or prints the XML for ``metadata``) but performs no org write.
Re-run with ``--confirm`` to create. (``--generate-only`` always writes its file —
it does not touch the org, so ``--confirm`` is not required for it.)

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias (e.g. ``rlm-base__beta``), never the CCI
alias. Pinned to Release 262 / v67.0. Destructive probing / round-trips run on
**scratch orgs only**, never the shared ``beta``.

Usage
-----
    # preview a metadata-path create (prints the XML), then deploy it
    python scripts/decision_tables/create_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json
    python scripts/decision_tables/create_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json --confirm

    # write the .decisionTable-meta.xml to a path you choose (no deploy)
    python scripts/decision_tables/create_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json \
        --generate-only ./RLM_MyTable.decisionTable-meta.xml

    # create via the Tooling or Connect API instead
    python scripts/decision_tables/create_decision_table.py \
        --target-org rlm-base__scratch --spec my_table.json --path tooling --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables import _payload  # noqa: E402
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DEFINITIONS_PATH,
    DecisionTableClientError,
    Transport,
    eprint,
)
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._schema import validate_spec  # noqa: E402


def _load_spec(path):
    """Load a canonical spec from a JSON file (or stdin when path is '-')."""
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a BRE Decision Table from a canonical spec. MUTATING "
                    "(preview by default; --confirm to create).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--spec", required=True,
                        help="Path to the canonical spec JSON ('-' for stdin).")
    parser.add_argument("--path", choices=("metadata", "tooling", "connect"),
                        default="metadata",
                        help="Authoring path (default: metadata → temp SFDX deploy).")
    parser.add_argument("--generate-only", metavar="XML_PATH",
                        help="metadata path only: write the .decisionTable-meta.xml to "
                             "this explicit path and skip the deploy.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually create. Without it, only PREVIEWS "
                             "(--generate-only writes its file regardless).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    if args.generate_only and args.path != "metadata":
        eprint("Error: --generate-only is only valid with --path metadata.")
        return 2

    try:
        spec = _load_spec(args.spec)
    except (OSError, ValueError) as exc:
        eprint(f"Error: could not read spec '{args.spec}': {exc}")
        return 1

    result = validate_spec(spec)
    eprint(result.format_report())
    if not result.passed:
        eprint("\nSpec has errors; not creating. Fix them and retry.")
        return 1

    api_name = spec.get("fullName")
    preview = not args.confirm

    # --generate-only is an offline file write (no org write) — always honored.
    if args.generate_only:
        xml = _payload.to_metadata_xml(spec)
        try:
            with open(args.generate_only, "w", encoding="utf-8") as fh:
                fh.write(xml)
        except OSError as exc:
            eprint(f"Error: could not write '{args.generate_only}': {exc}")
            return 1
        eprint(f"\nWrote {args.generate_only}. Deploy it with:\n"
               f"  sf project deploy start --source-dir <dir-containing-it> "
               f"--target-org {args.target_org}")
        if args.json:
            print(json.dumps({"action": "create", "path": "metadata",
                              "generateOnly": args.generate_only,
                              "apiName": api_name, "dryRun": False}, indent=2))
        return 0

    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)
    summary = {"action": "create", "path": args.path, "apiName": api_name,
               "dryRun": preview}

    eprint(f"\nCreate DecisionTable '{api_name}' via --path {args.path}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    try:
        if args.path == "metadata":
            xml = _payload.to_metadata_xml(spec)
            if preview:
                eprint("[preview] would deploy this .decisionTable-meta.xml:\n")
                eprint(xml)
            else:
                deploy = engine.deploy_metadata_xml(api_name, xml)
                summary["deploy"] = deploy
        elif args.path == "tooling":
            body = _payload.to_tooling(spec)
            resp = transport.tooling_sobject("POST", "DecisionTable", body=body)
            summary["response"] = resp
            if not preview and isinstance(resp, dict) and resp.get("id"):
                summary["id"] = resp["id"]
        else:  # connect
            body = _payload.to_connect(spec)
            resp = transport.connect("POST", DEFINITIONS_PATH, body)
            summary["response"] = resp
    except (DecisionTableClientError, LifecycleError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to create.")
    else:
        eprint("\nCreate complete. Verify with describe_decision_table.py "
               "(a Connect create echoes empty parameters — GET-back to confirm columns).")
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
