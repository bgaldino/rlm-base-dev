#!/usr/bin/env python3
"""
Build script for unpackaged/post_billing_ui/ module.
Copies and renames LWC components, Apex classes, static resources, and flexipages
from extracted/maaron-billinglwc/, applying RLM namespace prefixes throughout.
"""
import os
import re
import shutil
from pathlib import Path

ROOT = Path("/Users/brian/Documents/GitHub/bgaldino/_bgaldino/rlm-base-dev")
SRC = ROOT / "extracted" / "maaron-billinglwc"
DEST_MODULE = ROOT / "unpackaged" / "post_billing_ui"
DEST_FLEXIPAGES = ROOT / "templates" / "flexipages" / "standalone" / "billing_ui"

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
    "TransactionJournalRelatedListController": "RLM_TransactionJournalRelatedListController",
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

def apply_all_renames(text: str) -> str:
    """Apply all LWC and Apex rename substitutions to text content."""
    # Sort by length desc so longer keys don't get partially replaced first
    for old, new in sorted(LWC_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
    for old, new in sorted(APEX_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
    return text


def read_write(src_path: Path, dst_path: Path, transform=None):
    """Copy a file, optionally transforming its text content."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if transform is None:
        shutil.copy2(src_path, dst_path)
        print(f"  COPY  {src_path.relative_to(ROOT)}  →  {dst_path.relative_to(ROOT)}")
    else:
        content = src_path.read_text(encoding="utf-8")
        new_content = transform(content)
        dst_path.write_text(new_content, encoding="utf-8")
        changed = content != new_content
        marker = "[modified]" if changed else "[unchanged]"
        print(f"  WRITE {marker}  {dst_path.relative_to(ROOT)}")


# ── 1. LWC components ────────────────────────────────────────────────────────

print("\n=== LWC COMPONENTS ===")
lwc_src = SRC / "lwc"
lwc_dst = DEST_MODULE / "lwc"

for old_name, new_name in LWC_MAP.items():
    src_dir = lwc_src / old_name
    dst_dir = lwc_dst / new_name
    if not src_dir.exists():
        print(f"  WARN  source dir not found: {src_dir}")
        continue
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


# ── 2. Apex classes ──────────────────────────────────────────────────────────

print("\n=== APEX CLASSES ===")
cls_src = SRC / "classes"
cls_dst = DEST_MODULE / "classes"
cls_dst.mkdir(parents=True, exist_ok=True)

for old_name, new_name in APEX_MAP.items():
    for ext in (".cls", ".cls-meta.xml"):
        src_file = cls_src / f"{old_name}{ext}"
        dst_file = cls_dst / f"{new_name}{ext}"
        if not src_file.exists():
            print(f"  WARN  not found: {src_file}")
            continue

        if ext == ".cls":
            def make_cls_transform(old, new):
                def transform(text):
                    # Replace class declaration (handles with/without sharing variants)
                    text = re.sub(
                        rf'\bpublic\s+((?:with\s+sharing|without\s+sharing)\s+)?class\s+{re.escape(old)}\b',
                        lambda m: f'public {m.group(1) or ""}class {new}'.replace("  ", " "),
                        text
                    )
                    # Apply all cross-reference renames
                    text = apply_all_renames(text)
                    return text
                return transform
            read_write(src_file, dst_file, transform=make_cls_transform(old_name, new_name))
        else:
            # meta.xml: just apply renames (class name doesn't appear here typically,
            # but apply anyway for safety)
            read_write(src_file, dst_file, transform=apply_all_renames)


# ── 3. Static resources ──────────────────────────────────────────────────────

print("\n=== STATIC RESOURCES ===")
sr_src = SRC / "staticresources"
sr_dst = DEST_MODULE / "staticresources"
sr_dst.mkdir(parents=True, exist_ok=True)

for fname in ("InvoiceCardLogo.png", "InvoiceCardLogo.resource-meta.xml"):
    src_file = sr_src / fname
    dst_file = sr_dst / fname
    if not src_file.exists():
        print(f"  WARN  not found: {src_file}")
        continue
    if fname.endswith(".xml"):
        read_write(src_file, dst_file, transform=apply_all_renames)
    else:
        read_write(src_file, dst_file)


# ── 4. Flexipages ────────────────────────────────────────────────────────────

print("\n=== FLEXIPAGES ===")
fp_src = SRC / "flexipages"
DEST_FLEXIPAGES.mkdir(parents=True, exist_ok=True)

for old_name, new_name in FLEXIPAGE_MAP.items():
    src_file = fp_src / f"{old_name}.flexipage-meta.xml"
    dst_file = DEST_FLEXIPAGES / f"{new_name}.flexipage-meta.xml"
    if not src_file.exists():
        print(f"  WARN  not found: {src_file}")
        continue

    def make_fp_transform(old, new):
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

    print(f"\n  [{old_name}] → [{new_name}]")
    read_write(src_file, dst_file, transform=make_fp_transform(old_name, new_name))


# ── 5. Verification summary ──────────────────────────────────────────────────

print("\n\n=== VERIFICATION ===")

lwc_dirs = list((DEST_MODULE / "lwc").iterdir()) if (DEST_MODULE / "lwc").exists() else []
print(f"LWC components:      {len(lwc_dirs)}  (expected 17)")
for d in sorted(lwc_dirs):
    files = list(d.iterdir())
    print(f"  {d.name:45s}  ({len(files)} files)")

cls_files = list((DEST_MODULE / "classes").glob("*.cls")) if (DEST_MODULE / "classes").exists() else []
meta_files = list((DEST_MODULE / "classes").glob("*.cls-meta.xml")) if (DEST_MODULE / "classes").exists() else []
print(f"\nApex .cls files:     {len(cls_files)}  (expected 11)")
print(f"Apex meta files:     {len(meta_files)}  (expected 11)")
for f in sorted(cls_files):
    print(f"  {f.name}")

sr_files = list((DEST_MODULE / "staticresources").iterdir()) if (DEST_MODULE / "staticresources").exists() else []
print(f"\nStatic resources:    {len(sr_files)}  (expected 2)")
for f in sorted(sr_files):
    print(f"  {f.name}")

fp_files = list(DEST_FLEXIPAGES.glob("*.flexipage-meta.xml")) if DEST_FLEXIPAGES.exists() else []
print(f"\nFlexipages:          {len(fp_files)}  (expected 8)")
for f in sorted(fp_files):
    print(f"  {f.name}")

print("\nDone.")
