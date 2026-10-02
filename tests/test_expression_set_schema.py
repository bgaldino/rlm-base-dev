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


def test_output_only_top_level_warns():
    # Output-only fields (id/error) emitted by the Connect GET are tolerated on
    # an input payload (PATCH full-graph replace) but warned so authors don't
    # hand-maintain them.
    d = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    d["id"] = "0QM000000000000AAA"
    d["error"] = None
    r = validate_definition(d)
    check(
        "top-level output-only fields warn not error",
        r.passed and _has_warning_containing(r, "output-only field"),
    )


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


def test_shipped_approval_flags_passes_and_resets_first():
    # The approval-flags overlay must validate clean, run its reset step before
    # the three band steps (so a reprice that lowers the discount clears the old
    # flag), and never write the line Description.
    path = "datasets/expression_set_overlays/approval_flags.json"
    if not os.path.exists(path):
        print("  [SKIP] approval_flags.json not present")
        return
    ov = json.load(open(path))
    r = validate_overlay(ov)
    check("shipped approval_flags.json validates clean", r.passed and not r.errors)
    top = [s["name"] for s in ov.get("addSteps", []) if not s.get("parentStep")]
    check(
        "approval_flags reset step is the first top-level step",
        bool(top) and top[0] == "RLMApprovalFlagsReset" and len(top) == 4,
    )
    check(
        "approval_flags steps never reference ItemDescription",
        "ItemDescription" not in json.dumps(ov.get("addSteps", [])),
    )
    steps = {s["name"]: s for s in ov["addSteps"]}
    reset = steps["RLMApprovalFlagsResetAllLines"]["advancedCondition"]
    check("approval_flags reset covers blank and set discounts",
          reset["conditionLogic"] == "1 OR 2" and
          [c["operator"] for c in reset["criteria"]] == ["IsNull", "IsNotNull"] and
          all(c["sourceFieldName"] == "ItemDiscountPercentage" for c in reset["criteria"]))
    variables = {v["name"]: v["value"] for v in ov["addVariables"]}
    for tier, low, high, level, label in (
        ("None", None, None, "0", ""),
        ("Manager", "15", "25", "1", "🟡 Manager"),
        ("Director", "25", "35", "2", "🟠 Director"),
        ("VP", "35", "100", "3", "🔴 VP"),
    ):
        if low is not None:
            band = steps[f"RLMApprovalFlags{tier}Band"]["advancedCondition"]
            check(f"approval_flags {tier} band is [{low}, {high})",
                  band["conditionLogic"] == "1 AND 2 AND 3" and
                  [(c["operator"], c.get("value"), c["sourceFieldName"])
                   for c in band["criteria"]] == [
                       ("GreaterThanOrEquals", low, "ItemDiscountPercentage"),
                       ("LessThan", high, "ItemDiscountPercentage"),
                       ("IsNotNull", None, "ItemDiscountPercentage"),
                   ])
        check(f"approval_flags {tier} constants are correct",
              variables[f"RLMApprovalLevel{tier}"] == level and
              variables[f"RLMApprovalLabel{tier}"] == label)
        parameters = {p["name"]: p["value"] for p in
                      steps[f"RLMApprovalFlagsAssign{tier}"]["customElement"]["parameters"]}
        check(f"approval_flags {tier} writes both approval outputs",
              parameters["section-0-input1"] == f"RLMApprovalLevel{tier}" and
              parameters["section-1-input1"] == f"RLMApprovalLabel{tier}" and
              parameters["section-0-output"] == "RLM_Approval_Level_Calc__c" and
              parameters["section-1-output"] == "RLM_Approval__c" and
              all(json.loads(parameters[f"sectionJsonString{i}"])["whereConditions"][0]
                  ["value"]["value"] == output for i, output in (
                      (2, "RLM_Approval_Level_Calc__c"), (3, "RLM_Approval__c"))))


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


class _MutationTask(_CascadeTask):
    """_CascadeTask plus one ExpressionSetVersion ("ESV") for the lifecycle."""

    def __init__(self, plans, esv_active=True, fail_plan_reactivate=False,
                 fail_version_wait=False, esv_reads_active=False, fail_plan_ids=(),
                 esv_reactivate_error=None):
        import logging

        super().__init__(dict(plans, ESV=esv_active))
        self.fail_plan_reactivate = fail_plan_reactivate
        self.fail_version_wait = fail_version_wait
        # Models the stale read that made the deactivation poll time out.
        self.esv_reads_active = esv_reads_active
        self.fail_plan_ids = set(fail_plan_ids)
        self.esv_reactivate_error = esv_reactivate_error
        self.plan_ids = sorted(plans)
        # Plan reactivations to fail before they start succeeding.
        self.plan_reactivate_failures_left = 0
        self.logs = []

        class _Capture(logging.Handler):
            def emit(handler, record):
                self.logs.append(record.getMessage())

        self.logger = logging.getLogger(f"test_mutation_task_{id(self)}")
        self.logger.addHandler(_Capture())
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.org_config = type("Org", (), {"username": "user@example.org"})()

    def _find_referencing_procedure_plans(self, es_def_id):
        return [{"ProcedurePlanSection": {"ProcedurePlanVersionId": vid}}
                for vid in self.plan_ids]

    def _soql_query(self, soql):
        if any(f"'{rid}'" in soql for rid in getattr(self, "missing_ids", ())):
            return []
        if self.esv_reads_active and "FROM ExpressionSetVersion" in soql:
            return [{"Id": "ESV", "IsActive": True}]
        if getattr(self, "esv_reads_inactive", False) and "FROM ExpressionSetVersion" in soql:
            return [{"Id": "ESV", "IsActive": False}]
        return super()._soql_query(soql)

    def _patch_sobject(self, sobject, record_id, payload):
        if (payload.get("IsActive") and sobject == "ProcedurePlanDefinitionVersion"
                and (self.fail_plan_reactivate or record_id in self.fail_plan_ids)):
            raise RuntimeError(f"plan reactivate boom {record_id}")
        if (payload.get("IsActive") and sobject == "ProcedurePlanDefinitionVersion"
                and self.plan_reactivate_failures_left):
            self.plan_reactivate_failures_left -= 1
            raise RuntimeError(f"plan reactivate blip {record_id}")
        if sobject == "ExpressionSetVersion" and payload.get("IsActive") is False:
            self.esv_reads_inactive = False
        if sobject == "ExpressionSetVersion" and payload.get("IsActive"):
            if self.esv_reactivate_error:
                raise RuntimeError(self.esv_reactivate_error)
            self.esv_reads_active = False
        super()._patch_sobject(sobject, record_id, payload)

    def _wait_for_version_state(self, version_id, active):
        if self.fail_version_wait and active is False:
            raise RuntimeError("version state poll timed out")

    def run(self, activate_after=True, succeed=False):
        def boom():
            if not succeed:
                raise RuntimeError("PATCH boom")
        try:
            self._run_connect_mutation(
                es_def_id="ESD", esv={"Id": "ESV", "IsActive": True}, mutate=boom,
                dry_run=False, activate_after=activate_after, cascade=True,
                verb="Import",
            )
        except Exception as exc:  # noqa: BLE001 -- the test inspects whatever was raised
            return exc
        return None


def test_failed_connect_mutation_keeps_procedure_plans_online():
    # Pack 170: a failed PATCH used to leave the cascaded plan deactivated, which
    # silently takes pricing offline (plausible numbers, no error).
    task = _MutationTask({"PPV_A": True})
    error = task.run()
    check("failed PATCH still raises", error is not None and "boom" in str(error))
    check("failed PATCH leaves the expression-set version deactivated",
          task.states["ESV"] is False)
    check("failed PATCH reactivates the cascaded procedure plan",
          task.states["PPV_A"] is True)
    # Round 13: no activation command for a version a failed PATCH may have
    # half-written.
    check("health report names the inactive version without an activation command",
          any("ExpressionSetVersion ESV: no command" in m for m in task.logs)
          and not any("--record-id ESV" in m for m in task.logs))

    earlier = _MutationTask({"PPV_A": True, "PPV_B": False})
    earlier.run()
    check("an inactive plan version this run did not take down is left as found",
          earlier.states["PPV_B"] is False)
    check("it is listed for inspection without a restore command",
          any("PPV_B" in m and "check which" in m for m in earlier.logs)
          and not any("--record-id PPV_B" in m for m in earlier.logs))

    reactivate_fails = _MutationTask({"PPV_A": True}, fail_plan_reactivate=True)
    error2 = reactivate_fails.run(succeed=True)
    check("the plan restore command targets the org's username",
          any("--record-id PPV_A" in m and "user@example.org" in m
              for m in reactivate_fails.logs))
    check("a failed plan reactivation after a successful mutation still raises",
          error2 is not None and "plan reactivate boom" in str(error2))
    check("a failed plan reactivation still prints the plan's restore command",
          any("--record-id PPV_A" in m for m in reactivate_fails.logs))

    # PR #491 review round 2: the version PATCH lands but its poll times out.
    unconfirmed = _MutationTask({"PPV_A": True}, fail_version_wait=True)
    error3 = unconfirmed.run(succeed=True)
    check("an unconfirmed version deactivation raises",
          error3 is not None and "timed out" in str(error3))
    check("an unconfirmed version deactivation restores the version and the plan",
          unconfirmed.states["ESV"] is True and unconfirmed.states["PPV_A"] is True)

    # PR #491 review round 4: a stale read must not skip the reactivation PATCH.
    stale = _MutationTask({"PPV_A": True}, fail_version_wait=True, esv_reads_active=True)
    stale.run(succeed=True)
    check("a stale read still gets a real version reactivation",
          stale.states["ESV"] is True)

    # Round 5: a rejected forced reactivation must propagate despite a stale read.
    rejected = _MutationTask({"PPV_A": True}, fail_version_wait=True,
                             esv_reads_active=True, esv_reactivate_error="version reactivate boom")
    error5 = rejected.run(succeed=True)
    check("a rejected forced reactivation propagates despite a stale active read",
          error5 is not None and "version reactivate boom" in str(error5))
    check("plans are still restored after a rejected forced reactivation",
          rejected.states["PPV_A"] is True)
    enabled = _MutationTask({}, esv_reactivate_error="An enabled Expression Set Version cannot be updated/deleted.")
    try:
        enabled._set_version_active("ESV", True, False, force=True)
        ok6 = True
    except Exception:
        ok6 = False
    check("a forced PATCH rejected as already enabled is accepted", ok6)

    # Round 6: confirm the version off before restoring plans after a failed PATCH.
    reenabled = _MutationTask({"PPV_A": True})

    def reenable_then_fail():
        reenabled.states["ESV"] = True
        raise RuntimeError("PATCH boom")
    try:
        reenabled._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": True}, mutate=reenable_then_fail,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("a version a failed PATCH re-enabled is turned off again",
          reenabled.states["ESV"] is False)
    check("the plans are restored once the version is confirmed off",
          reenabled.states["PPV_A"] is True)
    # Round 9: if the version can't be confirmed off, the plans stay off and
    # the report says to deactivate the version before restoring them.
    stuck = _MutationTask({"PPV_A": True})

    def reenable_and_stick():
        stuck.states["ESV"] = True
        stuck.fail_on_deactivate = "ESV"
        raise RuntimeError("PATCH boom")
    try:
        stuck._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": True}, mutate=reenable_and_stick,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("plans stay off when the version can't be confirmed off",
          stuck.states["PPV_A"] is False)
    check("the report says to deactivate the unconfirmed version first",
          any("NOT confirmed inactive" in m for m in stuck.logs)
          and not any("Restore the plan before reading" in m for m in stuck.logs))
    # Round 10: a failed PATCH that re-enables the version is turned off even
    # with no plans to restore, under cascade=False or activate_after=False,
    # and when the version was off before the run.
    for label, plans, kw, was_active in (
        ("with no referencing plans", {}, {"cascade": True, "activate_after": True}, True),
        ("under cascade=False", {"PPV_A": True}, {"cascade": False, "activate_after": True}, True),
        ("under activate_after=False", {"PPV_A": True}, {"cascade": True, "activate_after": False}, True),
        ("when it was off before the run", {}, {"cascade": True, "activate_after": True}, False),
    ):
        task10 = _MutationTask(plans, esv_active=was_active)

        def reenable10(task10=task10):
            task10.states["ESV"] = True
            raise RuntimeError("PATCH boom")
        try:
            task10._run_connect_mutation(
                es_def_id="ESD", esv={"Id": "ESV", "IsActive": was_active}, mutate=reenable10,
                dry_run=False, verb="Import", **kw)
        except Exception:  # noqa: BLE001
            pass
        check(f"a version a failed PATCH re-enabled is turned off {label}",
              task10.states["ESV"] is False)
    stuck10 = _MutationTask({})

    def reenable_and_stick10():
        stuck10.states["ESV"] = True
        stuck10.fail_on_deactivate = "ESV"
        raise RuntimeError("PATCH boom")
    try:
        stuck10._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": True}, mutate=reenable_and_stick10,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("an unconfirmed version is flagged even with no plans involved",
          any("NOT confirmed inactive" in m for m in stuck10.logs)
          and not any("are active" in m for m in stuck10.logs))
    # Round 11: a record whose state read returns no row is reported as
    # unknown, never as active.
    for label, missing in (("plan", {"PPV_A"}), ("version", {"ESV"})):
        task11 = _MutationTask({"PPV_A": True})
        task11.missing_ids = missing
        task11._report_procedure_health("ESD", "ESV", taken_down=["PPV_A"],
                                        version_taken_down=True)
        check(f"a {label} with no state row is reported as unknown, not active",
              any("could not read the state" in m and next(iter(missing)) in m
                  for m in task11.logs)
              and not any("are active" in m for m in task11.logs))
    # A plan this run took down is read even if no option references it any more.
    task12 = _MutationTask({"PPV_A": True})
    task12.states["PPV_A"] = False
    task12.plan_ids = []
    task12._report_procedure_health("ESD", "ESV", taken_down=["PPV_A"],
                                    version_taken_down=False)
    check("a plan this run took down is reported even when no longer referenced",
          any("--record-id PPV_A" in m for m in task12.logs))
    # Round 12: version off before the run, plan active; the failed PATCH
    # re-enables the version and it can't be turned off. The plan must not keep
    # routing pricing to it, and gets a restore command.
    pre_off12 = _MutationTask({"PPV_A": True}, esv_active=False)

    def reenable_and_stick12():
        pre_off12.states["ESV"] = True
        pre_off12.fail_on_deactivate = "ESV"
        raise RuntimeError("PATCH boom")
    try:
        pre_off12._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": False}, mutate=reenable_and_stick12,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("an active plan is taken off when an unconfirmed version can't be turned off",
          pre_off12.states["PPV_A"] is False)
    check("the plan it took off gets a restore command",
          any("--record-id PPV_A" in m for m in pre_off12.logs))
    # Round 13: the emergency shutdown keeps the plans it turned off even when
    # another plan fails, and names them for restore.
    pre_off13 = _MutationTask({"PPV_A": True, "PPV_B": True}, esv_active=False)

    def reenable_and_stick13():
        pre_off13.states["ESV"] = True
        pre_off13.fail_on_deactivate = "ESV"
        raise RuntimeError("PATCH boom")
    real_patch = pre_off13._patch_sobject

    def patch13(sobject, record_id, payload):
        if record_id == "PPV_A" and payload.get("IsActive") is False:
            raise RuntimeError("plan deactivate boom PPV_A")
        return real_patch(sobject, record_id, payload)
    pre_off13._patch_sobject = patch13
    try:
        pre_off13._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": False}, mutate=reenable_and_stick13,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("the emergency shutdown doesn't roll back a plan it turned off",
          pre_off13.states["PPV_A"] is True and pre_off13.states["PPV_B"] is False)
    check("the plan it turned off gets a restore command",
          any("--record-id PPV_B" in m for m in pre_off13.logs))
    # Round 7: a stale false read must not skip the deactivation.
    stale_off = _MutationTask({"PPV_A": True})

    def reenable_with_stale_read():
        stale_off.states["ESV"] = True
        stale_off.esv_reads_inactive = True
        raise RuntimeError("PATCH boom")
    try:
        stale_off._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": True}, mutate=reenable_with_stale_read,
            dry_run=False, activate_after=True, cascade=True, verb="Import")
    except Exception:  # noqa: BLE001
        pass
    check("a re-enabled version behind a stale false read is really turned off",
          stale_off.states["ESV"] is False)
    plan_fails = _MutationTask({"PPV_A": True}, fail_plan_ids={"PPV_A"})
    error7 = plan_fails.run()
    check("a plan restore failure after a failed PATCH is in the raised error",
          error7 is not None and "recovery also failed" in str(error7) and "PPV_A" in str(error7))

    # Round 8: the cascade turns PPV_A off, fails on PPV_B and can't roll PPV_A
    # back. The partial IDs must still reach recovery and the health report.
    partial = _MutationTask({"PPV_A": True, "PPV_B": True}, fail_plan_ids={"PPV_A"})
    partial.fail_on_deactivate = "PPV_B"
    error8 = partial.run()
    check("a failed cascade rollback still raises", error8 is not None)
    check("a plan the failed cascade left off gets a restore command",
          any("--record-id PPV_A" in m for m in partial.logs))
    check("nothing was written, so the report doesn't warn of a half-written version",
          any("Restore the plan before reading" in m for m in partial.logs)
          and not any("NOT confirmed inactive" in m for m in partial.logs))
    blip = _MutationTask({"PPV_A": True, "PPV_B": True})
    blip.fail_on_deactivate = "PPV_B"
    blip.plan_reactivate_failures_left = 1
    blip.run()
    check("recovery retries a plan the failed cascade rollback left off",
          blip.states["PPV_A"] is True)

    # Round 4: one failing plan must not stop the next.
    multi = _MutationTask({"PPV_A": True, "PPV_B": True}, fail_plan_ids={"PPV_A"})
    error4 = multi.run(succeed=True)
    check("one failing plan does not stop the next from being reactivated",
          multi.states["PPV_B"] is True)
    check("the failing plan is named in the raised error",
          error4 is not None and "PPV_A" in str(error4))

    # Round 4: an already-inactive version is reported as such, not as active.
    pre_off = _MutationTask({"PPV_A": True}, esv_active=False)
    try:
        pre_off._run_connect_mutation(
            es_def_id="ESD", esv={"Id": "ESV", "IsActive": False},
            mutate=lambda: (_ for _ in ()).throw(RuntimeError("PATCH boom")),
            dry_run=False, activate_after=True, cascade=True, verb="Import",
        )
    except RuntimeError:
        pass
    check("an already-inactive version is not reported as active",
          not any("are active" in m for m in pre_off.logs))
    check("an already-inactive version is reported as it was before the run",
          any("as it was before this run" in m for m in pre_off.logs))

    kept_off = _MutationTask({"PPV_A": True})
    kept_off.run(activate_after=False)
    check("activate_after=False leaves the cascaded plan off after a failure",
          kept_off.states["PPV_A"] is False)


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


def test_delete_rollback_retries_plans_a_failed_cascade_left_off():
    # Round 8: when the cascade's own rollback fails, it raises before
    # returning; the delete rollback must still retry the plans it left off.
    import logging

    # The module's own symbol, so the suite still runs without CumulusCI.
    from tasks.rlm_expression_set_connect import TaskOptionsError

    class _DeleteTask(DeleteExpressionSet):
        def __init__(self):
            self.logger = logging.getLogger("test_delete_partial_cascade")
            self.logger.addHandler(logging.NullHandler())
            self.options = {"expression_set_api_name": "ESX", "confirm": True,
                            "dry_run": False}
            self.calls = []

        def _get_expression_set_id(self, api_name):
            return "ES_ID"

        def _get_expression_set_definition_id(self, api_name):
            return "ESD_ID"

        def _resolve_version_by_es_id(self, es_id):
            return {"Id": "ESV_ID", "IsActive": True}

        def _cascade_deactivate_procedure_plans(self, es_def_id, dry_run):
            error = TaskOptionsError("cascade and rollback failed")
            error.left_inactive = ["PPDV_1"]
            raise error

        def _cascade_reactivate_procedure_plans(self, vids, dry_run):
            self.calls.append(("cascade_reactivate", tuple(vids)))

    task = _DeleteTask()
    try:
        task._run_task()
    except TaskOptionsError:
        pass
    check("delete rollback retries a plan the failed cascade left off",
          task.calls == [("cascade_reactivate", ("PPDV_1",))])


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


def test_overlay_content_conflict_and_readback():
    from copy import deepcopy
    from tasks.expression_set_schema import overlay_step_content_errors
    from scripts.expression_sets._schema import overlay_step_content_errors as vendored
    task = _OverlayApplier()
    step = {"name": "S", "sequenceNumber": 1, "customElement": {"parameters": [
        {"name": "formula", "type": "Formula", "value": "1"}]}}
    changed = deepcopy(step)
    changed["customElement"]["parameters"][0]["value"] = "777"
    raised = False
    try:
        task._add_steps([deepcopy(step)], [changed])
    except Exception as exc:
        raised = "updateSteps" in str(exc)
    check("CCI conflicting addSteps fails before any mutation", raised)
    check("CCI matching addSteps stays idempotent", task._add_steps([deepcopy(step)], [step]) == [step])
    anchor = {"name": "Anchor", "sequenceNumber": 1}
    added = {"name": "Added", "sequenceNumber": 1, "placement": {"afterStep": "Anchor"}}
    once = task._add_steps([deepcopy(anchor)], [added])
    check("add replay ignores overwritten top-level sequence", task._add_steps(deepcopy(once), [added]) == once)
    shared = [{"name": "First", "placement": {"afterStep": "Anchor"}},
              {"name": "Second", "placement": {"afterStep": "Anchor"}}]
    shared_once = task._add_steps([deepcopy(anchor)], shared)
    check("shared-anchor batch is replayable", task._add_steps(deepcopy(shared_once), shared) == shared_once)
    before = {"steps": [{"name": "Anchor", "sequenceNumber": 1}, {"name": "Added", "sequenceNumber": 2}]}
    after = {"steps": [{"name": "Anchor", "sequenceNumber": 2}, {"name": "Added", "sequenceNumber": 1}]}
    ignored_shift = deepcopy(after)
    ignored_shift["steps"][0]["sequenceNumber"] = 1
    check("verification detects ignored sibling sequence shift", bool(overlay_step_content_errors(
        {"reorderSteps": [{"name": "Added", "sequenceNumber": 1}]}, after, ignored_shift)))

    expected = {"versions": [{"apiName": "V1", "steps": [changed]}]}
    actual = {"versions": [{"apiName": "V1", "steps": [step]}]}
    task._get_expression_set_via_connect = lambda _: actual
    task.options = {"version_api_name": "V1"}
    for op in ("addSteps", "updateSteps"):
        overlay = {op: [changed]}
        raised = False
        try:
            task._verify_overlay("9QLx", overlay, expected)
        except Exception as exc:
            raised = "formula" in str(exc)
        check("CCI " + op + " rejects stale read-back content", raised)
        args = (overlay, expected["versions"][0], actual["versions"][0])
        check("validator copies agree for " + op,
              overlay_step_content_errors(*args) == vendored(*args))
    # Exact name-set checks must work in both directions, including an empty
    # expected graph and overlays whose edits only concern variables.
    extra_cases = [
        ({"updateSteps": [{"name": "Formula"}]}, {"steps": [{"name": "Formula"}]},
         {"steps": [{"name": "Formula"}, {"name": "Unexpected"}]}),
        ({"removeSteps": [{"name": "Removed"}]}, {"steps": []},
         {"steps": [{"name": "Unexpected"}]}),
        ({"addVariables": [{"name": "Variable"}]}, {"steps": [{"name": "Formula"}]},
         {"steps": [{"name": "Formula"}, {"name": "Unexpected"}]}),
    ]
    for index, (overlay, wanted, stored) in enumerate(extra_cases):
        errors = overlay_step_content_errors(overlay, wanted, stored)
        check(f"unexpected stored step fails case {index}",
              any("unexpected step 'Unexpected'" in error for error in errors))
        check(f"matching graph passes case {index}",
              not overlay_step_content_errors(overlay, wanted, wanted))
        check(f"extra-step copies agree case {index}",
              errors == vendored(overlay, wanted, stored))
        task._get_expression_set_via_connect = lambda _, stored=stored: {"versions": [dict(stored, apiName="V1")]}
        try:
            task._verify_overlay("9QLx", overlay, {"versions": [dict(wanted, apiName="V1")]})
            check(f"CCI rejects unexpected step case {index}", False)
        except Exception as exc:
            check(f"CCI rejects unexpected step case {index}", "unexpected step" in str(exc))

    task._get_expression_set_via_connect = lambda _: expected
    task._verify_overlay("9QLx", {"updateSteps": [changed]}, expected)
    check("CCI matching updated body verifies", True)
    placement_state = {"versions": [{"apiName": "V1", "steps": [
        {"name": "Existing", "sequenceNumber": 1}, {"name": "Anchor", "sequenceNumber": 2}]}]}
    task._get_expression_set_via_connect = lambda _: placement_state
    try:
        task._verify_overlay("9QLx", {"addSteps": [{"name": "Existing", "placement": {"afterStep": "Anchor"}}]}, placement_state)
        check("CCI retains placement verification", False)
    except Exception as exc:
        check("CCI retains placement verification", "sequenceNumber" in str(exc))



class _LabelTask(Connect):
    """Bare instance with an in-memory ESV/ESDV for label-preservation tests.

    Only HTTP is faked: the real ``_patch_expression_set_via_connect`` runs
    (against a stubbed ``requests``) so the tests exercise the same
    clobber-flag path production does.
    """

    def __init__(self, labels, active=True, tooling_patch_fails=False, options=None):
        import logging

        self.logger = logging.getLogger("test_label_task")
        self.logger.addHandler(logging.NullHandler())
        self.options = dict(options or {})
        self.active = active
        self.tooling_patch_fails = tooling_patch_fails
        self.steps = [{"name": n, "label": l} for n, l in labels.items()]
        self.events = []

    # activation
    def _set_version_active(self, version_id, active, dry_run, *, force=False):
        self.events.append(("active", active))
        self.active = active

    def _wait_for_version_state(self, version_id, active):
        pass

    def _soql_query(self, soql):
        return [{"Id": "9QMx", "ApiName": "V1", "IsActive": self.active, "VersionNumber": 1}]

    # Tooling
    def _tooling_request(self, method, path, payload=None):
        if method == "GET" and path.startswith("query"):
            return {"records": [{"Id": "9QBx"}]}
        if method == "GET":
            return {"Metadata": {"steps": [dict(s) for s in self.steps],
                                 "urls": {"x": "y"}}}
        self.events.append(("tooling_patch", self.active))
        if self.tooling_patch_fails:
            raise RuntimeError("simulated Tooling failure")
        if "urls" in payload["Metadata"]:
            raise RuntimeError("urls must be stripped")
        self.steps = [dict(s) for s in payload["Metadata"]["steps"]]
        return {}

    # Connect PATCH: the real helper, with requests stubbed to "succeed" and
    # the platform side effect of resetting every label to its name.
    def connect_patch(self, add=()):
        import tasks.rlm_expression_set_connect as mod

        class _Resp:
            ok = True
            content = b""

        real = mod.requests.patch
        mod.requests.patch = lambda *a, **k: _Resp()
        try:
            type(self)._base_url = "https://x/services/data/v68.0"
            type(self)._headers = {}
            self._patch_expression_set_via_connect("9QLx", {})
        finally:
            mod.requests.patch = real
        self.steps = [{"name": s["name"], "label": s["name"]} for s in self.steps]
        self.steps += [{"name": n, "label": n} for n in add]

    def run(self, mutate, **kw):
        self._run_connect_mutation(
            es_def_id="9QAx", esv={"Id": "9QMx", "ApiName": "V1",
                                   "IsActive": self.active, "VersionNumber": 1},
            mutate=mutate, dry_run=kw.pop("dry_run", False),
            activate_after=kw.pop("activate_after", True), cascade=kw.pop("cascade", False),
            verb="test", **kw,
        )

    def label(self, name):
        return next(s["label"] for s in self.steps if s["name"] == name)


def test_connect_mutation_restores_clobbered_labels():
    task = _LabelTask({"GetPrices": "Get Prices", "Map": "Map Line Item"})
    task.run(lambda: task.connect_patch(add=["NewStep"]),
             extra_labels={"NewStep": "New Step"})
    check("labels restored after Connect PATCH",
          task.label("GetPrices") == "Get Prices" and task.label("Map") == "Map Line Item")
    check("overlay labels applied to added steps", task.label("NewStep") == "New Step")
    check("one deactivate/relabel/reactivate cycle",
          task.events == [("active", False), ("tooling_patch", False), ("active", True)])


def test_connect_mutation_skips_restore_without_patch():
    task = _LabelTask({"A": "A Label"})
    task.run(lambda: None)
    check("no Tooling PATCH when nothing was PATCHed",
          not any(e[0] == "tooling_patch" for e in task.events))


def test_connect_mutation_label_restore_opt_out():
    task = _LabelTask({"A": "A Label"}, options={"preserve_labels": "false"})
    task.run(lambda: task.connect_patch())
    check("preserve_labels=false leaves labels clobbered", task.label("A") == "A")


def test_connect_mutation_dry_run_does_not_relabel():
    task = _LabelTask({"A": "A Label"})
    task.run(lambda: None, dry_run=True)
    check("dry-run makes no Tooling PATCH",
          not any(e[0] == "tooling_patch" for e in task.events))
    from unittest.mock import Mock
    disabled = _LabelTask({"A": "A Label"}, options={"preserve_labels": "false"})
    disabled.logger = Mock()
    disabled.run(lambda: None, dry_run=True)
    check("dry-run with preservation disabled omits restoration claim",
          not any("restore step labels" in str(call).lower()
                  for call in disabled.logger.info.call_args_list))


def test_label_restore_failure_is_nonfatal_and_reactivates():
    task = _LabelTask({"A": "A Label"}, tooling_patch_fails=True)
    try:
        task.run(lambda: task.connect_patch())
        raised = False
    except Exception:
        raised = True
    check("label-restore failure does not fail the mutation", not raised)
    check("label-restore failure still reactivates the version", task.active is True)


def test_label_restore_lifecycle_failures_propagate():
    class FailingLifecycleTask(_LabelTask):
        def __init__(self, phase, label_fails):
            super().__init__({"A": "A Label"}, tooling_patch_fails=label_fails)
            self.phase = phase
            self.cycles = 0
            self.plan_active = True

        def _set_version_active(self, version_id, active, dry_run, *, force=False):
            if not active:
                self.cycles += 1
            if self.cycles == 1 and self.phase == ("activate" if active else "deactivate"):
                raise RuntimeError(self.phase + " failed")
            super()._set_version_active(version_id, active, dry_run, force=force)

        def _wait_for_version_state(self, version_id, active):
            if self.cycles == 1 and active and self.phase == "wait":
                raise RuntimeError("wait failed")

        def _cascade_deactivate_procedure_plans(self, es_def_id, dry_run, *, rollback=True):
            self.plan_active = False
            return ["plan"]

        def _cascade_reactivate_procedure_plans(self, version_ids, dry_run):
            if self.cycles == 1 and self.phase == "cascade":
                raise RuntimeError("cascade failed")
            self.plan_active = True

    for phase in ("deactivate", "activate", "wait", "cascade"):
        for label_fails in (False, True):
            task = FailingLifecycleTask(phase, label_fails)
            try:
                task.run(lambda: task.connect_patch(), cascade=True)
            except RuntimeError as exc:
                propagated = str(exc) == phase + " failed"
            else:
                propagated = False
            check(f"mutation cycle {phase} failure propagates (label_fails={label_fails})",
                  propagated)
            if phase == "activate":
                check("failed reactivation leaves version inactive and reports failure",
                      not task.active and propagated)
            if phase == "cascade":
                check("failed plan restoration leaves plan inactive and reports failure",
                      not task.plan_active and propagated)


def test_label_restore_keeps_version_inactive_when_requested():
    task = _LabelTask({"A": "A Label"})
    task.run(lambda: task.connect_patch(), activate_after=False)
    check("labels restored with activate_after=false",
          task.label("A") == "A Label" and task.active is False)


def test_failed_mutation_skips_label_restore():
    task = _LabelTask({"A": "A Label"})

    def mutate():
        task.connect_patch()
        raise RuntimeError("verify failed")

    try:
        task.run(mutate)
    except RuntimeError:
        pass
    check("failed mutation is not relabelled or reactivated",
          not any(e[0] == "tooling_patch" for e in task.events) and task.active is False)


def test_overlay_labels_validation_parity():
    from scripts.expression_sets._schema import validate_overlay as toolkit_validate
    for labels, valid in (
        (None, True), ({}, True), ({"StepA": "Readable label"}, True),
        (["StepA"], False), ({"StepA": 123}, False),
    ):
        for validate in (validate_overlay, toolkit_validate):
            result = validate({"addSteps": [], "labels": labels})
            check(f"{validate.__module__}: labels {labels!r} accepted={valid}",
                  result.passed == valid)


def test_overlay_step_label_validation_parity():
    from scripts.expression_sets._schema import validate_overlay as toolkit_validate
    for operation in ("addSteps", "updateSteps"):
        for label, valid in (("Readable label", True), (123, False), (None, False)):
            for validate in (validate_overlay, toolkit_validate):
                result = validate({operation: [{"name": "StepA", "label": label}]})
                flagged = any(
                    i.location == f"{operation}[0].label" for i in result.errors
                )
                check(f"{validate.__module__}: {operation} label {label!r} accepted={valid}",
                      flagged != valid)
        for scalar in (5, "StepA"):
            for validate in (validate_overlay, toolkit_validate):
                try:
                    result = validate({operation: scalar})
                    ok = not result.passed
                except Exception as exc:  # noqa: BLE001 — the regression is a crash
                    ok = False
                    print(f"    raised {exc!r}")
                check(f"{validate.__module__}: non-list {operation}={scalar!r} is reported, not a crash", ok)


def test_overlay_labels_merge_top_level_and_per_step():
    labels = Connect._overlay_labels({
        "labels": {"A": "Top A", "B": "Top B"},
        "addSteps": [{"name": "B", "label": "Step B"}, {"name": "C"}],
        "updateSteps": [{"name": "A", "label": "Updated A"}],
    })
    check("overlay labels: per-step wins over top-level",
          labels == {"A": "Updated A", "B": "Step B"})


def test_update_step_overlay_metadata_and_change_counts():
    from scripts.expression_sets._overlay import overlay_labels, update_steps
    from scripts.expression_sets._schema import validate_overlay as toolkit_validate
    task = _OverlayApplier()
    update = {"name": "A", "label": "Readable A", "formula": "2"}
    for apply in (task._update_steps, lambda steps, changes: update_steps(steps, changes)):
        result = apply([{"name": "A", "formula": "1"}], [update])
        check("updateSteps strips Tooling-only label from Connect content",
              result == [{"name": "A", "formula": "2"}])
    check("both overlay paths collect updated step labels",
          task._overlay_labels({"updateSteps": [update]}) == {"A": "Readable A"}
          and overlay_labels({"updateSteps": [update]}) == {"A": "Readable A"})
    for validate in (validate_overlay, toolkit_validate):
        result = validate({"updateSteps": [{"name": "A", "placement": {"afterStep": "B"}}]})
        check("updateSteps placement is rejected before deactivation",
              not result.passed and any("reorderSteps" in issue.message for issue in result.errors))
    before = {"steps": [{"name": "A", "formula": "1"}], "variables": []}
    after = {"steps": [{"name": "A", "formula": "2"}, {"name": "B"}],
             "variables": [{"name": "V"}]}
    check("summary counts actual graph changes",
          task._overlay_change_summary(before, after)
          == "steps +1/-0/changed 1; variables +1/-0/changed 0")


def test_empty_value_comparison_is_description_only():
    from tasks.expression_set_schema import step_content_differences as task_differences
    from scripts.expression_sets._schema import step_content_differences as toolkit_differences
    for compare in (task_differences, toolkit_differences):
        check("empty description may read back as null",
              not compare({"description": ""}, {"description": None}))
        check("empty formula cannot verify against absent field",
              compare({"formula": ""}, {}) == ["step.formula"])
        check("empty parameter value cannot verify against null",
              compare({"value": ""}, {"value": None}) == ["step.value"])


def test_connect_patch_keeps_version_inactive_until_labels_restored():
    payload = {"versions": [{"id": "target", "enabled": True}]}
    result = Connect._keep_patched_version_inactive(payload, "target")
    check("Connect PATCH cannot reactivate before Tooling label restore",
          result["versions"][0]["enabled"] is False)
    try:
        Connect._keep_patched_version_inactive(payload, "missing")
    except Exception:
        missing_rejected = True
    else:
        missing_rejected = False
    check("wrong version ID fails before PATCH", missing_rejected)


def test_overlay_step_label_not_sent_to_connect():
    check("label is an overlay-only step key",
          "label" in ApplyExpressionSetOverlay._OVERLAY_ONLY_STEP_KEYS)


def test_every_connect_patch_goes_through_label_preservation():
    """Guard: a Connect full-graph PATCH resets every step label, so each one
    must run inside a mutate body handed to _run_connect_mutation(es_id=...)."""
    import ast

    path = os.path.join(REPO_ROOT, "tasks", "rlm_expression_set_connect.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    bad = []

    def calls(fn):
        # Direct calls only: nested defs are visited as their own ``fn``.
        stack = list(fn.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(node, ast.Call):
                yield node
            stack.extend(ast.iter_child_nodes(node))

    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        for node in calls(fn):
            if not isinstance(node.func, ast.Attribute):
                continue
            attr = node.func.attr
            if attr == "_patch_expression_set_via_connect" and fn.name != "mutate":
                bad.append(f"{fn.name}: PATCH outside a mutate body")
    check("every Connect PATCH is label-preserving " + (str(bad) if bad else ""), not bad)



def test_build_schema_logging_keeps_actionable_warnings():
    from unittest.mock import Mock
    from scripts.expression_sets._schema import validate_definition as standalone

    definition = json.loads(json.dumps(MINIMAL_PRICING_DEF))
    definition["id"] = "server-id"
    version = definition["versions"][0]
    version["id"] = "version-id"
    version["steps"][1]["formula"] = "&quot;example&quot;"
    result = validate_definition(definition)
    check("transport warning codes agree in both validators",
          [i.code for i in result.warnings] == [i.code for i in standalone(definition).warnings]
          and {i.code for i in result.warnings} ==
          {"html_entities", "output_only_fields", "version_id"})

    task = _OverlayApplier()
    task.logger = Mock()
    task._preflight_validate_definition(definition, log_summary=False)
    task._preflight_validate_definition(definition)
    check("simulation and apply emit one transport summary and no warnings",
          task.logger.info.call_count == 1 and not task.logger.warning.called)
    check("handled transport warnings emit no per-field noise",
          not task.logger.debug.called)

    task.logger.reset_mock()
    task.options["normalize_html_entities"] = "false"
    task._preflight_validate_definition(definition)
    check("disabled normalization keeps HTML warning visible",
          task.logger.warning.call_count == 1 and
          "HTML entities" in task.logger.warning.call_args.args[-1])

    task.logger.reset_mock()
    task.options.clear()
    result.warn("future", "An actionable warning")
    task._raise_on_validation_errors(result, "definition")
    check("uncategorized warnings remain visible",
          task.logger.warning.call_count == 1 and
          task.logger.warning.call_args.args[-1] == "An actionable warning")
    result.error("steps", "A malformed graph")
    try:
        task._raise_on_validation_errors(result, "definition")
    except Exception as exc:
        raised = "A malformed graph" in str(exc)
    else:
        raised = False
    check("summarized transport warnings never suppress validation errors", raised)


def test_overlay_transform_details_are_debug_only():
    from unittest.mock import Mock

    task = _OverlayApplier()
    task.logger = Mock()
    overlay = {"addSteps": [{"name": "NewStep", "stepType": "ListGroup"}],
               "addVariables": [{"name": "NewVariable"}]}
    output = task._apply_overlay(MINIMAL_PRICING_DEF, overlay)
    check("overlay transformation retains step and variable additions",
          output["versions"][0]["steps"][-1]["name"] == "NewStep" and
          output["versions"][0]["variables"][-1]["name"] == "NewVariable")
    check("per-item transformation logs are DEBUG, not INFO",
          task.logger.debug.call_count == 2 and not task.logger.info.called)


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
