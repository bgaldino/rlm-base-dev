#!/usr/bin/env python3
"""Check the SFDMU data shapes for two layering hazards (todo 325).

Two checks, both read-only and offline, with several kinds of finding. A `sourceRecordsFilter`
in a form this check can't evaluate fails it too (`filter:`), so no plan's rows are skipped
unseen.

* `lookup` (gating): a `$$` lookup-reference column that SFDMU 5.8.0 can't resolve. A column
  such as `Pricebook2.$$Name$IsStandard` resolves only when its parts are exactly the parent
  object's `externalId` in the same pass; that shape loads correctly on built orgs (qb-pricing,
  qb-rates, qb-billing). It fails when the reference is **self-referential** (the parent is the
  same object, as in `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`), or when the plan's
  declaration of the parent keys it differently. This is the live part of "Bug 4"
  (AGENTS.md → SFDMU v5 bugs). A parent the pass doesn't declare is reported too: SFDMU sends
  a lookup whose parent isn't in the same pass as null. An `excluded` parent doesn't count.
  Only the lookup columns the declaration writes are checked (see "What a write is"), and a
  column with no values in any row is skipped, because neither asks SFDMU to resolve anything.

* `shared` (gating on change): a field of a record that more than one data shape writes,
  where the plans' final values aren't all the same. The shapes are qb, q3 and mfg (qb/ja is a
  locale overlay on qb and counts as qb for which plans are compared, though its conflicts are
  filed as `qb/ja`), plus `common`: the top-level plans every build loads
  whatever its shape (scratch_data's sample accounts, procedure-plans, inapp,
  configurator-flow), which therefore meet all three. Whichever plan loads last wins on that field, so
  loading a second shape into one org changes the first one's data. See
  docs/analysis/sfdmu-data-shape-layering.md → Shape ownership.
  - The known conflicts are in `KNOWN_SHARED_CONFLICTS`, one entry per record, field and pair of
    shapes that disagree (qb/ja filed apart from qb, as `qb/ja`), so a new record that conflicts
    fails, and so does a pair that agreed and drifts, though another pair still differs on that
    field (todo 340); an entry that no longer conflicts fails too. `--list` prints the current
    set in that form.
  - A plan's value for a field is the one its last pass writes, so Draft-then-Active staging
    inside one plan isn't a conflict. The order the shapes load in isn't known, so any
    disagreement between plans of different shapes counts.
  - Two plans of **one** shape that write different values to the same field of the same record
    are an `intra:` finding (todo 337), matched the same way and listed in
    `KNOWN_INTRA_SHAPE_CONFLICTS` with the same new/stale rules. A reload of either plan alone
    changes the data (qb-pcm and the retired qb-product-images blanked 155 product images). qb/ja
    isn't compared against qb/en-US: its plans rewrite qb's records with Japanese values by
    design (todo 212). A record counts only if a plan that loads into the pair's org creates it
    (for qb/ja, qb/en-US's too; for two top-level plans, any shape's).
  - Keys two shapes create that differ only in case (mfg `Warranty`, q3 `WARRANTY`) are listed in
    `KNOWN_CASE_COLLISIONS`, with the same new/stale rules: SFDMU matches case-sensitively,
    so the second load adds a near-duplicate.
  - A `deleteOldData` on an object another shape writes is listed in
    `KNOWN_CROSS_SHAPE_DELETES`, with the same new/stale rules. Unscoped (no `deleteQuery`, no
    WHERE), it deletes that shape's records whether or not any key meets. A scope is listed too,
    once a person has checked it spares them; this check can't tell what a scope selects.
  - Records are matched the way a load matches them: a record another shape's plan creates
    (Insert or Upsert) is the one this plan writes if its values for this plan's key fields
    are a key this plan writes. So two shapes keying an object differently still meet (mfg
    keys selling models on `Name`, qb on `Name;SellingModelType`), and a narrower key's load
    is checked against the wider key's extra fields. Key parts that appear only inside a `$$`
    column are split out of it. Two shapes' Updates to a record a third creates meet, and a
    lookup two shapes set through different parent keys counts as a conflict, as does one a shape
    clears where another sets it. Updates keyed differently meet through the record a third
    shape creates.

What a write is: every declaration that isn't `excluded`, `Readonly` or `Delete`, read from the
CSV SFDMU would read for that pass (the `objectset_source/object-set-N/` override for pass 2+
when `useSeparatedCSVFiles` is set, the plan root otherwise), keeping only the rows its
`sourceRecordsFilter` selects. A filter in a form this check doesn't evaluate fails it. Blank,
`#N/A`, `null`, `undefined`, `#ERROR!` and `#VALUE!` are null, as SFDMU reads them; other cells
keep their whitespace. A null `$$` lookup clears each of its parts (a blank `$$` key column
writes nothing). A key is built as SFDMU builds it, with empty parts dropped; a `$$` key that
drops a part this check can't place stops it (exit 2). Only the columns the query selects are
written (a CSV column it doesn't select is ignored at load), plus the `$$` key and lookup
columns and the `externalId` fields, which SFDMU queries either way. A lookup is excluded
through its Id field in `excludedFields`. `Id` and the loading plan's key fields aren't
compared; lookup columns are, `$$` composite ones included (compared part by part). Updates
create nothing, except to the platform-seeded records in `PLATFORM_SEEDED`. A
`skipExistingRecords` pass leaves a record an earlier pass of the plan created. A parent Id
key that the plan's `parent_id_lookups.json` fills at load is matched on the portable columns
it's resolved from; a declaration whose rows carry none of their key is listed in
`KNOWN_UNKEYED_WRITES`, as is one with no `externalId`; a `$$` lookup is compared whole as
well as part by part, and a key part only inside one that can't be split stops the check.

Limitations (a pass isn't a guarantee): seeded records are those in `PLATFORM_SEEDED` for a
USD-corporate org; a lookup two shapes set through partly overlapping key columns is compared on
the columns both carry only; values are compared as text, so `1` and `1.0` differ.

Usage:
    python scripts/ai/check_sfdmu_layering.py              # both checks
    python scripts/ai/check_sfdmu_layering.py --list       # also print every shared and intra-shape conflict

Exit codes: 0 = clean · 1 = findings · 2 = tool error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import sfdmu_export  # noqa: E402
import sfdmu_id_lookups  # noqa: E402

SFDMU = REPO / "datasets" / "sfdmu"
# Shape roots, relative to datasets/sfdmu. qb/ja is folded into qb: it is a locale overlay that
# reuses qb's keys, so its differences from qb/en-US are translations, not a second shape. Its
# shared conflicts with other shapes are still filed as `qb/ja` (`side_of`, todo 340).
SHAPE_ROOTS = {"qb/en-US": "qb", "qb/ja": "qb", "q3/en-US": "q3", "mfg/en-US": "mfg"}
# Top-level plans (scratch_data's sample accounts, procedure-plans, inapp, configurator-flow)
# load with every shape, so they count as one more shape that meets all the others.
COMMON = "common"
# SFDMU 5.8.0 reads these as null, case-insensitively on the trimmed cell (kept in step with
# `_SFDMU_CSV_NULL_TOKENS` in scripts/validate_sfdmu_v5_datasets.py).
NULL_TOKENS = frozenset({"", "#n/a", "null", "undefined", "#error!", "#value!"})
NOT_WRITTEN = frozenset({"readonly", "delete"})

# Lookup relationship names whose parent object isn't spelled the same as the relationship.
RELATIONSHIP_PARENT = {
    "ParentGroup": "ProductComponentGroup",
    "OverriddenProductAttributeDefinition": "ProductAttributeDefinition",
    "Pricebook": "Pricebook2",
    "ParentElement": "OmniProcessElement",
    "ActiveVersion": "AssessmentQuestionVersion",
    "ChildSellingModel": "ProductSellingModel",
    "ParentSellingModel": "ProductSellingModel",
    "ParentProductSellingModel": "ProductSellingModel",
    "RootProductSellingModel": "ProductSellingModel",
}

# `$$` lookup columns that don't resolve today, in plans no current build loads. Each is
# scoped to the exact plan, CSV and column, so a new one anywhere still fails. Remove an entry
# when its plan is converted.
KNOWN_UNRESOLVED_LOOKUPS = {
    # mfg guided selling (todo 111): self-referential and mis-keyed OmniProcess and
    # AssessmentQuestion references; the plan still uses Insert + deleteOldData.
    ("mfg/en-US/mfg-guidedselling", "AssessmentQuestion.csv", "ActiveVersion"),
    ("mfg/en-US/mfg-guidedselling", "OmniProcessAsmtQuestionVer.csv", "AssessmentQuestionVersion"),
    ("mfg/en-US/mfg-guidedselling", "OmniProcessElement.csv", "ParentElement"),
    # mfg pcm (todo 111): self-referential attribute-definition override.
    ("mfg/en-US/mfg-pcm", "ProductAttributeDefinition.csv", "OverriddenProductAttributeDefinition"),
    # The pass-2 Update of BillingTreatmentItem carries the parent as a `$$` column, but pass 2
    # declares no BillingTreatment and BillingTreatmentId is create-only (updateable false), so
    # an Update never sends it. Pass 1 sets it through the single-field `BillingTreatment.Name`:
    # a fresh ent-sb0 build had 18 items, none with a null treatment (2026-11-03).
    ("qb/en-US/qb-billing", "objectset_source/object-set-2/BillingTreatmentItem.csv", "BillingTreatment"),
}

# Shared-record conflicts known today (todo 325; summarized in the design doc's shared-records
# table), one per record, field and pair of shapes that disagree, as (object, record key, field,
# "a|b") with qb/ja apart from qb. Per pair, so a pair that agrees today (q3 and qb on currency
# rates, todo 328) fails the moment it drifts, though another pair still differs on that field
# (todo 340). The key is the one the loading plan matches on, so a pair keyed differently in two
# shapes (GL accounts: qb on AccountingCode, mfg on Name) shows from both sides. Regenerate with
# `--list`. A conflict on any other record, field or pair fails the check, and so does an entry
# that no longer conflicts.
KNOWN_SHARED_CONFLICTS = {
    # mfg against qb: mfg still ships its own copies of qb's shared records (rates, schedules,
    # legal entity, fulfillment steps, GL accounts by Name, cost book); reconciled in todo 327.
    ('CurrencyType', 'AUD', 'ConversionRate', 'mfg|qb'),
    ('CurrencyType', 'CAD', 'ConversionRate', 'mfg|qb'),
    ('CurrencyType', 'CHF', 'ConversionRate', 'mfg|qb'),
    ('CurrencyType', 'EUR', 'ConversionRate', 'mfg|qb'),
    ('CurrencyType', 'GBP', 'ConversionRate', 'mfg|qb'),
    ('CurrencyType', 'JPY', 'ConversionRate', 'mfg|qb'),
    ('FulfillmentFalloutRule', '000000001', 'RetriesAllowed', 'mfg|qb'),
    ('FulfillmentStepDefinition', 'Initiate Billing', 'UsageType', 'mfg|qb'),
    ('FulfillmentStepDefinition', 'Post Invoice', 'UsageType', 'mfg|qb'),
    ('FulfillmentStepDefinition', 'Receive Payment', 'UsageType', 'mfg|qb'),
    ('FulfillmentStepDefinitionGroup', 'Finance', 'UsageType', 'mfg|qb'),
    ('GeneralLedgerAccount', '4100', 'AccountingName', 'mfg|qb'),
    ('GeneralLedgerAccount', '4100', 'Name', 'mfg|qb'),
    ('GeneralLedgerAccount', '4200', 'AccountingName', 'mfg|qb'),
    ('GeneralLedgerAccount', '4200', 'Name', 'mfg|qb'),
    ('GeneralLedgerAccount', '4300', 'AccountingName', 'mfg|qb'),
    ('GeneralLedgerAccount', '4300', 'Name', 'mfg|qb'),
    ('GeneralLedgerAccount', '4400', 'AccountingName', 'mfg|qb'),
    ('GeneralLedgerAccount', '4400', 'Name', 'mfg|qb'),
    ('GeneralLedgerAccount', '5000', 'Description', 'mfg|qb'),
    ('GeneralLedgerAccount', '5000 Cost of Goods Sold (COGS)', 'Description', 'mfg|qb'),
    ('GeneralLedgerAccount', '5300', 'AccountingName', 'mfg|qb'),
    ('GeneralLedgerAccount', '5300', 'Name', 'mfg|qb'),
    ('GeneralLedgerAccount', '5600', 'Description', 'mfg|qb'),
    ('GeneralLedgerAccount', '5600 Professional Services', 'Description', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD CML Charges', 'CreditGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD CML Charges', 'DebitGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD CML Taxes', 'CreditGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD CML Taxes', 'DebitGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD Invoice Line Taxes', 'CreditGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD Invoice Line Taxes', 'DebitGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD PMT', 'CreditGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('GeneralLedgerAcctAsgntRule', 'USD PMT', 'DebitGeneralLedgerAccount (different parent keys)', 'mfg|qb'),
    ('LegalEntity', 'Default Legal Entity - US', 'CompanyName', 'mfg|qb'),
    ('PriceAdjustmentSchedule', 'Standard Attribute Based Adjustment', 'EffectiveFrom', 'mfg|qb'),
    ('PriceAdjustmentSchedule', 'Standard Bundle Based Adjustment', 'EffectiveFrom', 'mfg|qb'),
    ('PriceAdjustmentSchedule', 'Standard Price Adjustment Tier', 'EffectiveFrom', 'mfg|qb'),
    ('Pricebook2', 'Standard Price Book', 'CostBook.Name', 'mfg|qb'),
    ('Pricebook2', 'Standard Price Book;true', 'CostBook.Name', 'mfg|qb'),
    ('TaxPolicy', 'Default Tax Policy', 'DefaultTaxTreatment.Name', 'mfg|qb'),
    ('UnitOfMeasure', 'EACH', 'Description', 'mfg|qb'),
    ('UnitOfMeasure', 'EACH', 'UnitOfMeasureClass.Code', 'mfg|qb'),
    # mfg against q3: mfg's rate, schedule, cost-book and EACH differences, which q3 now shares
    # with qb, plus q3's own Standard Tier Based Adjustment schedule date (todo 327).
    ('CurrencyType', 'AUD', 'ConversionRate', 'mfg|q3'),
    ('CurrencyType', 'CAD', 'ConversionRate', 'mfg|q3'),
    ('CurrencyType', 'CHF', 'ConversionRate', 'mfg|q3'),
    ('CurrencyType', 'EUR', 'ConversionRate', 'mfg|q3'),
    ('CurrencyType', 'GBP', 'ConversionRate', 'mfg|q3'),
    ('CurrencyType', 'JPY', 'ConversionRate', 'mfg|q3'),
    ('PriceAdjustmentSchedule', 'Standard Attribute Based Adjustment', 'EffectiveFrom', 'mfg|q3'),
    ('PriceAdjustmentSchedule', 'Standard Bundle Based Adjustment', 'EffectiveFrom', 'mfg|q3'),
    ('PriceAdjustmentSchedule', 'Standard Price Adjustment Tier', 'EffectiveFrom', 'mfg|q3'),
    ('PriceAdjustmentSchedule', 'Standard Tier Based Adjustment', 'EffectiveFrom', 'mfg|q3'),
    ('Pricebook2', 'Standard Price Book', 'CostBook.Name', 'mfg|q3'),
    ('Pricebook2', 'Standard Price Book;true', 'CostBook.Name', 'mfg|q3'),
    ('UnitOfMeasure', 'EACH', 'Description', 'mfg|q3'),
    ('UnitOfMeasure', 'EACH', 'UnitOfMeasureClass.Code', 'mfg|q3'),
    # mfg against qb/ja: both differ from qb (todo 327, todo 212).
    # qb/ja's schedules are in JPY, its corporate currency, as the platform seeds them on a
    # JPY-corporate org; a qb/ja build never shares an org with a USD shape (todo 212).
    ('PriceAdjustmentSchedule', 'Standard Attribute Based Adjustment', 'CurrencyIsoCode', 'mfg|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Attribute Based Adjustment', 'EffectiveFrom', 'mfg|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Bundle Based Adjustment', 'CurrencyIsoCode', 'mfg|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Bundle Based Adjustment', 'EffectiveFrom', 'mfg|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Price Adjustment Tier', 'CurrencyIsoCode', 'mfg|qb/ja'),
    ('CurrencyType', 'AUD', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'CAD', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'CHF', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'EUR', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'GBP', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'JPY', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'JPY', 'IsCorporate', 'mfg|qb/ja'),
    ('CurrencyType', 'USD', 'ConversionRate', 'mfg|qb/ja'),
    ('CurrencyType', 'USD', 'IsCorporate', 'mfg|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Price Adjustment Tier', 'EffectiveFrom', 'mfg|qb/ja'),
    ('Pricebook2', 'Standard Price Book', 'CostBook.Name', 'mfg|qb/ja'),
    ('Pricebook2', 'Standard Price Book;true', 'CostBook.Name', 'mfg|qb/ja'),
    ('UnitOfMeasure', 'EACH', 'Description', 'mfg|qb/ja'),
    ('UnitOfMeasure', 'EACH', 'UnitOfMeasureClass.Code', 'mfg|qb/ja'),
    # q3 against qb/ja: qb/ja's JPY-based rates and Japanese names (todo 212). q3
    # and qb/en-US agree on all of these, which is the point of keying by pair (todo 340).
    ('PriceAdjustmentSchedule', 'Standard Attribute Based Adjustment', 'CurrencyIsoCode', 'q3|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Bundle Based Adjustment', 'CurrencyIsoCode', 'q3|qb/ja'),
    ('PriceAdjustmentSchedule', 'Standard Price Adjustment Tier', 'CurrencyIsoCode', 'q3|qb/ja'),
    ('AttributeCategory', 'AC-QB-CPU', 'Name', 'q3|qb/ja'),
    ('CurrencyType', 'AUD', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'CAD', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'CHF', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'EUR', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'GBP', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'JPY', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'JPY', 'IsCorporate', 'q3|qb/ja'),
    ('CurrencyType', 'USD', 'ConversionRate', 'q3|qb/ja'),
    ('CurrencyType', 'USD', 'IsCorporate', 'q3|qb/ja'),
    ('Pricebook2', 'Standard Price Book;true', 'CostBook.Name', 'q3|qb/ja'),
    ('UnitOfMeasure', 'GB', 'Name', 'q3|qb/ja'),
    ('UnitOfMeasure', 'MB', 'Name', 'q3|qb/ja'),
    ('UnitOfMeasure', 'm', 'Name', 'q3|qb/ja'),
    ('UnitOfMeasureClass', 'CURRENCY', 'BaseUnitOfMeasure.UnitCode', 'q3|qb/ja'),
    ('UnitOfMeasureClass', 'CURRENCY', 'DefaultUnitOfMeasure.UnitCode', 'q3|qb/ja'),
}


# Two plans of one shape writing different values to one field of one record: (object, record
# key, field). Same new/stale rules. Empty: the six found when the check was added (qb-prm and
# qb-prm-pricing on Robot Resellers and the Reseller Program, qb-accounting and qb-billing on GL
# account 3300's apostrophe) were fixed in the plans (todo 337).
KNOWN_INTRA_SHAPE_CONFLICTS: Set[Tuple[str, str, str]] = set()

# `deleteOldData` on an object another shape writes: (plan, object). An unscoped one wipes the
# other shapes' records on load; removing the delete needs owner approval (AGENTS.md). A
# `deleteQuery` or WHERE is listed here too, once a person has checked that it spares the
# other shapes' records, because this check can't tell what a scope selects.
KNOWN_CROSS_SHAPE_DELETES = {
    ("mfg/en-US/mfg-dro", "FulfillmentWorkspaceItem"),  # wipes qb's 4 items: todo 111
}

# Written declarations whose rows carry none of their key, so the shared check can't place
# them: (plan, object). Same new/stale rules.
KNOWN_UNKEYED_WRITES = {
    # Its externalId `JournalEntryRuleName` isn't a BillingBatchFilterCriteria field in the 264
    # schema, so no CSV column carries it. Only qb writes the object.
    ("qb/en-US/qb-accounting", "BillingBatchFilterCriteria"),
}

# Keys two shapes create that differ only in case, as (object, lowercased key along the
# narrower of the two plans' keys). The second shape's load adds a near-duplicate, or is
# rejected as a duplicate. Same new/stale rules.
KNOWN_CASE_COLLISIONS = {
    ("ProductCategory", "warranty"),          # q3 WARRANTY, mfg Warranty
    ("ProductComponentGroup", "accessories"),  # q3 ACCESSORIES, mfg Accessories
}


def plan_dirs(root: Path) -> Iterator[Path]:
    # Shape plans sit at <shape>/<locale>/<plan>; the plans every build loads whatever its shape
    # (scratch_data, procedure-plans, inapp, configurator-flow) sit at the top level.
    for export in sorted([*root.glob("*/export.json"), *root.glob("*/*/*/export.json")]):
        rel = export.parent.relative_to(root).as_posix()
        if "/test/" in f"/{rel}/" or ".bak" in rel or "extractions" in rel:
            continue
        yield export.parent


def shape_of(plan_rel: str) -> Optional[str]:
    for prefix, shape in SHAPE_ROOTS.items():
        if plan_rel.startswith(prefix + "/"):
            return shape
    # A top-level plan loads into every shape's org, so it's compared against each of them.
    return COMMON if "/" not in plan_rel else None


def declarations(export: dict) -> Iterator[Tuple[int, dict, str]]:
    """(0-based pass, declaration, object name) for every declaration in the plan."""
    for idx, obj_set in enumerate(sfdmu_export.normalize_object_sets(export)):
        for decl in obj_set.get("objects", []) or []:
            if isinstance(decl, dict):
                name = sfdmu_export.extract_object_name(decl.get("query", ""))
                if name:
                    yield idx, decl, name


def is_written(decl: dict) -> bool:
    if sfdmu_export.is_js_truthy(decl.get("excluded")):
        return False
    op = sfdmu_export.resolve_operation(decl.get("operation", "Readonly"))
    return op not in NOT_WRITTEN


def csv_for(plan: Path, export: dict, pass_idx: int, obj: str) -> Path:
    if pass_idx > 0 and sfdmu_export.is_js_truthy(export.get("useSeparatedCSVFiles")):
        override = plan / "objectset_source" / f"object-set-{pass_idx + 1}" / f"{obj}.csv"
        if override.exists():
            return override
    return plan / f"{obj}.csv"


def read_rows(path: Path) -> Tuple[List[str], List[dict]]:
    if not path.exists():
        return [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def key_parts(external_id: str) -> List[str]:
    return [p.strip() for p in str(external_id or "").split(";") if p.strip()]


def is_null(value: Optional[str]) -> bool:
    return (value or "").strip().lower() in NULL_TOKENS


class UnsupportedFilter(ValueError):
    """A `sourceRecordsFilter` this check can't evaluate."""


# The `sourceRecordsFilter` forms the plans use. SFDMU evaluates the filter with alasql over the
# CSV rows: `LIKE` is a case-insensitive whole-value match with `%` and `_`, `=` is strict
# equality and `<>` its negation. Anything else is reported rather than guessed at.
_FILTER = re.compile(r"^\s*(?:\[(?P<bracketed>[^\]]+)\]|(?P<plain>[A-Za-z_][A-Za-z0-9_]*))"
                     r"\s+(?P<op>LIKE|=|<>)\s+'(?P<val>[^']*)'\s*$", re.I)


def row_filter(expression: Optional[str], headers: List[str]):
    """A predicate over CSV rows for `expression`, or None when there is no filter.

    A dotted or `$$` column must be bracketed, as alasql reads an unbracketed `A.B` as a
    table and column. A column the CSV doesn't have is unsupported too: it would silently drop
    or keep every row.
    """
    expression = (expression or "").strip()
    if not expression:
        return None
    m = _FILTER.match(expression)
    if not m:
        raise UnsupportedFilter(expression)
    col = m.group("bracketed") or m.group("plain")
    if col not in headers:
        raise UnsupportedFilter(f"{expression}` (no `{col}` column in the CSV)")
    op, val = m.group("op").upper(), m.group("val")
    if op == "LIKE":
        pattern = re.compile("^" + "".join(
            "[\\s\\S]*" if c == "%" else "." if c == "_" else re.escape(c) for c in val) + "$", re.I)
        return lambda row: bool(pattern.match(row.get(col) or ""))
    if op == "=":
        return lambda row: (row.get(col) or "") == val
    return lambda row: (row.get(col) or "") != val


def filtered_rows(decl: dict, headers: List[str], rows: List[dict]) -> List[dict]:
    """The rows SFDMU writes for this declaration; an unsupported filter yields none (it is
    reported once, by `filter_errors`)."""
    try:
        keep = row_filter(decl.get("sourceRecordsFilter"), headers)
    except UnsupportedFilter:
        return []
    return rows if keep is None else [r for r in rows if keep(r)]


def filter_errors(root: Path = SFDMU) -> List[str]:
    """Every written declaration whose `sourceRecordsFilter` this check can't evaluate."""
    errors = []
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        for pass_idx, decl, obj in declarations(export):
            if not is_written(decl):
                continue
            headers, _ = read_rows(csv_for(plan, export, pass_idx, obj))
            try:
                row_filter(decl.get("sourceRecordsFilter"), headers)
            except UnsupportedFilter as exc:
                errors.append(f"{rel} pass {pass_idx + 1} {obj}: sourceRecordsFilter `{exc}` isn't "
                              f"a form this check evaluates (`[col] LIKE 'x'`, `col = 'x'`, "
                              f"`col <> 'x'`)")
    return errors


# ---- lookup check -------------------------------------------------------------------------

def lookup_findings(root: Path = SFDMU, allowed=None) -> Tuple[List[str], Set[tuple]]:
    """(findings, allowlist entries that suppressed a finding)."""
    allowed = KNOWN_UNRESOLVED_LOOKUPS if allowed is None else allowed
    findings, used = [], set()
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        # Per pass: SFDMU resolves a lookup only against a parent declared in the same pass.
        keys_by_pass: Dict[Tuple[int, str], Set[str]] = defaultdict(set)
        for pass_idx, decl, obj in declarations(export):
            if decl.get("externalId") and not sfdmu_export.is_js_truthy(decl.get("excluded")):
                keys_by_pass[(pass_idx, obj)].add(";".join(key_parts(decl["externalId"])))
        seen = set()
        for pass_idx, decl, obj in declarations(export):
            path = csv_for(plan, export, pass_idx, obj)
            marker = (pass_idx, path, decl.get("sourceRecordsFilter"), decl.get("query"),
                      json.dumps(decl.get("excludedFields")))
            if not is_written(decl) or marker in seen:
                continue
            seen.add(marker)
            headers, rows = read_rows(path)
            rows = filtered_rows(decl, headers, rows)
            # Only the lookups this declaration writes; SFDMU ignores a CSV column it doesn't.
            for col in written_columns(decl, headers):
                if col.startswith("$$") or ".$$" not in col:
                    continue
                if all(is_null(row.get(col)) for row in rows):
                    continue
                relationship, composite = col.split(".$$", 1)
                parts = ";".join(p for p in composite.split("$") if p)
                parent = RELATIONSHIP_PARENT.get(relationship, relationship)
                csv_rel = path.relative_to(plan).as_posix()
                where = f"{rel}/{csv_rel} column {col}"
                parent_keys = keys_by_pass.get((pass_idx, parent))
                if parent == obj:
                    finding = (f"{where}: self-referential `$$` lookup; use a single-field "
                               f"reference such as `{relationship}.<field>`")
                elif not parent_keys:
                    finding = (f"{where}: pass {pass_idx + 1} declares no {parent} to resolve it "
                               f"against (or add `{relationship}` to RELATIONSHIP_PARENT if its "
                               f"parent object is spelled differently)")
                elif parts not in parent_keys:
                    finding = (f"{where}: parts `{parts}` don't match {parent}'s externalId in "
                               f"pass {pass_idx + 1} ({', '.join(sorted(parent_keys))})")
                else:
                    continue
                # An allowlist entry counts as used only while it still suppresses a finding, so
                # one whose lookup has been fixed is reported stale.
                if (rel, csv_rel, relationship) in allowed:
                    used.add((rel, csv_rel, relationship))
                else:
                    findings.append(finding)
    return findings, used


# ---- shared-record check ------------------------------------------------------------------

# plan, pass, op, key, headers, rows, skipExistingRecords
Write = Tuple[str, int, str, List[str], List[str], List[dict], bool]
CREATES = frozenset({"insert", "upsert"})
# Records the platform creates in every (USD-corporate) org, as field values that identify
# them, so an Update to one lands on a record that exists without any plan inserting it.
# Observed on fresh 264 builds, 2026-11-03 (docs/analysis/sfdmu-data-shape-layering.md).
# The check models a USD-corporate org. What a JPY-corporate org (qb/ja's) seeds hasn't been
# checked; if it seeds JPY schedules, qb/ja's three JPY Updates land and conflict: Volume
# with q3's on IsActive, EffectiveFrom and CurrencyIsoCode; Attribute and Bundle with q3's and
# mfg's on CurrencyIsoCode. Extend the seeds with a qb/ja build (todo 212).
PLATFORM_SEEDED = {
    "PriceAdjustmentSchedule": [
        {"Name": "Standard Attribute Based Adjustment", "CurrencyIsoCode": "USD"},
        {"Name": "Standard Bundle Based Adjustment", "CurrencyIsoCode": "USD"},
        {"Name": "Standard Price Adjustment Tier", "CurrencyIsoCode": "USD"},
    ],
    "ProrationPolicy": [{"Name": "Default Proration Policy"}],
}


def is_seeded(obj: str, values: Dict[str, str]) -> bool:
    return any(all(values.get(f) == v for f, v in seed.items())
               for seed in PLATFORM_SEEDED.get(obj, []))


def written_columns(decl: dict, headers: List[str]) -> List[str]:
    """The CSV columns SFDMU writes for this declaration: the query's selected fields (all of
    them for `SELECT all`), less `excludedFields`, plus the `$$` columns for the key and for
    composite lookups, and the `externalId` fields, which SFDMU queries whether or not the
    query names them. A CSV column the query doesn't select is otherwise ignored at load."""
    selected = sfdmu_export.parse_select_fields(decl.get("query", ""))
    key = set(key_parts(decl.get("externalId", "")))  # SFDMU adds the key fields to the query
    excluded = set(decl.get("excludedFields") or [])
    if any(f.lower() == "all" for f in selected):
        keep = set(headers)
    else:
        keep = set(selected)
    def selected_lookup(rel: str) -> bool:
        # `Rel.Field` is written through the lookup the query selects, as `RelId`, `Rel__c`
        # for a custom `Rel__r`, or any `Rel.x` traversal.
        # `excludedFields` names object fields, so a lookup is excluded through its Id field.
        lookup = rel[:-3] + "__c" if rel.endswith("__r") else rel + "Id"
        if lookup in excluded:
            return False
        return lookup in keep or any(f.startswith(rel + ".") for f in keep)

    out = []
    for h in headers:
        if not h or h in excluded:
            continue
        if h.startswith("$$") or h in key or (h in keep and "." not in h):
            out.append(h)
        elif "." in h:
            rel = h.split(".$$", 1)[0] if ".$$" in h else h.split(".", 1)[0]
            if selected_lookup(rel):
                out.append(h)
    return out


def _split_into(values: Dict[str, str], names: List[str], value: str,
                clear_on_null: bool = False) -> None:
    if clear_on_null and is_null(value):
        # A null composite clears every part (a lookup set to null), so it's compared and merged.
        for name in names:
            values.setdefault(name, "")
        return
    pieces = (value or "").split(";")
    if len(pieces) < len(names):
        # SFDMU drops a composite's empty parts. When the parts known empty from their own
        # columns account for every dropped one, the rest line up by position; when the parts
        # known set from their own columns are exactly the pieces, the unknown ones are empty.
        empty = [n for n in names if n in values and is_null(values[n])]
        known = [n for n in names if n in values and not is_null(values[n])]
        if len(names) - len(empty) == len(pieces):
            names = [n for n in names if n not in empty]
        elif [values[n] for n in known] == pieces:
            for name in names:
                values.setdefault(name, "")
            return
        else:
            return  # ambiguous; `plan_records` reports the row if this leaves its key unknown
    if len(pieces) == len(names):
        for name, piece in zip(names, pieces):
            values.setdefault(name, piece)


def composite_names(header: str) -> List[str]:
    """The fields a `$$` lookup column carries: `Rel.$$A$B.C` gives `Rel.A` and `Rel.B.C`."""
    if not header or header.startswith("$$") or ".$$" not in header:
        return []
    rel, composite = header.split(".$$", 1)
    return [f"{rel}.{c}" for c in composite.split("$") if c]


def row_values(parts: List[str], headers: List[str], row: dict) -> Dict[str, str]:
    """The row's plain values, plus the fields that exist only inside a `$$` column, split out
    by position: the primary key column (`$$Product2.StockKeepingUnit$ProductSellingModel.Name`
    gives `ProductSellingModel.Name`) and composite lookups (`Pricebook2.$$Name$IsStandard`
    gives `Pricebook2.Name` and `Pricebook2.IsStandard`)."""
    # Raw: SFDMU keeps a non-null cell's surrounding whitespace, and trims only to test for null.
    values = {h: (row.get(h) or "") for h in headers if h and not h.startswith("$$")
              and ".$$" not in h}
    key_col = "$$" + "$".join(parts)
    if len(parts) > 1 and key_col in row:
        _split_into(values, parts, row.get(key_col))
    for h in headers:
        if h and ".$$" in h and not h.startswith("$$"):
            names = composite_names(h)
            _split_into(values, names, row.get(h), clear_on_null=True)
            # The whole value too, as SFDMU builds it (empty parts dropped), so a row that can't
            # be split still meets one that can, and a later pass's value replaces an earlier one's.
            values[h] = ";".join(p for p in (row.get(h) or "").split(";") if not is_null(p))
    return values


def key_of(values: Dict[str, str], fields: List[str]) -> Optional[Tuple[str, ...]]:
    """The row's key for `fields` as SFDMU builds it, with empty parts dropped (so `(X, '', Y)`
    and `(X, Y, '')` are both `X;Y`), or None when all are empty. A field the row doesn't carry
    is an empty part, as SFDMU drops an undefined one."""
    ident = tuple(values[f] for f in fields if not is_null(values.get(f)))
    return ident or None


def plan_records(obj: str, obj_writes: List[Write]):
    """{plan: (key fields, {key: final values}, {keys the plan creates})} for one object.

    A plan's key is its first declaration's `externalId`, and later passes override the fields
    they write on the same key, so Draft-then-Active staging leaves Active. A plan creates a
    record only through an Insert or Upsert row; an Update row changes a record only if
    something else created it. A platform-seeded record (`PLATFORM_SEEDED`) exists in every
    org, so an Update to it counts as a write another shape meets. A `skipExistingRecords` pass
    doesn't change a record an earlier pass of the plan created.
    """
    out = {}
    for rel, _, op, parts, headers, rows, skip_existing in obj_writes:
        key, records, created = out.setdefault(rel, (parts, {}, set()))
        for row in rows:
            values = row_values(parts, headers, row)
            ident = key_of(values, key)
            if ident is None and parts != key and key_of(values, parts) is not None:
                # SFDMU matches it on this pass's key, so it writes something; this check
                # can't tell which of the plan's records that is.
                raise ValueError(f"{rel}: a pass keys this object on {';'.join(parts)} and has a "
                                 f"row ({';'.join(key_of(values, parts))}) without the plan's "
                                 f"first key ({';'.join(key)}); this check can't place it")
            key_cell = row.get("$$" + "$".join(parts))
            if (len(parts) > 1 and not is_null(key_cell)
                    and any(f not in values for f in parts)):
                # The `$$` key carries parts this check couldn't place, so the row's key is
                # unknown; placing it on the parts it does know could merge distinct records.
                pieces = len(key_cell.split(";"))
                cause = (f"has {pieces} pieces for {len(parts)} key parts (a value containing "
                         f"`;`?)" if pieces > len(parts) else
                         f"drops empty parts this check can't place among {';'.join(parts)}; add "
                         f"the missing key columns to the CSV")
                raise ValueError(f"{rel}: a row's `$$` key ({key_cell}) {cause}")
            lost = [f for f in key if f not in values and any(
                f in composite_names(h) and not is_null(row.get(h)) for h in headers)]
            if lost:
                raise ValueError(f"{rel}: key part(s) {';'.join(lost)} are only in a `$$` lookup "
                                 f"this check can't split; add the column(s) to the CSV")
            if ident is None:
                continue
            if skip_existing and ident in created:
                continue  # an earlier pass of this plan created it, so this pass leaves it alone
            merged = records.setdefault(ident, {})
            # A lookup is one field: a pass that writes it through any column replaces the
            # columns earlier passes set it through.
            written = set(lookup_columns(values))
            for col in [c for c in merged if c not in values and relationship_of(c) in written]:
                del merged[col]
            merged.update({f: ("" if is_null(v) else v) for f, v in values.items() if f != "Id"})
            if op in CREATES or is_seeded(obj, merged):
                created.add(ident)
    return out


def portable_id_keys(plan: Path) -> Dict[Tuple[str, str], List[str]]:
    """{(object, Id column): portable key columns} from the plan's `parent_id_lookups.json`,
    which `LoadSFDMUData` resolves to target-org Ids before the load."""
    out = {}
    for lookup in sfdmu_id_lookups.load_lookups(str(plan)):
        for child in lookup["children"]:
            for obj in child["objects"]:
                out[(obj, child["idColumn"])] = list(child["keyColumns"])
    return out


def unkeyed_writes(root: Path = SFDMU) -> Dict[Tuple[str, str], str]:
    """{(plan, object): key} for every written declaration whose CSV rows carry none of its key
    fields, or that declares no `externalId`, so the shared check would skip it unseen."""
    out = {}
    for obj, obj_writes in _writes(root).items():
        for rel, _, _, parts, headers, rows, _ in obj_writes:
            if rows and not any(key_of(row_values(parts, headers, r), parts) for r in rows):
                out[(rel, obj)] = ";".join(parts)
    # A written declaration with no `externalId` isn't compared at all.
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        if not shape_of(rel):
            continue
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        for _, decl, obj in declarations(export):
            if is_written(decl) and not key_parts(decl.get("externalId", "")):
                out[(rel, obj)] = "(no externalId)"
    return out


def _writes(root: Path) -> Dict[str, List[Write]]:
    """Every written declaration of every shape's plans, by object, in pass order."""
    writes: Dict[str, List[Write]] = defaultdict(list)
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        if not shape_of(rel):
            continue
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        id_keys = portable_id_keys(plan)
        for pass_idx, decl, obj in sorted(declarations(export), key=lambda t: t[0]):
            parts = key_parts(decl.get("externalId", ""))
            if not is_written(decl) or not parts:
                continue
            # A parent Id key that `parent_id_lookups.json` fills at load time is matched on
            # the portable columns it's resolved from.
            parts = [c for p in parts for c in id_keys.get((obj, p), [p])]
            op = sfdmu_export.resolve_operation(decl.get("operation", "Readonly"))
            headers, rows = read_rows(csv_for(plan, export, pass_idx, obj))
            rows = filtered_rows(decl, headers, rows)
            skip = sfdmu_export.is_js_truthy(decl.get("skipExistingRecords"))
            writes[obj].append((rel, pass_idx, op, parts, written_columns(decl, headers), rows,
                                skip))
    return writes


def relationship_of(col: str) -> Optional[str]:
    """The lookup a traversal column writes (`Rel.Field`, `Rel.$$A$B`), or None."""
    if "." not in col or col.startswith("$$"):
        return None
    return col.split(".$$", 1)[0] if ".$$" in col else col.split(".", 1)[0]


def lookup_columns(values: Dict[str, str]) -> Dict[str, Set[str]]:
    """{relationship: the traversal columns that write it} for one record, cleared ones
    included (a null lookup clears the relationship)."""
    out: Dict[str, Set[str]] = defaultdict(set)
    for col in values:
        rel = relationship_of(col)
        if rel:
            out[rel].add(col)
    return out


def set_columns(values: Dict[str, str], cols: Set[str]) -> Set[str]:
    return {c for c in cols if not is_null(values.get(c))}


def parent_key_columns(values: Dict[str, str], cols: Set[str]) -> Set[str]:
    """The traversal columns that set a lookup, with a `$$` column left whole (it couldn't be
    split) standing for the fields it carries, so it overlaps a plain column of the same key."""
    out = set(cols)
    for col in cols:
        names = composite_names(col)
        if names and not any(n in values for n in names):
            out.update(names)
    return out


def locale_of(plan_rel: str) -> str:
    """The plan's shape root (`qb/en-US`, `qb/ja`, or `common` for a top-level plan): plans
    under one root load into one org."""
    return COMMON if "/" not in plan_rel else "/".join(plan_rel.split("/")[:2])


def shared_conflicts(root: Path = SFDMU) -> Dict[Tuple[str, str, str, str], str]:
    """{(object, record key, field, "a|b"): description} for every cross-shape value conflict,
    one entry per pair of shapes that disagree (qb/ja apart from qb, `side_of`).

    A plan's row lands on whatever record its own `externalId` finds, so plans are compared
    pairwise from the loading plan's side. For plans P and Q of different shapes, each record Q
    writes that exists (Q or any other plan creates it, so two shapes' Updates to a third's
    record meet) is the record P would write if Q's values for P's key fields are a key P writes.
    Every other field both carry is then compared. When P keys more narrowly than Q (mfg keys
    selling models on `Name`, qb on `Name;SellingModelType`), Q's extra key fields are compared
    too, because P's load would overwrite them. A lookup both set through different parent
    keys (qb's GL accounts by `AccountingCode`, mfg's by `Name`) is filed as "<Rel> (different
    parent keys)", as offline the two can't be shown to name the same parent, and one a shape
    clears where another sets it as "<Rel> (set in one plan, cleared in another)". Two plans'
    Updates also meet through a third shape's created record, so Updates keyed differently (by
    Name, by Code) reach the same record. The order shapes load in isn't known, so any
    disagreement counts.
    """
    return _shown(_value_conflicts(root, lambda p, q: shape_of(p) != shape_of(q), side_of,
                                   lambda p, c: True))


def side_of(plan_rel: str) -> Optional[str]:
    """The shape a cross-shape conflict is filed under, with qb/ja kept apart from qb (`qb/ja`):
    its JPY-based rates and Japanese names differ from every other shape by design (todo 212), so
    filing it as qb would let a q3/qb difference hide behind a q3/qb-ja one."""
    return "qb/ja" if locale_of(plan_rel) == "qb/ja" else shape_of(plan_rel)


def intra_shape_conflicts(root: Path = SFDMU) -> Dict[Tuple[str, str, str], str]:
    """{(object, record key, field): description} for every conflict between two plans of one
    shape (todo 337): qb-pcm and the retired qb-product-images both wrote `Product2.DisplayUrl`,
    so a reload of either plan alone changed the data. Matched as `shared_conflicts` matches,
    and labelled by plan. qb/ja isn't compared against qb/en-US: its plans rewrite qb's records
    with Japanese values by design (todo 212). Plans under one locale root are compared. A record
    exists for them if a plan of that root, a top-level plan, or their shape's en-US plans create
    it (qb/ja loads over a qb org); another shape's or locale's records don't count. Two
    top-level plans load into every shape's org, so any plan's record counts for them.
    """
    return _shown(_value_conflicts(
        root, lambda p, q: p != q and shape_of(p) == shape_of(q) and locale_of(p) == locale_of(q),
        lambda rel: rel, lambda p, c: locale_of(p) == COMMON
        or locale_of(c) in (locale_of(p), COMMON)
        or (shape_of(c) == shape_of(p) and locale_of(c).endswith("/en-US"))), by_pair=False)


def _shown(seen, by_pair: bool = True) -> Dict[tuple, str]:
    """{(object, record key, field[, "a|b"]): "a=[...]; b=[...]"}. Cross-shape conflicts stay one
    entry per pair of shapes that disagree, so a pair that agrees today fails once it drifts, though
    another pair still differs on that field (todo 340). Intra-shape ones are merged per field."""
    merged: Dict[tuple, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    for (obj, key, field, pair), by_label in seen.items():
        ident = (obj, key, field, pair) if by_pair else (obj, key, field)
        for name, values in by_label.items():
            merged[ident][name] |= values
    return {ident: "; ".join(f"{s}={sorted(v)}" for s, v in sorted(by.items()))
            for ident, by in merged.items()}


def _value_conflicts(root: Path, paired, label, creates_for):
    """The comparison behind `shared_conflicts` and `intra_shape_conflicts`, for plan pairs
    `paired(p, q)` selects, with each side's values filed under `label(plan)`. A record plan C
    creates exists for a pair loading plan P when `creates_for(P, C)`. Keyed by (object, record
    key, field, "a|b"), the two labels that disagree."""
    writes = _writes(root)
    seen: Dict[Tuple[str, str, str, str], Dict[str, Set[str]]] = defaultdict(
        lambda: defaultdict(set))
    for obj, obj_writes in writes.items():
        rels = {w[0] for w in obj_writes}
        if not any(paired(p, q) for p in rels for q in rels):
            continue
        records = plan_records(obj, obj_writes)
        created_by = [(rel, r[i]) for rel, (_, r, c) in records.items() for i in c]

        def note(obj, key, field, p_rel, p_value, q_rel, q_value):
            # Filed per pair of labels that disagree, so one pair's conflict can't hide
            # another's: q3 agreeing with qb on a rate isn't covered by mfg differing.
            pair = "|".join(sorted({label(p_rel), label(q_rel)}))
            seen[(obj, key, field, pair)][label(p_rel)].add(p_value)
            seen[(obj, key, field, pair)][label(q_rel)].add(q_value)

        def compare(p_rel, p_key, p_values, q_rel, q_values, key):
            for field in set(p_values) & set(q_values) - set(p_key):
                if p_values[field] != q_values[field]:
                    note(obj, key, field, p_rel, p_values[field], q_rel, q_values[field])
            # A lookup both write through different parent keys (qb's GL accounts by
            # AccountingCode, mfg's by Name) can't be compared field by field; whether they
            # name the same parent isn't known offline, so it counts. One that one shape sets
            # and the other clears differs whatever the keys.
            p_rels, q_rels = lookup_columns(p_values), lookup_columns(q_values)
            for rel in set(p_rels) & set(q_rels):
                p_set = set_columns(p_values, p_rels[rel])
                q_set = set_columns(q_values, q_rels[rel])
                if not p_set and not q_set:
                    continue  # both clear it
                if not p_set or not q_set:
                    if p_rels[rel] & q_rels[rel]:
                        continue  # a column both write carries the clear; compared above
                    field = f"{rel} (set in one plan, cleared in another)"
                elif parent_key_columns(p_values, p_set) & parent_key_columns(q_values, q_set):
                    continue  # a key both use; compared field by field above
                else:
                    field = f"{rel} (different parent keys)"
                shown = [", ".join(f"{c}={values[c]}" for c in sorted(cols)) or "cleared"
                         for values, cols in ((p_values, p_set), (q_values, q_set))]
                note(obj, key, field, p_rel, shown[0], q_rel, shown[1])

        for p_rel, (p_key, p_records, _) in records.items():
            for q_rel, (q_key, q_records, q_created) in records.items():
                if not paired(p_rel, q_rel):
                    continue
                # Q's record exists if Q creates it or a plan that loads with P does (Q may only
                # update it).
                created_keys = {key_of(v, q_key) for c_rel, v in created_by
                                if creates_for(p_rel, c_rel)}
                for q_ident, q_values in q_records.items():
                    if q_ident not in q_created and q_ident not in created_keys:
                        continue
                    ident = key_of(q_values, p_key)
                    p_values = p_records.get(ident) if ident else None
                    if p_values is not None:
                        compare(p_rel, p_key, p_values, q_rel, q_values, ";".join(ident))
                # Through another plan's created record, so Updates keyed differently (one by
                # Name, one by Code) still meet on the record they both reach. A record P or Q
                # creates itself is covered above.
                for c_rel, c_values in created_by:
                    if c_rel in (p_rel, q_rel) or not creates_for(p_rel, c_rel):
                        continue
                    p_ident, q_ident = key_of(c_values, p_key), key_of(c_values, q_key)
                    p_values = p_records.get(p_ident) if p_ident else None
                    q_values = q_records.get(q_ident) if q_ident else None
                    if p_values is not None and q_values is not None:
                        compare(p_rel, p_key, p_values, q_rel, q_values, ";".join(p_ident))
    return seen


def cross_shape_deletes(root: Path = SFDMU) -> Dict[Tuple[str, str], str]:
    """{(plan, object): other shapes} for every `deleteOldData` on an object another shape
    writes. With no `deleteQuery` and no WHERE in its query, the delete removes every record of
    the object, so loading this plan wipes the other shapes' records too, though no key of
    theirs ever meets this plan's. A scoped delete is reported as well: whether its scope
    spares the other shapes' records takes a person to judge, so it's allowlisted after that."""
    writes = _writes(root)
    out = {}
    for plan in plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        shape = shape_of(rel)
        if not shape:
            continue
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        for _, decl, obj in declarations(export):
            if (sfdmu_export.is_js_truthy(decl.get("excluded"))
                    or not sfdmu_export.is_js_truthy(decl.get("deleteOldData"))):
                continue
            others = sorted({shape_of(w[0]) for w in writes.get(obj, [])} - {shape})
            if others:
                out[(rel, obj)] = ", ".join(others)
    return out


def case_collisions(root: Path = SFDMU) -> Dict[Tuple[str, str], str]:
    """{(object, lowercased key): description} for keys two shapes create that differ only in
    case (mfg's `Warranty` against q3's `WARRANTY`). SFDMU matches case-sensitively, so the
    second load inserts a near-duplicate record, or the platform rejects it as a duplicate."""
    keys: Dict[Tuple[str, str], Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    for obj, obj_writes in _writes(root).items():
        records = plan_records(obj, obj_writes)
        for p_rel, (p_key, p_records, p_created) in records.items():
            folded = defaultdict(set)
            for ident in p_created:
                folded[tuple(v.lower() for v in ident)].add(ident)
            for q_rel, (q_key, q_records, q_created) in records.items():
                if shape_of(p_rel) == shape_of(q_rel):
                    continue
                # Matched along P's key, as P's load would match Q's record (see
                # `shared_conflicts`), and filed under the narrower key, so the two directions of
                # one collision share an entry.
                narrow = min(p_key, q_key, key=lambda k: (len(k), k))
                for q_ident in q_created:
                    ident = key_of(q_records[q_ident], p_key)
                    if ident is None or ident in p_created:
                        continue
                    for p_ident in folded.get(tuple(v.lower() for v in ident), ()):
                        # The narrow key's owner supplies its own values; the other plan fills
                        # only fields the owner's record lacks.
                        p_vals, q_vals = p_records[p_ident], q_records[q_ident]
                        both = {**p_vals, **q_vals} if narrow == q_key else {**q_vals, **p_vals}
                        filed = ";".join(key_of(both, narrow) or ()).lower()
                        keys[(obj, filed)][shape_of(p_rel)].add(";".join(p_ident))
                        keys[(obj, filed)][shape_of(q_rel)].add(";".join(q_ident))
    return {k: "; ".join(f"{s}={sorted(v)}" for s, v in sorted(by_shape.items()))
            for k, by_shape in keys.items()}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", action="store_true",
                        help="print every shared and intra-shape conflict, known or not")
    parser.add_argument("--root", type=Path, default=SFDMU, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = args.root
    try:
        lookups, used = lookup_findings(root)
        conflicts = shared_conflicts(root)
        intra = intra_shape_conflicts(root)
        cases = case_collisions(root)
        deletes = cross_shape_deletes(root)
        unkeyed = unkeyed_writes(root)
        bad_filters = filter_errors(root)
    except (OSError, ValueError, sfdmu_id_lookups.IdLookupError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    new = {k: v for k, v in conflicts.items() if k not in KNOWN_SHARED_CONFLICTS}
    stale = sorted(KNOWN_SHARED_CONFLICTS - set(conflicts))
    new_intra = {k: v for k, v in intra.items() if k not in KNOWN_INTRA_SHAPE_CONFLICTS}
    stale_intra = sorted(KNOWN_INTRA_SHAPE_CONFLICTS - set(intra))
    stale_lookups = sorted(KNOWN_UNRESOLVED_LOOKUPS - used)
    new_cases = sorted(set(cases) - KNOWN_CASE_COLLISIONS)
    stale_cases = sorted(KNOWN_CASE_COLLISIONS - set(cases))
    new_unkeyed = sorted(set(unkeyed) - KNOWN_UNKEYED_WRITES)
    stale_unkeyed = sorted(KNOWN_UNKEYED_WRITES - set(unkeyed))
    new_deletes = sorted(set(deletes) - KNOWN_CROSS_SHAPE_DELETES)
    stale_deletes = sorted(KNOWN_CROSS_SHAPE_DELETES - set(deletes))
    for line in lookups:
        print(f"lookup: {line}")
    for line in bad_filters:
        print(f"filter: {line}")
    for (obj, key, field, pair), shown in sorted(new.items()):
        print(f"shared: {obj} '{key}' {field} differs between {pair.replace('|', ' and ')} "
              f"({shown}) and isn't in KNOWN_SHARED_CONFLICTS for that pair")
    for (obj, key, field), shown in sorted(new_intra.items()):
        print(f"intra: {obj} '{key}' {field} differs between two plans of one shape ({shown}), so "
              f"a reload of either alone changes it, and isn't in KNOWN_INTRA_SHAPE_CONFLICTS")
    for obj, key, field in stale_intra:
        print(f"intra: {obj} '{key}' {field} is in KNOWN_INTRA_SHAPE_CONFLICTS but no longer "
              f"conflicts; remove it")
    for obj, key in new_cases:
        print(f"shared: {obj} keys differ only in case between shapes ({cases[(obj, key)]}) and "
              f"aren't in KNOWN_CASE_COLLISIONS")
    for obj, key in stale_cases:
        print(f"shared: ({obj!r}, {key!r}) is in KNOWN_CASE_COLLISIONS but no longer collides; "
              f"remove it")
    for plan, obj in new_unkeyed:
        print(f"shared: {plan} {obj} rows carry none of its key ({unkeyed[(plan, obj)]}), so "
              f"they can't be compared; add the key columns, or a parent_id_lookups.json entry "
              f"for a parent Id key, and it isn't in KNOWN_UNKEYED_WRITES")
    for plan, obj in stale_unkeyed:
        print(f"shared: ({plan!r}, {obj!r}) is in KNOWN_UNKEYED_WRITES but its rows are keyed now; "
              f"remove it")
    for plan, obj in new_deletes:
        print(f"shared: {plan} {obj} has deleteOldData on an object {deletes[(plan, obj)]} also "
              f"writes, and isn't in KNOWN_CROSS_SHAPE_DELETES (unscoped, it deletes their "
              f"records; scoped, check the scope spares them)")
    for plan, obj in stale_deletes:
        print(f"shared: ({plan!r}, {obj!r}) is in KNOWN_CROSS_SHAPE_DELETES but no longer deletes "
              f"another shape's records; remove it")
    for plan, name, relationship in stale_lookups:
        print(f"lookup: {plan}/{name} {relationship} is in KNOWN_UNRESOLVED_LOOKUPS but no longer "
              f"needs it; remove it")
    for obj, key, field, pair in stale:
        print(f"shared: {obj} '{key}' {field} is in KNOWN_SHARED_CONFLICTS for "
              f"{pair.replace('|', ' and ')}, but that pair no longer conflicts; remove it")
    if args.list:
        for (obj, key, field, pair), shown in sorted(conflicts.items()):
            print(f"known: ({obj!r}, {key!r}, {field!r}, {pair!r}),  # {shown}")
        for (obj, key, field), shown in sorted(intra.items()):
            print(f"known intra: ({obj!r}, {key!r}, {field!r}),  # {shown}")
    failed = bool(lookups or bad_filters or new or stale or new_intra or stale_intra
                  or stale_lookups or new_cases
                  or stale_cases or new_deletes or stale_deletes or new_unkeyed or stale_unkeyed)
    print(f"{len(lookups)} unresolvable `$$` lookup(s); {len(conflicts)} shared conflict(s), "
          f"{len(new)} new, {len(stale)} stale; {len(intra)} intra-shape conflict(s), "
          f"{len(new_intra)} new, {len(stale_intra)} stale; {len(cases)} case-only key collision(s), "
          f"{len(new_cases)} new, {len(stale_cases)} stale; {len(deletes)} cross-shape "
          f"delete(s), {len(new_deletes)} new, {len(stale_deletes)} stale; {len(unkeyed)} "
          f"unkeyed write(s), {len(new_unkeyed)} new, {len(stale_unkeyed)} stale. "
          f"{'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
