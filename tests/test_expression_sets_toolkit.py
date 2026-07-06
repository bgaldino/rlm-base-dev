#!/usr/bin/env python3
"""Offline unit tests for the self-contained ``scripts/expression_sets/`` toolkit.

No org, no ``sf`` CLI, no pytest — a plain ``check()`` runner (matching the style
of ``tests/test_expression_set_schema.py``). Exercises the package's OWN pure
modules — ``_graph`` (producer/consumer index + scope + orphans), ``_payload``
(verb-specific field rules + HTML-entity normalization), ``_overlay`` (step /
variable merge), ``_tooling`` (step-label read/derive/apply + Metadata read-only
strip), and ``export_expression_set_overlay.build_overlay`` (the slice-to-overlay
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
from scripts.expression_sets._tooling import (  # noqa: E402
    apply_labels,
    capture_labels,
    derive_labels,
    humanize_name,
    label_drift,
    labels_from_metadata_xml,
    readable_labels,
    relabel_version,
    resolve_esdv,
    restore_labels_after_clobber,
    step_labels,
    strip_metadata_readonly,
    warn_label_clobber,
)
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
                     _param("in3", "AppliedDiscount__std", input=True),
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

    # ordered_steps: flat execution order — top-level by sequenceNumber, a
    # parent's children nested right after it.
    og = ExpressionSetGraph({"versions": [{"apiName": "V", "variables": [], "steps": [
        {"name": "B", "parentStep": None, "sequenceNumber": 2, "customElement": {"parameters": []}},
        {"name": "A", "parentStep": None, "sequenceNumber": 1, "customElement": {"parameters": []}},
        {"name": "A_kid2", "parentStep": "A", "sequenceNumber": 2, "customElement": {"parameters": []}},
        {"name": "A_kid1", "parentStep": "A", "sequenceNumber": 1, "customElement": {"parameters": []}},
    ]}]})
    order = [s["name"] for s in og.ordered_steps()]
    check("ordered_steps nests children after parent in sequence order",
          order == ["A", "A_kid1", "A_kid2", "B"], order)


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

    # An overlay 'label' rides along for the Tooling relabel but must NEVER reach
    # the Connect step payload (Connect rejects it → JSON_PARSER_ERROR).
    labelled = add_steps(deepcopy(steps),
                         [{"name": "LBL", "label": "My Label",
                           "placement": {"afterStep": "A"}}])
    new_step = next(s for s in labelled if s["name"] == "LBL")
    check("overlay label stripped from Connect step", "label" not in new_step, new_step)
    check("overlay placement stripped from Connect step", "placement" not in new_step)

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

    # --- labels block: {name: label} map, string→string, optional ------------
    good = {"addSteps": [{"name": "NewStep", "stepType": "BusinessKnowledgeModel"}],
            "labels": {"NewStep": "New Step"}}
    check("overlay with valid labels block validates", validate_overlay(good).passed,
          validate_overlay(good).format_report())
    check("overlay with no labels block validates", validate_overlay(
        {"addSteps": [{"name": "S", "stepType": "BusinessKnowledgeModel"}]}).passed)
    not_a_map = validate_overlay({"addSteps": [], "labels": ["nope"]})
    check("labels-not-a-map is an error", not not_a_map.passed, not_a_map.format_report())
    bad_val = validate_overlay({"addSteps": [], "labels": {"S": 123}})
    check("labels non-string value is an error", not bad_val.passed, bad_val.format_report())


# --------------------------------------------------------------------------- #
# _graph Mermaid rendering
# --------------------------------------------------------------------------- #

def test_mermaid():
    print("test_mermaid")
    g = ExpressionSetGraph(_sample_definition())

    # --- node_kind: the finer display taxonomy over scope -----------------
    check("node_kind Constant_Markup=constant", g.node_kind("Constant_Markup") == "constant",
          g.node_kind("Constant_Markup"))
    check("node_kind RLM_RampMode__c=custom", g.node_kind("RLM_RampMode__c") == "custom")
    check("node_kind AppliedDiscount__std=std", g.node_kind("AppliedDiscount__std") == "std")
    check("node_kind NetPrice=context (bare standard)", g.node_kind("NetPrice") == "context",
          g.node_kind("NetPrice"))
    # A non-Constant version variable is 'variable', not 'constant'.
    gv = ExpressionSetGraph({"versions": [{"apiName": "V", "variables": [
        {"name": "LocalTmp", "type": "Variable", "dataType": "Numeric"}], "steps": [
        {"name": "S", "parentStep": None, "sequenceNumber": 1, "customElement": {
            "parameters": [_param("i", "LocalTmp", input=True)]}}]}]})
    check("node_kind non-Constant version var=variable", gv.node_kind("LocalTmp") == "variable",
          gv.node_kind("LocalTmp"))

    # --- flow view --------------------------------------------------------
    flow = g.to_mermaid_flow(title="TEST_Proc")
    check("flow starts with flowchart TD", flow.startswith("flowchart TD"), flow[:40])
    check("flow chains top-level steps in sequence order",
          "s_GetPrice --> s_ApplyMarkup" in flow and "s_ApplyMarkup --> s_DeadStep" in flow, flow)
    check("flow emits every step node",
          all(f"s_{n}[" in flow for n in ("GetPrice", "ApplyMarkup", "DeadStep")), flow)
    check("flow emits the step classDef", "classDef step" in flow, flow)
    check("flow legend has ONLY the step kind (no var kinds)",
          "classDef custom" not in flow and "classDef context" not in flow, flow)
    check("flow is deterministic", g.to_mermaid_flow(title="TEST_Proc") == flow)

    # Labels: readable label shown over the API name; label==name / no-label show name only.
    lflow = g.to_mermaid_flow(labels={"GetPrice": "Get Price", "ApplyMarkup": "ApplyMarkup"})
    check("flow label shown over api name",
          "Get Price<br/><small>GetPrice</small>" in lflow, lflow)
    check("flow label==name collapses to name (no <small>)",
          "ApplyMarkup<br/><small>" not in lflow, lflow)

    # A step with children (a ListGroup) becomes a subgraph CONTAINING them, and
    # the group box — not the parent node — participates in the top-level chain.
    child_defn = _sample_definition()
    child_defn["versions"][0]["steps"] += [
        {"name": "Kid2", "parentStep": "ApplyMarkup", "sequenceNumber": 2,
         "stepType": "BusinessKnowledgeModel", "customElement": {"parameters": []}},
        {"name": "Kid1", "parentStep": "ApplyMarkup", "sequenceNumber": 1,
         "stepType": "AdvancedListFilter", "customElement": {"parameters": []}},
    ]
    cflow = ExpressionSetGraph(child_defn).to_mermaid_flow()
    check("parent with children becomes a subgraph", 'subgraph sg_ApplyMarkup["ApplyMarkup"]' in cflow, cflow)
    check("subgraph declares top-to-bottom direction", "direction TB" in cflow, cflow)
    check("every subgraph is balanced with an end",
          cflow.count("subgraph ") == len([l for l in cflow.splitlines() if l.strip() == "end"]), cflow)
    check("children rendered as nodes inside", "s_Kid1[" in cflow and "s_Kid2[" in cflow, cflow)
    check("children chained in sequenceNumber order (Kid1 seq1 → Kid2 seq2)",
          "s_Kid1 --> s_Kid2" in cflow, cflow)
    # The group id (not the plain parent node) carries the top-level chain.
    check("top chain enters the group box, not the raw parent node",
          "s_GetPrice --> sg_ApplyMarkup" in cflow, cflow)
    check("top chain exits the group box to the next top-level step",
          "sg_ApplyMarkup --> s_DeadStep" in cflow, cflow)
    check("no dashed child edge remains", "-. child .->" not in cflow, cflow)
    check("group box is tinted with a style line", "style sg_ApplyMarkup fill:" in cflow, cflow)

    # A ListGroup whose only child is itself a ListGroup nests recursively.
    nested_defn = _sample_definition()
    nested_defn["versions"][0]["steps"] += [
        {"name": "Outer", "parentStep": None, "sequenceNumber": 4, "stepType": "ListGroup",
         "customElement": {"parameters": []}},
        {"name": "Inner", "parentStep": "Outer", "sequenceNumber": 1, "stepType": "ListGroup",
         "customElement": {"parameters": []}},
        {"name": "Leaf", "parentStep": "Inner", "sequenceNumber": 1,
         "stepType": "BusinessKnowledgeModel", "customElement": {"parameters": []}},
    ]
    nflow = ExpressionSetGraph(nested_defn).to_mermaid_flow()
    check("nested groups produce nested subgraphs",
          "subgraph sg_Outer[" in nflow and "subgraph sg_Inner[" in nflow, nflow)
    check("nested leaf rendered inside", "s_Leaf[" in nflow, nflow)

    # --- deps view: kind-shaped, kind-classed nodes -----------------------
    deps = g.to_mermaid_deps(title="TEST_Proc")
    check("deps starts with flowchart LR", deps.startswith("flowchart LR"), deps[:40])
    check("deps draws producer edge (step > var)", 's_GetPrice -->|">"| v_ListPrice' in deps, deps)
    check("deps draws consumer edge (var < step)", 'v_ListPrice -->|"<"| s_ApplyMarkup' in deps, deps)
    # Kind classes (finer than scope): constant / custom / std / context.
    check("deps classes version constant", "class v_Constant_Markup constant;" in deps, deps)
    check("deps classes custom ref", "class v_RLM_RampMode__c custom;" in deps, deps)
    check("deps classes __std field as std", "class v_AppliedDiscount__std std;" in deps, deps)
    check("deps classes bare standard as context", "class v_NetPrice context;" in deps, deps)
    # Kind shapes: constant hexagon {{ }}, __std subroutine [[ ]], context stadium ([ ]).
    check("constant node uses hexagon shape", 'v_Constant_Markup{{"Constant_Markup"}}' in deps, deps)
    check("__std node uses subroutine shape",
          'v_AppliedDiscount__std[["AppliedDiscount__std"]]' in deps, deps)
    check("context node uses stadium shape", 'v_NetPrice(["NetPrice"])' in deps, deps)
    check("custom node uses cylinder shape", 'v_RLM_RampMode__c[("RLM_RampMode__c")]' in deps, deps)
    # Legend lists only kinds actually drawn (custom present here; variable absent).
    check("deps legend includes drawn kinds", "classDef constant" in deps and "classDef std" in deps, deps)
    check("deps legend omits undrawn 'variable' kind", "classDef variable" not in deps, deps)
    check("deps is deterministic", g.to_mermaid_deps(title="TEST_Proc") == deps)

    # deps step labels too.
    ldeps = g.to_mermaid_deps(labels={"GetPrice": "Get Price"})
    check("deps step label shown over api name",
          "Get Price<br/><small>GetPrice</small>" in ldeps, ldeps)

    # --- deps scoped to one step's neighborhood ---------------------------
    scoped = g.to_mermaid_deps(only_steps={"ApplyMarkup"})
    check("scoped marks the focus step", "◆ focus" in scoped, scoped)
    check("scoped keeps the producer-neighbor (GetPrice via ListPrice)",
          "s_GetPrice[" in scoped, scoped)
    check("scoped excludes unrelated step (DeadStep)", "s_DeadStep[" not in scoped, scoped)
    check("scoped excludes unrelated var (UnusedOut)", "v_UnusedOut" not in scoped, scoped)

    # --- empty version renders without crashing --------------------------
    empty = ExpressionSetGraph({"versions": [{"apiName": "V", "steps": [], "variables": []}]})
    check("empty flow renders placeholder", "no steps" in empty.to_mermaid_flow(), empty.to_mermaid_flow())
    check("empty deps renders placeholder", "no variable references" in empty.to_mermaid_deps())

    # --- label with a double-quote is escaped -----------------------------
    q_defn = _sample_definition()
    q_defn["versions"][0]["steps"][0]["name"] = 'Say "hi"'
    qflow = ExpressionSetGraph(q_defn).to_mermaid_flow()
    check("double-quote in label is escaped", '#quot;hi#quot;' in qflow, qflow)


# --------------------------------------------------------------------------- #
# _tooling — step-label read / derive / apply (Tooling Metadata; pure half)
# --------------------------------------------------------------------------- #

def _sample_metadata():
    """A Tooling-Metadata-shaped blob: steps carry `label`; `urls` is read-only.

    Mirrors the live shape (v67.0): a readable label, a spaceless run-on whose
    label == name (Connect-clobbered drift), and a step with no label at all.
    """
    return {
        "urls": {"metadata": "/services/data/v67.0/tooling/…"},  # read-only
        "label": "Sample Procedure",
        "steps": [
            {"name": "MapContextTags", "label": "Map Context Tags", "sequenceNumber": 1},
            {"name": "ApplyHeaderPriceOverride", "label": "ApplyHeaderPriceOverride",
             "sequenceNumber": 2},                                  # drift: label == name
            {"name": "Uplift", "sequenceNumber": 3},                # drift: no label
        ],
    }


def test_tooling():
    print("test_tooling")

    md = _sample_metadata()

    # step_labels: one entry per named step, None preserved.
    labels = step_labels(md)
    check("step_labels maps name→label", labels.get("MapContextTags") == "Map Context Tags")
    check("step_labels keeps None label", labels.get("Uplift") is None, labels)
    check("step_labels has all 3 steps", len(labels) == 3, labels)

    # label_drift: label missing OR == name.
    drift = label_drift(md)
    check("drift flags label==name", "ApplyHeaderPriceOverride" in drift, drift)
    check("drift flags missing label", "Uplift" in drift, drift)
    check("drift excludes good label", "MapContextTags" not in drift, drift)

    # readable_labels: the complement — steps a Connect PATCH would reset.
    readable = readable_labels(md)
    check("readable is the drift complement", readable == ["MapContextTags"], readable)

    # humanize_name: underscores + camelCase split; lossy on lowercase run-ons.
    check("humanize underscores", humanize_name("Map_Context_Tags") == "Map Context Tags")
    check("humanize camelCase", humanize_name("ApplyHeaderPriceOverride") == "Apply Header Price Override")
    check("humanize acronym boundary", humanize_name("ESVName") == "ESV Name",
          humanize_name("ESVName"))
    check("humanize lossy on lowercase run-on",
          humanize_name("applyheaderdiscount") == "applyheaderdiscount")
    check("humanize empty is safe", humanize_name("") == "")

    # derive_labels: only_drift touches only the drift steps.
    derived = derive_labels(md, only_drift=True)
    check("derive covers only drift names",
          set(derived) == {"ApplyHeaderPriceOverride", "Uplift"}, set(derived))
    check("derive humanizes the drift step",
          derived["ApplyHeaderPriceOverride"] == "Apply Header Price Override", derived)
    all_derived = derive_labels(md, only_drift=False)
    check("derive only_drift=False covers all", len(all_derived) == 3, all_derived)

    # apply_labels: returns new blob + changed list; skips no-ops/blanks; no mutation.
    new_md, changed = apply_labels(md, {
        "ApplyHeaderPriceOverride": "Apply Header Price Override",  # real change
        "MapContextTags": "Map Context Tags",                       # no-op (already)
        "Uplift": "",                                               # blank → skipped
        "NoSuchStep": "Ignored",                                    # absent → skipped
    })
    changed_labels = step_labels(new_md)
    check("apply changes the drift step",
          changed_labels["ApplyHeaderPriceOverride"] == "Apply Header Price Override")
    check("apply reports only real change", changed == ["ApplyHeaderPriceOverride"], changed)
    check("apply skips blank label", changed_labels["Uplift"] is None, changed_labels)
    check("apply does not mutate input",
          step_labels(md)["ApplyHeaderPriceOverride"] == "ApplyHeaderPriceOverride")

    # strip_metadata_readonly: drops `urls`, keeps everything else; no mutation.
    stripped = strip_metadata_readonly(md)
    check("strip drops urls", "urls" not in stripped)
    check("strip keeps steps", len(stripped.get("steps", [])) == 3)
    check("strip does not mutate input", "urls" in md)

    # warn_label_clobber: best-effort pre-PATCH warning over a FAKE transport.
    # It resolves the ESDV (tooling/query) then GETs Metadata (tooling/sobjects/…),
    # counts readable labels, and must NEVER raise.
    class _FakeTransport:
        def __init__(self, *, query_records=None, metadata=None, raise_on=None):
            self._query_records = query_records
            self._metadata = metadata
            self._raise_on = raise_on or ()

        def connect(self, method, path, body=None, **kw):
            if any(tok in path for tok in self._raise_on):
                from scripts.expression_sets._client import ExpressionSetClientError
                raise ExpressionSetClientError("boom")
            if "tooling/query" in path:
                return {"records": self._query_records or []}
            if "tooling/sobjects/" in path:
                return {"Metadata": self._metadata or {}}
            return {}

    logs = []
    # Happy path: one readable label → count 1, one warning logged.
    n = warn_label_clobber(
        _FakeTransport(query_records=[{"Id": "9QBx"}], metadata=md),
        "TEST_V1", logs.append,
    )
    check("warn counts readable labels", n == 1, n)
    check("warn logs a reset warning", any("RESET" in m for m in logs), logs)

    # No version name → 0, no log, no call.
    logs2 = []
    check("warn no-version returns 0", warn_label_clobber(_FakeTransport(), None, logs2.append) == 0)
    check("warn no-version stays silent", logs2 == [], logs2)

    # Tooling read error → swallowed (returns 0, soft note, never raises).
    logs3 = []
    n3 = warn_label_clobber(
        _FakeTransport(raise_on=("tooling/query",)), "TEST_V1", logs3.append
    )
    check("warn swallows read error", n3 == 0, n3)
    check("warn notes read failure softly", any("could not" in m for m in logs3), logs3)

    # All-drift metadata → 0 readable, no warning (nothing to lose).
    logs4 = []
    all_drift_md = {"steps": [{"name": "X", "label": "X"}, {"name": "Y"}]}
    n4 = warn_label_clobber(
        _FakeTransport(query_records=[{"Id": "9QBx"}], metadata=all_drift_md),
        "TEST_V1", logs4.append,
    )
    check("warn 0 when no readable labels", n4 == 0, n4)
    check("warn silent when nothing to lose", logs4 == [], logs4)


# --------------------------------------------------------------------------- #
# _tooling — label PRESERVATION (capture / restore / metadata-XML / relabel core)
# --------------------------------------------------------------------------- #

class _StatefulTransport:
    """A fake Transport that keeps ExpressionSetVersion.IsActive + Tooling Metadata
    state, enough to drive the full relabel deactivate→PATCH→reactivate cycle
    offline (no org, no sf). Duck-types _client.Transport: connect/get/sobject/soql
    + dry_run/logger.
    """

    def __init__(self, *, esdv_id="9QBx", version_api_name="TEST_V1",
                 metadata=None, is_active=True, raise_on_patch=False):
        self.esdv_id = esdv_id
        self.version_api_name = version_api_name
        self.metadata = metadata if metadata is not None else _sample_metadata()
        self.is_active = is_active
        self.raise_on_patch = raise_on_patch
        self.dry_run = False
        self.logger = lambda *a, **k: None
        self.patched_metadata_count = 0
        self.last_tooling_query = None

    def connect(self, method, path, body=None, **kw):
        if "tooling/query" in path:
            from urllib.parse import unquote
            self.last_tooling_query = unquote(path.split("q=", 1)[-1])
            return {"records": [{"Id": self.esdv_id,
                                 "DeveloperName": self.version_api_name,
                                 "VersionNumber": 1}]}
        if "tooling/sobjects/" in path:
            if method == "GET":
                return {"Metadata": self.metadata}
            if method == "PATCH":
                if self.raise_on_patch:
                    from scripts.expression_sets._tooling import ToolingError
                    raise ToolingError("metadata patch boom")
                self.metadata = (body or {}).get("Metadata", self.metadata)
                self.patched_metadata_count += 1
                return {}
        return {}

    def get(self, path):
        return {}

    def sobject(self, method, sobject, record_id=None, body=None, **kw):
        if sobject == "ExpressionSetVersion" and method == "PATCH":
            self.is_active = bool((body or {}).get("IsActive"))
        return {}

    def soql(self, query):
        if "FROM ProcedurePlanOption" in query:
            return []  # no cascade in the fake
        if "FROM ExpressionSetVersion" in query:
            row = {"Id": "9QMv", "ApiName": self.version_api_name,
                   "IsActive": self.is_active, "VersionNumber": 1}
            return [row]
        if "FROM ExpressionSet " in query:
            return [{"Id": "9QLx", "ResourceInitializationType": "Off"}]
        return []


def test_label_preservation():
    print("test_label_preservation")
    from scripts.expression_sets._lifecycle import LifecycleEngine
    from scripts.expression_sets._overlay import overlay_labels

    # --- labels_from_metadata_xml: read {name: label} from shipped metadata ----
    xml_path = (REPO_ROOT / "force-app" / "main" / "default" / "expressionSetDefinition"
                / "RLM_DefaultRatingProcedure.expressionSetDefinition-meta.xml")
    if xml_path.exists():
        m = labels_from_metadata_xml(xml_path.read_text(encoding="utf-8"))
        check("xml maps step name→label",
              m.get("AttributeBasedRateDiscount") == "Attribute-Based Rate Discount", m)
        # nested <parameters><name> tags must NOT leak in as step keys.
        check("xml ignores nested parameter names", "AttributeValue" not in m, list(m)[:5])
        check("xml found all 4 labeled steps", len(m) == 4, len(m))
    # malformed XML → ToolingError (caught by the CLI loader as a ValueError).
    try:
        labels_from_metadata_xml("<not-valid")
        check("xml raises on bad input", False)
    except Exception as exc:
        check("xml raises ToolingError on bad input", exc.__class__.__name__ == "ToolingError", exc)

    # --- overlay_labels: top-level block + per-step label, per-step wins -------
    ov = {
        "addSteps": [
            {"name": "NewStepA", "label": "New Step A"},          # per-step
            {"name": "NewStepB"},                                  # none here
        ],
        "labels": {"NewStepB": "New Step B", "NewStepA": "OVERRIDDEN"},
    }
    ol = overlay_labels(ov)
    check("overlay per-step label wins over top-level", ol.get("NewStepA") == "New Step A", ol)
    check("overlay top-level label picked up", ol.get("NewStepB") == "New Step B", ol)
    check("overlay_labels empty when none", overlay_labels({"addSteps": [{"name": "X"}]}) == {})

    # --- resolve_esdv: prefer the STABLE (es_def_id, VersionNumber) key ---------
    # The ESDV DeveloperName is rewritten in place by a Connect full-graph PATCH
    # (live-verified), so the auto-restore path must resolve by the parent
    # definition id + version number, NOT the ApiName/DeveloperName.
    tq = _StatefulTransport()
    resolve_esdv(tq, es_def_id="9QAx", version_number=2)
    check("resolve_esdv(es_def_id) queries ExpressionSetDefinitionId",
          "ExpressionSetDefinitionId = '9QAx'" in tq.last_tooling_query, tq.last_tooling_query)
    check("resolve_esdv pins VersionNumber when given",
          "VersionNumber = 2" in tq.last_tooling_query, tq.last_tooling_query)
    tq2 = _StatefulTransport()
    resolve_esdv(tq2, version_api_name="TEST_V1")
    check("resolve_esdv(version_api_name) falls back to DeveloperName",
          "DeveloperName = 'TEST_V1'" in tq2.last_tooling_query, tq2.last_tooling_query)
    try:
        resolve_esdv(_StatefulTransport())
        check("resolve_esdv requires an identifier", False)
    except Exception as exc:
        check("resolve_esdv no-id raises ToolingError",
              exc.__class__.__name__ == "ToolingError", exc)

    # --- capture_labels: snapshot the readable labels a PATCH would clobber ----
    t = _StatefulTransport(metadata=_sample_metadata())
    captured = capture_labels(t, "TEST_V1")
    check("capture returns only readable labels",
          captured == {"MapContextTags": "Map Context Tags"}, captured)
    check("capture no-version returns {}", capture_labels(t, None) == {})
    # Stable-key capture: resolves via es_def_id even with no version_api_name.
    ts = _StatefulTransport(metadata=_sample_metadata())
    cap_stable = capture_labels(ts, None, es_def_id="9QAx", version_number=1)
    check("capture via es_def_id (no ApiName) still reads labels",
          cap_stable == {"MapContextTags": "Map Context Tags"}, cap_stable)
    check("capture via es_def_id used the stable query",
          "ExpressionSetDefinitionId = '9QAx'" in ts.last_tooling_query, ts.last_tooling_query)

    # --- relabel_version: the shared deactivate→Tooling PATCH→reactivate core --
    t2 = _StatefulTransport(metadata=_sample_metadata(), is_active=True)
    engine = LifecycleEngine(t2, logger=lambda *a, **k: None)
    esv = {"Id": "9QMv", "ApiName": "TEST_V1", "IsActive": True}
    res = relabel_version(
        engine, es_def_id="9QAx", esv=esv,
        name_to_label={"ApplyHeaderPriceOverride": "Apply Header Price Override"},
    )
    check("relabel_version reports the changed step",
          res["changed"] == ["ApplyHeaderPriceOverride"], res)
    check("relabel_version wrote the metadata once", t2.patched_metadata_count == 1,
          t2.patched_metadata_count)
    check("relabel_version left version reactivated", t2.is_active is True, t2.is_active)
    check("relabel_version persisted the label",
          step_labels(t2.metadata)["ApplyHeaderPriceOverride"] == "Apply Header Price Override")
    # A name matching no step is a silent no-op (safe for auto-restore).
    t3 = _StatefulTransport(metadata=_sample_metadata())
    engine3 = LifecycleEngine(t3, logger=lambda *a, **k: None)
    res3 = relabel_version(engine3, es_def_id="9QAx",
                           esv={"Id": "9QMv", "ApiName": "TEST_V1", "IsActive": True},
                           name_to_label={"GhostStep": "Nope"})
    check("relabel_version no-op on unknown name", res3["changed"] == [], res3)
    check("relabel_version no PATCH on no-op", t3.patched_metadata_count == 0)

    # --- restore_labels_after_clobber: re-applies, non-fatal on failure --------
    t4 = _StatefulTransport(metadata=_sample_metadata(), is_active=True)
    engine4 = LifecycleEngine(t4, logger=lambda *a, **k: None)
    r4 = restore_labels_after_clobber(
        engine4, es_id="9QLx", es_def_id="9QAx", version_api_name="TEST_V1",
        name_to_label={"ApplyHeaderPriceOverride": "Apply Header Price Override"},
    )
    check("restore reports ok", r4["ok"] is True, r4)
    check("restore lists changed step", r4["changed"] == ["ApplyHeaderPriceOverride"], r4)
    # Empty map / no version → silent success, nothing written.
    t5 = _StatefulTransport()
    engine5 = LifecycleEngine(t5, logger=lambda *a, **k: None)
    r5 = restore_labels_after_clobber(engine5, es_id="9QLx", es_def_id="9QAx",
                                      version_api_name="TEST_V1", name_to_label={})
    check("restore empty map is a no-op ok", r5 == {"ok": True, "changed": [], "error": None})
    check("restore empty map writes nothing", t5.patched_metadata_count == 0)
    # A Tooling PATCH failure must NOT raise — the Connect mutation already
    # succeeded, so restore reports ok=False and logs how to fix, never throws.
    logs6 = []
    t6 = _StatefulTransport(metadata=_sample_metadata(), raise_on_patch=True)
    engine6 = LifecycleEngine(t6, logger=lambda *a, **k: None)
    r6 = restore_labels_after_clobber(
        engine6, es_id="9QLx", es_def_id="9QAx", version_api_name="TEST_V1",
        name_to_label={"ApplyHeaderPriceOverride": "Apply Header Price Override"},
        logger=logs6.append,
    )
    check("restore swallows PATCH failure (ok=False, no raise)", r6["ok"] is False, r6)
    check("restore logs a fix hint on failure",
          any("relabel_expression_set.py" in m for m in logs6), logs6)


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
    for fn in (test_graph, test_payload, test_overlay, test_tooling,
               test_label_preservation, test_build_overlay, test_mermaid,
               test_shipped_fixtures):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
