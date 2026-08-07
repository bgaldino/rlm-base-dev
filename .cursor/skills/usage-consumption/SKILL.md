# Usage & Consumption — Building, Rating, and Verifying Metered Demos

Use this skill when work involves **metered/consumption products**: building assets
that carry usage entitlements, recording usage, driving rating and drawdown,
verifying the result, or resetting it. It covers the QuantumBit consumption demo and
the general Revenue Cloud usage model behind it.

The defining hazard of this domain: **almost every mistake is silent.** A wrong
ordering does not error — it produces a rated summary of zero, or a plausible price
that is not the one you configured. Assume nothing worked until a validator says so.

Objects and fields: `.cursor/skills/revenue-cloud-data-model/domains/usage.md`.
Scenarios and worked arithmetic: `docs/guides/qb-consumption-demo-scenarios.md`.
End-user runbook: `docs/guides/usage-consumption-runbook.md`.

## Quick Rules

1. **The order is `build asset → record usage → orchestrate`, once per period.**
   Getting this wrong is unrecoverable for that period.
2. **Book usage into a PAST period.** Drawdown and final rating settle only when a
   period *completes*; the current period stays open indefinitely.
3. **Record usage against the ANCHOR asset,** never the commitment. A commitment is
   a rate modifier, not a consumption target.
4. **Orchestrate several times.** One pass does not settle the pipeline —
   `python scripts/qb_usage.py orchestrate` loops for you.
5. **A commitment sale is three steps** — anchor, then commitment, then a
   `UsageCmtAssetRelatedObj` link. Without the link the commitment is inert.
6. **A commitment PURP may carry ONLY `UsageCommitmentPolicyId`** — platform-enforced
   for `Commit` / `CommitmentQuantity` / `CommitmentSpend`.
7. **Verify with a validator, not by reading numbers.** Offline:
   `python tests/test_qb_multicurrency_data.py`. Live:
   `sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <alias>`.
8. **Tear down with a convergent loop.** The usage graph's delete constraints are
   circular; no fixed order works.

## DO NOT

- **DO NOT** record usage after orchestrating that period — a `UsageSummary` at
  `RatableSummaryComplete` / `LiableSummaryComplete` **never reopens**, and the
  journals stay `Pending` forever with no error
- **DO NOT** expect `clearUsageData.apex` to reopen a closed period. It drains the
  summaries but the period state survives, so re-recording into the **same** period
  strands the journals exactly as above. Re-testing one period needs a full account
  reset and an asset rebuild
- **DO NOT** assume a freshly sold commitment's rate is live on an org built before
  `Commitment_based_Rate_Adjustment` was added to the `CreateAssetOrderEvent` refresh
  chain (`RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info`). It now
  refreshes on order activation like every other rate table, but on an older org
  nothing re-syncs it and consumption rates at the undiscounted anchor rate with no
  error. Check `LastSyncDate` is after the `AssetRateAdjustment` rows
- **DO NOT** read a non-zero `UsageRatableSummary.OverageQuantity` as commitment
  exhaustion — on ordinary rows it mirrors `TierQuantity` and means "beyond the
  included allowance"
- **DO NOT** put a `RatingFrequencyPolicyId` or `UsageAggregationPolicyId` on a
  commitment product's PURP
- **DO NOT** re-run `qb-rating` / `qb-rates` / `qb-pricing` into an org that already
  has usage assets — see `sfdmu-data-plans/SKILL.md` → *Reloading a Plan Into a Live
  Org*. Load new products surgically instead
- **DO NOT** infer runtime behaviour from a field description in the dev-guide or
  help snapshot — neither documents drawdown ordering or interaction. Establish it
  live and record it
- **DO NOT** wrap a usage teardown in a savepoint that rolls back on failure — the
  rollback hides all progress and you will chase a different error every run

---

## Entry Conditions

| Task | Use this skill? | Notes |
|------|-----------------|-------|
| Record/rate usage, debug a zero rated summary | Yes | Start with Quick Rules 1–4. |
| Build an asset that carries usage entitlements | Yes | See [building-usage-assets.md](building-usage-assets.md). |
| Add or change a commitment / pack / grant product | Yes | Check the PURP shape rule first. |
| Verify a consumption build, add an invariant | Yes | See [verification.md](verification.md). |
| Reset an org or account holding usage data | Yes | Convergent teardown — see below. |
| Understand a usage object's fields/relationships | Partly | Object reference is `revenue-cloud-data-model/domains/usage.md`. |
| Generate Quote→Order→**Invoice** demo volume | No | Use `txn-data-harness/SKILL.md`. |
| Change the rating/rates SFDMU plans themselves | Partly | Also read `sfdmu-data-plans/SKILL.md`. |
| Wire a pricing procedure or lookup step | No | Use `pricing-wiring/SKILL.md`. |

---

## The Pipeline

```
build asset (with entitlements, backdated)
        ↓
record usage        → TransactionJournal (Pending)
        ↓
orchestrate (xN)    → UsageSummary → UsageRatableSummary
        ↓             drawdown against UsageEntitlementBucket
verify              → amount = qty × rate, commitment before grant
```

Each stage is covered below; the two detailed stages have sub-files.

### 1. Build the asset — [building-usage-assets.md](building-usage-assets.md)

Usage needs an asset carrying entitlements, and the interesting cases are
**backdated** so a period has closed. `scripts/build_quote_to_asset.py` produces that
state reproducibly. Read the sub-file before touching quote creation — it records
which v67.0 endpoints are gone and why direct `QuoteLineItem` DML fails for
TermDefined products.

### 2. Record usage

```bash
# edit MULTIPLIER / USAGE_DATE / ONLY_ACCOUNTS at the top of the script first
sf apex run --file scripts/apex/consumeUsageProfile.apex --target-org <alias>
```

`USAGE_DATE` must be in a **past** period. `MULTIPLIER` scales the declared profile —
`1` for baseline scenarios, `3` to drive commitment exhaustion and overage.

### 3. Orchestrate

```bash
python scripts/qb_usage.py orchestrate --org <alias> [--passes N] [--interval SECS]
```

Rating is asynchronous and multi-stage. The command loops until journals stop
moving — which means **aggregated, not rated**. Rating continues afterwards in
Data Processing Engine jobs (`Create_Liable_Summary_v3`, `Create Ratable Summary
For …`), so "all journals processed" is not a completion signal for step 4.
Wait for those before validating, or you will see `New`/`InProgress` summaries
and read a healthy run as a failure:

```bash
sf data query -q "SELECT BatchJobDefinitionName, Status FROM BatchJob WHERE CreatedDate = TODAY AND Status != 'Completed'" --target-org <alias>
```

Watch for batch failures rather than assuming success —
`troubleshooting/SKILL.md` → *Async rating/entitlement batch failed*.

### 4. Verify — [verification.md](verification.md)

```bash
python scripts/qb_usage.py report --org <alias> [--accounts "Name" ...]
sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <alias>
```

### 5. Reset

```bash
sf apex run --file scripts/apex/clearUsageData.apex --target-org <alias>   # org-wide, usage only
```

Per-account, the in-org utility is `RLM_AccountUtilities.delAccountRelatedObjects`
(permission set `RLM_UtilitiesPermset`, assigned on `quantumbit` and `tso` —
destructive: it clears the account's transactional records **and** its usage graph).

Both use a **convergent loop** — attempt every object each round, stop when a round
makes no progress — and both clamp each delete to the transaction's remaining DML
row budget, reporting a partial teardown rather than throwing. Two consequences
worth knowing:

- **Re-run until the remaining counts read zero.** A partial teardown is expected on
  a large graph and is real progress, not a failure.
- **Usage teardown must sit outside any rollback boundary.** In
  `RLM_AccountUtilities` it deliberately runs *before* the savepoint: inside it, one
  later exception would roll back every usage row removed and the reset could never
  converge across reruns.

---

## How Drawdown Actually Works

Consumption settles **commitment → grant → overage**, and the two buckets decrement
on *different bases*:

| Consumer | Decrements by | Why |
|----------|---------------|-----|
| commitment bucket | the **discounted** quantity | 27,777.78 raw × 0.90 = exactly 25,000 |
| anchor grant | the **raw** quantity | a grant is an included allowance, not a discount — what it absorbs is never discounted |
| overage | per `UsageCommitmentPolicy.CommitmentRate` | see below |

`CommitmentRate` is a **design-time global switch that no runtime object snapshots** —
you cannot tell from runtime data which applied:

| Value | Past the commitment boundary |
|-------|------------------------------|
| `Lowest Commitment Rate` | the discount **survives** into overage |
| `Bounded Object Rate` | reverts to the **standard anchor rate** |

**Commit and Pack are opposites.** A Commit product *discounts* a rate and carries no
grant; a Pack product *adds* allowance and carries a grant but no commitment policy.

---

## Examples

### Example 1 — "The rated usage is zero and nothing errored"

Do **not** start by inspecting rates. Check ordering first:

1. Was usage recorded *before* that period was orchestrated? If not, the period is
   unrecoverable — pick a different period.
2. Was `USAGE_DATE` in a **past** period?
3. Is this the account's *first* orchestration? The first pass closes every past
   period empty.
4. Were the journals uploaded to the **anchor**, not the commitment?

Then `python scripts/qb_usage.py report --org <alias>` to see what actually landed.

### Example 2 — "Add a commitment product to the demo"

1. Add the product with `UsageModelType = Commit` to the catalog/pricing/rating CSVs.
2. Give its PURP **only** `UsageCommitmentPolicyId` — no period fields.
3. Load it **surgically** if the org is live (re-running the plan duplicates or fails).
4. Sell it in three steps and link with `UsageCmtAssetRelatedObj`.
5. Refresh decision tables and rebuild the search index — catalog/pricing changes
   require this, exactly as at the end of `prepare_rlm_org`.
6. Verify plan-level wiring on the next full build; a surgical load does not prove it.

### Example 3 — "Reset the demo org and start over"

Pick the tool by what must survive:

- **Clearing usage but keeping the assets** — only for **a different period**:
  `clearUsageData.apex` alone. It preserves `AssetRateCardEntry` by default —
  those rows are created with the asset and are **not** recreated for an existing
  one, so deleting them strands a rate-less asset. Set
  `DELETE_ASSET_RATE_CARD_ENTRIES = true` only when reloading `qb-rates` or when
  the assets are going away too.
- **Re-testing the SAME period**: a usage clear is **not enough**. The clear drains
  the summaries but leaves the period closed, so the next journals strand with
  *"stranded behind a period that already closed"* and the graph reads zero while
  `TransactionJournal` holds what you recorded. Reset the account and rebuild the
  asset.
- **Rebuilding assets from scratch**: `clearUsageData.apex` is **not enough** — it
  drains the usage graph but does **not** delete `Asset` records, and
  `build_quote_to_asset.py` matches on account + product, so a leftover asset for
  the same SKU makes the next build ambiguous. Use the full per-account reset
  (`RLM_AccountUtilities`, or Account Utilities in the org) first.

Re-run either until the reported remaining counts read 0.

If a reset fails with a delete error, do not add another ordered delete step —
confirm the teardown is a convergent loop and that no savepoint is discarding its
progress.

---

## Validation Checks

```bash
python tests/test_qb_multicurrency_data.py                  # offline invariants, no org
python scripts/validate_sfdmu_v5_datasets.py                # plan v5 compliance
python scripts/ai/check_plan_readme_consistency.py          # plan README ↔ CSVs
cci task run validate_multicurrency_rates --org <cci-alias> # live design+runtime
sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <sf-alias>
```

Before a PR that touches usage data or behaviour:

- Offline invariants pass, including `check_commitment_purp_has_no_periods`
- Plan READMEs report **0 errors** repo-wide (not just the plan you edited)
- If a product was added surgically, the owed full-build verification is recorded
- Any newly established runtime rule is written into
  `revenue-cloud-data-model/domains/usage.md`, not left in the PR description

## Related Skills

- **Data model** — `.cursor/skills/revenue-cloud-data-model/domains/usage.md`
- **SFDMU plans** — `.cursor/skills/sfdmu-data-plans/SKILL.md`
- **Troubleshooting** — `.cursor/skills/troubleshooting/SKILL.md`
- **Transaction demo data (invoices)** — `.cursor/skills/txn-data-harness/SKILL.md`
- **Pricing wiring** — `.cursor/skills/pricing-wiring/SKILL.md`
- **Grounding sources** — `.cursor/skills/revenue-cloud-docs/SKILL.md`
