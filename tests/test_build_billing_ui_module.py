"""Regression guard for scripts/build_billing_ui_module.py (todo pack 084).

The billing-UI generator is a one-shot bootstrap whose source tree is gitignored
and absent, so it cannot run in a fresh clone and its bugs stayed latent. Two of
them meant it could not regenerate its own committed output:

1. **Double prefix.** `make_cls_transform` rewrote the class declaration to
   `RLM_<Name>` and then `apply_all_renames` ran a plain `str.replace(old, new)`;
   because every APEX_MAP value *contains* its key as a substring, the just-renamed
   declaration got prefixed again — `RLM_RLM_SplitInvoicesController`. Fixed by a
   `(?<!RLM_)` negative lookbehind that makes the Apex renames idempotent.

2. **Over-length name.** APEX_MAP mapped `TransactionJournalRelatedListController`
   to `RLM_TransactionJournalRelatedListController` (43 chars), over Salesforce's
   40-char Apex-class cap; the shipped class was hand-shortened to
   `RLM_TxnJournalRelatedListController` (35) and the map never updated. Fixed the
   entry and added `validate_apex_map()` to fail loudly on any future >40 value.

This suite imports the module (side-effect-free now that the build lives under
`main()`), checks the transforms directly, and runs one end-to-end build against a
synthetic source tree with the output dirs redirected to a temp dir — so the run
never touches the committed module — asserting a second run is byte-identical.

Offline, no org: `python tests/test_build_billing_ui_module.py`.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "build_billing_ui_module.py"

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
    """Import the build script by path. Must be side-effect-free: the build runs
    only under `if __name__ == '__main__'`, so importing it must NOT write anything."""
    spec = importlib.util.spec_from_file_location("build_billing_ui_module", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_apex_map_within_limit(m):
    overlong = {v: len(v) for v in m.APEX_MAP.values() if len(v) > m.MAX_APEX_NAME_LEN}
    check("every APEX_MAP value fits the 40-char Apex cap", not overlong, str(overlong))
    check("real APEX_MAP passes validate_apex_map()",
          _no_raise(m.validate_apex_map))
    check("TransactionJournal maps to the shipped 35-char name",
          m.APEX_MAP["TransactionJournalRelatedListController"] == "RLM_TxnJournalRelatedListController",
          m.APEX_MAP["TransactionJournalRelatedListController"])


def test_guard_fails_loudly(m):
    bad = dict(m.APEX_MAP)
    bad["TransactionJournalRelatedListController"] = "RLM_TransactionJournalRelatedListController"  # 43
    raised = False
    try:
        m.validate_apex_map(bad)
    except ValueError:
        raised = True
    check("validate_apex_map() raises on an over-length target name", raised,
          "a 43-char value did not raise")


def test_no_double_prefix(m):
    src = ("public with sharing class SplitInvoicesController {\n"
           "  public static String go() { return InvoiceAgingController.x(); }\n"
           "}\n")
    out = m.make_cls_transform("SplitInvoicesController", "RLM_SplitInvoicesController")(src)
    check("class declaration is prefixed exactly once (no RLM_RLM_)",
          "RLM_RLM_" not in out and "class RLM_SplitInvoicesController" in out,
          out.splitlines()[0])
    check("cross-reference to another mapped class is still renamed",
          "RLM_InvoiceAgingController.x()" in out and "RLM_RLM_InvoiceAgingController" not in out)


def test_idempotent(m):
    # A corpus that exercises both a declaration path and bare cross-references.
    samples = [
        "class SplitInvoicesController { InvoiceAgingController a; PaymentsDataController b; }",
        "import x from 'c/invoiceAgingChart'; const y = invoiceAging; // billingStatus",
        "return TransactionJournalRelatedListController.run();",
        "already RLM_SplitInvoicesController and RLM_InvoiceAgingController stay put",
    ]
    for i, s in enumerate(samples):
        once = m.apply_all_renames(s)
        twice = m.apply_all_renames(once)
        check(f"apply_all_renames idempotent on sample {i}", once == twice, f"{once!r} != {twice!r}")

    # The whole cls transform (declaration rewrite + renames) must also be twice==once.
    t = m.make_cls_transform("SplitInvoicesController", "RLM_SplitInvoicesController")
    cls = "public class SplitInvoicesController { InvoiceAgingController a; }"
    once = t(cls)
    twice = t(once)
    check("make_cls_transform idempotent (twice == once)", once == twice, f"{once!r} != {twice!r}")
    check("already-renamed identifiers are left untouched",
          m.apply_all_renames("RLM_SplitInvoicesController") == "RLM_SplitInvoicesController")


def test_end_to_end_build_is_safe_and_idempotent(m):
    """Run the real script against a synthetic source, with outputs redirected to a
    temp tree, and assert the generated Apex is correct and a re-run is byte-identical."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "src"
        (src / "classes").mkdir(parents=True)
        (src / "classes" / "SplitInvoicesController.cls").write_text(
            "public with sharing class SplitInvoicesController {\n"
            "  public static String go() { return InvoiceAgingController.x(); }\n}\n",
            encoding="utf-8",
        )
        (src / "classes" / "SplitInvoicesController.cls-meta.xml").write_text(
            "<?xml version=\"1.0\"?><ApexClass></ApexClass>\n", encoding="utf-8"
        )
        (src / "classes" / "TransactionJournalRelatedListController.cls").write_text(
            "public class TransactionJournalRelatedListController {}\n", encoding="utf-8"
        )
        (src / "classes" / "TransactionJournalRelatedListController.cls-meta.xml").write_text(
            "<?xml version=\"1.0\"?><ApexClass></ApexClass>\n", encoding="utf-8"
        )

        def run(dest):
            env = dict(os.environ,
                       RLM_BILLING_LWC_SRC=str(src),
                       RLM_BILLING_UI_DEST=str(dest),
                       RLM_BILLING_UI_FLEXIPAGE_DEST=str(dest / "flexipages"))
            return subprocess.run([sys.executable, str(MODULE_PATH)],
                                  env=env, capture_output=True, text=True)

        dest1 = td / "out1"
        r1 = run(dest1)
        check("end-to-end run exits 0", r1.returncode == 0, r1.stderr[-300:])

        gen = (dest1 / "classes" / "RLM_SplitInvoicesController.cls")
        check("generated .cls has the RLM_-prefixed name", gen.exists())
        if gen.exists():
            body = gen.read_text(encoding="utf-8")
            check("generated declaration is single-prefixed",
                  "class RLM_SplitInvoicesController" in body and "RLM_RLM_" not in body)
            check("generated cross-reference renamed", "RLM_InvoiceAgingController.x()" in body)

        txn = (dest1 / "classes" / "RLM_TxnJournalRelatedListController.cls")
        check("over-length class emitted under the shortened name", txn.exists())
        check("the 43-char orphan name was NOT emitted",
              not (dest1 / "classes" / "RLM_TransactionJournalRelatedListController.cls").exists())

        # Re-run into a fresh dir; a maintained generator must be reproducible.
        dest2 = td / "out2"
        run(dest2)
        b1 = (dest1 / "classes" / "RLM_SplitInvoicesController.cls").read_text(encoding="utf-8") if gen.exists() else ""
        b2p = (dest2 / "classes" / "RLM_SplitInvoicesController.cls")
        b2 = b2p.read_text(encoding="utf-8") if b2p.exists() else "<missing>"
        check("re-running the build is byte-identical", b1 == b2)


def _no_raise(fn):
    try:
        fn()
        return True
    except Exception:
        return False


def main():
    print("=" * 80)
    print("build_billing_ui_module.py regression guard (pack 084)")
    print("=" * 80)
    m = _load_module()
    test_apex_map_within_limit(m)
    test_guard_fails_loudly(m)
    test_no_double_prefix(m)
    test_idempotent(m)
    test_end_to_end_build_is_safe_and_idempotent(m)
    print("=" * 80)
    print(f"{_passed}/{_total} checks passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
