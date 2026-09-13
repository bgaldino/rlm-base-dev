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
import json
import subprocess
import sys
import tempfile
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


def test_whole_plan_parse_records_malformed_entry(m):
    """A malformed (list) query must not abort parse_plan_structure, but it must be
    RECORDED in the `malformed` list — not silently dropped — so the caller can fail
    before syncing. Well-formed objects still parse."""
    export_json = {
        "objects": [
            {"query": "SELECT Id, Name FROM Account", "operation": "Upsert", "externalId": "Name"},
            {"query": ["SELECT Id FROM Product2"], "operation": "Upsert"},  # malformed: list
            {"query": "SELECT Id FROM Pricebook2", "operation": "Upsert", "externalId": "Id"},
        ]
    }
    raised = False
    result, passes, malformed = {}, {}, []
    try:
        result, passes, malformed = m.parse_plan_structure(export_json)
    except Exception:
        raised = True
    check("parse_plan_structure does not raise on a malformed query entry", not raised)
    check("well-formed objects still parsed", set(result) == {"Account", "Pricebook2"},
          sorted(result))
    check("malformed entry is not injected into plan_structure", "Product2" not in result)
    check("malformed entry is recorded in the malformed list",
          len(malformed) == 1 and malformed[0]["query"] == ["SELECT Id FROM Product2"],
          malformed)
    # Only an absent or empty STRING slot is non-malformed.
    _, _, absent = m.parse_plan_structure({"objects": [{"operation": "Upsert"}]})
    check("absent query is not flagged malformed", absent == [], absent)
    _, _, empty_str = m.parse_plan_structure({"objects": [{"query": ""}]})
    check("explicit empty-string query is not flagged malformed", empty_str == [], empty_str)

    # Every non-string value is malformed — including the FALSY ones a plain
    # truthiness test would have dropped back onto the unsafe raw-CSV sync path.
    for falsy in ([], {}, 0, False, None):
        _, _, mal = m.parse_plan_structure({"objects": [{"query": falsy}]})
        check(f"falsy non-string query {falsy!r} is flagged malformed",
              len(mal) == 1 and mal[0]["query"] == falsy, mal)
    # A non-empty string that fails to parse (no FROM) is also malformed.
    _, _, garbage = m.parse_plan_structure({"objects": [{"query": "SELECT nonsense"}]})
    check("non-empty unparseable string query is flagged malformed", len(garbage) == 1, garbage)


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


def test_copy_to_plan_refuses_on_malformed_query(m):
    """End-to-end guard for the corruption path both reviewers flagged: a malformed
    query drops the object from plan_structure, and under --copy-to-plan sync_to_plan
    would otherwise copy the object's RAW extracted CSV over the tracked plan CSV,
    bypassing all processing and exiting 0. The run must exit nonzero and leave the
    tracked plan CSV byte-for-byte untouched."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        plan = td / "plan"
        extraction = td / "extraction"
        plan.mkdir()
        extraction.mkdir()

        # export.json with a well-formed object and a malformed (list) query.
        (plan / "export.json").write_text(json.dumps({"objects": [
            {"query": "SELECT Id, Name FROM Account", "operation": "Upsert", "externalId": "Name"},
            {"query": ["SELECT Id, Name FROM Pricebook2"], "operation": "Upsert"},  # malformed
        ]}), encoding="utf-8")

        # Tracked, already-processed plan CSV for the malformed object — the file that
        # must NOT be clobbered by the raw extract.
        tracked = plan / "Pricebook2.csv"
        tracked_bytes = b"Name,IsStandard\nStandard Price Book,true\n"
        tracked.write_bytes(tracked_bytes)
        (plan / "Account.csv").write_bytes(b"Name\nAcme\n")

        # Raw extraction CSVs (different content — what a silent sync would overwrite with).
        (extraction / "Pricebook2.csv").write_bytes(b"Id,Name,IsStandard\n01s,RAW,false\n")
        (extraction / "Account.csv").write_bytes(b"Id,Name\n001,Acme\n")

        r = subprocess.run(
            [sys.executable, str(MODULE_PATH), str(extraction), str(plan),
             "--copy-to-plan", "--output-dir", str(td / "out")],
            capture_output=True, text=True,
        )
        check("--copy-to-plan run exits nonzero on a malformed query", r.returncode != 0,
              f"returncode={r.returncode}\n{(r.stdout + r.stderr)[-400:]}")
        check("failure output flags the malformed declaration as CRITICAL",
              "CRITICAL" in r.stdout, r.stdout[-400:])
        check("the tracked plan CSV was NOT overwritten by the raw extract",
              tracked.read_bytes() == tracked_bytes, tracked.read_text(encoding="utf-8"))


def main():
    print("=" * 80)
    print("post_process_extraction.py regression guard (pack 182)")
    print("=" * 80)
    m = _load_module()
    test_non_string_query_is_guarded(m)
    test_well_formed_query_unchanged(m)
    test_whole_plan_parse_records_malformed_entry(m)
    test_non_string_external_id_is_guarded(m)
    test_copy_to_plan_refuses_on_malformed_query(m)
    print("=" * 80)
    print(f"{_passed}/{_total} checks passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
