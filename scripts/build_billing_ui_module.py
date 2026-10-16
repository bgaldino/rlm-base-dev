#!/usr/bin/env python3
"""
Build script for unpackaged/post_billing_ui/ module.
Copies and renames LWC components, Apex classes, static resources, and flexipages
from extracted/maaron-billinglwc/, applying RLM namespace prefixes throughout.

⚠ This is a ONE-SHOT bootstrap, not a maintained round-trip generator. Its source
tree (extracted/maaron-billinglwc, gitignored — see .gitignore) is absent from a
fresh clone, so the script cannot run there. Only 11 of the 34 .cls files in
unpackaged/post_billing_ui/classes/ are its outputs; the other 23 (every *Test class
plus a handful of controllers) are hand-authored — see that directory's README.md.

Importing this module has no side effects: the build runs only under
`if __name__ == "__main__"` (via main()), so the rename helpers can be unit-tested in
isolation — see tests/test_build_billing_ui_module.py.

Overrides (env var or CLI arg), used by the tests so a run never touches the repo tree:
  RLM_BILLING_LWC_SRC / argv[1] — source bundle root (default extracted/maaron-billinglwc)
  RLM_BILLING_UI_DEST           — module output dir (default unpackaged/post_billing_ui)
  RLM_BILLING_UI_FLEXIPAGE_DEST — flexipage output dir (default templates/.../billing_ui)
"""
import os
import re
import shutil
import sys
from pathlib import Path

# Repo root = parent of this script's directory (scripts/).
ROOT = Path(__file__).resolve().parents[1]

# Salesforce caps Apex class names at 40 characters, so every APEX_MAP *value*
# must fit — a longer name could never deploy. validate_apex_map() enforces it.
MAX_APEX_NAME_LEN = 40

# ── Rename maps ──────────────────────────────────────────────────────────────

LWC_MAP = {
    "billingCaseMetrics":            "rlmBillingCaseMetrics",
    "billingScheduleGroupHierarchy": "rlmBillingScheduleGroupHierarchy",
    "billingStatus":                 "rlmBillingStatus",
    "bsgConsolidatedTimeline":       "rlmBsgConsolidatedTimeline",
    "bsgSchedulesTimeline":          "rlmBsgSchedulesTimeline",
    "collectionRuleBuilder":         "rlmCollectionRuleBuilder",
    "collectionsDashboard":          "rlmCollectionsDashboard",
    "disputeDetails":                "rlmDisputeDetails",
    "invoiceAging":                  "rlmInvoiceAging",
    "invoiceAgingChart":             "rlmInvoiceAgingChart",
    "invoiceHealth":                 "rlmInvoiceHealth",
    "invoiceProductSummary":         "rlmInvoiceProductSummary",
    "invoiceTaxSummaryRl":           "rlmInvoiceTaxSummary",
    "invoiceTransactionJournalsRl":  "rlmInvoiceTransactionJournals",
    "paymentsData":                  "rlmPaymentsData",
    "splitInvoicesCards":            "rlmSplitInvoicesCards",
    "splitInvoicesView":             "rlmSplitInvoicesView",
}

APEX_MAP = {
    "BSGTimelineController":                   "RLM_BSGTimelineController",
    "BillingCaseMetricsController":            "RLM_BillingCaseMetricsController",
    "BillingScheduleGroupController":          "RLM_BillingScheduleGroupController",
    "CollectionsDashboardController":          "RLM_CollectionsDashboardController",
    "DisputeDetailsController":                "RLM_DisputeDetailsController",
    "InvoiceAgingController":                  "RLM_InvoiceAgingController",
    "InvoiceProductSummaryController":         "RLM_InvoiceProductSummaryController",
    "InvoiceTaxSummaryController":             "RLM_InvoiceTaxSummaryController",
    "PaymentsDataController":                  "RLM_PaymentsDataController",
    "SplitInvoicesController":                 "RLM_SplitInvoicesController",
    # Shortened by hand to fit the 40-char cap (RLM_TransactionJournalRelatedListController
    # is 43 and could never deploy); the shipped class is RLM_TxnJournalRelatedListController.
    "TransactionJournalRelatedListController": "RLM_TxnJournalRelatedListController",
}

FLEXIPAGE_MAP = {
    "BSG_Layout_Test":                   "RLM_Billing_Schedule_Group_Record_Page",
    "Case_Record_Page":                  "RLM_Case_Record_Page",
    "Collections_Dashboard":             "RLM_Collections_Dashboard",
    "Collection_Rule_Builder":           "RLM_Collection_Rule_Builder",
    "Payment_Plans":                     "RLM_Payment_Plans",
    "RLM_Billing_Account_Record_Page":   "RLM_Billing_Account_Record_Page",
    "RLM_Billing_Invoice_Record_Page":   "RLM_Billing_Invoice_Record_Page",
    "RLM_Order_Record_Page":             "RLM_Order_Record_Page",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def validate_apex_map(apex_map=APEX_MAP):
    """Fail loudly if any target Apex class name exceeds Salesforce's 40-char cap.
    Called at the start of a build so a bad edit to APEX_MAP stops before writing
    an undeployable class; also exercised directly by the test suite."""
    overlong = {v: len(v) for v in apex_map.values() if len(v) > MAX_APEX_NAME_LEN}
    if overlong:
        raise ValueError(
            f"APEX_MAP target name(s) over the {MAX_APEX_NAME_LEN}-char Apex limit: {overlong}"
        )


def apply_all_renames(text: str) -> str:
    """Apply all LWC and Apex rename substitutions to text content.

    Idempotent: running it twice is a no-op (asserted by the test suite). The Apex
    pass uses a `(?<!RLM_)` negative lookbehind so an occurrence that is already the
    renamed, RLM_-prefixed form is left alone — a plain str.replace re-prefixed it to
    `RLM_RLM_…` because every APEX_MAP value contains its own key as a substring.
    The LWC pass keeps plain str.replace: each value capitalizes the key's first
    letter after `rlm`, so the lowercase key never occurs in the output.
    """
    # Sort by length desc so longer keys don't get partially replaced first
    for old, new in sorted(LWC_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
    for old, new in sorted(APEX_MAP.items(), key=lambda x: -len(x[0])):
        text = re.sub(rf'(?<!RLM_){re.escape(old)}', new, text)
    return text


def make_cls_transform(old, new):
    """Transform for a .cls file: rewrite the class declaration, then all renames."""
    def transform(text):
        # Replace class declaration (handles with/without sharing variants)
        text = re.sub(
            rf'\bpublic\s+((?:with\s+sharing|without\s+sharing)\s+)?class\s+{re.escape(old)}\b',
            lambda m: f'public {m.group(1) or ""}class {new}'.replace("  ", " "),
            text
        )
        # Apply all cross-reference renames (idempotent, so it will not re-prefix
        # the declaration just rewritten above)
        text = apply_all_renames(text)
        return text
    return transform


def make_fp_transform(old, new):
    """Transform for a flexipage: apply renames, then fix the masterLabel."""
    def transform(text):
        # Apply all LWC component name renames (covers <componentName> tags etc.)
        text = apply_all_renames(text)
        # Update masterLabel if it matches the old page name
        old_label = old.replace("_", " ")
        new_label = new.replace("_", " ")
        text = text.replace(f"<masterLabel>{old_label}</masterLabel>",
                             f"<masterLabel>{new_label}</masterLabel>")
        return text
    return transform


def missing_sources(src_root: Path):
    """Return every mapped source input (repo-relative to `src_root`) that is absent.

    This is the single source of truth for what a complete extraction must contain,
    used by main() as a PREFLIGHT: a fixed bundle has no valid subset, and the default
    destination is the committed module, so a partial extraction must be caught before
    the first write — otherwise it clobbers committed output with a mixed/partial
    bundle and only then exits nonzero. An LWC bundle needs at least its same-name
    .js and .js-meta.xml to deploy; Apex needs both .cls and .cls-meta.xml.
    """
    missing = []
    for old in LWC_MAP:
        for rel in (f"lwc/{old}/{old}.js", f"lwc/{old}/{old}.js-meta.xml"):
            if not (src_root / rel).exists():
                missing.append(rel)
    for old in APEX_MAP:
        for ext in (".cls", ".cls-meta.xml"):
            rel = f"classes/{old}{ext}"
            if not (src_root / rel).exists():
                missing.append(rel)
    for fname in ("InvoiceCardLogo.png", "InvoiceCardLogo.resource-meta.xml"):
        rel = f"staticresources/{fname}"
        if not (src_root / rel).exists():
            missing.append(rel)
    for old in FLEXIPAGE_MAP:
        rel = f"flexipages/{old}.flexipage-meta.xml"
        if not (src_root / rel).exists():
            missing.append(rel)
    return missing


def _disp(path: Path) -> str:
    """Render a path relative to ROOT when it lives inside the repo, else absolute.
    SRC may be overridden (RLM_BILLING_LWC_SRC / argv[1]) to a dir outside the repo,
    so source paths are not guaranteed to be under ROOT."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_write(src_path: Path, dst_path: Path, transform=None):
    """Copy a file, optionally transforming its text content."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if transform is None:
        shutil.copy2(src_path, dst_path)
        print(f"  COPY  {_disp(src_path)}  →  {_disp(dst_path)}")
    else:
        content = src_path.read_text(encoding="utf-8")
        new_content = transform(content)
        dst_path.write_text(new_content, encoding="utf-8")
        changed = content != new_content
        marker = "[modified]" if changed else "[unchanged]"
        print(f"  WRITE {marker}  {_disp(dst_path)}")


def main(argv=None):
    argv = sys.argv if argv is None else argv
    # Fail loudly before writing anything if the rename map is undeployable.
    validate_apex_map()

    # Source of the extracted billing LWC bundle. Defaults to extracted/maaron-billinglwc
    # under the repo, but can be overridden via RLM_BILLING_LWC_SRC or the first CLI arg.
    SRC = Path(
        os.environ.get("RLM_BILLING_LWC_SRC")
        or (argv[1] if len(argv) > 1 else ROOT / "extracted" / "maaron-billinglwc")
    ).resolve()
    # Output dirs default into the repo but are overridable, so the tests can point
    # a run at a throwaway tree instead of clobbering the committed module.
    DEST_MODULE = Path(
        os.environ.get("RLM_BILLING_UI_DEST") or ROOT / "unpackaged" / "post_billing_ui"
    ).resolve()
    DEST_FLEXIPAGES = Path(
        os.environ.get("RLM_BILLING_UI_FLEXIPAGE_DEST")
        or ROOT / "templates" / "flexipages" / "standalone" / "billing_ui"
    ).resolve()

    # ── 0. Preflight ─────────────────────────────────────────────────────────
    # Verify EVERY mapped source input exists before creating or writing a single
    # destination file. The default destination is the committed module, so a
    # broken/incomplete extraction must fail here — not after half the bundle has
    # already overwritten committed output. Nothing below runs unless the source
    # is complete.
    missing = missing_sources(SRC)
    if missing:
        print("=== PREFLIGHT FAILED ===")
        print(f"{len(missing)} mapped source input(s) missing — a broken/incomplete "
              "extraction, not a valid subset. Nothing was written:")
        for m in missing:
            print(f"  MISSING  {m}")
        return 1

    # ── 1. LWC components ────────────────────────────────────────────────────
    print("\n=== LWC COMPONENTS ===")
    lwc_src = SRC / "lwc"
    lwc_dst = DEST_MODULE / "lwc"

    for old_name, new_name in LWC_MAP.items():
        src_dir = lwc_src / old_name
        dst_dir = lwc_dst / new_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n  [{old_name}] → [{new_name}]")

        for src_file in sorted(src_dir.iterdir()):
            # Rename the file itself: replace old_name with new_name in filename
            new_filename = src_file.name.replace(old_name, new_name)
            dst_file = dst_dir / new_filename

            ext = src_file.suffix.lower()
            is_text = ext in (".js", ".html", ".css", ".xml", ".json", ".svg", ".txt", ".md")

            if is_text:
                read_write(src_file, dst_file, transform=apply_all_renames)
            else:
                read_write(src_file, dst_file)

    # ── 2. Apex classes ──────────────────────────────────────────────────────
    print("\n=== APEX CLASSES ===")
    cls_src = SRC / "classes"
    cls_dst = DEST_MODULE / "classes"
    cls_dst.mkdir(parents=True, exist_ok=True)

    for old_name, new_name in APEX_MAP.items():
        for ext in (".cls", ".cls-meta.xml"):
            src_file = cls_src / f"{old_name}{ext}"
            dst_file = cls_dst / f"{new_name}{ext}"
            if ext == ".cls":
                read_write(src_file, dst_file, transform=make_cls_transform(old_name, new_name))
            else:
                # meta.xml: just apply renames (class name doesn't appear here typically,
                # but apply anyway for safety)
                read_write(src_file, dst_file, transform=apply_all_renames)

    # ── 3. Static resources ──────────────────────────────────────────────────
    print("\n=== STATIC RESOURCES ===")
    sr_src = SRC / "staticresources"
    sr_dst = DEST_MODULE / "staticresources"
    sr_dst.mkdir(parents=True, exist_ok=True)

    for fname in ("InvoiceCardLogo.png", "InvoiceCardLogo.resource-meta.xml"):
        src_file = sr_src / fname
        dst_file = sr_dst / fname
        if fname.endswith(".xml"):
            read_write(src_file, dst_file, transform=apply_all_renames)
        else:
            read_write(src_file, dst_file)

    # ── 4. Flexipages ─────────────────────────────────────────────────────────
    print("\n=== FLEXIPAGES ===")
    fp_src = SRC / "flexipages"
    DEST_FLEXIPAGES.mkdir(parents=True, exist_ok=True)

    for old_name, new_name in FLEXIPAGE_MAP.items():
        src_file = fp_src / f"{old_name}.flexipage-meta.xml"
        dst_file = DEST_FLEXIPAGES / f"{new_name}.flexipage-meta.xml"
        print(f"\n  [{old_name}] → [{new_name}]")
        read_write(src_file, dst_file, transform=make_fp_transform(old_name, new_name))

    # ── 5. Verification summary ────────────────────────────────────────────────
    # Count only the generator's OWN outputs, against len(MAP). The default
    # destination also holds 23 hand-authored classes (see README.md), so globbing
    # the whole directory would report "34 (expected 11)" and contradict that split.
    print("\n\n=== VERIFICATION ===")

    lwc_present = [n for n in LWC_MAP.values() if (DEST_MODULE / "lwc" / n).exists()]
    print(f"LWC components:      {len(lwc_present)} / {len(LWC_MAP)} generator-owned present")

    cls_present = [n for n in APEX_MAP.values() if (DEST_MODULE / "classes" / f"{n}.cls").exists()]
    meta_present = [n for n in APEX_MAP.values() if (DEST_MODULE / "classes" / f"{n}.cls-meta.xml").exists()]
    print(f"Apex .cls files:     {len(cls_present)} / {len(APEX_MAP)} generator-owned present")
    print(f"Apex meta files:     {len(meta_present)} / {len(APEX_MAP)} generator-owned present")
    for n in sorted(cls_present):
        print(f"  {n}.cls")

    sr_names = ("InvoiceCardLogo.png", "InvoiceCardLogo.resource-meta.xml")
    sr_present = [n for n in sr_names if (DEST_MODULE / "staticresources" / n).exists()]
    print(f"\nStatic resources:    {len(sr_present)} / {len(sr_names)} generator-owned present")

    fp_present = [n for n in FLEXIPAGE_MAP.values() if (DEST_FLEXIPAGES / f"{n}.flexipage-meta.xml").exists()]
    print(f"\nFlexipages:          {len(fp_present)} / {len(FLEXIPAGE_MAP)} generator-owned present")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
