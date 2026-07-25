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

**A Pack product needs an anchor** it can draw against:

```bash
python scripts/build_quote_to_asset.py --org <alias> --accounts "Infinitech" \
    --sku QB-TOKENS-PACK --anchor-sku QB-DB-TOKEN
```

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

> ⚠ **"All journals processed" is not "rating finished."** This command returns when
> the pending journal count reaches zero — that means the journals were *aggregated*,
> not *rated*. Rating continues afterwards in Data Processing Engine batch jobs
> (`Create_Liable_Summary_v3`, `Create Ratable Summary For …`). Validate too soon and
> you will see summaries at `New`/`InProgress` and think the run failed. Wait for those
> jobs before step 4 — **Setup → Data Processing Engine → job runs**, or:
>
> ```bash
> sf data query -q "SELECT BatchJobDefinitionName, Status FROM BatchJob WHERE CreatedDate = TODAY AND Status != 'Completed'" --target-org <alias>
> ```

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

To rebuild from clean, the asset must go too:

| Goal | Do this |
|------|---------|
| Clear usage, keep assets (re-run a different usage period) | `clearUsageData.apex` alone (leave `DELETE_ASSET_RATE_CARD_ENTRIES = false`) |
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
| Commitment discount not applied | Missing `UsageCmtAssetRelatedObj` link between commitment and anchor |
| Discount applied where you expected full price (or vice versa) past the commitment | `Lowest Commitment Rate` vs `Bounded Object Rate` on the commitment policy — design-time only, not visible in runtime data |
| `OverageQuantity` non-zero, commitment not exhausted | Expected. It means "beyond the included allowance", not "beyond the commitment" |
| Activation fails `FAILED_ACTIVATION` | Account has no shipping address or bill-to contact |
| Prices right in USD, wrong in another currency | A pricing lookup step missing `CurrencyIsoCode` |
| `CommitmentQuantity` / `CommitmentSpend` entitlement stuck `PENDING` | Known platform issue in 262. `Commit` works |

Deeper diagnosis: [Troubleshooting skill](../../.cursor/skills/troubleshooting/SKILL.md)
→ *Usage & Consumption Errors*.

## Reference

| Need | Where |
|------|-------|
| Scenario catalog + arithmetic | [qb-consumption-demo-scenarios.md](qb-consumption-demo-scenarios.md) |
| Object/field model and platform rules | [`domains/usage.md`](../../.cursor/skills/revenue-cloud-data-model/domains/usage.md) |
| Building assets, endpoint contracts | [`building-usage-assets.md`](../../.cursor/skills/usage-consumption/building-usage-assets.md) |
| Verification layers, adding invariants | [`verification.md`](../../.cursor/skills/usage-consumption/verification.md) |
