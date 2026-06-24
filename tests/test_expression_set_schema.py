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
    DeleteExpressionSet,
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


def test_reference_facility_quantity_example_passes():
    # Environment-specific example retained outside the shipped overlay folder:
    # validates all-three-scope dependency capture without implying broad
    # applicability to every org.
    path = (
        "docs/references/expression-set-overlay-examples/"
        "facility-quantity.overlay.example.json"
    )
    if not os.path.exists(path):
        print("  [SKIP] facility-quantity example not present")
        return
    r = validate_overlay(json.load(open(path)))
    check("reference facility-quantity example validates clean", r.passed and not r.errors)


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


# ---- Duplicate-variable detection (PR #246 review) ----

def test_overlay_addvariables_duplicate_errors():
    # Two addVariables entries with the same name → engine rejects the second
    # PATCH after the version has already been deactivated. Validator must
    # catch this offline so the failure happens before any mutation.
    overlay = {
        "addVariables": [
            {"name": "dup", "type": "Constant", "dataType": "Text", "value": "a"},
            {"name": "dup", "type": "Constant", "dataType": "Text", "value": "b"},
        ]
    }
    r = validate_overlay(overlay)
    check(
        "overlay validator flags duplicate addVariables name",
        not r.passed and _has_error_containing(r, "duplicate added variable name 'dup'"),
    )


def test_definition_variables_duplicate_errors():
    d = {
        "apiName": "Dup_Vars",
        "versions": [{
            "apiName": "Dup_Vars_V1",
            "variables": [
                {"name": "dup", "type": "Constant", "dataType": "Text", "value": "a"},
                {"name": "dup", "type": "Constant", "dataType": "Text", "value": "b"},
            ],
            "steps": [],
        }],
    }
    r = validate_definition(d)
    check(
        "definition validator flags duplicate variable name",
        not r.passed and _has_error_containing(r, "duplicate variable name 'dup'"),
    )


def test_add_variables_helper_dedups_within_block():
    # _add_variables: even if validator is bypassed (skip_validation:true), the
    # apply helper must not append the same name twice within one overlay.
    applier = _OverlayApplier()
    result = applier._add_variables(
        [],
        [
            {"name": "x", "type": "Constant", "dataType": "Text", "value": "a"},
            {"name": "x", "type": "Constant", "dataType": "Text", "value": "b"},
        ],
    )
    check(
        "_add_variables dedups duplicates within one addVariables block",
        len(result) == 1 and result[0]["value"] == "a",
    )


# ---- _build_step pass-through (PR #246 review) ----

def test_build_step_preserves_unknown_overlay_fields():
    # The earlier _build_step allow-listed a subset of fields and silently
    # dropped anything else (e.g. populated passedMessageTokenMappings). A
    # future captured step would validate clean, apply successfully, and then
    # lose that behavior. Pass-through ensures the field reaches the payload.
    applier = _OverlayApplier()
    step_def = {
        "name": "S", "stepType": "BusinessKnowledgeModel",
        "passedMessageTokenMappings": [{"token": "x", "value": "1"}],
        "hasNestedExplainability": True,
        "placement": {"sequenceNumber": 1},
    }
    built = applier._build_step(step_def)
    check(
        "_build_step forwards passedMessageTokenMappings",
        built.get("passedMessageTokenMappings") == [{"token": "x", "value": "1"}],
    )
    check(
        "_build_step forwards hasNestedExplainability",
        built.get("hasNestedExplainability") is True,
    )
    check(
        "_build_step strips overlay-only placement before sending",
        "placement" not in built,
    )


def test_build_step_applies_required_defaults():
    applier = _OverlayApplier()
    built = applier._build_step({"name": "Minimal"})
    check(
        "_build_step still fills required defaults when overlay omits them",
        (
            built.get("stepType") == "BusinessKnowledgeModel"
            and built.get("resultIncluded") is False
            and built.get("shouldExposeExecPathMsgOnly") is True
            and built.get("sequenceNumber") == 1
        ),
    )


# ---- Round 2 review fixes ----

def test_rewrite_version_id_replaces_source_id():
    # PR #246 review: an export-from-source/import-into-target carries the
    # source org's 9QM... version id in versions[0].id; PATCH needs the target
    # org's resolved id.
    payload = {
        "apiName": "X",
        "versions": [{"id": "9QM_source_001", "apiName": "X_V1"}],
    }
    rewritten = Connect._rewrite_version_id(payload, "9QM_target_999")
    check(
        "_rewrite_version_id replaces source version id with target",
        rewritten["versions"][0]["id"] == "9QM_target_999",
    )


def test_rewrite_version_id_idempotent_when_already_matches():
    payload = {"versions": [{"id": "9QM_target", "apiName": "V1"}]}
    rewritten = Connect._rewrite_version_id(payload, "9QM_target")
    check(
        "_rewrite_version_id is a no-op when ids match (same-org re-import)",
        rewritten["versions"][0]["id"] == "9QM_target",
    )


def test_rewrite_version_id_handles_empty_versions():
    # Defensive — shouldn't reach here in practice (validator requires
    # versions[0]) but the helper must not crash.
    check(
        "_rewrite_version_id tolerates missing versions list",
        Connect._rewrite_version_id({"apiName": "X"}, "abc") == {"apiName": "X"},
    )
    check(
        "_rewrite_version_id tolerates empty versions list",
        Connect._rewrite_version_id({"versions": []}, "abc") == {"versions": []},
    )


def test_apply_overlay_dangling_parentstep_caught_locally():
    # PR #246 review (3463489841): removing a parent step but leaving its
    # children produces a dangling parentStep that only the post-merge
    # validation catches. The simulated merge before _run_connect_mutation
    # must surface this so we never deactivate the version on a purely local
    # validation failure.
    applier = _OverlayApplier()
    definition = {
        "apiName": "TestES",
        "versions": [{
            "apiName": "TestES_V1",
            "steps": [
                {"name": "Parent", "stepType": "BusinessKnowledgeModel",
                 "sequenceNumber": 1, "actionType": "PricingSettings"},
                {"name": "Child", "stepType": "BusinessKnowledgeModel",
                 "sequenceNumber": 1, "parentStep": "Parent"},
            ],
        }],
    }
    overlay = {"removeSteps": [{"name": "Parent"}]}
    merged = applier._apply_overlay(definition, overlay)
    # The child still references the removed parent.
    children = [
        s for s in merged["versions"][0]["steps"] if s.get("parentStep") == "Parent"
    ]
    check(
        "_apply_overlay leaves dangling parentStep when only parent is removed",
        len(children) == 1,
    )
    # ... and the definition-level validator catches it.
    r = validate_definition(merged)
    check(
        "validate_definition flags dangling parentStep on the merged definition",
        not r.passed and any(
            "parentStep" in i.message or "parent" in i.message.lower()
            for i in r.errors
        ),
    )


# ---- removeVariables shape (PR #246 live-verification follow-up) ----

def test_delete_rollback_restores_es_version_when_delete_fails():
    # Reviewer (samcheck) flagged a worse inconsistent state: on whole-ES
    # delete failure we restored cascaded procedure plans but left the ES
    # version deactivated, so plans could become active again pointing at an
    # inactive ES. Unlike apply/import (where a failed PATCH may have
    # corrupted the definition mid-write), a failed DELETE leaves the record
    # byte-identical, so reactivation is safe. The fix reactivates the ES
    # FIRST so the plans never reference a deactivated definition.
    import logging

    class _DeleteTask(DeleteExpressionSet):
        def __init__(self):
            self.logger = logging.getLogger("test_delete_task")
            self.logger.addHandler(logging.NullHandler())
            self.options = {
                "expression_set_api_name": "ESX",
                "confirm": True,
                "dry_run": False,
            }
            self.calls = []

        # Stub everything DeleteExpressionSet._run_task touches.
        def _get_expression_set_id(self, api_name):
            return "ES_ID"

        def _get_expression_set_definition_id(self, api_name):
            return "ESD_ID"

        def _resolve_version_by_es_id(self, es_id):
            return {"Id": "ESV_ID", "IsActive": True}

        def _cascade_deactivate_procedure_plans(self, es_def_id, dry_run):
            self.calls.append(("cascade_deactivate", es_def_id))
            return ["PPDV_1"]

        def _set_version_active(self, vid, active, dry_run):
            self.calls.append(("set_version_active", vid, active))

        def _wait_for_version_state(self, vid, active):
            self.calls.append(("wait_version", vid, active))

        def _delete_expression_set_via_connect(self, es_id):
            self.calls.append(("delete_attempt", es_id))
            raise RuntimeError("simulated DELETE failure")

        def _cascade_reactivate_procedure_plans(self, vids, dry_run):
            self.calls.append(("cascade_reactivate", tuple(vids)))

    task = _DeleteTask()
    try:
        task._run_task()
    except RuntimeError:
        pass  # expected — DELETE failure re-raises

    # Sequence must be: cascade-deactivate → ES off → DELETE attempt →
    # ES BACK ON (with confirm) → plans BACK ON.
    op_names = [c[0] for c in task.calls]
    check(
        "delete failure rolls back ES reactivation before plans",
        op_names == [
            "cascade_deactivate",
            "set_version_active",   # initial deactivate (False)
            "wait_version",         # wait False
            "delete_attempt",
            "set_version_active",   # rollback reactivate (True)
            "wait_version",         # wait True
            "cascade_reactivate",   # then plans
        ],
    )
    check(
        "rollback set_version_active(True) called on the same ES version",
        task.calls[4] == ("set_version_active", "ESV_ID", True),
    )
    check(
        "rollback waits for active before re-enabling plans",
        task.calls[5] == ("wait_version", "ESV_ID", True),
    )
    check(
        "rollback reactivates the same cascaded plans that were deactivated",
        task.calls[6] == ("cascade_reactivate", ("PPDV_1",)),
    )


def test_delete_rollback_skips_es_reactivation_when_already_inactive():
    # If the ES version was inactive before the delete attempt, the rollback
    # must NOT activate it (we never deactivated it ourselves).
    import logging

    class _DeleteTask(DeleteExpressionSet):
        def __init__(self):
            self.logger = logging.getLogger("test_delete_task_inactive")
            self.logger.addHandler(logging.NullHandler())
            self.options = {
                "expression_set_api_name": "ESX",
                "confirm": True,
                "dry_run": False,
            }
            self.calls = []

        def _get_expression_set_id(self, api_name):
            return "ES_ID"

        def _get_expression_set_definition_id(self, api_name):
            return "ESD_ID"

        def _resolve_version_by_es_id(self, es_id):
            return {"Id": "ESV_ID", "IsActive": False}  # already inactive

        def _cascade_deactivate_procedure_plans(self, es_def_id, dry_run):
            self.calls.append(("cascade_deactivate", es_def_id))
            return ["PPDV_1"]

        def _set_version_active(self, vid, active, dry_run):
            self.calls.append(("set_version_active", vid, active))

        def _wait_for_version_state(self, vid, active):
            self.calls.append(("wait_version", vid, active))

        def _delete_expression_set_via_connect(self, es_id):
            self.calls.append(("delete_attempt", es_id))
            raise RuntimeError("simulated DELETE failure")

        def _cascade_reactivate_procedure_plans(self, vids, dry_run):
            self.calls.append(("cascade_reactivate", tuple(vids)))

    task = _DeleteTask()
    try:
        task._run_task()
    except RuntimeError:
        pass

    op_names = [c[0] for c in task.calls]
    check(
        "delete failure does NOT reactivate an ES version that was already inactive",
        "set_version_active" not in op_names,
    )
    check(
        "delete failure still reactivates cascaded plans when ES was pre-inactive",
        op_names == ["cascade_deactivate", "delete_attempt", "cascade_reactivate"],
    )


def test_delete_rollback_skips_plan_reactivation_when_es_rollback_fails():
    # Reviewer: if the ES-version rollback fails, reactivating the cascaded
    # procedure plans recreates the exact inconsistent state the rollback
    # was meant to avoid (active plans pointing at an inactive ES). The
    # rollback must leave the plans deactivated in that case and surface
    # the ES failure for manual intervention.
    import logging

    captured_errors = []

    class _DeleteTask(DeleteExpressionSet):
        def __init__(self):
            self.logger = logging.getLogger("test_delete_task_es_rb_fail")
            self.logger.addHandler(logging.NullHandler())
            # Capture logger.error calls so we can assert on the message.
            orig = self.logger.error

            def _capture(msg, *args, **kw):
                captured_errors.append(msg % args if args else msg)
                orig(msg, *args, **kw)

            self.logger.error = _capture
            self.options = {
                "expression_set_api_name": "ESX",
                "confirm": True,
                "dry_run": False,
            }
            self.calls = []

        def _get_expression_set_id(self, api_name):
            return "ES_ID"

        def _get_expression_set_definition_id(self, api_name):
            return "ESD_ID"

        def _resolve_version_by_es_id(self, es_id):
            return {"Id": "ESV_ID", "IsActive": True}

        def _cascade_deactivate_procedure_plans(self, es_def_id, dry_run):
            self.calls.append(("cascade_deactivate", es_def_id))
            return ["PPDV_1", "PPDV_2"]

        def _set_version_active(self, vid, active, dry_run):
            self.calls.append(("set_version_active", vid, active))
            # Fail ONLY on the rollback reactivate (active=True), letting the
            # initial deactivate (active=False) succeed.
            if active is True:
                raise RuntimeError(f"simulated reactivate failure for {vid}")

        def _wait_for_version_state(self, vid, active):
            self.calls.append(("wait_version", vid, active))

        def _delete_expression_set_via_connect(self, es_id):
            self.calls.append(("delete_attempt", es_id))
            raise RuntimeError("simulated DELETE failure")

        def _cascade_reactivate_procedure_plans(self, vids, dry_run):
            self.calls.append(("cascade_reactivate", tuple(vids)))

    task = _DeleteTask()
    try:
        task._run_task()
    except RuntimeError:
        pass  # expected — DELETE failure re-raises

    op_names = [c[0] for c in task.calls]
    check(
        "ES rollback failure does NOT reactivate the cascaded plans",
        "cascade_reactivate" not in op_names,
    )
    check(
        "ES rollback failure DOES attempt to reactivate the ES version",
        ("set_version_active", "ESV_ID", True) in task.calls,
    )
    check(
        "rollback error message names both the ES failure and the plans left deactivated",
        any(
            "ExpressionSetVersion ESV_ID" in e
            and "LEFT DEACTIVATED" in e
            and "PPDV_1" in e
            for e in captured_errors
        ),
    )


def test_delete_single_version_scoped_to_expression_set():
    # Reviewer: single-version delete queries by ApiName only. Two
    # expression sets can have similarly-named versions; the destructive
    # path must require the version to belong to the named expression set.
    import logging

    class _DeleteTask(DeleteExpressionSet):
        def __init__(self, soql_response):
            self.logger = logging.getLogger("test_delete_single")
            self.logger.addHandler(logging.NullHandler())
            self.options = {
                "expression_set_api_name": "ESX",
                "version_api_name": "ESX_V1",
                "confirm": True,
                "dry_run": False,
            }
            self.last_query = None
            self._soql_response = soql_response
            self.delete_calls = []

        def _get_expression_set_id(self, api_name):
            # 9QL = runtime ExpressionSet Id (distinct from any 9QA
            # ExpressionSetDefinition Id) — the version-scope filter must use
            # ExpressionSetId, not ExpressionSetDefinitionId.
            return "9QL000000000001"

        def _soql_query(self, q):
            self.last_query = q
            return self._soql_response

        def _set_version_active(self, *_a, **_kw):
            pass

        def _wait_for_version_state(self, *_a, **_kw):
            pass

        def _delete_sobject(self, sobject, record_id):
            self.delete_calls.append((sobject, record_id))

    # Happy path: SOQL is scoped, delete proceeds.
    task = _DeleteTask([{"Id": "ESV_OK", "IsActive": False}])
    task._run_task()
    check(
        "single-version SOQL filters by ExpressionSetId (runtime FK, not "
        "ExpressionSetDefinitionId)",
        "ExpressionSetId = '9QL000000000001'" in (task.last_query or "")
        and "ExpressionSetDefinitionId" not in (task.last_query or ""),
    )
    check(
        "single-version SOQL still filters by ApiName",
        "ApiName = 'ESX_V1'" in (task.last_query or ""),
    )
    check(
        "single-version delete proceeds when version belongs to the ES",
        task.delete_calls == [("ExpressionSetVersion", "ESV_OK")],
    )

    # Mismatch: version exists with that name but under a DIFFERENT ES → SOQL
    # returns empty (scope filter excludes it). Must raise, not delete.
    task = _DeleteTask([])
    raised = False
    try:
        task._run_task()
    except Exception as exc:
        raised = "not found under expression set 'ESX'" in str(exc)
    check(
        "single-version delete refuses when name belongs to a different ES",
        raised and not task.delete_calls,
    )


def test_overlay_removevariables_accepts_string_list():
    # Live test surfaced that _remove_variables crashed with a cryptic
    # "string indices must be integers" when given a bare list of names —
    # the natural shape for an operation that has no other field to address.
    # Schema must accept it, and the helper must remove by name.
    overlay = {"removeVariables": ["v1", "v2"]}
    r = validate_overlay(overlay)
    check(
        "validator accepts removeVariables: [string, string]",
        r.passed,
    )
    applier = _OverlayApplier()
    remaining = applier._remove_variables(
        [{"name": "v1"}, {"name": "v2"}, {"name": "keep"}],
        ["v1", "v2"],
    )
    check(
        "_remove_variables removes by bare-string name",
        [v["name"] for v in remaining] == ["keep"],
    )


def test_overlay_removevariables_accepts_object_list():
    # Object shape stays supported for parity with removeSteps and so the
    # JSON can grow future fields without a breaking change.
    overlay = {"removeVariables": [{"name": "v1"}, {"name": "v2"}]}
    r = validate_overlay(overlay)
    check(
        "validator accepts removeVariables: [{name}, {name}]",
        r.passed,
    )
    applier = _OverlayApplier()
    remaining = applier._remove_variables(
        [{"name": "v1"}, {"name": "v2"}, {"name": "keep"}],
        [{"name": "v1"}, {"name": "v2"}],
    )
    check(
        "_remove_variables removes by object-with-name",
        [v["name"] for v in remaining] == ["keep"],
    )


def test_overlay_removevariables_rejects_bad_shape():
    overlay = {"removeVariables": [123]}
    r = validate_overlay(overlay)
    check(
        "validator rejects non-string non-object removeVariables entry",
        not r.passed and _has_error_containing(r, "string name or an object"),
    )
    overlay = {"removeVariables": [""]}
    r = validate_overlay(overlay)
    check(
        "validator rejects empty-string removeVariables entry",
        not r.passed and _has_error_containing(r, "non-empty"),
    )
    overlay = {"removeVariables": [{"notName": "v1"}]}
    r = validate_overlay(overlay)
    check(
        "validator rejects object entry without 'name'",
        not r.passed and _has_error_containing(r, "name"),
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
