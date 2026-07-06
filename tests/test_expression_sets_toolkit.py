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
    derive_labels,
    humanize_name,
    label_drift,
    readable_labels,
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
# _graph Mermaid rendering
# --------------------------------------------------------------------------- #

def test_mermaid():
    print("test_mermaid")
    g = ExpressionSetGraph(_sample_definition())

    # --- flow view --------------------------------------------------------
    flow = g.to_mermaid_flow(title="TEST_Proc")
    check("flow starts with flowchart TD", flow.startswith("flowchart TD"), flow[:40])
    check("flow chains top-level steps in sequence order",
          "s_GetPrice --> s_ApplyMarkup" in flow and "s_ApplyMarkup --> s_DeadStep" in flow, flow)
    check("flow emits every step node",
          all(f"s_{n}[" in flow for n in ("GetPrice", "ApplyMarkup", "DeadStep")), flow)
    check("flow includes the scope classDefs", "classDef custom" in flow, flow)
    check("flow is deterministic", g.to_mermaid_flow(title="TEST_Proc") == flow)

    # A child step hangs off its parent with a dashed 'child' edge, not a run-order arrow.
    child_defn = _sample_definition()
    child_defn["versions"][0]["steps"].append(
        {"name": "Kid", "parentStep": "ApplyMarkup", "sequenceNumber": 1,
         "stepType": "BusinessKnowledgeModel", "customElement": {"parameters": []}})
    cflow = ExpressionSetGraph(child_defn).to_mermaid_flow()
    check("child step uses dashed child edge", "s_ApplyMarkup -. child .-> s_Kid" in cflow, cflow)
    check("child step is NOT in the run-order chain", "--> s_Kid" not in cflow.replace("-. child .-> s_Kid", ""), cflow)

    # --- deps view --------------------------------------------------------
    deps = g.to_mermaid_deps(title="TEST_Proc")
    check("deps starts with flowchart LR", deps.startswith("flowchart LR"), deps[:40])
    check("deps draws producer edge (step > var)", 's_GetPrice -->|">"| v_ListPrice' in deps, deps)
    check("deps draws consumer edge (var < step)", 'v_ListPrice -->|"<"| s_ApplyMarkup' in deps, deps)
    check("deps classes version var green", "class v_Constant_Markup version;" in deps, deps)
    check("deps classes custom ref red", "class v_RLM_RampMode__c custom;" in deps, deps)
    check("deps classes standard ctx blue", "class v_NetPrice standard;" in deps, deps)
    check("deps is deterministic", g.to_mermaid_deps(title="TEST_Proc") == deps)

    # --- deps scoped to one step's neighborhood ---------------------------
    scoped = g.to_mermaid_deps(only_steps={"ApplyMarkup"})
    check("scoped marks the focus step", "◆ focus" in scoped, scoped)
    check("scoped keeps the producer-neighbor (GetPrice via ListPrice)",
          "s_GetPrice[" in scoped, scoped)
    check("scoped excludes unrelated step (DeadStep)", "s_DeadStep[" not in scoped, scoped)
    check("scoped excludes unrelated var (UnusedOut)", "v_UnusedOut(" not in scoped, scoped)

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
               test_build_overlay, test_mermaid, test_shipped_fixtures):
        fn()
    print(f"\n{_PASS} passed, {_FAIL} failed.")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
