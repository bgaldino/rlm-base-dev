#!/usr/bin/env python3
"""Offline unit tests for the self-contained ``scripts/expression_sets/`` toolkit.

No org, no ``sf`` CLI, no pytest — a plain ``check()`` runner (matching the style
of ``tests/test_expression_set_schema.py``). Exercises the package's OWN pure
modules — ``_graph`` (producer/consumer index + scope + orphans), ``_payload``
(verb-specific field rules + HTML-entity normalization), ``_overlay`` (step /
variable merge), and ``export_expression_set_overlay.build_overlay`` (the slice-to-overlay
logic) — plus a parity check that the two shipped overlay fixtures still pass the
vendored validator.

These are independent of the CCI task's suite (``tests/test_expression_set_schema.py``),
which tests ``tasks/`` — this file tests ``scripts/expression_sets/`` only.

Run:  python tests/test_expression_sets_toolkit.py
Exit: 0 = all pass, 1 = one or more failures.
"""

import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.expression_sets._graph import (  # noqa: E402
    SCOPE_CUSTOM,
    SCOPE_STANDARD,
    SCOPE_VERSION,
    ExpressionSetGraph,
)
from scripts.expression_sets._overlay import (  # noqa: E402
    OverlayError,
    add_steps,
    apply_overlay,
    remove_steps,
    renumber_top_level_steps,
)
from scripts.expression_sets._payload import (  # noqa: E402
    normalize_html_entities,
    rewrite_version_id,
    strip_readonly_fields,
    unescape_value,
)
from scripts.expression_sets._schema import validate_overlay  # noqa: E402
from scripts.expression_sets.export_expression_set_overlay import build_overlay  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

_PASS = 0
_FAIL = 0


def check(label, condition, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  FAIL: {label}" + (f"  ({detail})" if detail else ""))


def _param(name, value, *, input=False, output=False, ptype="Parameter"):
    """A customElement parameter in the real shape (name + input/output flags)."""
    return {"type": ptype, "name": name, "value": value,
            "input": input, "output": output}


def _sample_definition():
    """A small but realistically-shaped definition (mirrors the fixture param shape)."""
    return {
        "id": "OUTPUT_ONLY_TOP_ID",
        "developerName": "TEST_Proc",
        "versions": [{
            "id": "9QMsourceVERSIONid",
            "apiName": "TEST_Proc_V1",
            "enabled": True,
            "variables": [
                {"name": "Constant_Markup", "dataType": "Numeric", "type": "Constant"},
            ],
            "steps": [
                {"name": "GetPrice", "parentStep": None, "sequenceNumber": 1,
                 "stepType": "BusinessKnowledgeModel",
                 "customElement": {"definition": "LookupTable", "parameters": [
                     _param("out1", "ListPrice", output=True),
                     _param("in1", "RLM_RampMode__c", input=True)]}},
                {"name": "ApplyMarkup", "parentStep": None, "sequenceNumber": 2,
                 "stepType": "BusinessKnowledgeModel",
                 "customElement": {"definition": "Formula", "parameters": [
                     _param("in1", "ListPrice", input=True),
                     _param("in2", "Constant_Markup", input=True),
                     _param("out1", "NetPrice", output=True),
                     {"type": "Formula", "name": "f", "value": "ListPrice * Constant_Markup"}]}},
                {"name": "DeadStep", "parentStep": None, "sequenceNumber": 3,
                 "stepType": "BusinessKnowledgeModel",
                 "customElement": {"definition": "Formula", "parameters": [
                     _param("out1", "UnusedOut", output=True)]}},
            ],
        }],
    }


# --------------------------------------------------------------------------- #
# _graph
# --------------------------------------------------------------------------- #

def test_graph():
    print("test_graph")
    g = ExpressionSetGraph(_sample_definition())
    check("ListPrice produced by GetPrice", g.produced_by("ListPrice") == ["GetPrice"],
          g.produced_by("ListPrice"))
    check("ListPrice consumed by ApplyMarkup", g.consumed_by("ListPrice") == ["ApplyMarkup"],
          g.consumed_by("ListPrice"))
    check("Constant_Markup scope=version", g.scope("Constant_Markup") == SCOPE_VERSION)
    check("RLM_RampMode__c scope=custom", g.scope("RLM_RampMode__c") == SCOPE_CUSTOM)
    check("NetPrice scope=standard", g.scope("NetPrice") == SCOPE_STANDARD)

    orph = g.orphans()
    check("RLM_RampMode__c consumed-no-producer",
          "RLM_RampMode__c" in orph["consumed_no_producer"], orph["consumed_no_producer"])
    check("RLM_RampMode__c undeclared-custom",
          "RLM_RampMode__c" in orph["undeclared_custom"], orph["undeclared_custom"])
    check("NetPrice + UnusedOut produced-unused",
          set(orph["produced_unused"]) == {"NetPrice", "UnusedOut"}, orph["produced_unused"])
    check("Constant_Markup NOT orphaned (declared version var)",
          "Constant_Markup" not in orph["consumed_no_producer"])

    closure = g.step_closure("ApplyMarkup")
    consumed_names = {c["name"] for c in closure["consumes"]}
    check("ApplyMarkup closure produces NetPrice", closure["produces"] == ["NetPrice"])
    check("ApplyMarkup closure consumes ListPrice+Constant_Markup",
          {"ListPrice", "Constant_Markup"} <= consumed_names, consumed_names)


# --------------------------------------------------------------------------- #
# _payload
# --------------------------------------------------------------------------- #

def test_payload():
    print("test_payload")
    defn = _sample_definition()

    # PATCH shape: top-level id stripped, version id KEPT.
    patched = strip_readonly_fields(defn, for_create=False)
    check("PATCH strips top-level id", "id" not in patched)
    check("PATCH keeps version id", patched["versions"][0].get("id") == "9QMsourceVERSIONid")
    check("strip does not mutate input", "id" in defn)

    # POST-create shape: version id ALSO stripped.
    created = strip_readonly_fields(defn, for_create=True)
    check("POST strips top-level id", "id" not in created)
    check("POST strips version id", "id" not in created["versions"][0])

    # developerName (SObject field) → folded into apiName (Connect field) + dropped;
    # the Connect API rejects developerName with JSON_PARSER_ERROR.
    dev_only = {"developerName": "RLM_Foo", "versions": []}
    folded = strip_readonly_fields(dev_only)
    check("developerName folded into apiName", folded.get("apiName") == "RLM_Foo")
    check("developerName dropped after fold", "developerName" not in folded)
    # apiName wins when both present.
    both = strip_readonly_fields({"apiName": "RLM_Api", "developerName": "RLM_Dev", "versions": []})
    check("apiName preserved over developerName", both.get("apiName") == "RLM_Api")
    check("developerName dropped when apiName present", "developerName" not in both)

    # rewrite_version_id → target id (PATCH path).
    rw = rewrite_version_id(deepcopy(patched), "9QMtargetVERSIONid")
    check("rewrite sets target version id", rw["versions"][0]["id"] == "9QMtargetVERSIONid")

    # HTML-entity normalization inverts a GET-escaped value.
    escaped = {"a": "x &quot;y&quot; &#39;z&#39; &amp; w"}
    un = normalize_html_entities(escaped)
    check("normalize unescapes entities", un["a"] == 'x "y" \'z\' & w', un["a"])
    check("normalize(enabled=False) is a no-op",
          normalize_html_entities(escaped, enabled=False) == escaped)
    check("unescape_value recurses lists/dicts",
          unescape_value({"l": ["&amp;", {"k": "&lt;"}]}) == {"l": ["&", {"k": "<"}]})
    check("normalize does not mutate input", escaped["a"] == "x &quot;y&quot; &#39;z&#39; &amp; w")


# --------------------------------------------------------------------------- #
# _overlay
# --------------------------------------------------------------------------- #

def test_overlay():
    print("test_overlay")
    steps = [
        {"name": "A", "parentStep": None, "sequenceNumber": 1},
        {"name": "B", "parentStep": None, "sequenceNumber": 2},
        {"name": "C", "parentStep": None, "sequenceNumber": 3},
    ]

    # add after B → sequence 3, C bumps to 4.
    added = add_steps(deepcopy(steps), [{"name": "NEW", "placement": {"afterStep": "B"}}])
    seq = {s["name"]: s["sequenceNumber"] for s in added}
    check("add afterStep places at target+1", seq["NEW"] == 3, seq)
    check("add afterStep bumps later step", seq["C"] == 4, seq)

    # add before A → sequence 1, everything shifts up.
    before = add_steps(deepcopy(steps), [{"name": "PRE", "placement": {"beforeStep": "A"}}])
    bseq = {s["name"]: s["sequenceNumber"] for s in before}
    check("add beforeStep places at target", bseq["PRE"] == 1, bseq)
    check("add beforeStep shifts A", bseq["A"] == 2, bseq)

    # remove B → renumber contiguous.
    removed = remove_steps(deepcopy(steps), [{"name": "B"}])
    rseq = {s["name"]: s["sequenceNumber"] for s in removed}
    check("remove drops B", "B" not in rseq)
    check("remove renumbers contiguous", rseq == {"A": 1, "C": 2}, rseq)

    # renumber_top_level_steps leaves children alone.
    with_child = [
        {"name": "P", "parentStep": None, "sequenceNumber": 5},
        {"name": "K", "parentStep": "P", "sequenceNumber": 9},
    ]
    rn = renumber_top_level_steps(deepcopy(with_child))
    m = {s["name"]: s["sequenceNumber"] for s in rn}
    check("renumber sets top-level to 1", m["P"] == 1, m)
    check("renumber leaves child seq untouched", m["K"] == 9, m)

    # updateSteps on a missing target raises.
    raised = False
    try:
        apply_overlay(_sample_definition(), {"updateSteps": [{"name": "NOPE", "x": 1}]})
    except OverlayError:
        raised = True
    check("updateSteps missing target raises", raised)

    # full apply_overlay round trip: add a variable + a step.
    result = apply_overlay(_sample_definition(), {
        "addVariables": [{"name": "Constant_New", "dataType": "Numeric", "type": "Constant"}],
        "addSteps": [{"name": "Extra", "parentStep": None,
                      "customElement": {"definition": "Formula", "parameters": [
                          _param("out1", "ExtraOut", output=True)]},
                      "placement": {"afterStep": "ApplyMarkup"}}],
    })
    v = result["versions"][0]
    names = {s["name"] for s in v["steps"]}
    var_names = {x["name"] for x in v["variables"]}
    check("apply_overlay adds step", "Extra" in names)
    check("apply_overlay adds variable", "Constant_New" in var_names)
    check("apply_overlay does not mutate source",
          "Extra" not in {s["name"] for s in _sample_definition()["versions"][0]["steps"]})


# --------------------------------------------------------------------------- #
# export_expression_set_overlay.build_overlay
# --------------------------------------------------------------------------- #

def test_build_overlay():
    print("test_build_overlay")
    defn = _sample_definition()

    # Slicing ApplyMarkup pulls its version dep (Constant_Markup), no custom.
    ov = build_overlay(defn, ["ApplyMarkup"], after="GetPrice")
    check("slice sets placement.afterStep",
          ov["addSteps"][0]["placement"] == {"afterStep": "GetPrice"})
    check("slice emits version dep as addVariables",
          [v["name"] for v in ov.get("addVariables", [])] == ["Constant_Markup"])
    check("slice ApplyMarkup has no externalDependencies",
          "externalDependencies" not in ov, ov.get("externalDependencies"))
    check("sliced ApplyMarkup overlay validates", validate_overlay(ov).passed,
          validate_overlay(ov).format_report())

    # Slicing GetPrice pulls the custom ref into externalDependencies.customFields.
    ov2 = build_overlay(defn, ["GetPrice"])
    check("slice GetPrice emits custom ref under externalDependencies.customFields",
          (ov2.get("externalDependencies") or {}).get("customFields") == ["RLM_RampMode__c"],
          ov2.get("externalDependencies"))
    check("sliced GetPrice overlay validates", validate_overlay(ov2).passed,
          validate_overlay(ov2).format_report())

    # Missing step name raises.
    raised = False
    try:
        build_overlay(defn, ["NoSuchStep"])
    except Exception:
        raised = True
    check("build_overlay missing step raises", raised)


# --------------------------------------------------------------------------- #
# Shipped fixtures still validate (parity with the vendored validator)
# --------------------------------------------------------------------------- #

def test_shipped_fixtures():
    print("test_shipped_fixtures")
    overlays_dir = REPO_ROOT / "datasets" / "expression_set_overlays"
    for name in ("discount_distribution.json", "map_line_item.json"):
        path = overlays_dir / name
        if not path.exists():
            check(f"{name} present", False, "fixture missing")
            continue
        result = validate_overlay(json.loads(path.read_text(encoding="utf-8")))
        check(f"{name} validates clean", result.passed, result.format_report())


def main():
    for fn in (test_graph, test_payload, test_overlay, test_build_overlay,
               test_shipped_fixtures):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
