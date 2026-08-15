# Usage & Consumption Runbook

How to stand up, run, verify, and reset a metered/consumption demo in a Revenue Cloud
org. Written for SEs and demo users driving the QuantumBit consumption story.

- **What the scenarios are**, with verified arithmetic → [QB Consumption Demo Scenarios](qb-consumption-demo-scenarios.md)
- **How to execute one**, start to finish → this document

## The one thing to know first

**Consumption failures are silent.** If you record usage in the wrong order, or into
the wrong period, nothing errors — the rated result is simply zero, or the discount
you configured quietly does not apply. There is no warning banner and no failed job
to click into.

So the sequence below is not a suggestion. Two of its steps cannot be undone for a
given billing period.

## What changed in 264

If you last ran this on 262, four things moved. Each was checked on a freshly built 264
org rather than taken from release notes, and the whole sequence below was then run end
to end on that org — the step 4 validator passes on 264.

| Change | What it means here |
|--------|--------------------|
| The rating batch jobs are now `_v4` | `Create_Liable_Summary_v4` and `Create_Usage_Summary_v4`. The `_v3` names are **absent**, not aliased, so a step 3 wait keyed to them matches nothing and looks instantly finished |
| `TransactionUsageEntitlement` lost `ChargeForOverage`, `DrawdownOrder`, `RatingFrequencyPolicyId` and `UsageAggregationPolicyId` | Overage chargeability is no longer readable on the entitlement, which now carries no overage field or policy lookup at all. It comes from `UsageOveragePolicy.OverageChargeable`, reachable only through the product's `ProductUsageResourcePolicy` for that resource |
| Only an **Anchor** product may carry an overage policy | See the Pack note in step 1 — it changes where you look when an overage charge is missing |
| `CommitmentQuantity` / `CommitmentSpend` still strand at `PENDING` | Not fixed in 264. Sell a `Commit` product instead, which does reach `PROCESSED` on 264 — last row of [When something looks wrong](#when-something-looks-wrong) |

`ProductUsageGrant.DrawdownOrder` was **not** removed, so the drawdown order in step 4
still reads where it always did.

## Prerequisites

| Requirement | Check |
|-------------|-------|
| Org built with the **full** QB catalog | `prepare_rlm_org` completed. `prepare_rating` alone is NOT enough — building an asset also needs products and selling models (qb-pcm), per-currency pricebook entries (qb-pricing) and billing treatments (qb-billing) |
| An account that can transact | Needs a shipping address **and** a bill-to contact, or activation fails with `FAILED_ACTIVATION` |
| `sf` CLI authenticated | `sf org list` shows your alias |

Accounts known to work: Infinitech, Kingsbridge Digital, Coralbay Technologies,
Helvetia Cloud, Northlight Systems, Rheintech Solutions, Sakura Systems, Global Media.

Throughout, `<alias>` is your **sf CLI** alias (e.g. `rlm-base__beta`), not the CCI
alias — the two registries are different.

---

## Step 1 — Build a backdated asset

Usage can only be rated against an asset that carries entitlements, and the period
you record into must have **closed**. So the asset has to start in the past.

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "Infinitech" --sku QB-DB-TOKEN
```

This runs the real lifecycle — Opportunity → Quote → Order → Activation → Asset — and
exits non-zero if any account fails to reach an asset with usage buckets.

**Selling a commitment takes a second run plus a link.** A commitment is a separate
sale from its anchor, and it does nothing at all until the two assets are joined:

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "Infinitech" \
    --sku QB-CMT-TKN-FLAT --link-commitment QB-DB-TOKEN
```

Without `--link-commitment`, the commitment sits there looking correct while
consumption quietly drains the anchor's grant at the anchor's undiscounted rate.

> **The commitment rate table refreshes itself.** Selling a commitment creates its
> `AssetRateAdjustment` rows, and activating the order fires `CreateAssetOrderEvent`, which
> `RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info` handles by refreshing
> the rate decision tables — `Commitment_based_Rate_Adjustment` among them since
> **2026-07-26**, on both the 262 and 264 lines. A live check shows it refreshing within
> seconds of the asset rows being created — 3 on a 264 run.
>
> **On an org built before that date**, nothing re-syncs it and a commitment sold after the
> build is invisible to the commitment-rate lookup — consumption rates at the undiscounted
> anchor rate with no error anywhere. Refresh by hand there:
>
> ```bash
> cci task run refresh_dt_asset --org <cci_alias>
> ```
>
> Either way, confirm — and confirm it against the **source rows**, not on its own. A
> `Completed` refresh from before the sale looks identical to one that captured it, so read
> both timestamps and check `LastSyncDate` is the later:
>
> ```bash
> # 1. newest AssetRateAdjustment for the commitment you just sold.
> #    LastModifiedDate, not CreatedDate — an EDITED rate invalidates the table too.
> sf data query --target-org <sf_alias_or_username> \
>   -q "SELECT LastModifiedDate FROM AssetRateAdjustment
>       WHERE AssetRateCardEntry.Asset.Product2.StockKeepingUnit = '<COMMIT_SKU>'
>       ORDER BY LastModifiedDate DESC LIMIT 1"
>
> # 2. the table — LastSyncDate must be LATER than the value above
> sf data query --use-tooling-api --target-org <sf_alias_or_username> \
>   -q "SELECT DeveloperName, RefreshStatus, LastSyncDate FROM DecisionTable
>       WHERE DeveloperName = 'Commitment_based_Rate_Adjustment'"
> ```

**A Pack product needs an anchor** it can draw against:

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "Infinitech" \
    --sku QB-TOKENS-PACK --anchor-sku QB-DB-TOKEN
```

> **Overage belongs to the anchor, never to the Pack.** Only an Anchor product's
> `ProductUsageResourcePolicy` may carry a `UsageOveragePolicy` — the platform refuses one
> on a Pack (*"Change the product usage model type from Pack to another valid option"*) and
> on a Commit. On a built org all six overage-carrying policy rows sit on the two anchors,
> `QB-DB` and `QB-DB-TOKEN`. So when an overage charge is missing on a bundle, check the
> anchor's policy; there was never one on the Pack to find.

---

## Step 2 — Record usage into a PAST period

Open `scripts/apex/consumeUsageProfile.apex` and set the three values at the top:

| Setting | Meaning |
|---------|---------|
| `USAGE_DATE` | Must fall in a **completed** billing period |
| `MULTIPLIER` | `1` for baseline scenarios; `3` to drive commitment exhaustion and overage |
| `ONLY_ACCOUNTS` | Empty = every anchor asset; otherwise a set of account names |

```bash
sf apex run --file scripts/apex/consumeUsageProfile.apex --target-org <alias>
```

The standard profile is 5,000 CPU minutes + 50 TB storage = 25,500 tokens per month.

> **Record usage against the anchor, never the commitment.** The script does this for
> you. If you upload usage by hand in the UI, pick the anchor asset — journals posted
> to a commitment asset stay `Pending` forever.

---

## Step 3 — Orchestrate

```bash
python scripts/qb_usage.py orchestrate --org <alias>
```

Rating is asynchronous and multi-stage, so this loops until the journals stop moving.
A single pass is not enough.

> ⚠ **Read the exit code — "all journals processed" is not "rating finished."** Zero
> pending journals means *aggregated*, not *rated*: rating continues afterwards in Data
> Processing Engine batch jobs. The command already knows this and polls for them, so its
> exit code is the completion signal, not its final line of output:
>
> | Exit | Meaning |
> |------|---------|
> | `0` | Journals aggregated **and** the rating jobs have settled — safe to go to step 4 |
> | `1` | **Not ready.** Either journals are still pending, or aggregation finished while rating jobs are still running |
> | `2` | Stalled with journals pending — usually stranded behind a period that closed before the usage was recorded (see the ⛔ below) |
>
> So do not wait "just in case" after an exit `0`, and do not treat an exit `1` as a
> failed run — it means *come back and check*, which is why it is not `0`. The contract is
> stated at the top of `scripts/qb_usage.py`.
>
> The jobs it waits on are `Create_Liable_Summary_v4`, `Create_Usage_Summary_v4`, and
> `Create Ratable Summary For …`. **Those names are `_v4` on 264 — the `_v3` names are not
> merely renamed but absent**, which matters if you write your own wait: keyed to the old
> name it matches nothing and reads as "rating finished" immediately. The script itself is
> immune because it polls on non-terminal *status* rather than on job name.
>
> One residual gap the exit code cannot close: a rating job that starts *after* the final
> poll. On a single-account run `Create_Liable_Summary_v4` was still `InProgress` about five
> minutes after the command returned. So exit `0` is a strong signal rather than a
> guarantee, and it costs nothing to confirm before validating — **Setup → Data Processing
> Engine → job runs**, or:
>
> ```bash
> sf data query -q "SELECT BatchJobDefinitionName, Status FROM BatchJob WHERE CreatedDate = TODAY AND Status != 'Completed'" --target-org <alias>
> ```
>
> Validating too early shows summaries at `New`/`InProgress` and reads a healthy run as a
> failure.

> ⛔ **Do not run this before step 2 for the period you care about.** The first
> orchestration pass on an account closes every past period **empty**, and a closed
> summary never reopens. Usage recorded afterwards is stranded permanently.

---

## Step 4 — Verify

```bash
python scripts/qb_usage.py report --org <alias> --accounts "Infinitech"
sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <alias>
```

> ⚠ **Set `USAGE_PERIOD_START` / `USAGE_PERIOD_END` at the top of
> `validateRatedUsage.apex` to the period you recorded into in step 2.** Without a
> declared window the validator picks up every historical journal for these assets:
> an old pending journal fails a clean run, and old rated summaries satisfy the
> arithmetic while the usage you just uploaded never rated at all.

The report shows what the runtime actually did — buckets, drawdown, rating. The
validator asserts it: `TotalAmount = OverageQuantity × NetUnitRate`, that rating
actually reached `RatingComplete`, and that the commitment drained before the grant.

Expected drawdown order, and the bases each uses:

| Order | Consumer | Decrements by |
|-------|----------|---------------|
| 1 | Commitment | the **discounted** quantity |
| 2 | Anchor grant | the **raw** quantity |
| 3 | Overage | rated per the commitment policy |

The grant is an included *allowance*, not a discount — usage it absorbs is never
discounted at all. That asymmetry is intentional and is the most common source of
"the math looks wrong" reports.

To confirm overage is even chargeable, read the governing policy — since 264 the
entitlement no longer carries the answer:

```bash
sf data query --target-org <alias> \
  -q "SELECT ProductUsageResource.Product.StockKeepingUnit,
             ProductUsageResource.UsageResource.Name,
             UsageOveragePolicy.OverageChargeable
      FROM ProductUsageResourcePolicy
      WHERE UsageOveragePolicyId != null"
```

A resource is shared across products — `Quantum Tokens` by six of them — so read the
product column too. The policy is per product *and* resource, not per resource.

---

## Step 5 — Reset

**In the org (for demo users).** The Account Utilities action clears an account's
orders, assets, contracts, invoices, quotes, opportunities **and its entire usage
graph**. It requires the `RLM_UtilitiesPermset` permission set, assigned on both
`quantumbit` and `tso` builds. It is destructive and has no confirmation step —
it resets the account you invoke it on.

**From the CLI (whole org).**

```bash
sf apex run --file scripts/apex/clearUsageData.apex --target-org <alias>
```

> ⚠ **`clearUsageData.apex` drains the usage graph — it does NOT delete assets,**
> and by default it preserves their `AssetRateCardEntry` rows too, so the assets keep
> their rates and can be re-used for another usage period. (Those rows are created
> with the asset and are **not** recreated for an existing one, so deleting them
> would leave a rate-less asset that can never rate again.)
>
> It also means a usage-only clear is *not* enough before rebuilding:
> `build_quote_to_asset.py` matches on **account + product**, so a leftover asset for
> the same SKU makes the next build ambiguous.

> ⛔ **A clear does NOT reopen the period. Re-testing the *same* period needs a full
> asset rebuild.**
>
> `clearUsageData.apex` drains the summaries, but the period state on the
> `UsageEntitlementAccount` / buckets survives, and a closed period never reopens. So
> the "re-run a different usage period" in the table below is the literal constraint,
> not a suggestion: record usage into the *same* period after a clear and the journals
> are stranded exactly as if you had orchestrated before recording them —
>
> ```
> no progress for a full pass and 2 journal(s) still pending — either rating is
> complete for every open period, or these journals are stranded behind a period
> that already closed
> ```
>
> and the graph reads `UsageSummary 0 / UsageRatableSummary 0 / UsageBillingPeriodItem 0`
> while `TransactionJournal` sits at whatever you recorded. Nothing errors; the rated
> summary just reads zero. To re-run the same period, reset the account (Account
> Utilities) and rebuild the asset.

To rebuild from clean, the asset must go too:

| Goal | Do this |
|------|---------|
| Clear usage, then use a **different** period | `clearUsageData.apex` alone (leave `DELETE_ASSET_RATE_CARD_ENTRIES = false`) |
| Re-test the **same** period | Full per-account reset via **Account Utilities**, then rebuild the asset — a usage clear is not enough (see above) |
| Reload `qb-rates` design-time data | `clearUsageData.apex` with `DELETE_ASSET_RATE_CARD_ENTRIES = true` — ARCEs reference the RateCardEntry rows and block their replacement |
| Rebuild the asset from scratch | Full per-account reset via **Account Utilities** in the org (removes assets, orders, quotes **and** the usage graph), then rebuild |

Re-run whichever you use until the reported remaining counts read **0** — a partial
teardown is expected on a large graph and is real progress, not a failure.

---

## When something looks wrong

| Symptom | Most likely cause |
|---------|-------------------|
| Rated usage is **zero**, no error | Ordering. Usage recorded after orchestrating that period, or booked into the current (still open) period |
| Zero on a brand-new account | The first orchestration pass closed all past periods empty |
| Journals stuck at `Pending` | Uploaded to the commitment asset instead of the anchor |
| Commitment discount not applied | Missing `UsageCmtAssetRelatedObj` link between commitment and anchor — **or** a stale `Commitment_based_Rate_Adjustment`: check its `LastSyncDate` is later than the newest `AssetRateAdjustment.SystemModstamp` for that commitment (**not** `LastModifiedDate` — an internal process advances only the former, so a `LastModifiedDate` comparison can read fresh while the table is stale) (only bites on orgs built before 2026-07-26, when it joined the `CreateAssetOrderEvent` refresh chain) |
| Discount applied where you expected full price (or vice versa) past the commitment | `Lowest Commitment Rate` vs `Bounded Object Rate` on the commitment policy — design-time only, not visible in runtime data |
| `OverageQuantity` non-zero, commitment not exhausted | Expected. It means "beyond the included allowance", not "beyond the commitment" |
| Activation fails `FAILED_ACTIVATION` | Account has no shipping address or bill-to contact |
| Prices right in USD, wrong in another currency | A pricing lookup step missing `CurrencyIsoCode` |
| `CommitmentQuantity` / `CommitmentSpend` entitlement stuck `PENDING` | Platform issue, **still present in 264**. On a fresh 264 org both model types hold every entitlement at `PENDING` and produce zero buckets, while an `Anchor` sold on the same org reaches `PROCESSED` — so the asset looks fine and simply never rates. Sell a `Commit` product (`QB-CMT-TKN-*`) instead |

Deeper diagnosis: [Troubleshooting skill](../../.cursor/skills/troubleshooting/SKILL.md)
→ *Usage & Consumption Errors*.

## Reference

| Need | Where |
|------|-------|
| Scenario catalog + arithmetic | [qb-consumption-demo-scenarios.md](qb-consumption-demo-scenarios.md) |
| Object/field model and platform rules | [`domains/usage.md`](../../.cursor/skills/revenue-cloud-data-model/domains/usage.md) |
| Building assets, endpoint contracts | [`building-usage-assets.md`](../../.cursor/skills/usage-consumption/building-usage-assets.md) |
| Verification layers, adding invariants | [`verification.md`](../../.cursor/skills/usage-consumption/verification.md) |
