# Renewal Asset Creation — expiry-bucket spread + lifecycle event history

Use this skill to produce renewal-ready Revenue Cloud **Assets** the realistic
way — Quote → Order → Activation, so every lifecycle field (`LifecycleEndDate`,
state periods) is platform-derived, never hand-inserted — spread across the four
renewal **expiry windows** (≤30 / 30-60 / 60-90 / >90 days), and optionally give
them a multi-year Renewal/Upsell/Downsell **event history** for renewal
revenue-insights and renewal-quote testing.

The toolkit lives in `scripts/renewal_assets/`; its file-level reference is
`scripts/renewal_assets/README.md`. The per-asset Quote → Order → Activation flow
is **reused** from `scripts/build_quote_to_asset.py` — this skill does not
reimplement it.

Ported from the eng toolkit `git.soma.salesforce.com/tsubramaniam/RevAssetCreation`
(the `create-revenue-asset-from-quote` skill), adapted to this repo's conventions
(v68.0, feature-branch + PR, reuse of the existing builder).

## Quick Rules

1. **Assets are built through Quote → Order → Activation, never inserted.**
   `build_quote_to_asset.py` places the quote via Place Sales Transaction, orders
   via `createOrdersFromQuote`, and activates by the Draft → Activated transition
   — the same path a seller/admin uses, so the platform derives `LifecycleEndDate`
   and the Initial-Sale action/state period. Direct `Asset`/`QuoteLineItem` DML is
   not viable for TermDefined products.
2. **Expiry-bucket spread comes from `build_renewal_buckets.py`.** It computes the
   4 windows from *today*, back-solves `start = end − term`, and shells out to the
   builder once per asset. There is no second flow implementation to keep in sync.
3. **Accounts must pre-exist.** The builder resolves accounts by name and does not
   create them. Reset an account (no existing asset for the SKU) or rely on the
   per-run `--allow-existing-asset` the driver passes so a repeat SKU on the same
   account still waits for a genuinely NEW asset id.
4. **Renewal term products skip usage verification.** `build_quote_to_asset.py`
   asserts usage buckets (it was built for usage anchors); the driver passes
   `--skip-usage-verify` by default so a plain term product isn't failed for
   carrying none. Pass `--verify-usage` for usage-anchor SKUs (QB-DB etc.).
5. **Augment is additive, pristine-only, and read-your-work.**
   `augment_asset_lifecycle.apex` layers events onto EXISTING assets, reusing each
   asset's real PBE/PSM/UnitPrice, and derives MRR from the Initial-Sale state
   period (not `UnitPrice`, which is per-term). It **only** touches *pristine*
   assets — exactly one Initial-Sale action and one state period; any asset that
   already carries lifecycle history is skipped (logged), never modified. It is
   **not** de-duped — smoke on one `ASSET_IDS` first, verify, then scale by
   `ACCOUNT_NAME_LIKE`; `reset_augment.apex` before re-running. `DELTAS` are
   **absolute** unit changes (not a fraction of base qty) — tune them to your qty.
   `reset_augment.apex` deletes **only** records carrying augment's provenance
   marker (`AssetActionSource.ExternalReference` / `AssetStatePeriod.SegmentName`
   = `RLM_AUGMENT_LIFECYCLE`), never by the generic `Type='Change'`, so real
   Renewal/Upsell/Downsell history on the same asset is untouched.
6. **Everything ships through a feature branch + PR.** Never commit to `264` /
   `main` / `release/*`. This skill and its scripts are their own branch — adding
   them to an unrelated feature branch trips `check_branch_scope.py`.

## DO NOT

- **DO NOT** insert `Asset`, `AssetStatePeriod`, or `AssetAction` to *create* an
  asset or hand-set `LifecycleEndDate` — build it through the flow so the platform
  derives lifecycle records. (The augment Apex only *adds* history to an asset the
  platform already made, and reuses that asset's own selling model.)
- **DO NOT** run `augment_asset_lifecycle.apex` twice on the same assets — it
  layers a second event series (no de-dupe). Use `reset_augment.apex` first.
- **DO NOT** point the augment Apex at a broad `ACCOUNT_NAME_LIKE` before a
  one-asset smoke run — a wrong pattern rewrites state periods on unintended
  assets. Both selectors are empty by default for this reason.
- **DO NOT** read `--skip-usage-verify` as "usage buckets don't matter here" for a
  SKU you *want* rated — it only tells the driver not to *fail* an asset for
  carrying none. `QB-DB` is fine as a plain **Term Annual** renewal asset (that is
  what the examples build); pass `--verify-usage` when you specifically want its
  usage buckets asserted. The default (`QB-DB` without `--verify-usage`) is
  supported and intentional — the two are not in conflict.
- **DO NOT** add **Pack** (drawdown), **Commit**, or **Bundle** SKUs to `--skus` for
  a plain renewal spread — those need binding/anchor handling this driver doesn't do
  (see `build_quote_to_asset.py` `--anchor-sku` / `--link-commitment`). A usage-anchor
  SKU sold as a straight term asset (like `QB-DB` on `Term Annual`) is **not** in this
  set and is the documented default.

## Entry Conditions

| Situation | Use this skill? |
|-----------|-----------------|
| Need renewal-due assets spread across the 4 expiry windows for renewal insights | Yes |
| Give existing assets a realistic Renewal/Upsell/Downsell lifecycle timeline | Yes — the augment Apex |
| One renewable termed asset to exercise a reprice/price-revision path | Yes (or `build_quote_to_asset.py` directly for a single account) |
| A usage-rating demo (assets with usage wallets/buckets) | No → `build_quote_to_asset.py` with `--verify-usage`; see `usage-consumption/SKILL.md` |
| Seed transaction/invoice demo data (stops before assets) | No → `txn-data-harness/SKILL.md` |
| Prep a DF Hands-On workshop clone | No → `df-workshop-setup/SKILL.md` |

## Workflow

### 1. Pick accounts + SKU(s)
Confirm the target accounts already exist and (ideally) carry no prior asset for
the SKU. Choose a **TermDefined** selling model **Name** that the SKU actually
offers — expiry windows need a `LifecycleEndDate`, so Evergreen/OneTime are
unsupported, and the name must exist for the SKU (e.g. QB-DB offers only
`Term Annual`; QB-DAT-THPT offers `Term Annual` and `Term Monthly`). The selling
model, not the product, dictates which line fields are legal.

### 2. Dry-run the plan (no org writes)
```bash
python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
    --accounts "Infinitech" --skus QB-DB --per-bucket 1 \
    --term-months 12 --selling-model "Term Annual" --billing-frequency Annual --dry-run
```
Prints the bucket / start / end / sku / account for every scheduled asset.

### 3. Build the assets
Drop `--dry-run`. Each asset is built by `build_quote_to_asset.py`; results are
logged to `/tmp/renewal_bucket_results.csv`. Total assets = `4 × --per-bucket`.
```bash
python scripts/renewal_assets/build_renewal_buckets.py --org <alias> \
    --accounts "Infinitech,Kingsbridge Digital" --skus QB-DB \
    --per-bucket 1 --term-months 12 --selling-model "Term Annual" --billing-frequency Annual
```

### 4. (Optional) Layer lifecycle history
Edit the target selector at the top of `augment_asset_lifecycle.apex`
(`ASSET_IDS` for a smoke test, then `ACCOUNT_NAME_LIKE` for the set) and adjust
`FRACS`/`CATS`/`DELTAS` if the default 6-event series isn't what you want.
```bash
sf apex run --file scripts/renewal_assets/augment_asset_lifecycle.apex --target-org <alias>
```
Re-running? `reset_augment.apex` (scoped to `ASSET_IDS`) first — augment is additive.

## Examples

**Single renewal asset per window, one product, one account:**
```bash
python scripts/renewal_assets/build_renewal_buckets.py --org rlm-base__beta \
    --accounts "Infinitech" --skus QB-DB --per-bucket 1 \
    --term-months 12 --selling-model "Term Annual" --billing-frequency Annual
```
→ 4 assets (one in each of ≤30 / 30-60 / 60-90 / >90), all on Infinitech.

**Product-mix, multiple accounts, 2 per bucket:**
```bash
python scripts/renewal_assets/build_renewal_buckets.py --org rlm-base__beta \
    --accounts "Acme,Globex" --skus "QB-DB,QB-DAT-THPT" --per-bucket 2 \
    --term-months 12 --selling-model "Term Annual" --billing-frequency Annual
```
→ 8 assets; each bucket gets one QB-DB + one QB-DAT-THPT, distributed round-robin
across Acme and Globex. (`Term Annual` is used because it is the one TermDefined
model both SKUs share — QB-DB has no `Term Monthly`.)

**Augment a smoke asset, then the full set:**
```bash
# 1) ASSET_IDS = { '02i...' } in augment_asset_lifecycle.apex, then:
sf apex run --file scripts/renewal_assets/augment_asset_lifecycle.apex --target-org rlm-base__beta
# 2) verify (below), then ACCOUNT_NAME_LIKE = 'Infinitech%' (clear ASSET_IDS), re-run.
```
→ each asset ends with 1 Initial Sale + 6 Change events and 7 contiguous state periods.

## Validation Checks

Scripts compile and the driver's plan is deterministic offline:
```bash
python -m py_compile scripts/build_quote_to_asset.py scripts/renewal_assets/build_renewal_buckets.py
python scripts/renewal_assets/build_renewal_buckets.py --org dummy \
    --accounts "A,B" --skus "QB-DB,QB-DAT-THPT" --per-bucket 2 --today 2026-09-10 --dry-run
```

After a build (read-only, against the org):
```bash
# assets landed in their windows (LifecycleEndDate ordering)
sf data query --target-org <alias> -q "SELECT Name, LifecycleStartDate, LifecycleEndDate, CurrentMrr, Product2.Name FROM Asset WHERE Account.Name IN ('Infinitech','Kingsbridge Digital') ORDER BY LifecycleEndDate"
# per-window count (repeat per window; ≤30 shown — use the driver's printed dates)
sf data query --target-org <alias> -q "SELECT COUNT(Id) cnt, SUM(CurrentMrr) mrr FROM Asset WHERE Account.Name = 'Infinitech' AND LifecycleEndDate >= 2026-09-11T00:00:00Z AND LifecycleEndDate <= 2026-10-10T23:59:59Z"
```

After augment (doer ≠ checker — every asset should report `N+1` periods, default 7):
```bash
sf data query --target-org <alias> -q "SELECT CategoryEnum, COUNT(Id) FROM AssetAction WHERE Asset.Account.Name LIKE 'Infinitech%' GROUP BY CategoryEnum"
sf data query --target-org <alias> -q "SELECT AssetId, COUNT(Id) periods FROM AssetStatePeriod WHERE Asset.Account.Name LIKE 'Infinitech%' GROUP BY AssetId"
```
Expect `Initial Sale` once per asset plus the added `Renewals`/`Upsells`/`Downsells`,
and a uniform `periods` count. A short count means an asset was skipped — missing
Initial-Sale source, null lifecycle dates, or **not pristine** (it already had
lifecycle history, so augment left it untouched). The Apex logs each skip with the
reason.

> **Behavioral verification.** The two Apex scripts and the end-to-end bucket
> build write to an org and are **not** verified by the offline checks above.
> Run them against a live scratch/dev org before relying on the result or merging
> a behavioral change to them.

Before the PR: `python -m py_compile scripts/renewal_assets/*.py`, run
`python scripts/ai/pr_gate.py --base origin/264`, and follow
`doc-consistency/SKILL.md` (this skill is registered in `AGENTS.md`).
