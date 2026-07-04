#!/usr/bin/env python3
"""Unit tests for scripts.context_service.validate_context_plan.

Self-contained — no pytest required (matches this repo's lightweight test
convention; see tests/test_expression_set_schema.py). Run from the repo root
with base Python:

    python tests/test_context_plan_validator.py

Exits 0 when all checks pass, 1 otherwise. Covers the offline lint gate the
project relies on pre-merge (AGENTS.md: "must be 0 errors"): the dataType /
fieldType / mappingType enums, the scoped ``__c`` custom-name rule (skipped for
create-new plans), the per-node / total / referenced-definition limits, the
banned ``primaryDomainObject`` key, the traversal INFO signal, and the
``nodeName`` (attribute) vs ``contextNode`` (mapping rule) key-name asymmetry
that is an easy authoring trip.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The module bootstraps its own siblings with a bare ``import`` off its own
# directory, so put that directory on the path for a standalone import.
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "context_service"))

import validate_context_plan as V  # noqa: E402
from validate_context_plan import (  # noqa: E402
    LIMIT_ATTRS_PER_NODE,
    LIMIT_REFERENCED_DEFINITIONS,
    LIMIT_TOTAL_ATTRS,
    PlanResult,
    Severity,
)

RESULTS = []


# ----------------------------------------------------------------------
# Harness
# ----------------------------------------------------------------------

def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


def _validate(plan):
    """Run the per-plan rule set over a plan dict and return the PlanResult."""
    result = PlanResult(path="<test>")
    V._validate_plan_object(plan, result, "test")
    return result


def _errors(result):
    return [i.message for i in result.errors]


def _warnings(result):
    return [i.message for i in result.warnings]


def _infos(result):
    return [i.message for i in result.issues if i.severity is Severity.INFO]


def _has(messages, substring):
    return any(substring in m for m in messages)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

def _minimal_extend_plan():
    """A minimal additive plan onto a standard/extended base (not create-new)."""
    return {
        "developerName": "RLM_SalesTransactionContext",
        "contextAttributesByName": [
            {
                "nodeName": "SalesTransaction",
                "name": "RampMode__c",
                "dataType": "STRING",
                "fieldType": "INPUTOUTPUT",
            }
        ],
        "mappingRules": [
            {
                "mappingName": "QuoteEntitiesMapping",
                "contextNode": "SalesTransaction",
                "contextAttribute": "RampMode__c",
                "mappingType": "SOBJECT",
                "sObject": "Quote",
                "sObjectField": "RLM_RampMode__c",
            }
        ],
    }


def _clone(plan):
    return json.loads(json.dumps(plan))


# ----------------------------------------------------------------------
# Tests — happy path
# ----------------------------------------------------------------------

def test_minimal_extend_plan_passes():
    r = _validate(_minimal_extend_plan())
    check("minimal additive plan validates with 0 errors", not r.errors)


def test_committed_plans_pass():
    """The plans shipped in datasets/context_plans/ must lint with 0 errors."""
    from pathlib import Path

    manifests = V.discover_manifests(include_archive=False)
    check("at least one committed manifest discovered", len(manifests) > 0)
    for m in manifests:
        r = V.validate_manifest(Path(m))
        check(f"committed manifest lints clean: {Path(m).parent.name}", not r.errors)


# ----------------------------------------------------------------------
# Tests — enums
# ----------------------------------------------------------------------

def test_bad_datatype_errors():
    p = _clone(_minimal_extend_plan())
    p["contextAttributesByName"][0]["dataType"] = "Bogus"
    r = _validate(p)
    check("invalid dataType errors", _has(_errors(r), "invalid dataType 'Bogus'"))


def test_bad_fieldtype_errors():
    p = _clone(_minimal_extend_plan())
    p["contextAttributesByName"][0]["fieldType"] = "Nope"
    r = _validate(p)
    check("invalid fieldType errors", _has(_errors(r), "invalid fieldType 'Nope'"))


def test_bad_mappingtype_errors():
    p = _clone(_minimal_extend_plan())
    p["mappingRules"][0]["mappingType"] = "WEIRD"
    r = _validate(p)
    check("invalid mappingType errors", _has(_errors(r), "invalid mappingType 'WEIRD'"))


# ----------------------------------------------------------------------
# Tests — __c suffix rule (scoped: extend base yes, create-new no)
# ----------------------------------------------------------------------

def test_missing_c_suffix_on_extend_errors():
    p = _clone(_minimal_extend_plan())
    p["contextAttributesByName"][0]["name"] = "RampMode"  # no __c
    r = _validate(p)
    check(
        "custom attr on extended base without __c errors",
        _has(_errors(r), "should end with '__c'"),
    )


def test_missing_c_suffix_on_create_new_ok():
    p = _clone(_minimal_extend_plan())
    p["create"] = True
    p["label"] = "My Custom Context"
    p["contextAttributesByName"][0]["name"] = "RampMode"  # no __c, but create-new
    r = _validate(p)
    check(
        "create-new plan exempts the __c suffix rule",
        not _has(_errors(r), "should end with '__c'"),
    )


def test_stdctx_suffix_is_not_flagged():
    p = _clone(_minimal_extend_plan())
    p["contextAttributesByName"][0]["name"] = "SomeInherited__stdctx"
    r = _validate(p)
    check(
        "a __stdctx-suffixed name is not flagged as needing __c",
        not _has(_errors(r), "should end with '__c'"),
    )


# ----------------------------------------------------------------------
# Tests — key-name asymmetry (nodeName vs contextNode)
# ----------------------------------------------------------------------

def test_attribute_uses_nodeName_not_node():
    p = _clone(_minimal_extend_plan())
    del p["contextAttributesByName"][0]["nodeName"]
    p["contextAttributesByName"][0]["node"] = "SalesTransaction"  # wrong key
    r = _validate(p)
    check(
        "attribute keyed on 'node' errors (must be 'nodeName')",
        _has(_errors(r), "attribute missing required 'nodeName'"),
    )


def test_mapping_rule_uses_contextNode_not_nodeName():
    p = _clone(_minimal_extend_plan())
    del p["mappingRules"][0]["contextNode"]
    p["mappingRules"][0]["nodeName"] = "SalesTransaction"  # wrong key for a rule
    r = _validate(p)
    check(
        "mapping rule keyed on 'nodeName' errors (must be 'contextNode')",
        _has(_errors(r), "mapping rule missing required 'contextNode'"),
    )


# ----------------------------------------------------------------------
# Tests — limits
# ----------------------------------------------------------------------

def test_total_attr_limit_errors():
    p = _clone(_minimal_extend_plan())
    # spread across many nodes so the per-node limit is not what trips first
    p["contextAttributesByName"] = [
        {"nodeName": f"Node{i // LIMIT_ATTRS_PER_NODE}", "name": f"A{i}__c",
         "dataType": "STRING", "fieldType": "INPUTOUTPUT"}
        for i in range(LIMIT_TOTAL_ATTRS + 1)
    ]
    r = _validate(p)
    check(
        "exceeding the total attribute limit errors",
        _has(_errors(r), "exceeding the total limit"),
    )


def test_per_node_attr_limit_errors():
    p = _clone(_minimal_extend_plan())
    p["contextAttributesByName"] = [
        {"nodeName": "SalesTransaction", "name": f"A{i}__c",
         "dataType": "STRING", "fieldType": "INPUTOUTPUT"}
        for i in range(LIMIT_ATTRS_PER_NODE + 1)
    ]
    r = _validate(p)
    check(
        "exceeding the per-node attribute limit errors",
        _has(_errors(r), "exceeding the per-node limit"),
    )


def test_referenced_definition_limit_errors():
    p = _clone(_minimal_extend_plan())
    p["mappingRules"] = [
        {
            "mappingName": f"CtxMap{i}",
            "contextNode": "SalesTransaction",
            "contextAttribute": "RampMode__c",
            "mappingType": "CONTEXT",
            "sourceContextNode": "N",
            "sourceContextAttribute": "A",
            "mappedContextDefinitionName": f"RLM_Ref{i}Context",
        }
        for i in range(LIMIT_REFERENCED_DEFINITIONS + 1)
    ]
    r = _validate(p)
    check(
        "exceeding the referenced-definition limit errors",
        _has(_errors(r), "exceeding the limit"),
    )


# ----------------------------------------------------------------------
# Tests — banned keys, required keys, traversal signal
# ----------------------------------------------------------------------

def test_banned_primary_domain_object_errors():
    for banned in ("primaryDomainObject", "primaryObject"):
        p = _clone(_minimal_extend_plan())
        p[banned] = "Quote"
        r = _validate(p)
        check(
            f"banned key '{banned}' errors",
            _has(_errors(r), f"'{banned}' is not accepted"),
        )


def test_missing_developer_name_errors():
    p = _clone(_minimal_extend_plan())
    del p["developerName"]
    r = _validate(p)
    check(
        "missing developerName errors",
        _has(_errors(r), "missing required 'developerName'"),
    )


def test_sobject_rule_missing_sobject_errors():
    p = _clone(_minimal_extend_plan())
    del p["mappingRules"][0]["sObject"]
    r = _validate(p)
    check(
        "SOBJECT rule without sObject errors",
        _has(_errors(r), "SOBJECT rule missing required 'sObject'"),
    )


def test_traversal_rule_emits_info_signal():
    p = _clone(_minimal_extend_plan())
    p["mappingRules"][0]["childSObject"] = "Product2"
    p["mappingRules"][0]["childSObjectField"] = "ProductCode"
    r = _validate(p)
    check(
        "relationship-traversal rule emits the SObject-REST INFO note",
        _has(_infos(r), "relationship-traversal rule"),
    )


def test_traversal_child_field_without_child_object_errors():
    p = _clone(_minimal_extend_plan())
    p["mappingRules"][0]["childSObjectField"] = "ProductCode"  # no childSObject
    r = _validate(p)
    check(
        "childSObjectField without childSObject errors",
        _has(_errors(r), "'childSObjectField' without 'childSObject'"),
    )


# ----------------------------------------------------------------------

def main():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    print(f"Running {len(tests)} validator test groups...\n")
    for t in tests:
        t()
    print()
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"{passed}/{total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
