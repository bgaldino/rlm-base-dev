#!/usr/bin/env python3
"""Create a BRE Decision Table from a canonical JSON spec.

The default path deploys generated Metadata from a temporary SFDX project;
``--path tooling`` uses a Tooling create. The requested status is sent unchanged
so platform validation remains authoritative. The command previews by default
and requires ``--confirm`` to write to an org.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables import _payload  # noqa: E402
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DecisionTableClientError,
    Transport,
    eprint,
    fail_json,
)
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._resolve import (  # noqa: E402
    ResolveError,
    resolve_decision_table,
)
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
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--spec", required=True,
                        help="Path to the canonical spec JSON ('-' for stdin).")
    parser.add_argument("--path", choices=("metadata", "tooling"),
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
        return fail_json(
            args.json,
            "Error: --generate-only is only valid with --path metadata.",
            {"action": "create", "path": args.path},
            code=2,
        )

    try:
        spec = _load_spec(args.spec)
    except (OSError, ValueError) as exc:
        return fail_json(args.json, f"Error: could not read spec '{args.spec}': {exc}")

    result = validate_spec(spec, path=args.path)
    eprint(result.format_report())
    if not result.passed:
        return fail_json(args.json, "Spec has errors; not creating. Fix them and retry.",
                         {"action": "create"})

    api_name = spec.get("fullName")
    preview = not args.confirm

    # --generate-only is an offline file write (no org write) — always honored.
    if args.generate_only:
        xml = _payload.to_metadata_xml(spec)
        try:
            with open(args.generate_only, "w", encoding="utf-8") as fh:
                fh.write(xml)
        except OSError as exc:
            return fail_json(
                args.json,
                f"Error: could not write '{args.generate_only}': {exc}",
                {"action": "create", "path": "metadata",
                 "generateOnly": args.generate_only, "apiName": api_name},
            )
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

    # Honor the spec's requested status as-is — the platform is the authority.
    # An accepted write stores the definition faithfully; a bad one is rejected
    # with a clear error. A CsvUpload table cannot be Active
    # at create time (no active file-import version yet), so warn — the platform
    # would otherwise reject it with INVALID_INPUT.
    requested_status = spec.get("status")
    if (requested_status == "Active"
            and spec.get("dataSourceType") == "CsvUpload"):
        eprint("\nNOTE: a CsvUpload table cannot be created Active — it has no "
               "active file-import version yet, and the platform will reject "
               "status=Active. Create it Draft, then load rows with "
               "upload_decision_table_data.py and activate with "
               "activate_decision_table.py.")
    summary = {"action": "create", "path": args.path, "apiName": api_name,
               "requestedStatus": requested_status, "dryRun": preview}

    eprint(f"\nCreate DecisionTable '{api_name}' via --path {args.path}, "
           f"status={requested_status}, {'PREVIEW' if preview else 'CONFIRM'}")

    try:
        if args.path == "metadata":
            xml = _payload.to_metadata_xml(spec)
            if preview:
                eprint("[preview] would deploy this .decisionTable-meta.xml:\n")
                eprint(xml)
            else:
                summary["deploy"] = engine.deploy_metadata_xml(api_name, xml)
        else:  # tooling
            resp = transport.tooling_sobject(
                "POST", "DecisionTable", body=_payload.to_tooling(spec))
            summary["response"] = resp
            if not preview and isinstance(resp, dict) and resp.get("id"):
                summary["id"] = resp["id"]

        # Activation is async: if Active was requested, poll past
        # ActivationInProgress so a follow-on read sees a settled state.
        if not preview and requested_status == "Active" \
                and spec.get("dataSourceType") != "CsvUpload":
            record_id = summary.get("id") \
                or resolve_decision_table(transport, api_name)["Id"]
            summary["id"] = record_id
            engine.wait_for_status(record_id, "Active")
    except (DecisionTableClientError, LifecycleError, ResolveError) as exc:
        return fail_json(args.json, f"FAILED: {exc}", summary)

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to create.")
    else:
        eprint("\nCreate complete. Verify with describe_decision_table.py.")
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
