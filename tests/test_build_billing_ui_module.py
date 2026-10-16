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
import shutil
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


def _write_full_source(m, src: Path):
    """Materialize a COMPLETE synthetic source tree — every mapped input the
    generator expects (all LWC_MAP dirs, all APEX_MAP .cls/.cls-meta pairs, both
    static resources, all FLEXIPAGE_MAP pages) — so a build over it has nothing
    missing and must exit 0. Returns nothing; writes under `src`."""
    (src / "classes").mkdir(parents=True, exist_ok=True)
    for old in m.APEX_MAP:
        # A body that references another mapped class exercises the cross-reference
        # rename + the single-prefix guard on every class, not just one.
        (src / "classes" / f"{old}.cls").write_text(
            f"public with sharing class {old} {{\n"
            f"  public static String go() {{ return InvoiceAgingController.x(); }}\n}}\n",
            encoding="utf-8",
        )
        (src / "classes" / f"{old}.cls-meta.xml").write_text(
            "<?xml version=\"1.0\"?><ApexClass></ApexClass>\n", encoding="utf-8"
        )

    # Pick a second, distinct LWC name to cross-reference in each component body so
    # the end-to-end build actually exercises LWC name renaming (and, since
    # `invoiceAging` is a prefix of `invoiceAgingChart`, the length-desc ordering
    # guard) — not just the Apex cross-reference.
    lwc_names = list(m.LWC_MAP)
    for i, old in enumerate(lwc_names):
        other = lwc_names[(i + 1) % len(lwc_names)]
        d = src / "lwc" / old
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{old}.js").write_text(
            "import { LightningElement } from 'lwc';\n"
            f"import Other from 'c/{other}';\n"
            f"export default class extends LightningElement {{}} // {old}\n",
            encoding="utf-8",
        )
        (d / f"{old}.js-meta.xml").write_text(
            "<?xml version=\"1.0\"?><LightningComponentBundle></LightningComponentBundle>\n",
            encoding="utf-8",
        )

    (src / "staticresources").mkdir(parents=True, exist_ok=True)
    (src / "staticresources" / "InvoiceCardLogo.png").write_bytes(b"\x89PNG\r\n")
    (src / "staticresources" / "InvoiceCardLogo.resource-meta.xml").write_text(
        "<?xml version=\"1.0\"?><StaticResource></StaticResource>\n", encoding="utf-8"
    )

    (src / "flexipages").mkdir(parents=True, exist_ok=True)
    for old in m.FLEXIPAGE_MAP:
        label = old.replace("_", " ")
        (src / "flexipages" / f"{old}.flexipage-meta.xml").write_text(
            f"<?xml version=\"1.0\"?><FlexiPage><masterLabel>{label}</masterLabel></FlexiPage>\n",
            encoding="utf-8",
        )


def _run(src: Path, dest: Path):
    env = dict(os.environ,
               RLM_BILLING_LWC_SRC=str(src),
               RLM_BILLING_UI_DEST=str(dest),
               RLM_BILLING_UI_FLEXIPAGE_DEST=str(dest / "flexipages"))
    return subprocess.run([sys.executable, str(MODULE_PATH)],
                          env=env, capture_output=True, text=True)


def test_end_to_end_build_is_safe_and_idempotent(m):
    """Run the real script against a COMPLETE synthetic source, outputs redirected
    to a temp tree, and assert it exits 0, the generated Apex is correct, and a
    re-run is byte-identical."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "src"
        _write_full_source(m, src)

        dest1 = td / "out1"
        r1 = _run(src, dest1)
        check("complete-source run exits 0", r1.returncode == 0,
              (r1.stderr or r1.stdout)[-400:])

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

        # Every mapped output present — the verification block's own success criterion.
        check("all APEX_MAP classes emitted",
              all((dest1 / "classes" / f"{n}.cls").exists() for n in m.APEX_MAP.values()))
        check("all LWC_MAP components emitted",
              all((dest1 / "lwc" / n).exists() for n in m.LWC_MAP.values()))
        check("all FLEXIPAGE_MAP pages emitted",
              all((dest1 / "flexipages" / f"{n}.flexipage-meta.xml").exists()
                  for n in m.FLEXIPAGE_MAP.values()))

        # LWC cross-reference import must be renamed to the mapped `rlm…` name (and
        # never left as the lowercase source name), across the whole bundle.
        def _lwc_body(dest, new_name):
            f = dest / "lwc" / new_name / f"{new_name}.js"
            return f.read_text(encoding="utf-8") if f.exists() else ""
        lwc_names = list(m.LWC_MAP)
        lwc_xref_ok = True
        for i, old in enumerate(lwc_names):
            new = m.LWC_MAP[old]
            other_new = m.LWC_MAP[lwc_names[(i + 1) % len(lwc_names)]]
            body = _lwc_body(dest1, new)
            if f"c/{other_new}" not in body or f"c/{old}" in body or f"'c/{lwc_names[(i + 1) % len(lwc_names)]}'" in body:
                lwc_xref_ok = False
                break
        check("LWC cross-reference imports renamed to mapped rlm… names", lwc_xref_ok)

        # True re-run idempotency: run AGAIN into the same dir and assert every
        # generator-owned .cls is byte-for-byte unchanged (not just one file).
        def _all_cls(dest):
            return {n: (dest / "classes" / f"{n}.cls").read_text(encoding="utf-8")
                    for n in m.APEX_MAP.values()
                    if (dest / "classes" / f"{n}.cls").exists()}
        before = _all_cls(dest1)
        r2 = _run(src, dest1)
        check("second run into the same dir also exits 0", r2.returncode == 0,
              (r2.stderr or r2.stdout)[-400:])
        after = _all_cls(dest1)
        check("re-running into the same dir is byte-identical for every class",
              before and before == after,
              f"{sum(1 for k in before if before.get(k) != after.get(k))} class(es) differ")


def test_partial_source_fails(m):
    """A partial source tree (missing mapped inputs) is a broken extraction, not a
    valid subset. The build must exit NONZERO and name the missing inputs rather
    than silently writing an incomplete module."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "src"
        _write_full_source(m, src)
        # Remove one mapped input of each kind: a whole class, a whole LWC dir, and
        # — critically — a required file from an LWC dir that otherwise EXISTS, which
        # a bare directory-exists check would wave through.
        (src / "classes" / "SplitInvoicesController.cls").unlink()
        lwc_names = list(m.LWC_MAP)
        shutil.rmtree(src / "lwc" / lwc_names[0])
        gutted = lwc_names[1]
        (src / "lwc" / gutted / f"{gutted}.js").unlink()  # dir stays, .js gone

        dest = td / "out"
        r = _run(src, dest)
        check("partial-source run exits nonzero", r.returncode != 0,
              f"returncode={r.returncode}")
        check("failure output names a missing input",
              "MISSING" in r.stdout and "SplitInvoicesController.cls" in r.stdout,
              r.stdout[-400:])
        check("an existing-but-incomplete LWC bundle is caught",
              f"{gutted}.js" in r.stdout, r.stdout[-400:])
        # Preflight must fail BEFORE any write, so a partial extraction cannot
        # clobber committed output with a half-written bundle.
        wrote = list(dest.rglob("*")) if dest.exists() else []
        check("a failed preflight leaves the destination untouched", not wrote,
              f"unexpected writes: {[str(p) for p in wrote][:5]}")


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
    test_partial_source_fails(m)
    print("=" * 80)
    print(f"{_passed}/{_total} checks passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
