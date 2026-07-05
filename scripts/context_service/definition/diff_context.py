#!/usr/bin/env python3
"""Diff Context Definitions (read-only) — the drift tool.

Two modes (the **target org is always the examined/right side**; the baseline is
the source org or the plan on the left):

  * **org-vs-org** — compare a definition (or all definitions) between two orgs:
        --source-org BASELINE --target-org EXAMINED [--developer-name NAME]
    Same-named defs compare by name; to compare **differently-named** defs across
    the two orgs, scope each side explicitly:
        --source-org A --source-dev-name RLM_FooContext \
        --target-org B --target-dev-name RLM_BarContext
  * **plan-vs-org** — compare a repo plan manifest against what an org actually
    has (directional drift check):
        --target-org EXAMINED --plan-file datasets/context_plans/<Name>/manifest.json

Both normalize each side through ``_model.normalize_definition`` /
``normalize_plan`` and report added / removed / changed for nodes, attributes,
mappings, hydration, and tags. Output is human-readable by default; ``--json``
emits the structured diff.

Auth is delegated to the sf CLI (see _client.py) — no tokens are handled here.
The GET response shape is pinned to Release 262 / API v67.0.

Caveats
-------
* **plan-vs-org is directional.** Repo plans are *additive* — they declare only
  what they add onto a standard/extended base. So "in org, not in plan" is
  usually an **inherited** artifact, not drift; "in plan, not in org" is the
  real signal that the plan has not been applied (or drifted). The report labels
  the two directions and does not treat inherited org artifacts as errors.
* **CONTEXT-to-CONTEXT sources** are compared on their SObject + hydration hop
  only; the CONTEXT reference itself is **excluded from equality**. The org side
  carries a raw ``mappedContextDefinitionId`` (an ``11O…`` ID) and the plan side
  a ``mappedContextDefinitionName`` (a developerName, usually empty because repo
  rules author ``sourceContextNode``/``sourceContextAttribute`` instead), which
  can never compare equal — so including it flagged every CONTEXT mapping as
  perpetually changed. It is retained for display on a row that changed for a
  real reason. **Limitation:** because neither normalizer captures
  ``sourceContextNode`` / ``sourceContextAttribute``, a *changed* CONTEXT source
  is not detected — only its presence/absence. Confirm CONTEXT sources with
  ``describe_context``.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.context_service._client import (  # noqa: E402
    ContextClientError,
    connect_get,
    definition_developer_name,
    normalize_definition_list,
)
from scripts.context_service._model import normalize_definition, normalize_plan  # noqa: E402


# ---- fetch helpers ---------------------------------------------------------

def _definition_index(target_org: str, api_version: str) -> dict:
    """GET the definition collection once → ``{developerName: contextDefinitionId}``.

    Callers that resolve more than one definition against the same org should
    fetch this once and reuse it, rather than re-listing the whole collection per
    definition (the per-call list GET is the dominant cost of an all-definitions
    diff).
    """
    response = connect_get(
        "connect/context-definitions?includeInactive=true", target_org, api_version
    )
    index = {}
    for item in normalize_definition_list(response):
        name = definition_developer_name(item)
        ctx_id = item.get("contextDefinitionId")
        if name and ctx_id:
            index[name] = ctx_id
    return index


def _list_developer_names(target_org: str, api_version: str) -> list:
    return sorted(_definition_index(target_org, api_version))


def _fetch_model(developer_name: str, target_org: str, api_version: str, index: dict = None):
    """GET one definition by developerName and return its normalized model.

    Pass ``index`` (from :func:`_definition_index`) to skip the collection GET
    when resolving several definitions against the same org; omit it for a
    one-shot lookup and the collection is fetched inline.

    Returns None when the definition does not exist in the org (so the diff can
    report it as removed/added rather than crashing).
    """
    if index is None:
        index = _definition_index(target_org, api_version)
    ctx_id = index.get(developer_name)
    if not ctx_id:
        return None
    defn = connect_get(
        f"connect/context-definitions/{ctx_id}", target_org, api_version
    )
    if isinstance(defn, list):
        defn = defn[0] if defn and isinstance(defn[0], dict) else {}
    if not isinstance(defn, dict) or not defn:
        return None
    return normalize_definition(defn)


# ---- diff engine -----------------------------------------------------------

def _diff_dicts(left: dict, right: dict, compare=None):
    """Return (added, removed, changed) for two name->value dicts.

    ``added`` = keys only in ``right`` (the second/target side).
    ``removed`` = keys only in ``left`` (the first/baseline side).
    ``changed`` = keys in both whose values differ (per ``compare`` or ``==``).
    """
    left = left or {}
    right = right or {}
    lkeys, rkeys = set(left), set(right)
    added = sorted(rkeys - lkeys)
    removed = sorted(lkeys - rkeys)
    changed = []
    for key in sorted(lkeys & rkeys):
        lv, rv = left[key], right[key]
        differs = (lv != rv) if compare is None else compare(lv, rv)
        if differs:
            changed.append({"key": key, "left": lv, "right": rv})
    return added, removed, changed


def _flatten_mapping_attrs(mappings: dict) -> dict:
    """Flatten a mappings tree to ``mapping/node/attr -> {sObject,hydration,ref}``.

    Comparing at the attribute-mapping grain is what surfaces the ramp-mode
    signal (an sObject/hydration present on one side, absent on the other).

    ``input`` (the GET's ``contextInputAttributeName``) is deliberately excluded:
    it is an internal context-input-attribute name that repo plans do not model,
    so including it would flag every plan-vs-org mapping as "changed". The
    hydration hop (``Object.field``) carries the field mapping both sides share.

    ``mappedContextDefinitionId`` is carried for **display only** (so a changed
    row can show the CONTEXT ref) but is deliberately **excluded from equality**
    by :func:`_mapping_attr_differs` — see that function for why the plan-side
    name and org-side ID can never be compared directly.
    """
    flat = {}
    for mname, mapping in (mappings or {}).items():
        for node_name, node_map in (mapping.get("nodes") or {}).items():
            sobj = node_map.get("sObject")
            for attr_name, attr_map in (node_map.get("attributes") or {}).items():
                flat[f"{mname}/{node_name}/{attr_name}"] = {
                    "sObject": sobj,
                    "hydration": attr_map.get("hydration") or [],
                    "mappedContextDefinitionId": attr_map.get(
                        "mappedContextDefinitionId"
                    ),
                }
    return flat


def _mapping_attr_differs(left: dict, right: dict) -> bool:
    """Equality for a flattened attribute-mapping row, excluding the CONTEXT ref.

    ``mappedContextDefinitionId`` is **not** comparable across the two sides:

    * the **plan** side stores ``mappedContextDefinitionName`` (a developerName,
      and in practice ``None`` — repo CONTEXT rules author
      ``sourceContextNode``/``sourceContextAttribute`` and leave the name slot
      empty), while
    * the **org** side stores the raw ``11O…``-prefixed ``ContextDefinition`` ID.

    A ``name`` (or ``None``) vs an org-scoped ID never satisfy ``==``, so
    including this field flagged **every** CONTEXT mapping as ``~ changed`` on
    every run — permanent, non-convergent drift. Resolving the org ID back to a
    developerName would not help the dominant plan-vs-org case (the plan side is
    ``None``), so the field is excluded from equality entirely; the SObject and
    hydration hop — which both sides model faithfully — are what the mapping diff
    compares on.

    Known limitation: ``sourceContextNode`` / ``sourceContextAttribute`` (the
    fields that actually define a CONTEXT source) are not captured by either
    normalizer, so a *changed* CONTEXT source is not detected here — only its
    presence/absence (via added/removed). See P6 in the follow-up plan.
    """
    left = left or {}
    right = right or {}
    return (left.get("sObject"), left.get("hydration") or []) != (
        right.get("sObject"), right.get("hydration") or []
    )


def diff_models(left: dict, right: dict) -> dict:
    """Full structured diff of two normalized models (or None for absent side)."""
    if left is None and right is None:
        return {"present": {"left": False, "right": False}}
    left = left or {}
    right = right or {}

    n_added, n_removed, n_changed = _diff_dicts(
        left.get("nodes"), right.get("nodes"),
        # depth is informational and differs plan(None) vs org(int); compare parent only.
        compare=lambda a, b: (a or {}).get("parent") != (b or {}).get("parent"),
    )
    a_added, a_removed, a_changed = _diff_dicts(
        left.get("attributes"), right.get("attributes")
    )
    m_added, m_removed, m_changed = _diff_dicts(
        _flatten_mapping_attrs(left.get("mappings")),
        _flatten_mapping_attrs(right.get("mappings")),
        # CONTEXT mappings carry a name (plan) vs org-scoped ID (org) that can
        # never compare equal; exclude it from equality (compare sObject +
        # hydration only) so a CONTEXT mapping no longer reports perpetual drift.
        compare=_mapping_attr_differs,
    )
    t_added, t_removed, t_changed = _diff_dicts(left.get("tags"), right.get("tags"))

    return {
        "present": {"left": bool(left), "right": bool(right)},
        "developerName": right.get("developerName") or left.get("developerName"),
        "isActive": {"left": left.get("isActive"), "right": right.get("isActive")},
        "nodes": {"added": n_added, "removed": n_removed, "changed": n_changed},
        "attributes": {"added": a_added, "removed": a_removed, "changed": a_changed},
        "mappings": {"added": m_added, "removed": m_removed, "changed": m_changed},
        "tags": {"added": t_added, "removed": t_removed, "changed": t_changed},
    }


def _has_changes(d: dict) -> bool:
    for section in ("nodes", "attributes", "mappings", "tags"):
        s = d.get(section) or {}
        if s.get("added") or s.get("removed") or s.get("changed"):
            return True
    if d.get("isActive", {}).get("left") != d.get("isActive", {}).get("right"):
        return True
    if not d.get("present", {}).get("left") or not d.get("present", {}).get("right"):
        return True
    return False


# ---- plan loading ----------------------------------------------------------

def _load_plan_models(manifest_path: Path) -> dict:
    """Resolve a plan manifest to {developerName: normalized-plan-model}.

    Mirrors validate_context_plan's manifest -> plan-file merge so multiple
    contexts (or an inline plan) all normalize consistently.
    """
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    models = {}

    def _add(plan_obj: dict):
        model = normalize_plan(plan_obj)
        name = model.get("developerName")
        if name:
            # A repo splits one definition across multiple plans (e.g. RampMode
            # + ConstraintEngineNodeStatus both target RLM_SalesTransactionContext);
            # merge their artifacts so the org diff sees the union.
            if name in models:
                _merge_models(models[name], model)
            else:
                models[name] = model

    contexts = manifest.get("contexts") if isinstance(manifest, dict) else None
    if not isinstance(contexts, list) or not contexts:
        _add(manifest)
        return models

    for entry in contexts:
        if not isinstance(entry, dict):
            continue
        plan_file = entry.get("planFile")
        if not plan_file:
            _add(entry)
            continue
        plan_path = manifest_path.parent / plan_file
        with open(plan_path, "r", encoding="utf-8") as handle:
            plan_obj = json.load(handle)
        merged = {**plan_obj, **{k: v for k, v in entry.items() if k != "planFile"}}
        _add(merged)
    return models


def _merge_models(base: dict, extra: dict):
    for key in ("nodes", "attributes", "tags"):
        base[key].update(extra.get(key) or {})
    for mname, mapping in (extra.get("mappings") or {}).items():
        if mname not in base["mappings"]:
            base["mappings"][mname] = mapping
            continue
        base["mappings"][mname]["isDefault"] = (
            base["mappings"][mname]["isDefault"] or mapping.get("isDefault")
        )
        for node_name, node_map in (mapping.get("nodes") or {}).items():
            dest = base["mappings"][mname]["nodes"].setdefault(
                node_name, {"sObject": node_map.get("sObject"), "attributes": {}}
            )
            dest["attributes"].update(node_map.get("attributes") or {})


# ---- rendering -------------------------------------------------------------

def _render_section(title: str, section: dict, left_label: str, right_label: str,
                    lines: list):
    added = section.get("added") or []
    removed = section.get("removed") or []
    changed = section.get("changed") or []
    if not (added or removed or changed):
        return
    lines.append(f"  {title}:")
    for key in added:
        lines.append(f"    + {key}  (only in {right_label})")
    for key in removed:
        lines.append(f"    - {key}  (only in {left_label})")
    for ch in changed:
        lines.append(f"    ~ {ch['key']}")
        lines.append(f"        {left_label}: {ch['left']}")
        lines.append(f"        {right_label}: {ch['right']}")


def _render_human(diffs: dict, left_label: str, right_label: str,
                  plan_mode: bool) -> str:
    lines = []
    any_changes = False
    for name in sorted(diffs):
        d = diffs[name]
        if not _has_changes(d):
            continue
        any_changes = True
        lines.append(f"\n=== {name} ===")
        present = d.get("present", {})
        if not present.get("left"):
            lines.append(f"  (absent in {left_label})")
        if not present.get("right"):
            lines.append(f"  (absent in {right_label})")
        act = d.get("isActive", {})
        if act.get("left") != act.get("right"):
            lines.append(f"  isActive: {left_label}={act.get('left')} "
                         f"{right_label}={act.get('right')}")
        for title, key in (
            ("Nodes", "nodes"), ("Attributes", "attributes"),
            ("Mappings", "mappings"), ("Tags", "tags"),
        ):
            _render_section(title, d.get(key, {}), left_label, right_label, lines)

    if not any_changes:
        return "No differences."
    if plan_mode:
        lines.append(
            f"\nNote: plan-vs-org is directional. '+ (only in {right_label})' "
            f"items are usually INHERITED from the standard/extended base, not "
            f"drift. '- (only in {left_label})' items are plan artifacts the org "
            f"is missing — the real drift signal."
        )
    return "\n".join(lines)


# ---- main ------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Diff Context Definitions (read-only).")
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username for the examined org — the right side of the "
        "diff (NOT the CCI alias). In plan-vs-org mode this is the org checked "
        "against the plan.",
    )
    parser.add_argument(
        "--source-org",
        help="SF CLI alias/username for the baseline org (left side) — enables "
        "org-vs-org mode.",
    )
    parser.add_argument(
        "--plan-file",
        help="Plan manifest.json — enables plan-vs-org mode (vs --target-org).",
    )
    parser.add_argument(
        "--developer-name",
        help="Scope to one definition. Applies to BOTH sides in org-vs-org mode "
        "(same name each org); plan-vs-org uses the plan's own definitions. "
        "For differently-named defs, use --source-dev-name / --target-dev-name.",
    )
    parser.add_argument(
        "--source-dev-name",
        help="developerName on the SOURCE org when it differs from the target's "
        "(org-vs-org only). Pair with --target-dev-name.",
    )
    parser.add_argument(
        "--target-dev-name",
        help="developerName on the TARGET org when it differs from the source's "
        "(org-vs-org only). Pair with --source-dev-name.",
    )
    parser.add_argument("--api-version", default="67.0", help="API version (default 67.0).")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    args = parser.parse_args(argv)

    if bool(args.source_org) == bool(args.plan_file):
        parser.error("choose exactly one mode: --source-org (org-vs-org) OR "
                     "--plan-file (plan-vs-org).")
    if (args.source_dev_name or args.target_dev_name):
        if args.plan_file:
            parser.error("--source-dev-name / --target-dev-name apply to "
                         "org-vs-org mode only (not with --plan-file).")
        if bool(args.source_dev_name) != bool(args.target_dev_name):
            parser.error("--source-dev-name and --target-dev-name must be used "
                         "together (one name per org).")
        if args.developer_name:
            parser.error("use EITHER --developer-name (same name both orgs) OR the "
                         "--source-dev-name/--target-dev-name pair, not both.")

    try:
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
            diffs = {}
            target_index = _definition_index(args.target_org, args.api_version)
            for name, plan_model in plan_models.items():
                org_model = _fetch_model(name, args.target_org, args.api_version,
                                         index=target_index)
                diffs[name] = diff_models(plan_model, org_model)
            left_label, right_label = "plan", f"org:{args.target_org}"
            plan_mode = True
        elif args.source_dev_name:
            # Mismatched developer names: one paired comparison, source(left)
            # vs target(right), keyed by a combined "src -> tgt" label.
            left = _fetch_model(args.source_dev_name, args.source_org, args.api_version)
            right = _fetch_model(args.target_dev_name, args.target_org, args.api_version)
            key = f"{args.source_dev_name} -> {args.target_dev_name}"
            diffs = {key: diff_models(left, right)}
            left_label = f"org:{args.source_org}:{args.source_dev_name}"
            right_label = f"org:{args.target_org}:{args.target_dev_name}"
            plan_mode = False
        else:
            src_index = _definition_index(args.source_org, args.api_version)
            tgt_index = _definition_index(args.target_org, args.api_version)
            if args.developer_name:
                names = [args.developer_name]
            else:
                names = sorted(set(src_index) | set(tgt_index))
            diffs = {}
            for name in names:
                left = _fetch_model(name, args.source_org, args.api_version, index=src_index)
                right = _fetch_model(name, args.target_org, args.api_version, index=tgt_index)
                diffs[name] = diff_models(left, right)
            left_label = f"org:{args.source_org}"
            right_label = f"org:{args.target_org}"
            plan_mode = False
    except ContextClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        # Prune unchanged definitions for a focused machine payload.
        payload = {n: d for n, d in diffs.items() if _has_changes(d)}
        print(json.dumps({
            "left": left_label, "right": right_label, "definitions": payload,
        }, indent=2))
        return 0

    print(_render_human(diffs, left_label, right_label, plan_mode))
    return 0


if __name__ == "__main__":
    sys.exit(main())
