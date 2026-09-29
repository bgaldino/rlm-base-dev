# dassault-pcm Data Plan

SFDMU data plan for the Dassault Systèmes product catalog (PCM). The CSVs are
generated from the customer workbook `Portfolio Sample for Salesforce.xlsx`
("Reference Portfolio" and "Industry Portfolio" sheets) by:

```bash
python scripts/dassault/build_dassault_catalog.py "<path>/Portfolio Sample for Salesforce.xlsx"
```

Do not hand-edit the CSVs; change the workbook or the generator and regenerate.
Prices are in the companion plan [`dassault-pricing`](../dassault-pricing/README.md).

## Loading

No CCI task is registered yet. Load directly with SFDMU:

```bash
sf sfdmu run --sourceusername CSVFILE --targetusername <username> \
  -p datasets/sfdmu/dassault/en-US/dassault-pcm --canmodify <my-domain host> --noprompt
```

Load this plan before `dassault-pricing`.

## Workbook → Revenue Cloud mapping

| Workbook | Revenue Cloud | Notes |
|----------|---------------|-------|
| Product Number (e.g. `5CC-AP2`) | `Product2.StockKeepingUnit` | Unique key; 39 priced products |
| Item Trig | `Product2.ProductCode` | |
| Item Name | `Product2.Name` | Several names exist per product number; the Industry Portfolio name is used when available, otherwise the first one. The others are listed in `Description` ("Also sold as") |
| Portfolio Name (Reference) | `Product2.Family` + `DS_REFERENCE_PORTFOLIO` attribute | A product belongs to exactly one reference portfolio, and it must reach the quote |
| Portfolio › Theme › Discipline | Catalog `DS-CAT-REF`, three category levels | Category codes are the workbook internal IDs (`DS-PRTF083`, `DS-SOL001261`, `DS-GRP003333`) |
| Industry › Segment › ISE › IPE | Catalog `DS-CAT-IND`, four category levels | ISE names are suffixed with On Premise / Public Cloud because the same name exists for both |
| Version + deployment | Product classification (`BasedOn`) | See below |
| License Scheme, License Type, Latest release | Attributes | They are printed on quote and invoice, so they must flow to transaction lines |
| Price List / Currency / price columns | `dassault-pricing` plan | |

### Classifications

| Code | Name | Products |
|------|------|----------|
| `DS-PC-V5-ONPREM` | DELMIA V5 (On Premise) | V5 items |
| `DS-PC-3DX-ONPREM` | 3DEXPERIENCE (On Premise) | V6 on-premise items |
| `DS-PC-3DX-CLOUD` | 3DEXPERIENCE (Public Cloud) | `-OC` items and Industry items marked Public Cloud |

### Attributes (category `DS-ATTR-LICENSING`)

| Code | Type | Behaviour |
|------|------|-----------|
| `DS_RELEASE` | Picklist | Required, editable. Defaults to the latest available release of the classification |
| `DS_LICENSE_SCHEME` | Picklist | Read-only at product level (Named User, Casual Named User, Concurrent, Add-On, Credit Base) |
| `DS_LICENSE_TYPE` | Picklist | Read-only at product level (Named User, Configuration, Package, Add-On) |
| `DS_DEPLOYMENT` | Picklist | Read-only, defaulted by the classification |
| `DS_REFERENCE_PORTFOLIO` | Text | Read-only at product level |
| `DS_LICENSE_COMMITMENT` | Picklist | On-premise classifications. 1 Year (default), 2 Years, 3 Years. Price impacting |
| `DS_SUBSCRIPTION_COMMITMENT` | Picklist | Public Cloud classification. 1 Year (default), 3 Years. Price impacting |

Salesforce requires a default value on a visible read-only attribute, so
attributes whose value differs per product are editable on the classification
and locked on each product. When the workbook has no value (Industry-only
products have no license scheme or type), the product attribute is hidden.

Both commitment attributes display as "Commitment"; their `Name` values differ
("Commitment (License)", "Commitment (Subscription)") because `Name` must be
unique. The commitment is hidden (and not required) on products without
multi-year prices: the credit packs and the Industry-only products. The prices
themselves are attribute-based adjustments in `dassault-pricing`.

### Selling models

The org's standard selling models are reused. Salesforce allows only one
selling model per type/term/unit combination and requires a term of 1 for
Annual, so one model per workbook price code is not possible.

| Price code | Selling model |
|------------|---------------|
| PLC, PSC | One-Time |
| ALC, ASC | Evergreen Annual |
| YLC, YSC | Term Annual (default option) |
| QLC | Term Based - Quarterly |
| TBL2, TBL3, TSC3 | Term Annual + `Commitment` attribute price override (see `dassault-pricing`) |
| ELC | Not loaded (zero for every product) |

### Bundles

The workbook has no component lists, so no bundles are created. "Package" and
"Configuration" license types are carried as the `DS_LICENSE_TYPE` attribute.

## Industry-only products

39 of the 45 Industry Portfolio products are not in the Reference Portfolio.
They are created and placed in the Industry catalog so it is complete, but they
have no price and no selling model and cannot be quoted until priced.

## Objects

| # | Object | Operation | External ID | Records |
|---|--------|-----------|-------------|---------|
| 1 | AttributePicklist | Upsert | `Name` | 6 |
| 2 | AttributePicklistValue | Upsert | `Code` | 18 |
| 3 | AttributeDefinition | Upsert | `Code` | 7 |
| 4 | AttributeCategory | Upsert | `Code` | 1 |
| 5 | AttributeCategoryAttribute | Upsert | `AttributeCategory.Code;AttributeDefinition.Code` | 7 |
| 6 | ProductClassification | Upsert | `Code` | 3 |
| 7 | ProductClassificationAttr | Upsert | `Name` | 18 |
| 8 | Product2 | Upsert | `StockKeepingUnit` | 78 |
| 9 | ProductAttributeDefinition | Upsert | `AttributeDefinition.Code;Product2.StockKeepingUnit` | 468 |
| 10 | ProductSellingModel | Readonly | `Name` | 4 |
| 11 | ProrationPolicy | Readonly | `Name` | 1 |
| 12 | ProductSellingModelOption | Upsert | `Product2.StockKeepingUnit;ProductSellingModel.Name` | 138 |
| 13 | ProductCatalog | Upsert | `Code` | 2 |
| 14 | ProductCategory | Upsert | `Code` | 47 |
| 15 | ProductCategoryProduct | Upsert | `ProductCategory.Code;Product.StockKeepingUnit` | 84 |

## Idempotency

All objects use `Upsert` or `Readonly`; nothing is deleted. The composite
traversal keys follow the `qb-pcm` / `vusion-pcm` pattern (parents with unique
`Code` / `StockKeepingUnit`). A second run against a loaded org reported no
inserts or updates and no duplicates.
