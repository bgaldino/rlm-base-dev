#!/usr/bin/env python3
"""Extract a Context Definition diff into an applicable **patch** (read-only).

This is the emit-a-patch companion to ``diff_context.py``. It computes the same
drift, then serializes the *delta* as repo **plan JSON** — the additive format
consumed by the ``manage_context_definition`` CCI task and linted by
``validate_context_plan.py``. It **never mutates an org**: it only writes (or
prints) a patch file for you to review, lint, and apply yourself.

NOT a Salesforce-native feature
-------------------------------
"Context plan patch" is **repo tooling, not a platform capability.** Salesforce
has no diff/patch primitive for Context Definitions and no context *import*
format. This script is our logic layered on standard platform primitives: it
*reads* via the standard Connect / SObject-REST APIs, and a patch *applies*
(when you run it) via those same APIs through our CCI task — but the diff, the
patch concept, and the plan-JSON format are all homegrown. Consequences:

* A patch is only as correct as our normalizer (``_model.py``) and serializer —
  there is no platform round-trip guarantee. That is why the workflow routes
  every patch through ``validate_context_plan.py`` (also ours) before applying,
  and why CONTEXT-to-CONTEXT / traversal reversals are *flagged* (``_caveats`` /
  ``_todo``), not silently emitted.
* The one platform-native reconciliation is ``upgradeMode: Preview`` on
  ``connect/context-definitions/upgrades`` — but that only reconciles an
  *extended* definition against its *standard base* across a release. It cannot
  diff two arbitrary orgs or an org against a repo plan, which is what this does.

Why plan JSON (not Connect payloads or MDAPI ``.contextDefinition``)?
---------------------------------------------------------------------
* **Connect/SObject REST** is the *runtime apply* path — but it lives inside the
  CCI task (``tasks/rlm_context_service.py``), which owns idempotency, dry-run,
  traversal hydration, and verification. Re-authoring that write orchestration
  standalone would fork 1,600+ lines and needs ``access_token`` handling the
  repo forbids on the ``sf`` CLI. So the patch targets the task's *input*
  (plan JSON), not the wire protocol.
* **MDAPI ``.contextDefinition``** deploys a definition as **one atomic unit**
  (no ``childXmlNames``); it cannot express "add just these N artifacts" and
  cannot set activation / default mapping. A plan-JSON delta is the granular,
  applicable-anywhere artifact.

So a patch **round-trips**: ``patch_context.py`` -> ``validate_context_plan.py``
-> ``cci task run manage_context_definition``.

Three directions (each makes a **target** match a **source**)
-------------------------------------------------------------
``--plan-file P --target-org O``               plan is truth; patch brings the org
    (default ``--apply-to org``)               up to the plan.
``--source-org A --target-org B``              source org A is truth; patch makes
                                               target B match A.
``--plan-file P --target-org O --apply-to plan``  org is truth; patch folds the org's
                                               custom state back into the repo plan.

In every direction the **source is truth** and the **target is what the emitted
patch would bring into line** (source-org / plan on the left, target-org on the
right — matching ``diff_context.py``).

v1 scope — **adds & updates only.** The plan format and ``manage_context_definition``
are additive (no per-artifact delete directive), so artifacts present in the
*target* but absent from the *source* (candidate deletions) are **reported, not
emitted**. Removing them is a manual unlink/deactivate step — a documented
followup. Nothing here ever deletes.

Auth is delegated to the sf CLI (see _client.py) — no tokens handled here.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._client import ContextClientError  # noqa: E402
from scripts.context_service._model import model_to_plan  # noqa: E402
from scripts.context_service.definition.diff_context import (  # noqa: E402
    _definition_index,
    _fetch_model,
    _load_plan_models,
    diff_models,
)


def _delta_keys(section: dict) -> set:
    """Keys to emit from the *source* for one diff section: source-only + changed.

    ``diff_models(source, target)`` labels ``removed`` = keys only in the source
    (left) and ``changed`` = keys differing between the two. Both must be applied
    to the target to make it match the source. ``added`` (target-only) is a
    candidate deletion — excluded here (see the module docstring, v1 scope).
    """
    keys = set(section.get("removed") or [])
    for ch in section.get("changed") or []:
        keys.add(ch["key"])
    return keys


def _is_custom(name: str) -> bool:
    """Custom artifacts carry the ``__c`` suffix; inherited standard ones do not."""
    return bool(name) and name.endswith("__c")


def _filter_custom_keys(category: str, keys: set) -> set:
    """Keep only custom (``__c``) artifacts — used when folding org state into a plan.

    The repo plan should carry only the *custom* layer added onto a standard
    base, never the inherited standard artifacts. The relevant name is the last
    dotted/slashed segment: ``node.attr`` -> ``attr``, ``mapping/node/attr`` ->
    ``attr``, ``node.tag`` -> ``tag``, node -> the node name itself.
    """
    kept = set()
    for key in keys:
        if category == "mappings":
            name = key.rsplit("/", 1)[-1]
        elif category in ("attributes", "tags"):
            name = key.rsplit(".", 1)[-1]
        else:  # nodes
            name = key
        if _is_custom(name):
            kept.add(key)
    return kept


def _build_include(diff: dict, custom_only: bool) -> dict:
    """Turn a per-definition diff into the ``include`` filter for ``model_to_plan``."""
    include = {}
    for category in ("nodes", "attributes", "mappings", "tags"):
        keys = _delta_keys(diff.get(category, {}))
        if custom_only:
            keys = _filter_custom_keys(category, keys)
        include[category] = keys
    return include


def _candidate_deletions(diff: dict, custom_only: bool) -> dict:
    """Target-only artifacts (``added``) — reported, never emitted (v1)."""
    out = {}
    for category in ("nodes", "attributes", "mappings", "tags"):
        keys = set(diff.get(category, {}).get("added") or [])
        if custom_only:
            keys = _filter_custom_keys(category, keys)
        if keys:
            out[category] = sorted(keys)
    return out


def _has_delta(include: dict) -> bool:
    return any(include.get(cat) for cat in ("nodes", "attributes", "mappings", "tags"))


def _emit_patch(source_model: dict, diff: dict, custom_only: bool,
                source_is_full: bool) -> dict:
    """Serialize the source-side delta as a plan-JSON patch (+ metadata).

    ``source_is_full`` gates the candidate-deletions report: it is only
    meaningful when the *source* is a full definition (an org). When the source
    is an additive repo plan (plan-vs-org, ``--apply-to org``), target-only
    artifacts are the org's **inherited base**, not deletions — so the report is
    suppressed to avoid thousands of false "deletion" lines.
    """
    include = _build_include(diff, custom_only)
    plan = model_to_plan(source_model, include=include)
    caveats = plan.pop("_caveats", [])
    return {
        "plan": plan,
        "hasDelta": _has_delta(include),
        "caveats": caveats,
        "candidateDeletions": (
            _candidate_deletions(diff, custom_only) if source_is_full else {}
        ),
    }


# ---- rendering -------------------------------------------------------------

def _render_summary(name: str, patch: dict, lines: list):
    plan = patch["plan"]
    counts = {
        "nodes": len(plan.get("contextNodeDefinitions") or []),
        "attributes": len(plan.get("contextAttributesByName") or []),
        "mappingRules": len(plan.get("mappingRules") or []),
        "tags": len(plan.get("contextTagsByName") or []),
    }
    parts = ", ".join(f"{v} {k}" for k, v in counts.items() if v)
    lines.append(f"  {name}: {parts or 'no additive delta'}")
    for cav in patch["caveats"]:
        lines.append(f"    ! caveat: {cav}")
    dels = patch["candidateDeletions"]
    if dels:
        total = sum(len(v) for v in dels.values())
        lines.append(
            f"    ~ {total} target-only artifact(s) NOT in this patch "
            f"(candidate deletions — manual unlink, see docs): "
            f"{ {k: v for k, v in dels.items()} }"
        )


# ---- main ------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract a Context Definition diff into an applicable plan-JSON patch "
        "(read-only; never mutates an org).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username for the org the patch would bring into line "
        "(NOT the CCI alias). In plan-vs-org mode this is the org compared to the "
        "plan.",
    )
    parser.add_argument(
        "--source-org",
        help="SF CLI alias/username for the source-of-truth org — enables "
        "org-vs-org mode (the patch makes --target-org match --source-org).",
    )
    parser.add_argument(
        "--plan-file",
        help="Plan manifest.json — enables plan-vs-org mode.",
    )
    parser.add_argument(
        "--apply-to", choices=("org", "plan"), default="org",
        help="plan-vs-org direction: 'org' (default; plan is truth, patch updates the "
        "org) or 'plan' (org is truth, fold the org's custom state into the plan).",
    )
    parser.add_argument(
        "--developer-name",
        help="Scope to one definition (org-vs-org only; both orgs must share the "
        "developerName).",
    )
    parser.add_argument(
        "--include-inherited", action="store_true",
        help="When --apply-to plan, also emit inherited (non-__c) artifacts. "
        "Default keeps only the custom (__c) layer the repo plan should own.",
    )
    parser.add_argument(
        "--out",
        help="Write the patch here (per-definition file if multiple). Default: stdout JSON.",
    )
    parser.add_argument("--api-version", default="67.0", help="API version (default 67.0).")
    args = parser.parse_args(argv)

    if bool(args.source_org) == bool(args.plan_file):
        parser.error("choose exactly one mode: --source-org (org-vs-org) OR "
                     "--plan-file (plan-vs-org).")
    if args.source_org and args.apply_to == "plan":
        parser.error("--apply-to plan is only valid in plan-vs-org mode.")

    try:
        # Build {developerName: (source_model, target_model, custom_only,
        # source_is_full)} so each definition serializes from its source (the
        # side that is "truth"). ``source_is_full`` is True when the source is a
        # full org definition (candidate deletions are meaningful), False when it
        # is an additive repo plan (target-only artifacts are inherited base).
        entries = {}
        if args.plan_file:
            plan_path = Path(args.plan_file).resolve()
            if not plan_path.is_file():
                print(f"Error: plan file not found: {args.plan_file}", file=sys.stderr)
                return 1
            plan_models = _load_plan_models(plan_path)
            if not plan_models:
                print("Error: plan declared no definitions (no developerName).",
                      file=sys.stderr)
                return 1
            target_index = _definition_index(args.target_org, args.api_version)
            for name, plan_model in plan_models.items():
                org_model = _fetch_model(name, args.target_org, args.api_version,
                                         index=target_index)
                if args.apply_to == "org":
                    # plan is truth -> patch updates the org. Source is a plan.
                    entries[name] = (plan_model, org_model or {}, False, False)
                else:
                    # org is truth -> fold the org's custom state into the plan.
                    entries[name] = (
                        org_model or {}, plan_model, not args.include_inherited, True
                    )
        else:
            source_index = _definition_index(args.source_org, args.api_version)
            target_index = _definition_index(args.target_org, args.api_version)
            names = ([args.developer_name] if args.developer_name
                     else sorted(set(source_index) | set(target_index)))
            for name in names:
                source = _fetch_model(name, args.source_org, args.api_version,
                                      index=source_index)
                target = _fetch_model(name, args.target_org, args.api_version,
                                      index=target_index)
                # source org is truth -> patch makes the target match it. Source
                # is a full org (candidate deletions are meaningful).
                entries[name] = (source or {}, target or {}, False, True)
    except ContextClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    patches = {}
    for name, (source, target, custom_only, source_is_full) in entries.items():
        diff = diff_models(source, target)
        patch = _emit_patch(source, diff, custom_only, source_is_full)
        # Emit a patch entry only when there is an additive delta OR a caveat /
        # candidate-deletion worth surfacing.
        if patch["hasDelta"] or patch["caveats"] or patch["candidateDeletions"]:
            patches[name] = patch

    if not patches:
        print("No additive delta — nothing to patch.")
        return 0

    if args.out:
        _write_patches(patches, Path(args.out))
    else:
        # stdout: emit just the apply-ready plan(s); metadata to stderr.
        plans = [p["plan"] for p in patches.values()]
        payload = plans[0] if len(plans) == 1 else {
            "contexts": [{**p} for p in plans]
        }
        print(json.dumps(payload, indent=2))

    lines = ["\nPatch summary (read-only; nothing applied):"]
    for name in sorted(patches):
        _render_summary(name, patches[name], lines)
    lines.append(
        "\nNext: lint with `python scripts/context_service/definition/validate_context_plan.py <file>`, "
        "then apply with `cci task run manage_context_definition` (see the "
        "context-service skill). Candidate deletions require a manual unlink."
    )
    print("\n".join(lines), file=sys.stderr)
    return 0


def _write_patches(patches: dict, out_path: Path):
    """Write apply-ready plan JSON. Single definition -> the file; multiple ->
    a manifest-style ``contexts`` wrapper at ``out_path``."""
    if len(patches) == 1:
        plan = next(iter(patches.values()))["plan"]
        out_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote patch: {out_path}", file=sys.stderr)
        return
    wrapper = {"contexts": [p["plan"] for p in patches.values()]}
    out_path.write_text(json.dumps(wrapper, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(patches)} definition patches: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
