# Delta Term Builder — Product Catalog (PCM) dataset

Product Catalog Management data for the **Delta Term Builder** demo app
(`unpackaged/post_term_builder/`). It stands up a small, self-contained
route-negotiation catalog: one **Term** bundle whose components are chosen
dynamically from a **fare-class** classification, plus the route attributes a rep
edits on the Term.

This plan loads **PCM structure only**. Pricing (Standard `PricebookEntry` at
`UnitPrice = 0` for the Term and each fare) is a separate concern and lives in the
sibling `dl-pricing` plan — **load `dl-termbuilder` first, then `dl-pricing`.**

## Catalog model

- **Catalog** `DL-CONTRACTS` → **Category** `DL-TERMS` (contains only `DL-TERM`).
- **Classifications:** `PC-DL-TERM` (the Term) and `PC-DL-FARE` (fare classes).
- **Term bundle** `DL-TERM` — `Type = Bundle`, `BasedOn = PC-DL-TERM`,
  `ConfigureDuringSale = Allowed`.
- **Dynamic component** — one `ProductRelatedComponent` links the Term to the fare
  *classification* (not a fixed child): `ParentProduct = DL-TERM`,
  `ChildProductClassification = PC-DL-FARE`, component group `DL-TERM-FARES`
  (Min 0 / Max 20), relationship type
  *Bundle to Product Classification Component Relationship*. So any `PC-DL-FARE`
  product is addable under a Term, and the same fare may be added repeatedly.
- **Five fare products** (all `BasedOn = PC-DL-FARE`, `IsSoldOnlyWithOtherProds`):
  Delta One (`DL-FARE-ONE`), Premium Select (`DL-FARE-PS`), Comfort
  (`DL-FARE-COMF`), Main (`DL-FARE-MAIN`), Main Basic (`DL-FARE-BASIC`).

### Fare codes

Airline booking / fare-basis class codes (e.g. Delta One = `J, C, D, I, Z`) are
**not** baked into product names. They live in a shared, restricted
`MultiselectPicklist` global value set **`DL_Fare_Codes`** and are stored on two
fields (both in `post_term_builder`, deployed with the app, **not** loaded by this
plan):

- `Product2.DL_DefaultFareCodes__c` — the canonical codes intrinsic to each fare,
  **carried in this dataset's `Product2.csv`** (`;`-delimited multiselect values).
- `QuoteLineItem.DL_FareCodes__c` — the editable per-line copy, **seeded** from the
  product default when a fare is added to a Term (see
  `RLM_DeltaTermBuilderController.buildFareLineFields`). A rep may adjust the set
  per deal. Non-price-impacting; persisted inline via Place Sales Transaction.

### Route + geography attributes (on `PC-DL-TERM`, all `IsPriceImpacting = false`)

`DL_ScopeType` sets scope granularity (`Airport`, `City`, `Country`, `Region`,
`Super-region`, `Custom`); `DL_MarketGroup` is the free-text market/route grouping
the scope applies to. `DL_Origin` / `DL_Destination` share one curated endpoint
picklist (`ATL`, `JFK`, `LHR`, `US50`, `EMEAI`); `DL_Directionality` (Between /
Directional); `DL_Measure` (Share Gap / Share of Flights / No Requirement);
`DL_RequirementValue` and `DL_SpecialConditions` are free text. Fare lines carry
no attributes.

> **Includes/Excludes is not an attribute.** The scope operator (Includes vs
> Excludes) is a **transient, client-only UI toggle** on the Term rail card — it is
> deliberately *not* seeded here and not a `DL_*` attribute, so it never persists on
> the Term. `dlDemoModel`'s `scopeLabel` / `resolveTermForMarket` take the operator
> as a parameter (default `Includes`).

## Load order & operations

Objects load top-to-bottom (parents before children). `ProductRelationshipType`
is **Readonly** — a pre-provisioned platform record used only as lookup context
for FK resolution. `ProductSellingModel` is **Upsert** (not Readonly) — this
plan provisions the `Term Annual` (`TermDefined`, 1-year) selling model itself
rather than assuming it pre-exists, so a fresh org gets it regardless of load
order relative to other catalogs. All Term and fare products default to Term
Annual, so new Term-Builder lines pick up `BillingFrequency = Annual` /
`PeriodBoundary = Anniversary` automatically.

| # | Object | Operation | External ID | Records |
|---|--------|-----------|-------------|---------|
| 1 | AttributePicklist | Upsert | `Name` | 4 |
| 2 | AttributePicklistValue | Upsert | `Code` | 16 |
| 3 | AttributeDefinition | Upsert | `Code` | 8 |
| 4 | AttributeCategory | Upsert | `Code` | 1 |
| 5 | AttributeCategoryAttribute | Upsert | `AttributeCategory.Code;AttributeDefinition.Code` | 8 |
| 6 | ProductClassification | Upsert | `Code` | 2 |
| 7 | ProductClassificationAttr | Upsert | `Name` | 8 |
| 8 | Product2 | Upsert | `StockKeepingUnit` | 6 |
| 9 | ProductSellingModel | Upsert | `Name;SellingModelType` | 1 |
| 10 | ProductSellingModelOption | Upsert | `Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType` | 6 |
| 11 | ProductRelationshipType | Readonly | `Name` | 1 |
| 12 | ProductComponentGroup | Upsert | `Code` | 1 |
| 13 | ProductRelatedComponent | Upsert | `ChildProductClassification.Code;ChildProduct.StockKeepingUnit;ParentProduct.StockKeepingUnit;ProductComponentGroup.Code;ProductRelationshipType.Name` | 1 |
| 14 | ProductCatalog | Upsert | `Code` | 1 |
| 15 | ProductCategory | Upsert | `Code` | 1 |
| 16 | ProductCategoryProduct | Upsert | `ProductCategory.Code;Product.StockKeepingUnit` | 1 |

All writable objects use **direct-field or composite Upsert** externalIds, so the
plan is idempotent — rerunning it matches existing `DL-*` records rather than
duplicating them. No `deleteOldData`; targets a clean demo org.

## Files

```
export.json                       # 16-object plan (this dir)
AttributePicklist.csv             # 4 records
AttributePicklistValue.csv        # 16 records
AttributeDefinition.csv           # 8 records
AttributeCategory.csv             # 1 records
AttributeCategoryAttribute.csv    # 8 records
ProductClassification.csv         # 2 records
ProductClassificationAttr.csv     # 8 records
Product2.csv                      # 6 records  (DL-TERM + 5 fares; carries DL_DefaultFareCodes__c)
ProductSellingModel.csv           # 1 records  (Term Annual)
ProductSellingModelOption.csv     # 6 records
ProductRelationshipType.csv       # 1 records  (Readonly: classification-component)
ProductComponentGroup.csv         # 1 records
ProductRelatedComponent.csv       # 1 records  (dynamic Term ↔ PC-DL-FARE)
ProductCatalog.csv                # 1 records
ProductCategory.csv               # 1 records
ProductCategoryProduct.csv        # 1 records
```

## Run

```bash
sf sfdmu run --sourceusername csvfile --targetusername Delta \
  --path datasets/sfdmu/dl/en-US/dl-termbuilder
# then the sibling pricing plan:
sf sfdmu run --sourceusername csvfile --targetusername Delta \
  --path datasets/sfdmu/dl/en-US/dl-pricing
```

## Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/dl/en-US/dl-termbuilder
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/dl/en-US/dl-termbuilder
```
