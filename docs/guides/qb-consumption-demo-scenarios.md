# QuantumBit Consumption Demo Scenarios

Every consumption permutation QuantumBit can demonstrate, what to sell, what to
record, and the exact number that must come out. All nine scenarios below were
verified live on a 262 scratch org; the arithmetic is what the platform actually
produced, not what the design intends.

Ground records in `docs/enablement/master/qb-scenario-reference.md`. Design-time
data lives in `datasets/sfdmu/qb/en-US/{qb-rating,qb-rates}` — their READMEs carry
the platform rules referenced here.

---

## Before anything else: three rules that silently produce zeroes

These are not tips. Break any one and the demo shows nothing, with no error
anywhere to tell you why.

### 1. Order is `build asset → record usage → orchestrate`, per period

`Create Empty Summaries` runs at assetization and seeds a `UsageSummary` per
resource per accumulation period. A journal is absorbed only while its period's
summary is still open (`New` or `UsageSummaryInProgress`). Once the period reaches
`RatableSummaryComplete` / `LiableSummaryComplete` **it never reopens**, and a
journal arriving afterwards stays `Pending` forever — never aggregated, never
rated, no error. The rated summary just reads `TierQuantity 0, TotalAmount 0`.

**The first orchestration pass on an account closes every past period, empty.** So
a backdated demo gets exactly one attempt per account. If you orchestrate before
consuming, that period is gone; recover by consuming into a period that is still
open, or rebuild on a fresh account.

### 2. Book usage into a PAST period

Drawdown and final rating only settle when a period **completes**. The current
billing period stays open indefinitely, so usage booked into it sits at
`InProgress` with buckets untouched — which reads as "full discount, no drawdown"
and is not a result you can trust.

### 3. Orchestration needs several passes

Pass 1 seeds the empty summaries; a later pass aggregates the journals and rates
them. `RLM_UsageOrchestrationController.startOrchestration()` is safe to call
repeatedly — loop until `TransactionJournal.Status = 'Pending'` stops falling.

Then assert with `scripts/apex/validateRatedUsage.apex`, which checks all three of
the above plus the drawdown order.

---

## How consumption actually draws down

Established live, and every demo number depends on it:

| | |
|---|---|
| **Commitment drains first** | The anchor grant is the *last* line of defence, not the first. With a commitment linked and balance remaining, the grant is untouched. |
| **The two buckets use different bases** | The commitment decrements by the **discounted** quantity; the anchor grant decrements by the **raw** quantity. |
| **A grant is an allowance, not a discount** | Usage a grant absorbs is never discounted at all. |
| **The discount can survive overage** | Governed by `UsageCommitmentPolicy` — see scenarios 7 and 8. |

Worked example (scenario 7): 76,500 raw tokens against a 25,000 commitment at
−10% plus a 10,000 anchor grant.

```
commitment   27,777.78 raw x 0.90 = 25,000 exactly   (exhausted)
anchor grant  8,500 compute + 1,500 storage = 10,000 (exhausted, raw)
overage      75,000 - 36,277.78 = 38,722.22 raw x 0.90 = 34,850 tokens
```

> ⚠️ `UsageRatableSummary.OverageQuantity` **mirrors `TierQuantity` on ordinary
> rows**. It means "charged beyond the included allowance", *not* "beyond the
> commitment", so it alone is not evidence a commitment was exceeded. Decompose
> with `UsageSummary.ConsumptionUnits / DebitedUnits / OverageUnits`.

> ⚠️ The **total** overage is deterministic; the **per-resource split is not**.
> Two identical runs attributed the anchor grant differently between compute and
> storage — same total, same bill. Never script an assertion on a per-resource debit.

---

## The standard monthly profile

Every scenario uses one profile so results are comparable:

| Resource | Quantity | Token conversion |
|---|---:|---:|
| CPU time | 5,000 min | × 5 = 25,000 tokens |
| Data storage | 50 TB | × 10 = 500 tokens |
| **Total** | | **25,500 tokens** |

Scenario 7 and 8 use **3× this profile** (15,000 min + 150 TB = 76,500 tokens) to
blow through the commitment.

---

## The nine scenarios

All verified live. Currencies differ per scenario deliberately — it costs nothing
and proves multicurrency at the same time.

### 1 — Direct-currency tiered rating (the baseline)

**Sell** `QB-DB` · **Currency** CHF · no add-on.

The control. Shows tiered rating and grant drawdown with nothing else in play.

| | |
|---|---|
| CPU | 5,000 min @ 0.0041 (tier 3000–6000) = **20.50** |
| Storage | 50 TB consumed − 10 TB granted = **40 TB** @ 12.21 (tier 25–100) = **488.40** |

The storage line is the teaching moment: the grant absorbs 10 TB before anything
is billed.

### 2 — Token two-step rating

**Sell** `QB-DB-TOKEN` · **Currency** USD · no add-on.

Usage converts to tokens, then tokens convert to currency. Two `UsageRatableSummary`
rows per resource — the `-TKN` row (usage→tokens) and the `QB-TOKEN` row
(tokens→currency).

The token rate is currency-aware and exact: **USD 0.5/token, GBP 0.3739
(= 0.5 × 0.7478), AUD 0.7151 (= 0.5 × 1.4302)**.

### 3 — Flat commitment discount

**Sell** `QB-DB-TOKEN`, then `QB-CMT-TKN-FLAT`, then **link them** · **Currency** GBP.

| | |
|---|---|
| Design | 10% on both token resources |
| Result | 25,000 → **22,500** · 500 → **450** |

### 4 — Per-resource commitment discount

**Sell** `QB-DB-TOKEN` + `QB-CMT-TKN-EACH`, linked · **Currency** AUD.

| | |
|---|---|
| Design | 5% compute / 4% storage |
| Result | 25,000 → **23,750** · 500 → **480** |

The point: two different discounts on one commitment, compounding correctly into
a single bucket draw (24,230 total).

### 5 — Tiered commitment discount

**Sell** `QB-DB-TOKEN` + `QB-CMT-TKN-TIER`, linked · **Currency** USD.

| | |
|---|---|
| Design | 10 / 20 / 30% at 0–10k / 10k–25k / 25k+ |
| Result | 25,500 tokens lands in tier 3 → 25,000 → **17,500** · 500 → **350** (−30%) |

### 6 — Pack top-up

**Sell** an anchor, then `QB-TOKENS-PACK` or `QB-DAT-THPT` with
`BindingInstanceTargetId` set to the anchor asset.

A pack **cannot be sold standalone** — activation fails with "the usage product is
missing a binding instance". Drawdown is visible: throughput overage came out
**45 GB not 50**, because the pack's grant was consumed first.

### 7 — Commitment exhaustion → overage, discount SURVIVES

**Sell** `QB-DB-TOKEN` + `QB-CMT-TKN-FLAT`, linked · **Currency** USD · **3× profile**.

| | |
|---|---|
| Consumed | 76,500 raw tokens |
| Commitment | 25,000 exhausted · Anchor grant 10,000 exhausted |
| Overage | 38,722.22 × 0.90 = **34,850 tokens** |
| **Billed** | **17,425.00 USD** |

`QB-CMT-TKN-FLAT` uses `UsageCommitmentPolicy = Lowest Rate`, so the −10% carries
past the committed amount.

### 8 — Same spike, discount STOPS at the commitment

**Sell** `QB-DB-TOKEN` + `QB-CMT-TKN-BND`, linked · **Currency** USD · **3× profile**.

| | |
|---|---|
| Consumed | 76,500 raw tokens (identical to scenario 7) |
| Drawdown | identical — both buckets exhausted the same way |
| Overage | 38,722.22 **raw**, no discount |
| **Billed** | **19,361.11 USD** |

`QB-CMT-TKN-BND` is a byte-for-byte clone of FLAT except its
`ProductUsageResourcePolicy` rows carry `Bounded Object Rate`. **Run 7 and 8 back
to back**: same product shape, same usage, same drawdown — **1,936.11 USD apart**,
exactly the 10% the customer forfeits.

> This needs two *products*, not two accounts. `UsageCommitmentPolicy` is a global
> design-time switch that **no runtime object snapshots** — changing it alters
> every deal on that product that later re-rates, and nothing records which policy
> produced a given result.

### 9 — Quantity and spend commitments ⛔ BLOCKED

**Sell** `QB-DB` + `QB-QTY-CMT` (CAD) or `QB-MTY-CMT` (EUR), linked.

**Do not demo these yet.** Both assetize and link cleanly, but their
`TransactionUsageEntitlement` rows never leave `PENDING`: no commitment
`UsageEntitlementAccount`, no buckets, and they rate at **exactly the undiscounted
anchor tier** — indistinguishable from scenario 1. An identically-built token
`Commit` processes fine, so the differentiator is `Product2.UsageModelType`.

Neither documented remediation (`retriggerEntlCreaProc`,
`refreshUsageEntitlementBucket`) changes anything, and nothing errors. Tracked as a
platform issue.

---

## Selling a commitment is THREE steps

The step everyone misses:

1. Quote → order → asset for the **anchor**.
2. Quote → order → asset for the **commitment** (a separate, standalone sale).
3. **Link them** through `UsageCmtAssetRelatedObj`:
   `AssetId` = the commitment, `RelatedObjectId` = the anchor.

Without step 3 the commitment is **inert** — consumption drains the anchor's grant
and rates at the anchor's rate, and the commitment bucket shows 0 consumed. Nothing
in the catalog can express the pairing: a commit product is rejected by
`UsagePrdGrantBindingPolicy` ("Select a Product with the Usage Model Type as Anchor
or Pack"). It is transactional data, which is why it can never live in a data plan.

**Commit and Pack are opposites.** A Pack *requires*
`QuoteLineItem.BindingInstanceTargetId`; a Commit *rejects* binding entirely and
uses the junction.

A commitment **never needs a Contract** — Contract is merely one of four grant
binding target types.

---

## Driving it

```bash
python3 scripts/build_quote_to_asset.py --org <alias> --accounts "<account>" --sku QB-DB-TOKEN
python3 scripts/build_quote_to_asset.py --org <alias> --accounts "<account>" \
    --sku QB-CMT-TKN-FLAT --link-commitment QB-DB-TOKEN
```

Then record usage into a past period, orchestrate until journals stop moving, and
assert:

```bash
sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <alias>
```

Not every scratch account can transact — several ship with no shipping address or
contact and fail activation with `FAILED_ACTIVATION`. The QuantumBit demo accounts
(Infinitech, Kingsbridge Digital, Coralbay Technologies, Helvetia Cloud, Northlight
Systems, Rheintech Solutions, Sakura Systems, Global Media) all have both.

---

## Not yet built

Permutations with no scenario. None are blocked by the platform except where noted.

| Permutation | Note |
|---|---|
| One commitment → multiple anchors | Account-level pooling, with documented end-date ordering and highest-rate-first tiebreak |
| Binding targets other than `Self` | Account / Contract / Custom pooling |
| Rollover and renewal policies | Records exist in `qb-rating`; behaviour never exercised |
| Proration | Mid-period amendment cutting a bucket's validity |
| Multicurrency commitments | Only USD/GBP/AUD proven on commit paths |
| Amend / renew / cancel | Lifecycle against a live commitment |
| Invoicing rated usage | `UsageBillingPeriodItem` → Invoice |
| Monetary minimum-spend billing | Bill the committed minimum when usage falls short — needs scenario 9 unblocked |
| Commitment expiry mid-term | Distinct from exhaustion; policy-driven |
