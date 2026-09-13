"""Regression guard for scripts/post_process_extraction.py (todo pack 182).

`get_object_name_from_query` and `parse_select_fields` parse SOQL out of a plan's
`export.json`. A hand-edited export.json can carry a non-string `query` (e.g. a JSON
list), which used to hit `.upper()` on a list and raise AttributeError straight out of
the caller — aborting the whole post-processing run over one malformed declaration. The
validator's equivalent pair was hardened for exactly this in PR #397; these copies were
not. This suite pins the `isinstance(query, str)` guards and proves:

  1. a non-string query is skipped (returns ""/[]) rather than raising,
  2. a whole-plan parse survives a malformed entry and simply drops it, and
  3. well-formed queries still parse identically (no regression on the #N/A backfill
     logic that consumes the object name + fields).

The same crash class reaches `get_key_columns` via a non-string `externalId` (another
hand-editable export.json field, which hits `.split(";")`); that guard is pinned here too.

Offline, no org: `python tests/test_post_process_extraction.py`.
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "post_process_extraction.py"

_passed = 0
_total = 0


def check(name, cond, detail=""):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def _load_module():
    """Import the script by path. Import must be side-effect-free (the run lives under
    `if __name__ == '__main__'`)."""
    spec = importlib.util.spec_from_file_location("post_process_extraction", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_non_string_query_is_guarded(m):
    for bad in ([], ["SELECT Id FROM Account"], {"q": "x"}, None, 42):
        raised_name = raised_fields = False
        name = fields = None
        try:
            name = m.get_object_name_from_query(bad)
        except Exception:
            raised_name = True
        try:
            fields = m.parse_select_fields(bad)
        except Exception:
            raised_fields = True
        check(f"get_object_name_from_query({type(bad).__name__}) returns '' without raising",
              not raised_name and name == "", f"raised={raised_name} name={name!r}")
        check(f"parse_select_fields({type(bad).__name__}) returns [] without raising",
              not raised_fields and fields == [], f"raised={raised_fields} fields={fields!r}")


def test_well_formed_query_unchanged(m):
    q = "SELECT Id, Name, Product2.StockKeepingUnit FROM Account WHERE Name != null"
    check("object name parsed from a well-formed query",
          m.get_object_name_from_query(q) == "Account", m.get_object_name_from_query(q))
    check("select fields parsed from a well-formed query",
          m.parse_select_fields(q) == ["Id", "Name", "Product2.StockKeepingUnit"],
          m.parse_select_fields(q))
    # No FROM / no SELECT edge cases keep their prior contract.
    check("query without FROM yields no object name", m.get_object_name_from_query("SELECT Id") == "")
    check("query without SELECT/FROM yields no fields", m.parse_select_fields("garbage") == [])


def test_whole_plan_parse_survives_malformed_entry(m):
    """A malformed (list) query in one object must not abort parse_plan_structure — the
    bad entry is dropped and the good ones still parse, matching the caller's `if not
    name: continue` contract."""
    export_json = {
        "objects": [
            {"query": "SELECT Id, Name FROM Account", "operation": "Upsert", "externalId": "Name"},
            {"query": ["SELECT Id FROM Product2"], "operation": "Upsert"},  # malformed: list
            {"query": "SELECT Id FROM Pricebook2", "operation": "Upsert", "externalId": "Id"},
        ]
    }
    raised = False
    try:
        result, passes = m.parse_plan_structure(export_json)
    except Exception as e:
        raised = True
        result = {}
    check("parse_plan_structure does not raise on a malformed query entry", not raised)
    check("well-formed objects still parsed", set(result) == {"Account", "Pricebook2"},
          sorted(result))
    check("malformed entry was dropped, not injected", "Product2" not in result)


def test_non_string_external_id_is_guarded(m):
    """`externalId` is read from the same hand-editable export.json and reaches
    `.split(";")`. A populated non-string value (e.g. ["Name"]) must not raise — the
    `not external_id` check alone doesn't catch it. Falls back to all plan headers."""
    headers = ["Id", "Name", "Code"]
    for bad in (["Name"], {"f": "Name"}, 7):
        raised = False
        out = None
        try:
            out = m.get_key_columns(headers, bad)
        except Exception:
            raised = True
        check(f"get_key_columns with a {type(bad).__name__} externalId does not raise",
              not raised, f"raised={raised}")
        check(f"non-string externalId falls back to all headers ({type(bad).__name__})",
              out == headers, out)
    # Well-formed externalId still maps to the matching key columns.
    check("well-formed externalId maps to matching key columns",
          m.get_key_columns(headers, "Name;Code") == ["Name", "Code"],
          m.get_key_columns(headers, "Name;Code"))


def main():
    print("=" * 80)
    print("post_process_extraction.py regression guard (pack 182)")
    print("=" * 80)
    m = _load_module()
    test_non_string_query_is_guarded(m)
    test_well_formed_query_unchanged(m)
    test_whole_plan_parse_survives_malformed_entry(m)
    test_non_string_external_id_is_guarded(m)
    print("=" * 80)
    print(f"{_passed}/{_total} checks passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
