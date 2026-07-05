#!/usr/bin/env python3
"""Offline linter for Revenue Cloud Context Service *plan JSON* files.

This validates this repo's context **plan** format (the JSON consumed by
``manage_context_definition`` / ``ExtendStandardContext`` under
``datasets/context_plans/``) — NOT the MDAPI ``.contextDefinition`` file format
under ``force-app/main/default/contextDefinitions/``.

It is a static, offline check (no org, no network), modeled on
``scripts/validate_sfdmu_v5_datasets.py`` (offline validator) and
``scripts/ai/query_erd.py`` (describe/inspect CLI). See the context-service
skill (``.cursor/skills/context-service/SKILL.md``) for the grounding.

Checks performed
----------------
- JSON well-formedness of the manifest and every referenced plan file.
- manifest -> plan-file resolution (``contexts[].planFile`` exists and parses).
- Canonical ``dataType`` / ``fieldType`` enum values (Core UDD, API v67.0).
- Required keys on attributes, nodes, mapping rules, and tags.
- ``mappingType`` in {SOBJECT, CONTEXT} with the matching required keys.
- Guardrail limits (nodes, attrs/node, total attrs, hierarchy depth) against
  the counts *declared in the plan* (offline cannot see inherited org-side counts).
- ``primaryDomainObject`` / ``primaryObject`` present -> ERROR (JSON_PARSER_ERROR
  on the create endpoint; the task strips them).
- ``__c`` suffix on custom artifact names created against a standard/extended
  base (ERROR); for create-new custom definitions (``create: true``) the suffix
  check is skipped entirely — their names are wholly author-chosen and collide
  with nothing inherited, so ``__c`` is not required.
- Distinct referenced context definitions (<= 2, ERROR). Tags per node has a
  recommended guideline (<= 10) surfaced as INFO only — a shipped plan exceeds
  it and works, so it never fails the build.
- All-traversal mapping rules -> informational note (handled via SObject REST).

Usage
-----
    # canonical: validate the active (non-archive) plans
    python scripts/context_service/validate_context_plan.py \
        datasets/context_plans/{Billing,ConstraintEngineNodeStatus,DocGen,PartnerAccount,PrmPricing,RampMode}/manifest.json

    # or discover all active manifests (skips archive/ unless --include-archive)
    python scripts/context_service/validate_context_plan.py
    python scripts/context_service/validate_context_plan.py --include-archive
    python scripts/context_service/validate_context_plan.py --strict   # warnings fail too

Exit code: non-zero if any ERROR is found (or any warning under --strict).
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# definition/validate_context_plan.py → context_service → scripts → <repo root>
REPO_ROOT = Path(__file__).resolve().parents[3]
CONTEXT_PLANS_DIR = REPO_ROOT / "datasets" / "context_plans"

# Canonical Core enums (UDD, API v67.0). The file-based .contextDefinition format
# / internal validator uses a slightly different allow-list (e.g. INTEGER,
# lowercase intents); the Connect-API plan format uses the values below.
VALID_DATA_TYPES = {
    "STRING", "NUMBER", "BOOLEAN", "DATE", "DATETIME", "PERCENT", "PICKLIST",
    "CURRENCY", "REFERENCE", "DOUBLE", "INT", "MAP", "SELFREFERENCE", "LOOKUP",
}
VALID_FIELD_TYPES = {"INPUT", "INPUTOUTPUT", "OUTPUT", "AGGREGATE"}
VALID_MAPPING_TYPES = {"SOBJECT", "CONTEXT"}

# Guardrail limits — strict validator numbers ("Shweta rules"); Salesforce Help
# quotes higher ceilings for some (nodes up to 50, total attrs up to 1000). We
# lint against the strict numbers and note the discrepancy in the skill.
LIMIT_NODES = 30
LIMIT_ATTRS_PER_NODE = 50
LIMIT_TOTAL_ATTRS = 250
LIMIT_HIERARCHY_DEPTH = 5
# Tags-per-node is a *guideline*, not an enforced ceiling: a shipped plan
# (DocGen) exceeds it and works — so exceeding it is INFO, never ERROR.
TAGS_PER_NODE_GUIDELINE = 10
LIMIT_REFERENCED_DEFINITIONS = 2

# Suffixes that are legitimately NOT __c on a custom attribute name:
#   __std  -> a standard/inherited attribute referenced by the plan
_STANDARD_SUFFIXES = ("__std", "__stdctx")


class Severity(Enum):
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"


@dataclass
class Issue:
    severity: Severity
    message: str
    location: str = ""


@dataclass
class PlanResult:
    path: str
    issues: List[Issue] = field(default_factory=list)

    def add(self, severity: Severity, message: str, location: str = ""):
        self.issues.append(Issue(severity, message, location))

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity is Severity.WARN]


class _LoadError:
    """Sentinel wrapper for a JSON-load failure (file access or parse error)."""

    def __init__(self, message: str):
        self.message = message


def _load_json(path: Path):
    """Load JSON from ``path``; on any failure return a ``_LoadError`` (never raise).

    Covers parse errors and every filesystem error (missing file, a directory,
    a permission problem) so the linter always emits a structured [FAIL] line
    instead of an uncaught traceback.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        return _LoadError(f"is not valid JSON: {exc}")
    except OSError as exc:
        return _LoadError(str(exc))


def _is_create_new(plan: Dict[str, Any]) -> bool:
    """A plan that creates a brand-new custom definition (create: true) rather
    than extending an existing standard/extended base."""
    return str(plan.get("create", "")).lower() in {"1", "true", "yes"}


def _needs_c_suffix(name: str) -> bool:
    """True if a custom artifact name should carry a __c suffix but does not."""
    if not name:
        return False
    if name.endswith("__c"):
        return False
    if name.endswith(_STANDARD_SUFFIXES):
        return False
    return True


def _validate_attributes(plan: Dict[str, Any], result: PlanResult, loc: str):
    attrs = plan.get("contextAttributesByName")
    if attrs is None:
        return
    if not isinstance(attrs, list):
        result.add(Severity.ERROR, "contextAttributesByName must be a list", loc)
        return

    # The __c convention applies to custom artifacts added to a standard/extended
    # base (to distinguish them from inherited standard names). Create-new custom
    # definitions have wholly author-chosen names that collide with nothing
    # inherited, so the suffix check does not apply to them.
    check_suffix = not _is_create_new(plan)
    attrs_per_node: Dict[str, int] = {}

    for i, attr in enumerate(attrs):
        aloc = f"{loc} contextAttributesByName[{i}]"
        if not isinstance(attr, dict):
            result.add(Severity.ERROR, "attribute entry must be an object", aloc)
            continue
        node_name = attr.get("nodeName")
        name = attr.get("name")
        if not node_name:
            result.add(Severity.ERROR, "attribute missing required 'nodeName'", aloc)
        if not name:
            result.add(Severity.ERROR, "attribute missing required 'name'", aloc)
        if node_name:
            attrs_per_node[node_name] = attrs_per_node.get(node_name, 0) + 1

        data_type = attr.get("dataType", "STRING")
        if data_type not in VALID_DATA_TYPES:
            result.add(
                Severity.ERROR,
                f"invalid dataType '{data_type}' (expected one of {sorted(VALID_DATA_TYPES)})",
                aloc,
            )
        field_type = attr.get("fieldType", "INPUTOUTPUT")
        if field_type not in VALID_FIELD_TYPES:
            result.add(
                Severity.ERROR,
                f"invalid fieldType '{field_type}' (expected one of {sorted(VALID_FIELD_TYPES)})",
                aloc,
            )
        if check_suffix and name and _needs_c_suffix(name):
            result.add(
                Severity.ERROR,
                f"custom attribute name '{name}' should end with '__c' "
                f"(added to a standard/extended base)",
                aloc,
            )

    for node_name, count in attrs_per_node.items():
        if count > LIMIT_ATTRS_PER_NODE:
            result.add(
                Severity.ERROR,
                f"node '{node_name}' declares {count} attributes (plan-declared) "
                f"exceeding the per-node limit of {LIMIT_ATTRS_PER_NODE}",
                loc,
            )
    total = len(attrs)
    if total > LIMIT_TOTAL_ATTRS:
        result.add(
            Severity.ERROR,
            f"plan declares {total} attributes exceeding the total limit of {LIMIT_TOTAL_ATTRS}",
            loc,
        )


def _node_depth(node_defs: List[Dict[str, Any]]) -> int:
    """Compute hierarchy depth from parentNodeName references (create-new plans)."""
    by_name = {n.get("name"): n for n in node_defs if isinstance(n, dict) and n.get("name")}
    max_depth = 0
    for node in node_defs:
        if not isinstance(node, dict):
            continue
        depth = 1
        seen = set()
        cur = node
        while cur is not None:
            name = cur.get("name")
            if name in seen:  # cycle guard
                break
            seen.add(name)
            parent = cur.get("parentNodeName")
            if not parent:
                break
            parent_node = by_name.get(parent)
            if parent_node is None:
                # Parent is not declared in this plan (inherited from the base):
                # it does not add an in-plan hierarchy level, so stop here
                # without counting the missing hop.
                break
            cur = parent_node
            depth += 1
        max_depth = max(max_depth, depth)
    return max_depth


def _validate_nodes(plan: Dict[str, Any], result: PlanResult, loc: str):
    node_defs = plan.get("contextNodeDefinitions")
    if node_defs is None:
        return
    if not isinstance(node_defs, list):
        result.add(Severity.ERROR, "contextNodeDefinitions must be a list", loc)
        return

    # Node names on create-new definitions are author-chosen (e.g. Quote, Line)
    # and are not expected to carry __c; only enforce the suffix when adding
    # nodes to a standard/extended base.
    check_suffix = not _is_create_new(plan)

    names = set()
    for i, node in enumerate(node_defs):
        nloc = f"{loc} contextNodeDefinitions[{i}]"
        if not isinstance(node, dict):
            result.add(Severity.ERROR, "node entry must be an object", nloc)
            continue
        name = node.get("name")
        if not name:
            result.add(Severity.ERROR, "node missing required 'name'", nloc)
        else:
            names.add(name)
        if check_suffix and name and _needs_c_suffix(name):
            result.add(
                Severity.ERROR,
                f"custom node name '{name}' should end with '__c' "
                f"(added to a standard/extended base)",
                nloc,
            )

    # parentNodeName references must resolve within the plan.
    for i, node in enumerate(node_defs):
        if not isinstance(node, dict):
            continue
        parent = node.get("parentNodeName")
        if parent and parent not in names:
            result.add(
                Severity.WARN,
                f"node '{node.get('name')}' references parentNodeName '{parent}' "
                f"not declared in this plan (may be inherited from the base)",
                f"{loc} contextNodeDefinitions[{i}]",
            )

    if len(node_defs) > LIMIT_NODES:
        result.add(
            Severity.ERROR,
            f"plan declares {len(node_defs)} nodes exceeding the limit of {LIMIT_NODES}",
            loc,
        )
    depth = _node_depth(node_defs)
    if depth > LIMIT_HIERARCHY_DEPTH:
        result.add(
            Severity.ERROR,
            f"node hierarchy depth {depth} exceeds the limit of {LIMIT_HIERARCHY_DEPTH}",
            loc,
        )


def _validate_mapping_rules(plan: Dict[str, Any], result: PlanResult, loc: str):
    rules = plan.get("mappingRules")
    if rules is None:
        return
    if not isinstance(rules, list):
        result.add(Severity.ERROR, "mappingRules must be a list", loc)
        return

    referenced_definitions = set()

    for i, rule in enumerate(rules):
        rloc = f"{loc} mappingRules[{i}]"
        if not isinstance(rule, dict):
            result.add(Severity.ERROR, "mapping rule must be an object", rloc)
            continue

        # CONTEXT-source mappings may point at another context definition via
        # mappedContextDefinitionName (see tasks/rlm_context_service.py). Track
        # distinct referenced definitions to enforce the platform ceiling.
        ref_def = rule.get("mappedContextDefinitionName")
        if ref_def:
            referenced_definitions.add(ref_def)
        for req in ("mappingName", "contextNode", "contextAttribute"):
            if not rule.get(req):
                result.add(Severity.ERROR, f"mapping rule missing required '{req}'", rloc)

        mapping_type = (rule.get("mappingType") or "SOBJECT").upper()
        if mapping_type not in VALID_MAPPING_TYPES:
            result.add(
                Severity.ERROR,
                f"invalid mappingType '{mapping_type}' (expected SOBJECT or CONTEXT)",
                rloc,
            )
            continue

        if mapping_type == "SOBJECT":
            if not rule.get("sObject"):
                result.add(Severity.ERROR, "SOBJECT rule missing required 'sObject'", rloc)
            # sObjectField may be legitimately absent (e.g. transient attributes).
            if rule.get("childSObjectField") and not rule.get("childSObject"):
                result.add(
                    Severity.ERROR,
                    "traversal rule has 'childSObjectField' without 'childSObject'",
                    rloc,
                )
            if rule.get("childSObjectField"):
                result.add(
                    Severity.INFO,
                    "relationship-traversal rule (childSObjectField set) — applied via "
                    "SObject REST, not the Connect PATCH (which rejects traversals)",
                    rloc,
                )
        else:  # CONTEXT
            for req in ("sourceContextNode", "sourceContextAttribute"):
                if not rule.get(req):
                    result.add(Severity.ERROR, f"CONTEXT rule missing required '{req}'", rloc)

    if len(referenced_definitions) > LIMIT_REFERENCED_DEFINITIONS:
        result.add(
            Severity.ERROR,
            f"plan references {len(referenced_definitions)} distinct context definitions "
            f"({sorted(referenced_definitions)}) exceeding the limit of "
            f"{LIMIT_REFERENCED_DEFINITIONS}",
            loc,
        )


def _validate_tags(plan: Dict[str, Any], result: PlanResult, loc: str):
    tags = plan.get("contextTagsByName")
    if tags is None:
        return
    if not isinstance(tags, list):
        result.add(Severity.ERROR, "contextTagsByName must be a list", loc)
        return

    check_suffix = not _is_create_new(plan)

    # Index attributes declared in this plan for tag<->attribute alignment.
    declared_attrs = set()
    for attr in plan.get("contextAttributesByName", []) or []:
        if isinstance(attr, dict):
            declared_attrs.add((attr.get("nodeName"), attr.get("name")))

    tags_per_node: Dict[str, int] = {}

    for i, tag in enumerate(tags):
        tloc = f"{loc} contextTagsByName[{i}]"
        if not isinstance(tag, dict):
            result.add(Severity.ERROR, "tag entry must be an object", tloc)
            continue
        name = tag.get("name")
        node_name = tag.get("nodeName")
        attr_name = tag.get("attributeName")
        if not name:
            result.add(Severity.ERROR, "tag missing required 'name'", tloc)
        if not node_name:
            result.add(Severity.ERROR, "tag missing required 'nodeName'", tloc)
        else:
            tags_per_node[node_name] = tags_per_node.get(node_name, 0) + 1
        if check_suffix and name and _needs_c_suffix(name):
            result.add(
                Severity.ERROR,
                f"custom tag name '{name}' should end with '__c' "
                f"(added to a standard/extended base)",
                tloc,
            )
        # Attribute-level tag alignment: if it targets an attribute this plan
        # declares, we can confirm it; otherwise it may reference an inherited
        # attribute, so only warn.
        if attr_name and (node_name, attr_name) not in declared_attrs:
            result.add(
                Severity.WARN,
                f"tag targets attribute '{node_name}.{attr_name}' not declared in this "
                f"plan (ok if inherited from the base; otherwise the attribute is missing)",
                tloc,
            )

    # Guideline (not a hard limit): tags per node. A shipped, live-validated plan
    # (DocGen) declares 20 tags on one node and works, so this is informational —
    # it never fails the build, even under --strict.
    for node_name, count in tags_per_node.items():
        if count > TAGS_PER_NODE_GUIDELINE:
            result.add(
                Severity.INFO,
                f"node '{node_name}' declares {count} tags (plan-declared), above the "
                f"recommended guideline of {TAGS_PER_NODE_GUIDELINE} per node "
                f"(guideline, not an enforced limit)",
                loc,
            )


def _validate_plan_object(plan: Dict[str, Any], result: PlanResult, loc: str):
    if not isinstance(plan, dict):
        result.add(Severity.ERROR, "plan must be a JSON object", loc)
        return

    if not plan.get("developerName"):
        result.add(Severity.ERROR, "plan missing required 'developerName'", loc)

    for banned in ("primaryDomainObject", "primaryObject"):
        if banned in plan:
            result.add(
                Severity.ERROR,
                f"'{banned}' is not accepted by the context-definitions create endpoint "
                f"(JSON_PARSER_ERROR) — remove it",
                loc,
            )

    if _is_create_new(plan) and not plan.get("label"):
        result.add(
            Severity.WARN,
            "create-new plan (create: true) should set 'label' (display name)",
            loc,
        )

    _validate_nodes(plan, result, loc)
    _validate_attributes(plan, result, loc)
    _validate_mapping_rules(plan, result, loc)
    _validate_tags(plan, result, loc)


def validate_manifest(manifest_path: Path) -> PlanResult:
    result = PlanResult(path=str(manifest_path.relative_to(REPO_ROOT)) if _under_repo(manifest_path) else str(manifest_path))
    loaded = _load_json(manifest_path)
    if isinstance(loaded, _LoadError):
        result.add(Severity.ERROR, f"manifest {loaded.message}")
        return result
    if not isinstance(loaded, dict):
        result.add(Severity.ERROR, "manifest must be a JSON object")
        return result

    contexts = loaded.get("contexts")
    if not isinstance(contexts, list) or not contexts:
        # A manifest may itself be a single inline plan (no 'contexts' list).
        _validate_plan_object(loaded, result, "manifest")
        return result

    for idx, entry in enumerate(contexts):
        cloc = f"contexts[{idx}]"
        if not isinstance(entry, dict):
            result.add(Severity.ERROR, "contexts entry must be an object", cloc)
            continue
        plan_file = entry.get("planFile")
        if not plan_file:
            # Inline plan definition inside the manifest entry.
            _validate_plan_object(entry, result, cloc)
            continue
        plan_path = manifest_path.parent / plan_file
        ploc = f"{cloc} -> {plan_file}"
        plan_loaded = _load_json(plan_path)
        if isinstance(plan_loaded, _LoadError):
            result.add(Severity.ERROR, f"planFile {plan_loaded.message}", ploc)
            continue
        # The manifest entry can override/augment the plan file (task merges them).
        merged = {**plan_loaded, **{k: v for k, v in entry.items() if k != "planFile"}}
        _validate_plan_object(merged, result, ploc)
    return result


def _under_repo(path: Path) -> bool:
    try:
        path.relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def discover_manifests(include_archive: bool) -> List[Path]:
    if not CONTEXT_PLANS_DIR.is_dir():
        return []
    manifests = sorted(CONTEXT_PLANS_DIR.glob("*/manifest.json"))
    if not include_archive:
        manifests = [m for m in manifests if "archive" not in m.parts]
    return manifests


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline linter for Context Service plan JSON files.",
    )
    parser.add_argument(
        "manifests",
        nargs="*",
        help="Explicit manifest.json paths. If omitted, discovers active manifests "
        "under datasets/context_plans/ (archive/ excluded unless --include-archive).",
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="Include datasets/context_plans/archive/ during discovery.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (non-zero exit).",
    )
    args = parser.parse_args(argv)

    if args.manifests:
        manifest_paths = [Path(p).resolve() for p in args.manifests]
    else:
        manifest_paths = discover_manifests(args.include_archive)
        if not manifest_paths:
            print("No manifests found under datasets/context_plans/.")
            return 1

    total_errors = 0
    total_warnings = 0
    for manifest_path in manifest_paths:
        result = validate_manifest(manifest_path)
        errors = result.errors
        warnings = result.warnings
        infos = [i for i in result.issues if i.severity is Severity.INFO]
        total_errors += len(errors)
        total_warnings += len(warnings)

        status = "FAIL" if errors else ("WARN" if warnings else "OK")
        print(f"[{status}] {result.path}")
        for issue in errors + warnings + infos:
            loc = f" ({issue.location})" if issue.location else ""
            print(f"    {issue.severity.value}: {issue.message}{loc}")

    print()
    print(f"Summary: {len(manifest_paths)} manifest(s), "
          f"{total_errors} error(s), {total_warnings} warning(s).")

    if total_errors:
        return 1
    if args.strict and total_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
