# plg-pcm - NovaSpark Product Catalog (Minimal PLG)

SFDMU plan that loads the minimal product-model dependencies required by `post_plg` pricing metadata.

## Key Product Selection

This plan intentionally includes only these three product codes:

- `NS-STARTER`
- `NS-PRO`
- `NS-ENTERPRISE`

`NS-PRO2` is intentionally excluded.

Why: `RLM_PricingPageController` currently resolves Pro via:

- `SELECT ... FROM Product2 WHERE Name LIKE 'NovaSpark Pro%' ... LIMIT 1`

In `MuthuPLGDEMO`, that query resolves to product code `NS-PRO` (not `NS-PRO2`).

## Objects Loaded

| Object | Operation | externalId |
|---|---|---|
| `ProrationPolicy` | Upsert | `Name` |
| `ProductSellingModel` | Upsert | `Name;SellingModelType` |
| `Product2` | Upsert | `StockKeepingUnit` |
| `ProductSellingModelOption` | Upsert | `Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType` |
| `ProductRampSegment` | Insert | traversal composite key |

## Product Ramp Segments

`ProductRampSegment` records are included for these products when present in source.

`StockKeepingUnit` is normalized to match `ProductCode` (`NS-STARTER`, `NS-PRO`, `NS-ENTERPRISE`) so SKU is the canonical product key for PLG plans.

Because `ProductRampSegment` identity is lookup-based and `Name` is auto-numbered, this plan uses `Insert`. Re-running without cleanup may create duplicates.

## Extraction (Read-Only Source)

```bash
sf sfdmu run \
  --sourceusername MuthuPLGDEMO \
  --targetusername csvfile \
  --path datasets/sfdmu/plg/en-US/plg-pcm
```

## Load Order

Load this plan before `plg-pricing`.

```bash
sf sfdmu run \
  --sourceusername csvfile \
  --targetusername <sf-org-alias> \
  --path datasets/sfdmu/plg/en-US/plg-pcm
```

