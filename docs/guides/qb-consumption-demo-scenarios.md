# QuantumBit Consumption Demo Scenarios

Every consumption permutation QuantumBit can demonstrate, what to sell, what to
record, and the exact number that must come out. **Scenarios 1–8 were verified
live** on a 262 scratch org — the arithmetic is what the platform actually
produced, not what the design intends. **Scenario 9 is a blocked path**: it
documents a platform issue and has no valid arithmetic to demo.

⚠ Scenario 6's drawdown figure predates the current pack grant sizes and is flagged
inline for re-verification. Everything else reflects the shipped data.

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
overage      76,500 - 37,777.78 = 38,722.22 raw x 0.90 = 34,850 tokens
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

1–8 verified live (see the caveat on 6); 9 is a blocked path. Currencies differ per
scenario deliberately — it costs nothing and proves multicurrency at the same time.

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
missing a binding instance". The pack's grant is consumed **before** the anchor's,
so recorded usage up to the grant size produces no overage at all.

Shipped grant sizes (`qb-rating/ProductUsageGrant.csv`): `QB-TOKENS-PACK` = **5,000
tokens**, `QB-DAT-THPT` = **100 GB**.

> ⚠ **Re-verify this scenario's numbers before demoing.** The drawdown figure
> recorded here (`45 GB` overage from 50 GB recorded) was observed when the
> throughput grant was **5 GB**; the shipped grant is now **100 GB**, which would
> absorb a 50 GB recording entirely and yield **zero** overage. To demo partial
> drawdown, record more than the grant — or reduce the grant.

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

**Re-checked on 264 — still blocked.** On a freshly built 264 org both model types
were sold and linked against a `QB-DB` anchor, and every entitlement stayed at
`PENDING` (`CommitmentQuantity` 2 rows, `CommitmentSpend` 3) with zero buckets, while
the anchor's own entitlements on that same org reached `PROCESSED`. Do not plan a 264
demo around this scenario.

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

Then record usage into a past period, orchestrate until journals stop moving, wait
for the Data Processing Engine rating jobs to finish (journals stopping means
aggregated, not rated — see [the runbook](usage-consumption-runbook.md)), and assert:

```bash
sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <alias>
```

Not every scratch account can transact — several ship with no shipping address or
contact and fail activation with `FAILED_ACTIVATION`. The QuantumBit demo accounts
(Infinitech, Kingsbridge Digital, Coralbay Technologies, Helvetia Cloud, Northlight
Systems, Rheintech Solutions, Sakura Systems, Global Media) all have both.

---

## Coverage beyond the nine scenarios

**"No scenario written" is not the same as "not built."** Several of these are configured
and shipping today — you can demo them now; what they lack is a walkthrough above, an
asserted result, or both. Others need real work. They are separated here so you can tell
at a glance which is which.

**Already covered, listed only because it reads like a gap:** *binding to a target other
than `Self`* has a scenario — scenario 6 (Pack top-up) **is** this, built and verified.
`QB-TOKENS-PACK` and `QB-DAT-THPT` both use `GrantBindingType = Target` with
`GrantBindingTargetType = Product` (`qb-rating/UsagePrdGrantBindingPolicy.csv`). Only the
**`Account` / `Contract` / `Custom`** target *types* are unbuilt, and those are in the
"not built" table below.

### Built and demoable today — no scenario written

| Permutation | Where the setup already is |
|---|---|
| **Multicurrency commitments** | All 6 commit SKUs (`QB-CMT-TKN-FLAT/EACH/TIER/BND`, `QB-QTY-CMT`, `QB-MTY-CMT`) carry `PricebookEntry` rows in **7/7** currencies. Build is complete; only USD/GBP/AUD have been exercised at runtime |

### Built and silently active — never isolated or asserted

| Permutation | State |
|---|---|
| **Rollover and renewal policies** | Not merely present — **wired to all 12 `ProductUsageGrant` rows**, in the data and in the org (`QB-DB-ROLLOVER`: rollover allowed, no max count; `QB-DB-REFRESH`: renewal every 1 month). They were attached during **every one of the nine scenarios**. Nothing asserts them, so whether rollover or renewal actually *fired* is unknown |

### Exercised end-to-end, with a known-wrong result

| Permutation | State |
|---|---|
| **Invoicing rated usage** | Runs to a posted invoice: `UsageBillingPeriodItem` → invoice line carrying the correct quantities and a **zero amount**, because the usage-definition products carry no `PricebookEntry` and no `RateCardEntry`. Demoable — but do not demo the amount. Tracked as a defect, not a coverage gap |

### Not built — needs new data or lifecycle work

| Permutation | Note |
|---|---|
| Binding target types `Account` / `Contract` / `Custom` | No **QuantumBit** `UsagePrdGrantBindingPolicy` row uses them. The `q3` plan does ship one `Custom` example (`API Access Premium` / `CLOUD001-2`), so there is a shape to copy — but it is not a QB capability, and `Custom` additionally needs `BindingObjectCustomExt` records, which **no plan in this repo seeds**. The quote-line UI offers all four target types regardless of the product's design-time policy, so this is a trap as well as a gap — under investigation |
| One commitment → multiple anchors | The object model allows it — `UsageCmtAssetRelatedObj` has no uniqueness on either FK — but **the shipped CLI cannot produce it**: every `build_quote_to_asset.py` run sells and assetizes a *new* commitment before `link_commitment()` binds it, so running it twice yields two commitments with one anchor each. Needs either a second `UsageCmtAssetRelatedObj` row inserted directly or a `--link-existing-commitment` mode. How the platform pools across anchors is the real unknown |
| Proration | Mid-period amendment cutting a bucket's validity |
| Amend / renew / cancel | Lifecycle against a live commitment |
| Commitment expiry mid-term | Distinct from exhaustion; policy-driven |

### Blocked

| Permutation | Note |
|---|---|
| Monetary minimum-spend billing | Bill the committed minimum when usage falls short — needs scenario 9 unblocked (`CommitmentQuantity`/`CommitmentSpend` entitlements never leave `PENDING`) |
