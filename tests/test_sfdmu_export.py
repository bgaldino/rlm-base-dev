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
# SFDMU merge (pack 168): a non-empty top-level `objects` alongside a non-empty
# `objectSets` is unshifted as pass 1, ahead of the existing sets (not dropped).
check("objects + objectSets: objects unshifted as pass 1, sets follow in order",
      se.normalize_object_sets(
          {"objectSets": [{"objects": ["a"]}, {"objects": ["b"]}], "objects": ["flat"]}),
      [{"objects": ["flat"]}, {"objects": ["a"]}, {"objects": ["b"]}])
check("an empty top-level objects does not prepend a pass",
      se.normalize_object_sets({"objectSets": [{"objects": ["a"]}], "objects": []}),
      [{"objects": ["a"]}])
check("only an empty top-level objects (no objectSets) -> no pass",
      se.normalize_object_sets({"objects": []}), [])

# --- extract_object_name -----------------------------------------------------
check("basic FROM", se.extract_object_name("SELECT Id FROM Account"), "Account")
check("lowercase from is matched", se.extract_object_name("select id from Widget__c"), "Widget__c")
check("leading whitespace/newline before FROM",
      se.extract_object_name("SELECT Id\n  FROM Account"), "Account")
check("no FROM -> empty", se.extract_object_name("SELECT Id"), "")
check("non-string query -> empty (does not raise)", se.extract_object_name(["SELECT"]), "")
check("None query -> empty", se.extract_object_name(None), "")
# Subquery-aware (pack 163): the inner FROM must not be mistaken for the outer object.
check("SELECT-clause subquery -> outer object, not the subquery's",
      se.extract_object_name("SELECT Id, Name, (SELECT Id FROM Contacts) FROM Account"), "Account")
check("nested subqueries -> outer object",
      se.extract_object_name("SELECT Id, (SELECT Id, (SELECT Id FROM X) FROM Y) FROM Account"), "Account")
check("paren inside a subquery's string literal is not structural -> outer object",
      se.extract_object_name("SELECT Id, (SELECT Id FROM Contacts WHERE Name = '(') FROM Account"),
      "Account")
check("escaped quote inside a subquery literal does not end the string early -> outer object",
      se.extract_object_name(r"SELECT Id, (SELECT Id FROM Contacts WHERE Name = '\'(') FROM Account"),
      "Account")
check("trailing WHERE...IN(...) does not shift the object (baseline shape)",
      se.extract_object_name("SELECT Id FROM RecordType WHERE X IN ('a','b')"), "RecordType")

# --- parse_select_fields -----------------------------------------------------
check("basic field list",
      se.parse_select_fields("SELECT Id, Name FROM Account"), ["Id", "Name"])
check("relationship traversal preserved",
      se.parse_select_fields("SELECT Id, Product.Name FROM PricebookEntry"),
      ["Id", "Product.Name"])
check("no SELECT -> empty", se.parse_select_fields("DELETE FROM Account"), [])
check("non-string -> empty", se.parse_select_fields(42), [])
# Subquery-aware (pack 163): read the outer field list, and drop the empty token the removed
# subquery's trailing comma would otherwise leave behind.
check("SELECT-clause subquery -> outer fields only, no empty token",
      se.parse_select_fields("SELECT Id, (SELECT Id FROM Contacts) FROM Account"), ["Id"])
check("outer fields around a subquery preserved",
      se.parse_select_fields("SELECT Id, Name, (SELECT Id FROM Contacts), Type FROM Account"),
      ["Id", "Name", "Type"])
check("paren inside a subquery's string literal does not corrupt outer field parsing",
      se.parse_select_fields("SELECT Id, (SELECT Id FROM Contacts WHERE Name = '(') FROM Account"),
      ["Id"])
check("trailing WHERE...IN(...) leaves the field list unchanged (baseline shape)",
      se.parse_select_fields("SELECT Id, DeveloperName FROM RecordType WHERE X IN ('a','b')"),
      ["Id", "DeveloperName"])

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
check("numeric index 0 -> insert (DeleteSFDMUData reads Insert declarations)", se.resolve_operation(0), "insert")
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

# --- object_set_dir_number ---------------------------------------------------
# The canonical object-set-N directory rule the SFDMU validator and the tasks/rlm_sfdmu.py
# runtime sync each used to spell differently (pack 161, finding 4). Returns the 1-based
# number AS WRITTEN, or None for a non-canonical name a caller must skip.
check("object-set-1 -> 1", se.object_set_dir_number("object-set-1"), 1)
check("object-set-2 -> 2", se.object_set_dir_number("object-set-2"), 2)
check("object-set-10 -> 10 (multi-digit)", se.object_set_dir_number("object-set-10"), 10)
check("object-set-0 -> 0 (admitted; caller range-checks the 1-based typo)",
      se.object_set_dir_number("object-set-0"), 0)
check("object-set-1-backup -> None (trailing suffix, not anchored)",
      se.object_set_dir_number("object-set-1-backup"), None)
check("object-set-01 -> None (leading zero)", se.object_set_dir_number("object-set-01"), None)
check("object-set- -> None (no number)", se.object_set_dir_number("object-set-"), None)
check("object-set-1x -> None (trailing non-digit)", se.object_set_dir_number("object-set-1x"), None)
# re.ASCII: \d must NOT match Unicode digits — SFDMU builds names from JS String(index+1),
# always ASCII, so object-set-1<U+0661> is a name it never reads (would parse as 11 without it).
check("object-set-1١ -> None (Arabic-Indic digit, ASCII-only \\d)",
      se.object_set_dir_number("object-set-1١"), None)
check("source -> None (unrelated dir)", se.object_set_dir_number("source"), None)
check("empty string -> None", se.object_set_dir_number(""), None)
check("non-string (None) -> None, not a crash", se.object_set_dir_number(None), None)

# --- validator still delegates to the module (no drift) ----------------------
# A same-output comparison (`wrapper(x) == module(x)`) does NOT prove delegation: an identical
# reimplementation left in the wrapper would pass it, so the "no drift" invariant would go
# unenforced. Instead patch the module function to return a unique sentinel and assert the
# validator's wrapper returns exactly that sentinel — which can only happen if the wrapper actually
# calls the module. The validator does `import sfdmu_export` and looks the name up at call time on
# the same module object `se` references, so patching an attribute on `se` reaches its calls.
from validate_sfdmu_v5_datasets import SFDMUValidator  # noqa: E402


def delegates(label, module_fn_name, call_wrapper):
    sentinel = object()
    original = getattr(se, module_fn_name)
    setattr(se, module_fn_name, lambda *a, **k: sentinel)
    try:
        got = call_wrapper()
    finally:
        setattr(se, module_fn_name, original)
    check(label, got, sentinel)


delegates("validator._normalized_object_sets calls module.normalize_object_sets",
          "normalize_object_sets", lambda: SFDMUValidator._normalized_object_sets({"objects": [1]}))
delegates("validator._extract_object_name calls module.extract_object_name",
          "extract_object_name", lambda: SFDMUValidator._extract_object_name(None, "SELECT Id FROM X"))
delegates("validator._parse_select_fields calls module.parse_select_fields",
          "parse_select_fields", lambda: SFDMUValidator._parse_select_fields(None, "SELECT Id FROM X"))
delegates("validator._resolve_operation calls module.resolve_operation",
          "resolve_operation", lambda: SFDMUValidator._resolve_operation("Upsert"))
delegates("validator._is_js_truthy calls module.is_js_truthy",
          "is_js_truthy", lambda: SFDMUValidator._is_js_truthy([]))
check("validator SFDMU_OPERATION_BY_INDEX is the module tuple (same object, not a copy)",
      SFDMUValidator.SFDMU_OPERATION_BY_INDEX is se.SFDMU_OPERATION_BY_INDEX, True)

print("=" * 60)
if _failures:
    print(f"FAIL: {len(_failures)} check(s) failed")
    sys.exit(1)
print("All checks passed")
