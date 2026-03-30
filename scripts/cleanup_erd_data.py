#!/usr/bin/env python3
"""Clean up data quality issues in docs/erds/erd-data.json.

Fixes:
  1. BilllingArrangement typo (triple-L) in keys, refersTo, relationship targets
  2. PDF extraction artifacts in descriptions (SEE ALSO, page numbers, bullets, truncation)
  3. Infer empty types from field name conventions
  4. Fix mistyped types (address on non-address fields, reference on date fields, etc.)
  5. Fill missing domainShort from domain using DOMAIN_MAP

Usage:
  python scripts/cleanup_erd_data.py                # apply fixes and write
  python scripts/cleanup_erd_data.py --dry-run      # show what would change
  python scripts/cleanup_erd_data.py --verbose       # show each individual change
  python scripts/cleanup_erd_data.py --dry-run --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ERD_DATA_PATH = Path(__file__).resolve().parent.parent / "docs" / "erds" / "erd-data.json"

# ---------------------------------------------------------------------------
# Domain mapping — mirrors build_erds.py DOMAIN_MAP
# ---------------------------------------------------------------------------
DOMAIN_MAP: dict[str, str] = {
    "Product Catalog Management": "PCM",
    "Product Catalog Management (Core Object)": "PCM",
    "Salesforce Pricing": "Pricing",
    "Rate Management": "Rates",
    "Product Configurator": "Configurator",
    "Transaction Management": "Transactions",
    "Transaction Management (Core Object)": "Transactions",
    "Advanced Approvals": "Approvals",
    "Dynamic Revenue Orchestrator": "DRO",
    "Usage Management": "Usage",
    "Usage Management (Core Object)": "Usage",
    "Billing": "Billing",
    "Billing (Core Object)": "Billing",
}

# ---------------------------------------------------------------------------
# Known short words / abbreviations that should NOT be treated as truncated
# ---------------------------------------------------------------------------
KNOWN_SHORT_TOKENS = {
    "id", "or", "on", "in", "is", "it", "to", "of", "an", "as", "at", "be",
    "by", "do", "go", "he", "if", "me", "my", "no", "so", "up", "us", "we",
    "the", "and", "for", "not", "are", "but", "its", "was", "has", "had",
    "can", "may", "set", "use", "new", "old", "key", "api", "org", "url",
    "tax", "log", "dml", "csv", "sql", "vat", "etc", "e.g", "i.e",
    "true", "null", "v62", "v63", "v64", "v65", "v66", "v67",
}

# Regex: trailing page-number footer like "2214 PaymentTerm Billing"
# Pattern: space, 3-4 digit number, space, one or two CamelCase/Title words at end
RE_PAGE_FOOTER = re.compile(
    r"\s+\d{3,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s*$"
)

# Regex: SEE ALSO and everything after
RE_SEE_ALSO = re.compile(r"\s*SEE ALSO[:\s].*$", re.DOTALL)

# Regex: trailing incomplete bullet enumeration (ends with bullet item but no closing)
# e.g. "• Active •" or "• CalculateTax"
RE_TRAILING_BULLETS = re.compile(
    r"\s*\u2022\s*[A-Za-z]+(?:\s*\u2022\s*[A-Za-z]*)*\s*$"
)


class ChangeTracker:
    """Accumulates change descriptions by category."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.counts: dict[str, int] = {}
        self.details: list[str] = []

    def record(self, category: str, detail: str) -> None:
        self.counts[category] = self.counts.get(category, 0) + 1
        if self.verbose:
            self.details.append(f"  [{category}] {detail}")

    def summary(self) -> str:
        lines = ["Changes summary:"]
        total = 0
        for cat in sorted(self.counts):
            lines.append(f"  {cat}: {self.counts[cat]}")
            total += self.counts[cat]
        lines.append(f"  TOTAL: {total}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fix 1: BilllingArrangement typo
# ---------------------------------------------------------------------------
def fix_typo_billarrangement(data: dict, tracker: ChangeTracker) -> dict:
    """Fix triple-L typo in object keys, refersTo, and relationship targets."""
    objects = data.get("objects", {})

    # Fix object key
    if "BilllingArrangement" in objects and "BillingArrangement" not in objects:
        objects["BillingArrangement"] = objects.pop("BilllingArrangement")
        tracker.record("typo_key", "Renamed object key BilllingArrangement -> BillingArrangement")
    elif "BilllingArrangement" in objects:
        # Both exist — merge is risky; just remove the typo key
        objects.pop("BilllingArrangement")
        tracker.record("typo_key", "Removed duplicate BilllingArrangement key (BillingArrangement already exists)")

    # Fix refersTo and relationship targets everywhere
    for obj_name, obj in objects.items():
        if not isinstance(obj, dict):
            continue
        for fname, fdata in obj.get("fields", {}).items():
            if not isinstance(fdata, dict):
                continue
            for key in ("refersTo", "relationshipName"):
                val = fdata.get(key, "")
                if isinstance(val, str) and "BilllingArrangement" in val:
                    fixed = val.replace("BilllingArrangement", "BillingArrangement")
                    fdata[key] = fixed
                    tracker.record("typo_refersTo", f"{obj_name}.{fname}.{key}: {val} -> {fixed}")
        for rel in obj.get("relationships", []):
            if isinstance(rel, dict):
                target = rel.get("target", "")
                if isinstance(target, str) and "BilllingArrangement" in target:
                    fixed = target.replace("BilllingArrangement", "BillingArrangement")
                    rel["target"] = fixed
                    tracker.record("typo_rel_target", f"{obj_name} relationship target: {target} -> {fixed}")

    return data


# ---------------------------------------------------------------------------
# Fix 2: Clean PDF extraction artifacts from descriptions
# ---------------------------------------------------------------------------
def clean_description(desc: str, obj_name: str, field_name: str, tracker: ChangeTracker) -> str:
    """Clean PDF extraction artifacts from a field description."""
    if not desc:
        return desc
    original = desc

    # Strip SEE ALSO and everything after
    desc = RE_SEE_ALSO.sub("", desc)

    # Strip trailing page number footers (e.g. "2214 PaymentTerm Billing")
    desc = RE_PAGE_FOOTER.sub("", desc)

    # Strip trailing incomplete bullet enumerations (e.g. ending with "• Active •")
    # Only strip if the bullet section at the end looks incomplete (ends with •)
    # or the last bullet item is suspiciously short
    if "\u2022" in desc:
        # Check if description ends with a lone bullet or bullet + short word
        match = re.search(r"\s*\u2022\s*$", desc)
        if match:
            desc = desc[:match.start()]

    # Strip incomplete sentences at the end:
    # If description doesn't end with terminal punctuation and the last token
    # is very short (< 4 chars) and not a known abbreviation, trim the last clause
    desc = desc.rstrip()
    if desc and desc[-1] not in ".!?\"')":
        tokens = desc.split()
        if tokens:
            last_token = tokens[-1].rstrip(",;:")
            if len(last_token) < 4 and last_token.lower() not in KNOWN_SHORT_TOKENS:
                # Trim back to the last sentence-ending punctuation
                # or to the last complete-looking clause
                for i in range(len(desc) - 1, -1, -1):
                    if desc[i] in ".!?":
                        desc = desc[: i + 1]
                        break
                else:
                    # No sentence-ender found — leave as-is rather than destroying content
                    desc = original  # revert this specific fix

    # Final cleanup
    desc = desc.rstrip()

    if desc != original:
        # Truncate for display
        short_orig = original[:80] + "..." if len(original) > 80 else original
        short_new = desc[:80] + "..." if len(desc) > 80 else desc
        tracker.record("clean_description", f"{obj_name}.{field_name}: \"{short_orig}\" -> \"{short_new}\"")

    return desc


def fix_descriptions(data: dict, tracker: ChangeTracker) -> dict:
    """Clean PDF artifacts from all field descriptions."""
    for obj_name, obj in data.get("objects", {}).items():
        if not isinstance(obj, dict):
            continue
        for fname, fdata in obj.get("fields", {}).items():
            if not isinstance(fdata, dict):
                continue
            desc = fdata.get("description", "")
            if desc:
                cleaned = clean_description(desc, obj_name, fname, tracker)
                if cleaned != desc:
                    fdata["description"] = cleaned
    return data


# ---------------------------------------------------------------------------
# Fix 3: Infer empty types from field name conventions
# ---------------------------------------------------------------------------
TYPE_INFERENCE_RULES: list[tuple[str, str]] = [
    # Order matters — more specific patterns first
    # Suffix-based
    ("Description$", "textarea"),
    ("DateTime$", "dateTime"),
    ("Date$", "dateTime"),
    ("Url$|URL$", "url"),
    ("Amount$|Price$|Total$|Balance$", "currency"),
    ("Percent$|Rate$", "percent"),
    ("Count$|Quantity$", "int"),
    ("Name$", "string"),
    ("Code$|Number$", "string"),
    # Prefix-based
    ("^Is|^Has|^Should|^May|^Can", "boolean"),
    # Must be after suffix rules: Id suffix (but not just "Id")
    (".+Id$", "reference"),
    # Exact or suffix match for Status/Type
    ("^Status$|^Type$|Status$|Type$", "picklist"),
]

# Pre-compile
_INFERENCE_COMPILED = [(re.compile(pat), typ) for pat, typ in TYPE_INFERENCE_RULES]


def infer_type(field_name: str) -> str | None:
    """Infer a type from field name conventions. Returns None if no match."""
    for pattern, typ in _INFERENCE_COMPILED:
        if pattern.search(field_name):
            return typ
    return None


def fix_empty_types(data: dict, tracker: ChangeTracker) -> dict:
    """Infer types for fields with empty or missing type."""
    for obj_name, obj in data.get("objects", {}).items():
        if not isinstance(obj, dict):
            continue
        for fname, fdata in obj.get("fields", {}).items():
            if isinstance(fdata, dict):
                current_type = fdata.get("type", "")
            elif fdata == {}:
                current_type = ""
            else:
                continue

            if current_type:
                continue  # already has a type

            inferred = infer_type(fname)
            if inferred:
                if not isinstance(fdata, dict):
                    # Convert empty dict to proper dict
                    obj["fields"][fname] = {"type": inferred}
                else:
                    fdata["type"] = inferred
                tracker.record("infer_type", f"{obj_name}.{fname}: \"\" -> \"{inferred}\"")

    return data


# ---------------------------------------------------------------------------
# Fix 4: Fix mistyped types
# ---------------------------------------------------------------------------
def fix_mistyped_types(data: dict, tracker: ChangeTracker) -> dict:
    """Correct obviously wrong type assignments from PDF extraction."""
    for obj_name, obj in data.get("objects", {}).items():
        if not isinstance(obj, dict):
            continue
        for fname, fdata in obj.get("fields", {}).items():
            if not isinstance(fdata, dict):
                continue
            current_type = fdata.get("type", "")
            if not current_type:
                continue

            new_type = None

            # address type on non-address fields
            if current_type == "address" and "Address" not in fname:
                new_type = ""  # clear it; inference (fix 3) may handle it
                tracker.record("fix_mistype", f"{obj_name}.{fname}: type \"address\" cleared (name has no 'Address')")

            # *Date or *DateTime fields with type "reference"
            if current_type == "reference" and re.search(r"Date(Time)?$", fname):
                new_type = "dateTime"
                tracker.record("fix_mistype", f"{obj_name}.{fname}: \"reference\" -> \"dateTime\"")

            # Specific known fix: BillingResumptionDate
            if fname == "BillingResumptionDate" and current_type == "reference":
                new_type = "dateTime"
                # Don't double-record if already caught by the rule above

            # Is* or Has* fields with wrong type
            if re.match(r"^(Is|Has)", fname) and current_type in ("picklist", "address"):
                new_type = "boolean"
                tracker.record("fix_mistype", f"{obj_name}.{fname}: \"{current_type}\" -> \"boolean\"")

            if new_type is not None:
                if new_type == "":
                    fdata.pop("type", None)
                else:
                    fdata["type"] = new_type

    return data


# ---------------------------------------------------------------------------
# Fix 5: Fill missing domainShort
# ---------------------------------------------------------------------------
def fix_missing_domain_short(data: dict, tracker: ChangeTracker) -> dict:
    """Derive domainShort from domain when missing."""
    for obj_name, obj in data.get("objects", {}).items():
        if not isinstance(obj, dict):
            continue
        domain = obj.get("domain", "")
        domain_short = obj.get("domainShort", "")

        if domain and not domain_short:
            # Try DOMAIN_MAP first
            short = DOMAIN_MAP.get(domain)
            if not short:
                # Fallback: strip (Core Object) suffix
                short = domain.replace(" (Core Object)", "").strip()
            obj["domainShort"] = short
            tracker.record("fill_domainShort", f"{obj_name}: domain=\"{domain}\" -> domainShort=\"{short}\"")

    return data


# ---------------------------------------------------------------------------
# Post-fix: run type inference again for fields that were cleared by fix 4
# ---------------------------------------------------------------------------
def reinfer_cleared_types(data: dict, tracker: ChangeTracker) -> dict:
    """After fix_mistyped_types clears bad types, try inference again."""
    for obj_name, obj in data.get("objects", {}).items():
        if not isinstance(obj, dict):
            continue
        for fname, fdata in obj.get("fields", {}).items():
            if not isinstance(fdata, dict):
                continue
            current_type = fdata.get("type", "")
            if current_type:
                continue
            inferred = infer_type(fname)
            if inferred:
                fdata["type"] = inferred
                tracker.record("reinfer_type", f"{obj_name}.{fname}: (cleared) -> \"{inferred}\"")
    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Clean up data quality issues in erd-data.json")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--verbose", action="store_true", help="Show each individual change")
    parser.add_argument("--input", type=Path, default=ERD_DATA_PATH, help="Path to erd-data.json")
    args = parser.parse_args()

    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tracker = ChangeTracker(verbose=args.verbose)

    # Apply fixes in order
    data = fix_typo_billarrangement(data, tracker)
    data = fix_descriptions(data, tracker)
    data = fix_mistyped_types(data, tracker)  # fix 4 before fix 3 so cleared types get inferred
    data = fix_empty_types(data, tracker)
    data = reinfer_cleared_types(data, tracker)
    data = fix_missing_domain_short(data, tracker)

    # Print results
    if tracker.verbose and tracker.details:
        print("Detailed changes:")
        for detail in tracker.details:
            print(detail)
        print()

    if tracker.counts:
        print(tracker.summary())
    else:
        print("No changes needed.")
        return

    if args.dry_run:
        print(f"\n--dry-run: no changes written to {input_path}")
    else:
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")  # trailing newline
        print(f"\nWrote cleaned data to {input_path}")


if __name__ == "__main__":
    main()
