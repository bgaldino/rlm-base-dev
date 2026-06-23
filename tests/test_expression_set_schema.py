#!/usr/bin/env python3
"""Unit tests for tasks.expression_set_schema.

Self-contained — no pytest required (matches this repo's lightweight test
convention). Run from the repo root with base Python:

    python tests/test_expression_set_schema.py

Exits 0 when all checks pass, 1 otherwise. Covers the validator's enum,
required-key, duplicate-parameter, sequenceNumber, placement, and
pricing-procedure-shape rules for both definitions and overlays, plus the
overlay↔definition cross-check.
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from tasks.expression_set_schema import (  # noqa: E402
    validate_definition,
    validate_overlay,
    validate_overlay_against_definition,
)
from tasks.rlm_expression_set_connect import (  # noqa: E402
    ExpressionSetConnectBase as Connect,
    ApplyExpressionSetOverlay,
)

RESULTS = []


class _OverlayApplier(ApplyExpressionSetOverlay):
    """Bare instance for unit-testing the pure step-merge helpers.

    Bypasses the CCI task __init__ (which needs a project/org context) so the
    pure transformation methods (_add_steps, _build_step, _renumber_top_level_
    steps) can be exercised in base Python, matching this file's no-pytest
    convention.
    """

    def __init__(self):
        import logging

        self.logger = logging.getLogger("test_overlay_applier")
        self.logger.addHandler(logging.NullHandler())
        self.options = {}


class _CascadeTask(Connect):
    """Bare instance for testing cascade deactivate/reactivate behavior."""

    def __init__(self, states, fail_on_deactivate=None):
        import logging

        self.logger = logging.getLogger("test_cascade_task")
        self.logger.addHandler(logging.NullHandler())
        self.options = {}
        self.states = dict(states)
        self.fail_on_deactivate = fail_on_deactivate
        self.patch_calls = []

    def _find_referencing_procedure_plans(self, es_def_id):
        return [
            {"ProcedurePlanSection": {"ProcedurePlanVersionId": vid}}
            for vid in self.states
        ]

    def _soql_query(self, soql):
        for vid, active in self.states.items():
            if f"'{vid}'" in soql:
                return [{"Id": vid, "IsActive": active}]
        return []

    def _patch_sobject(self, sobject, record_id, payload):
        self.patch_calls.append((sobject, record_id, dict(payload)))
        active = payload.get("IsActive")
        if active is False and record_id == self.fail_on_deactivate:
            raise RuntimeError(f"simulated deactivate failure for {record_id}")
        self.states[record_id] = active


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


def _has_error_containing(result, substring):
    return any(substring in i.message for i in result.errors)


def _has_warning_containing(result, substring):
    return any(substring in i.message for i in result.warnings)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

MINIMAL_PRICING_DEF = {
    "apiName": "ZZ_Test",
    "name": "ZZ Test",
    "usageType": "DefaultPricing",
    "versions": [
        {
            "apiName": "ZZ_Test_V1",
            "versionNumber": 1,
            "rank": 1,
            "steps": [
                {
                    "name": "PricingSetting",
                    "sequenceNumber": 1,
                    "stepType": "BusinessKnowledgeModel",
                    "actionType": "PricingSettings",
                },
                {
                    "name": "SecondStep",
                    "sequenceNumber": 2,
                    "stepType": "ListGroup",
                },
            ],
            "variables": [],
        }
    ],
}


def test_valid_definition_passes():
    r = validate_definition(MINIMAL_PRICING_DEF)
    check("valid pricing definition passes", r.passed and not r.errors)


def test_real_export_passes():
    # The committed real GET export validates with 0 errors. It DOES carry
    # HTML-entity warnings (raw GET output) — expected, since the send-time
    # normalization step is what cleans them, not the validator.
    path = "tests/data/expression_set/RLM_DefaultPricingProcedure_export.json"
    if not os.path.exists(path):
        print(f"  [SKIP] real export not present at {path}")
        return
    r = validate_definition(json.load(open(path)))
    check("real export validates with 0 errors", r.passed and not r.errors)
    check(
        "real export carries HTML-entity warnings (raw GET output)",
        _has_warning_containing(r, "HTML entities"),
    )


def test_bad_usage_type_warns():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["usageType"] = "Nonsense"
    r = validate_definition(d)
    # unknown usageType is a warning (forward-compat), not an error
    check("unknown usageType warns not errors", r.passed and r.warnings)


def test_bad_step_type_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["steps"][1]["stepType"] = "Bogus"
    r = validate_definition(d)
    check("invalid stepType errors", not r.passed and _has_error_containing(r, "invalid stepType"))


def test_bad_variable_datatype_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["variables"] = [{"name": "v1", "dataType": "Double"}]
    r = validate_definition(d)
    check("invalid variable dataType errors", not r.passed and _has_error_containing(r, "invalid variable dataType"))


def test_missing_pricing_setting_first_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    # swap so a non-PricingSettings step is first by sequenceNumber
    d["versions"][0]["steps"][0]["actionType"] = "AssignmentElement"
    r = validate_definition(d)
    check(
        "pricing proc must start with PricingSettings",
        not r.passed and _has_error_containing(r, "must start with a PricingSettings"),
    )


def test_assignment_under_bre_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["usageType"] = "Bre"
    d["versions"][0]["steps"][0]["actionType"] = "PricingSettings"  # keep first valid? Bre has no pricing
    d["versions"][0]["steps"][1]["actionType"] = "AssignmentElement"
    r = validate_definition(d)
    check(
        "AssignmentElement under Bre errors",
        _has_error_containing(r, "only available under usageType"),
    )


def test_duplicate_sequence_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["steps"][1]["sequenceNumber"] = 1  # dup of first
    r = validate_definition(d)
    check("duplicate sequenceNumber errors", not r.passed and _has_error_containing(r, "duplicate sequenceNumber"))


def test_dangling_parent_step_errors():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["steps"][1]["parentStep"] = "NoSuchStep"
    r = validate_definition(d)
    check("dangling parentStep errors", not r.passed and _has_error_containing(r, "parentStep 'NoSuchStep'"))


def test_per_parent_sequence_scope_ok():
    # A child step restarting at sequenceNumber 1 under its parent is valid.
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["steps"].append(
        {
            "name": "Child",
            "sequenceNumber": 1,
            "stepType": "ListFilter",
            "parentStep": "SecondStep",
        }
    )
    r = validate_definition(d)
    check("child seq restart at 1 under parent is valid", r.passed and not r.errors)


# ---- Overlay tests ----

def test_duplicate_param_name_errors():
    # Regression guard for the original map_line_item.json defect: two params
    # with the same name within one customElement (silently drops a mapping).
    overlay = {
        "addSteps": [
            {
                "name": "MapStep",
                "stepType": "BusinessKnowledgeModel",
                "customElement": {
                    "parameters": [
                        {"name": "sectionJsonString9", "type": "Literal", "value": "a"},
                        {"name": "sectionJsonString9", "type": "Literal", "value": "b"},
                    ]
                },
            }
        ]
    }
    r = validate_overlay(overlay)
    check(
        "validator flags duplicate parameter name in customElement",
        not r.passed and _has_error_containing(r, "duplicate parameter name 'sectionJsonString9'"),
    )


def test_shipped_map_line_item_passes():
    # After the §4 data fix, the shipped overlay must validate clean.
    path = "datasets/expression_set_overlays/map_line_item.json"
    if not os.path.exists(path):
        print("  [SKIP] map_line_item.json not present")
        return
    r = validate_overlay(json.load(open(path)))
    check("shipped map_line_item.json validates clean", r.passed and not r.errors)


def test_shipped_discount_distribution_passes():
    # The discount-distribution overlay adds ListGroup parents WITH nested
    # children (the first overlay to do so); it must validate clean.
    path = "datasets/expression_set_overlays/discount_distribution.json"
    if not os.path.exists(path):
        print("  [SKIP] discount_distribution.json not present")
        return
    r = validate_overlay(json.load(open(path)))
    check("shipped discount_distribution.json validates clean", r.passed and not r.errors)


def test_shipped_discount_distribution_ships_constants():
    # The overlay must carry the 4 version-level Constant_DDS_* the steps
    # reference (the deployment-gap fix); without addVariables a target lacking
    # them would reference undefined variables.
    path = "datasets/expression_set_overlays/discount_distribution.json"
    if not os.path.exists(path):
        print("  [SKIP] discount_distribution.json not present")
        return
    ov = json.load(open(path))
    names = {v.get("name") for v in ov.get("addVariables", [])}
    expected = {
        "Constant_DDS_Amount", "Constant_DDS_NetUnitPrice",
        "Constant_DDS_Override", "Constant_DDS_Percentage",
    }
    check(
        "discount_distribution overlay ships the 4 Constant_DDS_* in addVariables",
        expected.issubset(names),
    )


# ---- External-dependency detection (custom field / context node) ----

def test_extdep_warns_on_undeclared_custom_field():
    # A step consuming a __c custom field that isn't declared in an
    # externalDependencies block (and isn't produced by an added step) → warn so
    # the author documents the requirement.
    overlay = {
        "addSteps": [
            {
                "name": "S", "stepType": "BusinessKnowledgeModel",
                "customElement": {"parameters": [
                    {"name": "i", "type": "Parameter", "input": True,
                     "value": "My_Custom_Field__c"}
                ]},
            }
        ]
    }
    r = validate_overlay(overlay)
    check(
        "undeclared custom field reference warns",
        r.passed and _has_warning_containing(r, "My_Custom_Field__c"),
    )


def test_extdep_silent_when_declared():
    overlay = {
        "externalDependencies": {
            "customFields": ["My_Custom_Field__c (mapped into SomeContext)"]
        },
        "addSteps": [
            {
                "name": "S", "stepType": "BusinessKnowledgeModel",
                "customElement": {"parameters": [
                    {"name": "i", "type": "Parameter", "input": True,
                     "value": "My_Custom_Field__c"}
                ]},
            }
        ],
    }
    r = validate_overlay(overlay)
    check(
        "declared custom field suppresses the external-dependency warning",
        not _has_warning_containing(r, "My_Custom_Field__c"),
    )


def test_extdep_standard_std_field_not_flagged():
    # __std (and no-suffix) names are STANDARD context fields shipped with the
    # standard context definitions — they must NOT be flagged as a dependency.
    overlay = {
        "addSteps": [
            {
                "name": "S", "stepType": "BusinessKnowledgeModel",
                "customElement": {"parameters": [
                    {"name": "i", "type": "Parameter", "input": True,
                     "value": "ItemDetailListPrice__std"},
                    {"name": "j", "type": "Parameter", "input": True,
                     "value": "NetUnitPrice"},
                ]},
            }
        ]
    }
    r = validate_overlay(overlay)
    check(
        "__std / standard fields are not flagged as external dependencies",
        not _has_warning_containing(r, "__std")
        and not _has_warning_containing(r, "custom reference"),
    )


def test_extdep_detects_custom_field_inside_formula():
    # FormulaBasedPricing references fields inside an expression string, not as
    # discrete Parameter params — detection must tokenize the formula.
    overlay = {
        "addSteps": [
            {
                "name": "F", "stepType": "BusinessKnowledgeModel",
                "actionType": "FormulaBasedPricing",
                "customElement": {"parameters": [
                    {"name": "formula-section-0-input", "type": "Formula",
                     "input": True, "value": "Hospitals__c - ItemStartQuantity"}
                ]},
            }
        ]
    }
    r = validate_overlay(overlay)
    check(
        "custom field referenced inside a Formula is detected",
        _has_warning_containing(r, "Hospitals__c"),
    )


def test_extdep_block_shape_errors():
    overlay = {
        "externalDependencies": {"customFields": "not-a-list"},
        "addSteps": [],
    }
    r = validate_overlay(overlay)
    check(
        "externalDependencies.customFields must be a list of strings",
        not r.passed and _has_error_containing(r, "must be a list of strings"),
    )


def test_extdep_block_unknown_key_warns():
    overlay = {"externalDependencies": {"bogusKey": []}, "addSteps": []}
    r = validate_overlay(overlay)
    check(
        "unknown externalDependencies key warns",
        r.passed and _has_warning_containing(r, "unknown key"),
    )


def test_shipped_overlays_declare_their_external_dependencies():
    # Every shipped overlay must leave no undeclared custom-ref warning — guards
    # against re-introducing an undocumented external dependency.
    import glob
    for path in sorted(glob.glob("datasets/expression_set_overlays/*.json")):
        ov = json.load(open(path))
        r = validate_overlay(ov)
        leftover = [w.message for w in r.warnings if "custom reference" in w.message]
        check(
            f"{os.path.basename(path)} declares all custom-ref dependencies",
            not leftover,
        )


# ---- Overlay variable-dependency guard (cross-check) ----

# A tiny target definition: one declared version variable + one step that
# references a context field (NetUnitPriceCtx) — proving the bound context
# supplies it — so the guard treats that name as satisfied.
_GUARD_TARGET = {
    "apiName": "ZZ_Guard",
    "name": "ZZ Guard",
    "usageType": "DefaultPricing",
    "versions": [
        {
            "apiName": "ZZ_Guard_V1",
            "versionNumber": 1,
            "rank": 1,
            "variables": [
                {"name": "ExistingConst", "type": "Constant", "dataType": "Text"}
            ],
            "steps": [
                {
                    "name": "PricingSetting",
                    "sequenceNumber": 1,
                    "stepType": "BusinessKnowledgeModel",
                    "actionType": "PricingSettings",
                },
                {
                    "name": "Base",
                    "sequenceNumber": 2,
                    "stepType": "BusinessKnowledgeModel",
                    "customElement": {
                        "parameters": [
                            {"name": "i", "type": "Parameter", "input": True,
                             "value": "NetUnitPriceCtx"}
                        ]
                    },
                },
            ],
        }
    ],
}


def _added_step_consuming(value, name="NewStep"):
    return {
        "name": name,
        "stepType": "BusinessKnowledgeModel",
        "placement": {"afterStep": "Base"},
        "customElement": {
            "parameters": [
                {"name": "in1", "type": "Parameter", "input": True, "value": value}
            ]
        },
    }


def test_guard_warns_on_unresolved_version_variable():
    # A step consuming a variable that is NOT in addVariables, NOT a target
    # version var, NOT produced by an added step, and NOT used by any existing
    # target step → warn (the missing-Constant class).
    overlay = {"addSteps": [_added_step_consuming("MissingConst")]}
    r = validate_overlay_against_definition(overlay, _GUARD_TARGET, "ZZ_Guard_V1")
    check(
        "guard warns when added step references an unresolved variable",
        _has_warning_containing(r, "MissingConst") and r.passed,  # warning, not error
    )


def test_guard_silent_when_addVariables_supplies_it():
    overlay = {
        "addVariables": [{"name": "MissingConst", "type": "Constant", "dataType": "Text"}],
        "addSteps": [_added_step_consuming("MissingConst")],
    }
    r = validate_overlay_against_definition(overlay, _GUARD_TARGET, "ZZ_Guard_V1")
    check(
        "guard silent when addVariables supplies the referenced variable",
        not _has_warning_containing(r, "MissingConst"),
    )


def test_guard_silent_for_context_field_used_by_existing_step():
    # NetUnitPriceCtx is referenced by an existing target step → the bound
    # context supplies it → no warning even though it's not a version variable.
    overlay = {"addSteps": [_added_step_consuming("NetUnitPriceCtx")]}
    r = validate_overlay_against_definition(overlay, _GUARD_TARGET, "ZZ_Guard_V1")
    check(
        "guard silent for a context field already used by an existing step",
        not _has_warning_containing(r, "NetUnitPriceCtx"),
    )


def test_guard_silent_when_produced_by_an_added_step():
    # An added step produces Derived; another added step consumes it → satisfied.
    producer = {
        "name": "Producer", "stepType": "BusinessKnowledgeModel",
        "placement": {"afterStep": "Base"},
        "customElement": {"parameters": [
            {"name": "o", "type": "Parameter", "output": True, "value": "Derived"}
        ]},
    }
    overlay = {"addSteps": [producer, _added_step_consuming("Derived", name="Consumer")]}
    r = validate_overlay_against_definition(overlay, _GUARD_TARGET, "ZZ_Guard_V1")
    check(
        "guard silent when a referenced variable is produced by an added step",
        not _has_warning_containing(r, "Derived"),
    )


def test_add_steps_preserves_child_sequence():
    # Regression: a child step (parentStep set, no placement) must keep its own
    # per-parent sequenceNumber. Before the fix it fell into the top-level
    # else-branch and was overwritten with max_top_level+1, collapsing sibling
    # children onto the same slot. Mirrors the discount_distribution overlay
    # shape: a ListGroup parent placed afterStep, with two children at seq 1/2.
    applier = _OverlayApplier()
    base = [
        {"name": "Anchor", "sequenceNumber": 1, "stepType": "BusinessKnowledgeModel",
         "parentStep": None},
        {"name": "Tail", "sequenceNumber": 2, "stepType": "BusinessKnowledgeModel",
         "parentStep": None},
    ]
    to_add = [
        {"name": "Group", "stepType": "ListGroup",
         "placement": {"afterStep": "Anchor"}},
        {"name": "Filter", "stepType": "AdvancedListFilter",
         "parentStep": "Group", "sequenceNumber": 1},
        {"name": "Assign", "stepType": "BusinessKnowledgeModel",
         "parentStep": "Group", "sequenceNumber": 2},
    ]
    result = applier._add_steps([dict(s) for s in base], [dict(s) for s in to_add])
    by_name = {s["name"]: s for s in result}
    parent_seq = by_name["Group"]["sequenceNumber"]
    filter_seq = by_name["Filter"]["sequenceNumber"]
    assign_seq = by_name["Assign"]["sequenceNumber"]
    tail_seq = by_name["Tail"]["sequenceNumber"]
    check(
        "ListGroup parent lands immediately after its afterStep target",
        parent_seq == 2 and tail_seq == 3,
    )
    check(
        "child steps keep distinct per-parent sequenceNumber (1, 2)",
        filter_seq == 1 and assign_seq == 2,
    )


def test_cascade_deactivate_returns_successfully_deactivated_versions():
    task = _CascadeTask({"PPV_A": True, "PPV_B": True, "PPV_C": False})

    deactivated = task._cascade_deactivate_procedure_plans("ESD", dry_run=False)

    check(
        "cascade deactivate returns only active procedure plan versions it changed",
        deactivated == ["PPV_A", "PPV_B"],
    )
    check(
        "cascade deactivate sets active procedure plan versions inactive",
        task.states == {"PPV_A": False, "PPV_B": False, "PPV_C": False},
    )


def test_cascade_deactivate_rolls_back_partial_failure():
    task = _CascadeTask(
        {"PPV_A": True, "PPV_B": True},
        fail_on_deactivate="PPV_B",
    )

    error = None
    try:
        task._cascade_deactivate_procedure_plans("ESD", dry_run=False)
    except Exception as exc:
        error = exc

    check(
        "cascade partial failure raises with rollback context",
        error is not None and "rolled them back" in str(error),
    )
    check(
        "cascade partial failure reactivates already-deactivated versions",
        task.states == {"PPV_A": True, "PPV_B": True},
    )
    check(
        "cascade partial failure attempts rollback after failed deactivate",
        task.patch_calls == [
            ("ProcedurePlanDefinitionVersion", "PPV_A", {"IsActive": False}),
            ("ProcedurePlanDefinitionVersion", "PPV_B", {"IsActive": False}),
            ("ProcedurePlanDefinitionVersion", "PPV_A", {"IsActive": True}),
        ],
    )


def test_cascade_deactivate_dry_run_does_not_patch():
    task = _CascadeTask({"PPV_A": True, "PPV_B": True})

    deactivated = task._cascade_deactivate_procedure_plans("ESD", dry_run=True)

    check(
        "cascade dry-run reports active procedure plan versions",
        deactivated == ["PPV_A", "PPV_B"],
    )
    check(
        "cascade dry-run does not patch or mutate active state",
        task.patch_calls == [] and task.states == {"PPV_A": True, "PPV_B": True},
    )


def test_valid_overlay_passes():
    overlay = {
        "expressionSetApiName": "ZZ_Test",
        "addSteps": [
            {
                "name": "NewStep",
                "stepType": "BusinessKnowledgeModel",
                "placement": {"afterStep": "PricingSetting"},
            }
        ],
    }
    r = validate_overlay(overlay)
    check("valid overlay passes (no sequenceNumber required)", r.passed and not r.errors)


def test_overlay_multiple_placement_errors():
    overlay = {
        "addSteps": [
            {
                "name": "NewStep",
                "stepType": "ListGroup",
                "placement": {"afterStep": "A", "beforeStep": "B"},
            }
        ]
    }
    r = validate_overlay(overlay)
    check("overlay with conflicting placement errors", not r.passed and _has_error_containing(r, "only one of"))


def test_overlay_against_definition_dangling_target():
    overlay = {
        "addSteps": [
            {"name": "NewStep", "stepType": "ListGroup", "placement": {"afterStep": "Ghost"}}
        ]
    }
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "overlay placement target missing in def errors",
        not r.passed and _has_error_containing(r, "target step 'Ghost' not found"),
    )


def test_overlay_against_definition_chained_placement_ok():
    # A later addSteps entry may be placed afterStep/beforeStep a sibling added
    # earlier in the SAME overlay (chained ListGroup blocks). The cross-check
    # must not reject this — _add_steps processes addSteps in array order.
    overlay = {
        "addSteps": [
            {"name": "First", "stepType": "ListGroup",
             "placement": {"afterStep": "PricingSetting"}},
            {"name": "Second", "stepType": "ListGroup",
             "placement": {"afterStep": "First"}},  # First is added above, not pre-existing
        ]
    }
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "chained placement target (earlier added step) is accepted",
        r.passed and not _has_error_containing(r, "'First' not found"),
    )


def test_overlay_against_definition_forward_placement_errors():
    # But a placement referencing a sibling added LATER in the array is still
    # invalid (the target won't exist yet when this step is processed).
    overlay = {
        "addSteps": [
            {"name": "First", "stepType": "ListGroup",
             "placement": {"afterStep": "Second"}},  # Second appears later → not yet added
            {"name": "Second", "stepType": "ListGroup",
             "placement": {"afterStep": "PricingSetting"}},
        ]
    }
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "forward placement target (later added step) errors",
        not r.passed and _has_error_containing(r, "'Second' not found"),
    )


def test_overlay_against_definition_valid_target():
    overlay = {
        "addSteps": [
            {"name": "NewStep", "stepType": "ListGroup", "placement": {"afterStep": "PricingSetting"}}
        ]
    }
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check("overlay placement target present in def passes", r.passed and not r.errors)


def test_overlay_against_definition_dangling_update_target():
    # The cross-check (now wired into ApplyExpressionSetOverlay before any
    # deactivation) must catch a typo'd updateSteps target, not just addSteps
    # placement — otherwise the apply would deactivate a live version and then
    # silently no-op the update.
    overlay = {"updateSteps": [{"name": "Ghost", "description": "x"}]}
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "overlay updateSteps target missing in def errors",
        not r.passed and _has_error_containing(r, "step 'Ghost' not found"),
    )


def test_overlay_against_definition_dangling_reorder_target():
    overlay = {"reorderSteps": [{"name": "Ghost", "sequenceNumber": 2}]}
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "overlay reorderSteps target missing in def errors",
        not r.passed and _has_error_containing(r, "step 'Ghost' not found"),
    )


def test_overlay_against_definition_dangling_remove_target():
    overlay = {"removeSteps": [{"name": "Ghost"}]}
    r = validate_overlay_against_definition(overlay, MINIMAL_PRICING_DEF, "ZZ_Test_V1")
    check(
        "overlay removeSteps target missing in def errors",
        not r.passed and _has_error_containing(r, "step 'Ghost' not found"),
    )


# ---- Version-level id handling (definition warning + create strip) ----

def test_version_id_warns_in_definition():
    # A definition carrying versions[].id is fine for a PATCH-replace but must
    # be stripped for a POST-create; the validator warns so a hand-authored
    # create payload is not surprised by it.
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["id"] = "9QMxxxxxxxxxxxxxxx"
    r = validate_definition(d)
    check(
        "version-level id warns (not errors)",
        r.passed and _has_warning_containing(r, "must be omitted on a POST-create"),
    )


def test_strip_readonly_keeps_version_id_for_patch():
    payload = {
        "id": "9QLtop",
        "error": None,
        "apiName": "ZZ",
        "versions": [{"id": "9QMv1", "versionNumber": 1, "steps": []}],
    }
    out = Connect._strip_readonly_fields(payload)
    check(
        "PATCH strip removes top-level id/error, KEEPS version id",
        "id" not in out and "error" not in out
        and out["versions"][0]["id"] == "9QMv1",
    )


def test_strip_readonly_drops_version_id_for_create():
    payload = {
        "id": "9QLtop",
        "apiName": "ZZ",
        "versions": [
            {"id": "9QMv1", "versionNumber": 1, "steps": []},
            {"id": "9QMv2", "versionNumber": 2, "steps": []},
        ],
    }
    out = Connect._strip_readonly_fields(payload, for_create=True)
    check(
        "POST-create strip removes top-level id AND every version id",
        "id" not in out
        and all("id" not in v for v in out["versions"]),
    )


def test_strip_readonly_create_does_not_mutate_input():
    payload = {"apiName": "ZZ", "versions": [{"id": "9QMv1", "steps": []}]}
    Connect._strip_readonly_fields(payload, for_create=True)
    check(
        "for_create strip does not mutate caller's payload",
        payload["versions"][0]["id"] == "9QMv1",
    )


# ---- HTML-entity normalization (Connect._unescape_value) ----

def test_unescape_quot_blob():
    s = "{&quot;whereConditions&quot;:[]}"
    out = Connect._unescape_value(s)
    check("unescape &quot; yields valid JSON", json.loads(out) == {"whereConditions": []})


def test_unescape_apos_literal():
    check(
        "unescape &#39; yields quoted literal",
        Connect._unescape_value("&#39;Evergreen&#39;") == "'Evergreen'",
    )


def test_unescape_idempotent_on_clean_string():
    check(
        "no-op on entity-free string",
        Connect._unescape_value("Constant_DDS_Amount") == "Constant_DDS_Amount",
    )


def test_unescape_recurses_nested_dict_and_list():
    payload = {
        "versions": [
            {
                "steps": [
                    {"customElement": {"parameters": [
                        {"name": "s1", "value": "{&quot;a&quot;:1}"}]}},
                    {"advancedCondition": {"criteria": [{"value": "&#39;X&#39;"}]}},
                ]
            }
        ]
    }
    out = Connect._unescape_value(payload)
    pv = out["versions"][0]["steps"][0]["customElement"]["parameters"][0]["value"]
    cv = out["versions"][0]["steps"][1]["advancedCondition"]["criteria"][0]["value"]
    check("recursive walk unescapes param value", pv == '{"a":1}')
    check("recursive walk unescapes criteria value", cv == "'X'")


def test_unescape_double_escape_single_pass():
    # &amp;quot; decodes ONE level to &quot; (does NOT over-decode to ").
    check("single-pass on double-escape", Connect._unescape_value("&amp;quot;") == "&quot;")


def test_unescape_preserves_non_strings():
    payload = {"n": 2, "b": True, "x": None, "f": 1.5}
    check("non-string leaves pass through unchanged", Connect._unescape_value(payload) == payload)


def test_unescape_does_not_mutate_input():
    src = {"v": "&quot;"}
    out = Connect._unescape_value(src)
    check(
        "input not mutated, output unescaped",
        src["v"] == "&quot;" and out["v"] == '"',
    )


# ---- Validator HTML-entity WARNING ----

def test_param_value_html_entity_warns():
    overlay = {
        "addSteps": [
            {
                "name": "S",
                "stepType": "BusinessKnowledgeModel",
                "customElement": {
                    "parameters": [
                        {"name": "p", "type": "Literal", "value": "{&quot;a&quot;:[]}"}
                    ]
                },
            }
        ]
    }
    r = validate_overlay(overlay)
    check(
        "HTML entity in param value warns (not errors)",
        r.passed and _has_warning_containing(r, "HTML entities"),
    )


def test_advanced_condition_value_html_entity_warns():
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["versions"][0]["steps"][1]["stepType"] = "AdvancedListFilter"
    d["versions"][0]["steps"][1]["advancedCondition"] = {
        "conditionLogic": "1",
        "criteria": [{"value": "&#39;X&#39;", "valueType": "Literal"}],
    }
    r = validate_definition(d)
    check(
        "HTML entity in advancedCondition criteria value warns",
        _has_warning_containing(r, "HTML entities"),
    )


def test_clean_definition_no_entity_warning():
    r = validate_definition(MINIMAL_PRICING_DEF)
    check(
        "no false-positive entity warning on clean definition",
        not _has_warning_containing(r, "HTML entities"),
    )


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
