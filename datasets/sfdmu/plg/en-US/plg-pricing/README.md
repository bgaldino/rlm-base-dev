# plg-pricing - NovaSpark Pricing (Minimal PLG)

SFDMU plan that loads minimal pricing dependencies for `post_plg` runtime (pricebooks, entries, and optional adjustment tiers).

## Product Scope

This plan is scoped to:

- `NS-STARTER`
- `NS-PRO`
- `NS-ENTERPRISE`

`NS-PRO2` is intentionally excluded to align with pricing-page runtime selection.

## Objects Loaded

| Object | Operation | externalId |
|---|---|---|
| `Product2` | Readonly | `StockKeepingUnit` |
| `ProductSellingModel` | Readonly | `Name;SellingModelType` |
| `Pricebook2` | Readonly | `Name;IsStandard` |
| `PricebookEntry` | Insert | `Product2.StockKeepingUnit;ProductSellingModel.Name;Pricebook2.Name` |
| `PriceAdjustmentSchedule` | Upsert | `Name` (excluded by default) |
| `PriceAdjustmentTier` | Insert | composite traversal key |

## Notes on Idempotency

- `PricebookEntry` and `PriceAdjustmentTier` use lookup-traversal composite keys and are configured as `Insert` (repository pattern used for SFDMU v5 traversal limitations).
- Re-running this plan without cleanup may create duplicates for those objects.
- SKU is canonical in this plan: `Product2.StockKeepingUnit` is expected to match `ProductCode` for all PLG products.
- Pricebook scope is Standard Price Book only (`Pricebook2.IsStandard = true`), matching fallback logic in the PLG controller.

## Extraction (Read-Only Source)

```bash
sf sfdmu run \
  --sourceusername MuthuPLGDEMO \
  --targetusername csvfile \
  --path datasets/sfdmu/plg/en-US/plg-pricing
```

## Loading

Run after `plg-pcm`.

```bash
sf sfdmu run \
  --sourceusername csvfile \
  --targetusername <sf-org-alias> \
  --path datasets/sfdmu/plg/en-US/plg-pricing
```

