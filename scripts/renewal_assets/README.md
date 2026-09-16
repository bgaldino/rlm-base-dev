# `scripts/renewal_assets/` — renewal-asset creation toolkit

Standalone `sf`-CLI toolkit (no CCI) for producing renewal-ready Revenue Cloud
**Assets** and giving them a realistic multi-year lifecycle history. Owned by the
`renewal-asset-creation` skill (`.cursor/skills/renewal-asset-creation/SKILL.md`)
— read that for the full workflow, Quick Rules, and Validation Checks. This file
is the file-level reference.

The core Quote → Order → Activation flow is **not** reimplemented here: it is
`scripts/build_quote_to_asset.py`. This directory adds the two things that script
does not do — spreading assets across the four renewal expiry windows, and
layering a Renewal/Upsell/Downsell event history onto assets that already exist.

## Files

| File | What it does | Runs |
|------|--------------|------|
| `build_renewal_buckets.py` | Computes the 4 expiry windows (≤30 / 30-60 / 60-90 / >90 days) from today, back-solves a start date per asset, and shells out to `../build_quote_to_asset.py` once per asset. Single-SKU or product-mix; distributes across pre-existing accounts. `--dry-run` prints the plan and touches nothing. | `python` |
| `augment_asset_lifecycle.apex` | **Additive, post-run, pristine-only.** Layers contiguous Renewal/Upsell/Downsell `AssetAction` + `AssetActionSource` + `AssetStatePeriod` records onto assets a run already created, reusing each asset's REAL PricebookEntry / ProductSellingModel / pricing / `PeriodBoundary` and deriving amounts from the Initial-Sale **state period** (booked, post-discount — never the list `UnitPrice`) and MRR from it too (not per-term `UnitPrice`). Only touches assets with exactly one Initial-Sale action + one state period; assets that already carry history are skipped. `DELTAS` are absolute unit changes. Never creates or reprices assets. Target via `ASSET_IDS` (smoke) or `ACCOUNT_NAME_LIKE` (full set) — both empty by default, so it no-ops until you set one. | `sf apex run` |
| `reset_augment.apex` | Undo an augment run on `ASSET_IDS`. Deletes **only** records carrying augment's provenance marker (`AssetActionSource.ExternalReference` / `AssetStatePeriod.SegmentName` = `RLM_AUGMENT_LIFECYCLE`) — never by the generic `Type='Change'`. **Preflighted:** before any DML it verifies the surviving (unmarked) records are exactly one action + one state period; an asset that gained REAL renewal/amendment history after augment is **refused entirely** (no delete, no restore, logged), since the restore would otherwise overlap/clobber it. Eligible assets have their surviving Initial-Sale period restored to the full window. A second augment run is a no-op (the pristine guard skips already-augmented assets, not layering a duplicate series), so reset first to rebuild the series. | `sf apex run` |

## The `build_quote_to_asset.py --skip-usage-verify` flag

`build_quote_to_asset.py` was written for **usage-anchor** products and asserts
that each new asset carries usage buckets. A plain renewal term product carries
none, so `build_renewal_buckets.py` passes `--skip-usage-verify` by default
(pass `--verify-usage` to re-enable it for QB-DB and other usage anchors). The
asset's existence is still confirmed either way.

## Quick start

```bash
# 1. dry-run the plan (no org writes)
python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
    --accounts "Infinitech" --skus QB-DB --per-bucket 1 \
    --term-months 12 --selling-model "Term Annual" --billing-frequency Annual --dry-run

# 2. build the assets (one per bucket)
python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
    --accounts "Infinitech,Kingsbridge Digital" --skus QB-DB \
    --per-bucket 1 --term-months 12 --selling-model "Term Annual" --billing-frequency Annual

# 3. (optional) layer lifecycle history — smoke on ONE id first, then a pattern
#    edit ASSET_IDS / ACCOUNT_NAME_LIKE at the top of the script, then:
sf apex run --file scripts/renewal_assets/augment_asset_lifecycle.apex --target-org <alias>
```

## Provenance

Ported from the internal eng toolkit `git.soma.salesforce.com/tsubramaniam/RevAssetCreation`
(the `create-revenue-asset-from-quote` skill). This repo version reuses the
existing `build_quote_to_asset.py` for the per-asset flow rather than shipping a
second Quote → Order → Activation implementation, and drops the eng config-runner
in favor of the driver above. The lifecycle-augment Apex is a faithful port with
org-specific defaults removed.
