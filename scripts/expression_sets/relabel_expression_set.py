#!/usr/bin/env python3
"""Set readable step **labels** on a BRE Expression Set via the Tooling API (MUTATING).

A step's readable UI label lives ONLY in the Tooling
``ExpressionSetDefinitionVersion.Metadata.steps[].label`` — the Connect API has no
``label`` field, and a Connect full-graph PATCH (``import_expression_set`` /
``apply_expression_set_overlay``) rebuilds every label from the spaceless ``name``,
so a Connect-built procedure shows run-on names (``Applyheaderpriceoverride``) in
the UI. This tool writes readable labels back through the Tooling ``Metadata``
PATCH, run inside the same deactivate → PATCH → reactivate lifecycle a Connect
mutation uses (an active version rejects the PATCH with ``INVALID_ID_FIELD:
LatestVersionSnapshotId not found``).

Label sources (combine freely; later overrides earlier):

  1. ``--auto`` — derive a best-effort label from each spaceless name for steps
     that currently lack a readable label (``label`` missing or == ``name``).
     **Lossy** — despacing already discarded the original casing/punctuation, so
     an all-lowercase run-on can't be fully recovered. Prefer an explicit map.
  2. ``--labels-file <json>`` — a JSON object ``{"StepName": "Readable Label"}``
     (or ``{"labels": { … }}``).
  3. ``--set StepName="Readable Label"`` (repeatable) — inline overrides.

**Run relabel LAST.** Any later Connect mutation on the same version clobbers
these labels back to the names. See ``metadata-vs-connect.md`` → *Step names vs.
labels*.

**Preview by default.** Without ``--confirm`` the tool resolves ids, reads the
current labels, prints the exact ``name → label`` changes, and writes nothing.
Re-run with ``--confirm`` to apply.

Quick Rule 8 — apply to a disposable clone, never a shipped procedure.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled
here. ``--target-org`` is the *SF CLI* alias, never the CCI alias. Pinned to
Release 262 / v67.0.

Usage
-----
    # preview auto-derived labels for the run-on (drift) steps
    python scripts/expression_sets/relabel_expression_set.py \
        --target-org rlm-base__beta --expression-set RLM_MyClone --auto

    # apply an explicit label map
    python scripts/expression_sets/relabel_expression_set.py \
        --target-org rlm-base__beta --expression-set RLM_MyClone \
        --labels-file /tmp/labels.json --confirm

    # one-off inline override
    python scripts/expression_sets/relabel_expression_set.py \
        --target-org rlm-base__beta --expression-set RLM_MyClone \
        --set Applyheaderpriceoverride="Apply Header Price Override" --confirm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    Transport,
    eprint,
)
from scripts.expression_sets._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.expression_sets._resolve import (  # noqa: E402
    ResolveError,
    resolve_definition_id,
    resolve_expression_set_id,
    resolve_version_by_es_id,
)
from scripts.expression_sets._tooling import (  # noqa: E402
    ToolingError,
    apply_labels,
    derive_labels,
    fetch_metadata,
    patch_metadata,
    resolve_esdv,
    step_labels,
)


def _parse_set(pairs):
    """Turn ``["Name=Label", …]`` into ``{Name: Label}`` (raises on a bad entry)."""
    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"--set '{pair}' must be NAME=LABEL.")
        name, label = pair.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError(f"--set '{pair}' has an empty step name.")
        out[name] = label
    return out


def _load_labels_file(path_str):
    """Load a ``{name: label}`` map from a JSON file (accepts a ``labels`` wrapper)."""
    path = Path(path_str)
    if not path.exists():
        raise ValueError(f"labels file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("labels"), dict):
        data = data["labels"]
    if not isinstance(data, dict):
        raise ValueError(
            f"labels file must be a JSON object of {{name: label}} (got {type(data).__name__})."
        )
    bad = [k for k, v in data.items() if not isinstance(v, str)]
    if bad:
        raise ValueError(f"labels file values must be strings; non-string for: {bad}")
    return data


def _resolve_target_version(engine, es_id, version_api_name, target_org, api_version):
    """Resolve the ExpressionSetVersion (9QM) to relabel — explicit or active/latest."""
    if version_api_name:
        rows = engine.t.soql(
            "SELECT Id, ApiName, IsActive, VersionNumber FROM ExpressionSetVersion "
            f"WHERE ExpressionSetId = '{es_id}' AND ApiName = '{version_api_name}'"
        )
        if not rows:
            raise ResolveError(
                f"Version '{version_api_name}' not found under ExpressionSet {es_id}."
            )
        return rows[0]
    return resolve_version_by_es_id(
        es_id, target_org=target_org, api_version=api_version, logger=eprint
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Set readable step labels on a BRE Expression Set via the Tooling "
                    "API. MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--expression-set", dest="es_api_name", required=True,
                        help="ExpressionSetDefinition DeveloperName.")
    parser.add_argument("--version", dest="version_api_name",
                        help="Target a specific version apiName (default: active/latest).")
    parser.add_argument("--auto", action="store_true",
                        help="Derive best-effort labels (lossy) for steps that lack a "
                             "readable one (label missing or == name).")
    parser.add_argument("--labels-file",
                        help="JSON object {name: label} (or {\"labels\": {…}}).")
    parser.add_argument("--set", dest="set_pairs", action="append", default=[],
                        metavar="NAME=LABEL",
                        help="Inline label override (repeatable). Overrides file/auto.")
    parser.add_argument("--no-verify", action="store_true",
                        help="Skip the post-PATCH verification re-read.")
    parser.add_argument("--no-activate", action="store_true",
                        help="Leave the version DEACTIVATED after the relabel.")
    parser.add_argument("--no-cascade", action="store_true",
                        help="Do NOT cascade-deactivate referencing procedure-plan versions.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually write the labels. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    if not (args.auto or args.labels_file or args.set_pairs):
        eprint("Error: provide at least one label source (--auto, --labels-file, or --set).")
        return 2

    try:
        file_map = _load_labels_file(args.labels_file) if args.labels_file else {}
        set_map = _parse_set(args.set_pairs)
    except ValueError as exc:
        eprint(f"Error: {exc}")
        return 2

    preview = not args.confirm
    activate_after = not args.no_activate
    cascade = not args.no_cascade
    verify = not args.no_verify
    transport = Transport(
        target_org=args.target_org, api_version=args.api_version,
        dry_run=preview, logger=eprint,
    )
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        es_id = resolve_expression_set_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        es_def_id = resolve_definition_id(
            args.es_api_name, target_org=args.target_org, api_version=args.api_version
        )
        esv = _resolve_target_version(
            engine, es_id, args.version_api_name, args.target_org, args.api_version
        )
        version_api_name = esv.get("ApiName")

        # ---- local pre-flights (BEFORE any deactivation) ----------------- #
        esdv = resolve_esdv(transport, version_api_name=version_api_name)
        esdv_id = esdv["Id"]
        preflight_md = fetch_metadata(transport, esdv_id)
        current = step_labels(preflight_md)

        # Build the {name: label} map: auto (base) → file → set (each overrides).
        name_to_label = {}
        if args.auto:
            name_to_label.update(derive_labels(preflight_md, only_drift=True))
        name_to_label.update(file_map)
        name_to_label.update(set_map)

        # Fail loudly on a typo'd step name from an explicit source (file/set) —
        # a silent no-op is how a mislabeled step slips through. --auto names are
        # derived from the metadata so are always present.
        explicit = set(file_map) | set(set_map)
        unknown = sorted(n for n in explicit if n not in current)
        if unknown:
            eprint(f"Error: label map references step name(s) not in version "
                   f"'{version_api_name}': {unknown}")
            return 1

        # The set of labels that would actually change (skip no-ops / blanks).
        planned = {
            n: l for n, l in name_to_label.items()
            if l and current.get(n) != l
        }
        if args.auto:
            eprint("Note: --auto labels are best-effort (lossy) — despacing "
                   "discarded the original casing/punctuation. Review before --confirm.")
        if not planned:
            eprint(f"No label changes needed for version '{version_api_name}' "
                   f"({len(current)} step(s) already labeled as requested).")
            if args.json:
                print(json.dumps({
                    "action": "relabel", "expressionSet": args.es_api_name,
                    "expressionSetId": es_id, "version": version_api_name,
                    "esdvId": esdv_id, "changed": [], "dryRun": preview,
                }, indent=2))
            return 0

        eprint(f"Relabel '{args.es_api_name}' version {version_api_name} "
               f"(esdv={esdv_id}), {len(planned)} step(s), "
               f"activate_after={activate_after}, cascade={cascade}, "
               f"{'PREVIEW' if preview else 'CONFIRM'}")
        for name in sorted(planned):
            old = current.get(name)
            eprint(f"    {name}: {old!r} → {planned[name]!r}")
        eprint("Reminder: run this LAST — a later Connect import/overlay clobbers "
               "these labels back to the step names.")

        def mutate():
            # Re-read post-deactivation so the PATCH reflects the current stored
            # Metadata; re-apply the map as a guard against drift.
            metadata = fetch_metadata(transport, esdv_id)
            new_md, changed = apply_labels(metadata, name_to_label, logger=engine.log)
            if not changed:
                engine.log("No label changes to write after re-read; skipping PATCH.")
                return
            patch_metadata(transport, esdv_id, new_md)
            engine.log(f"PATCHed Tooling Metadata for {esdv_id} "
                       f"({len(changed)} label(s)).")
            if verify and not preview:
                _verify(transport, esdv_id, planned)

        engine.run_mutation(
            es_def_id=es_def_id, esv=esv, mutate=mutate,
            activate_after=activate_after, cascade=cascade, verb="Relabel",
        )

    except (ExpressionSetClientError, ResolveError, LifecycleError, ToolingError) as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    else:
        eprint(f"\nSuccessfully relabeled {len(planned)} step(s) on {args.es_api_name}.")
    if args.json:
        print(json.dumps({
            "action": "relabel", "expressionSet": args.es_api_name,
            "expressionSetId": es_id, "version": version_api_name,
            "esdvId": esdv_id, "changed": sorted(planned), "dryRun": preview,
        }, indent=2))
    return 0


def _verify(transport, esdv_id, planned):
    """Confirm the intended labels are present after the PATCH."""
    labels = step_labels(fetch_metadata(transport, esdv_id))
    missing = {n: l for n, l in planned.items() if labels.get(n) != l}
    if missing:
        raise LifecycleError(
            f"Verification failed: {len(missing)} label(s) did not persist: "
            f"{sorted(missing)}."
        )
    eprint(f"Verified {len(planned)} label(s) applied.")


if __name__ == "__main__":
    raise SystemExit(main())
