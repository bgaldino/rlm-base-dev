#!/usr/bin/env python3
"""Standalone scripts escape SOQL literals by one rule, and refuse a value that is not a record Id (todo 502).

    python tests/test_script_soql_literal.py   (no org, stdlib only)

scripts/soql_literal.py carries tasks/soql_utils.py's `soql_quote` rule for scripts that do not import
`tasks/`: backslash, quote, newline and carriage return. Every escaper todo 502 changed must turn a
NASTY value into exactly `soql_quote(NASTY)` (or its inside), and verify_backdated_billing.py quotes the
Ids the org returns and refuses an `--asset`/`--order` that is not a whole record Id.
The txn_data_harness escapers need `requests`; tests/txn_data_harness/test_apply_rules.py covers them.
"""
import importlib
import importlib.util
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.soql_literal import is_record_id, soql_quote, soql_text  # noqa: E402
from tasks.soql_utils import soql_quote as task_soql_quote  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


def load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NASTY = "a'b\\c\nd\re"
LIT = "'a\\'b\\\\c\\nd\\re'"

print("scripts/soql_literal.py")
check("soql_quote escapes a quote", soql_quote("a'b") == "'a\\'b'", soql_quote("a'b"))
check("soql_quote escapes a backslash", soql_quote("a\\b") == "'a\\\\b'", soql_quote("a\\b"))
check("soql_quote escapes a newline", soql_quote("a\nb") == "'a\\nb'", soql_quote("a\nb"))
check("soql_quote escapes a carriage return", soql_quote("a\rb") == "'a\\rb'", soql_quote("a\rb"))
check("soql_quote escapes the backslash before the quote it adds", soql_quote("\\'") == "'\\\\\\''", soql_quote("\\'"))
check("soql_quote matches tasks.soql_utils.soql_quote", soql_quote(NASTY) == task_soql_quote(NASTY) == LIT,
      soql_quote(NASTY))
check("soql_text is soql_quote without the quotes", f"'{soql_text(NASTY)}'" == LIT, soql_text(NASTY))
check("soql_quote stringifies a non-string", soql_quote(42) == "'42'", soql_quote(42))

ID15, ID18 = "001e600000AbCdE", "001e600000AbCdEAAZ"
check("is_record_id accepts a 15-character Id", is_record_id(ID15))
check("is_record_id accepts an 18-character Id", is_record_id(ID18))
for bad in ("", ID15[:14], ID18[:16], ID18[:17], ID18 + "A", ID18 + "\n", ID15 + "\n", " " + ID15,
            "001e600000AbC'E", "001e60000\\AbCdE", "001e600000AbC_E", None, 1234567890123456):
    check(f"is_record_id refuses {bad!r}", not is_record_id(bad))

print("todo 502: each changed escaper gives soql_quote's result")
qb = load("qb_usage", "scripts/qb_usage.py")
check("qb_usage.soql_str", qb.soql_str(NASTY) == LIT, qb.soql_str(NASTY))
ext = load("df_extract", "scripts/df_workshop/extract_workshop_quotes.py")
check("extract_workshop_quotes.soql_str", ext.soql_str(NASTY) == LIT, ext.soql_str(NASTY))
ins = load("df_insert", "scripts/df_workshop/insert_workshop_quotes.py")
check("insert_workshop_quotes.soql_str", ins.soql_str(NASTY) == LIT, ins.soql_str(NASTY))
bq = load("build_quote_to_asset", "scripts/build_quote_to_asset.py")
check("build_quote_to_asset.soql_str", bq.soql_str(NASTY) == LIT, bq.soql_str(NASTY))
check("build_quote_to_asset.esc (Apex literals)", f"'{bq.esc(NASTY)}'" == LIT, bq.esc(NASTY))
cca = load("check_classification_attrs", "scripts/check_classification_attrs.py")
check("check_classification_attrs.soql_literal", cca.soql_literal(NASTY) == LIT, cca.soql_literal(NASTY))
for module in ("scripts.context_service._client", "scripts.decision_tables._client",
               "scripts.expression_sets._engine", "scripts.expression_sets._client"):
    got = importlib.import_module(module).soql_literal(NASTY)
    check(f"{module}.soql_literal", f"'{got}'" == LIT, got)

print("todo 502: verify_backdated_billing quotes org Ids and refuses a non-Id argument")
vb = load("verify_backdated_billing", "scripts/backdated_arc/verify_backdated_billing.py")
vb.log = lambda msg: None
check("soql_ids quotes each Id", vb.soql_ids([NASTY, ID18]) == f"{LIT},'{ID18}'", vb.soql_ids([NASTY, ID18]))
sent = []
real_query = vb.sf_query
vb.sf_query = lambda org, soql: sent.append(soql) or [{"Id": ID18}]
vb.account_orders("o", NASTY)
vb.wait = lambda label, fn, timeout: fn()
vb.create_order = lambda org, quote, timeout, poll: ID18
vb.wait_for_calculation = lambda *a, **k: None
vb.wait_for_order("o", "0Q0" + NASTY)
check("account_orders quotes the account Id", sent[0] == f"SELECT Id FROM Order WHERE AccountId = {LIT}", sent[0])
check("wait_for_order quotes a quote Id the action returned",
      sent[1].startswith(f"SELECT Id FROM Quote WHERE Id = {soql_quote('0Q0' + NASTY)} AND"), sent[1])
vb.sf_query = real_query


class _Accepted(Exception):
    """Raised by the stubbed org: the arguments were accepted."""


def refused(*argv):
    """True when main() refuses the arguments (exit 2) before any org call."""
    sys.argv = ["verify_backdated_billing.py", "--org", "x", "--account", "A", "--scenario", "cancel", *argv]
    stderr, sys.stderr = sys.stderr, open(os.devnull, "w")
    vb.sf_query = lambda org, soql: (_ for _ in ()).throw(_Accepted())
    try:
        vb.main()
    except SystemExit as exc:
        return exc.code == 2
    except _Accepted:
        return False
    finally:
        sys.stderr.close()
        sys.stderr = stderr
        vb.sf_query = real_query
    return False


check("an 18-character --asset is accepted", not refused("--asset", ID18))
check("an --asset with a trailing newline is refused", refused("--asset", ID18 + "\n"))
check("an --order with a trailing newline is refused", refused("--asset", ID18, "--order", "801e600000BopYr\n"))
check("an --asset with a quote is refused", refused("--asset", "02ie6000003'WQn"))

if FAILURES:
    print(f"\n{len(FAILURES)} failure(s)")
    sys.exit(1)
print("\nPASS test_script_soql_literal")
