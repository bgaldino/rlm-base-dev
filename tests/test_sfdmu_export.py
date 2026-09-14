#!/usr/bin/env python3
"""Direct unit tests for the shared SFDMU export.json parsing primitives.

`scripts/sfdmu_export.py` is the one copy of the rules that used to be duplicated
across the validator, the plan-README scripts, `tasks/rlm_sfdmu.py`, and
`diff_schemas.py` (todo pack 191). Pinning the primitives here — rather than only
through each caller — means the follow-on behavioral packs (163/165/167/168/169)
change the module against these tests, and a regression is attributable to the
module rather than to whichever caller happened to notice.

Also asserts the validator's staticmethods still delegate here, so the extraction
stays a pure refactor: the two must not drift back apart.

Run: `python tests/test_sfdmu_export.py` (offline, no org).
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import sfdmu_export as se  # noqa: E402

_failures: list[str] = []


def check(label: str, got, want) -> None:
    if got == want:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}: got {got!r}, want {want!r}")
        _failures.append(label)


# --- normalize_object_sets ---------------------------------------------------
check("objectSets passed through verbatim",
      se.normalize_object_sets({"objectSets": [{"objects": [1]}, {"objects": [2]}]}),
      [{"objects": [1]}, {"objects": [2]}])
check("flat objects wrapped as a single pass",
      se.normalize_object_sets({"objects": [1, 2]}),
      [{"objects": [1, 2]}])
check("empty objectSets falls back to flat objects",
      se.normalize_object_sets({"objectSets": [], "objects": [1]}),
      [{"objects": [1]}])
check("neither key present -> empty list",
      se.normalize_object_sets({}), [])

# --- extract_object_name -----------------------------------------------------
check("basic FROM", se.extract_object_name("SELECT Id FROM Account"), "Account")
check("lowercase from is matched", se.extract_object_name("select id from Widget__c"), "Widget__c")
check("leading whitespace/newline before FROM",
      se.extract_object_name("SELECT Id\n  FROM Account"), "Account")
check("no FROM -> empty", se.extract_object_name("SELECT Id"), "")
check("non-string query -> empty (does not raise)", se.extract_object_name(["SELECT"]), "")
check("None query -> empty", se.extract_object_name(None), "")

# --- parse_select_fields -----------------------------------------------------
check("basic field list",
      se.parse_select_fields("SELECT Id, Name FROM Account"), ["Id", "Name"])
check("relationship traversal preserved",
      se.parse_select_fields("SELECT Id, Product.Name FROM PricebookEntry"),
      ["Id", "Product.Name"])
check("no SELECT -> empty", se.parse_select_fields("DELETE FROM Account"), [])
check("non-string -> empty", se.parse_select_fields(42), [])

# --- is_js_truthy ------------------------------------------------------------
check("empty list is JS-truthy (unlike Python)", se.is_js_truthy([]), True)
check("empty dict is JS-truthy (unlike Python)", se.is_js_truthy({}), True)
check("empty string is falsy", se.is_js_truthy(""), False)
check("zero is falsy", se.is_js_truthy(0), False)
check("None is falsy", se.is_js_truthy(None), False)
check("non-empty string is truthy", se.is_js_truthy("x"), True)
check("True is truthy", se.is_js_truthy(True), True)

# --- resolve_operation -------------------------------------------------------
check("string 'Upsert' -> upsert", se.resolve_operation("Upsert"), "upsert")
check("padded/mixed-case ' ReadOnly ' -> readonly", se.resolve_operation(" ReadOnly "), "readonly")
check("numeric index 2 -> upsert", se.resolve_operation(2), "upsert")
check("integral float 2.0 -> upsert", se.resolve_operation(2.0), "upsert")
check("non-integral float 2.5 -> None", se.resolve_operation(2.5), None)
check("bool True dropped (not read as 1)", se.resolve_operation(True), None)
check("bool False dropped (not read as 0)", se.resolve_operation(False), None)
check("index 8 -> unknown fallback", se.resolve_operation(8), "unknown")
check("string 'Unknown' -> unknown", se.resolve_operation("Unknown"), "unknown")
check("out-of-range index -> None", se.resolve_operation(99), None)
check("unrecognized word -> None", se.resolve_operation("frobnicate"), None)
check("None -> None", se.resolve_operation(None), None)

# --- validator still delegates to the module (no drift) ----------------------
from validate_sfdmu_v5_datasets import SFDMUValidator  # noqa: E402

check("validator._normalized_object_sets delegates",
      SFDMUValidator._normalized_object_sets({"objects": [1]}),
      se.normalize_object_sets({"objects": [1]}))
check("validator._extract_object_name delegates",
      SFDMUValidator._extract_object_name(None, "SELECT Id from foo"),
      se.extract_object_name("SELECT Id from foo"))
check("validator._resolve_operation delegates",
      SFDMUValidator._resolve_operation("Unknown"), se.resolve_operation("Unknown"))
check("validator._is_js_truthy delegates",
      SFDMUValidator._is_js_truthy([]), se.is_js_truthy([]))
check("validator SFDMU_OPERATION_BY_INDEX is the module tuple",
      SFDMUValidator.SFDMU_OPERATION_BY_INDEX, se.SFDMU_OPERATION_BY_INDEX)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
