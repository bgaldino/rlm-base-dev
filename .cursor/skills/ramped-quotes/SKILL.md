# Ramped Quotes — Build & Verify Multi-Year Group Ramps

Use this skill to build, verify, or report a **multi-year ramped** Revenue Cloud
quote (one commitment segment per period) over the Connect API, and to get the
per-segment **price uplift** — including **compound** uplift — right. It is
consumable by any AI agent (Cursor, Claude Code, Copilot, Codex, Windsurf,
Aider).

> **Pinned to Release 264 / API v68.0.** Field legality and enums below are
> live-observed on a 264 org (v68.0); re-verify on the target release at merge
> time. Ramp build is **transaction authoring**; the compound-uplift *engine*
> (the pricing procedure's `PriceRevision` element) belongs to
> `.cursor/skills/expression-sets/SKILL.md` — this skill links to it, not
> duplicates it.

Two distinct ramp mechanisms exist — do not confuse them:

| Mechanism | Shape | Compounds? |
|---|---|---|
| **Group ramp** (this skill) — `placeSalesTransaction` create → `groupRampAction: EditGroup` → clone × (N−1) | one **`QuoteLineGroup`** per period; segments carry `RampIdentifier` | **Yes** — the group holds `RampUpliftType`, so uplift can compound |
| **Line ramp** — `createRampDeal` on a single line (`/connect/revenue-management/sales-transaction-contexts/{lineId}/actions/ramp-deal-create`) | ungrouped segments (`QuoteLineGroupId=null`) | **No** — no group to hold the uplift mode |
| *(legacy)* `/commerce/sales-transactions/ramp-deals` (v63–66) | quantity/revenue **commitment** ramp on the deprecated `/commerce/` path | out of scope |

**Compound price uplift requires the group ramp.** Build it with the sequence below.

## Quick Rules

1. **A group ramp is one `QuoteLineGroup` per period.** Build it in exactly this
   order: (1) `placeSalesTransaction` **create** — Quote + one group (period 1) +
   one `QuoteLineItem` per product, all `POST` in a single graph; (2)
   `placeSalesTransaction` with **`groupRampAction: "EditGroup"`** — flip period-1's
   group to `IsRamped=true`, `SegmentType=Yearly`, which stamps `RampIdentifier` on
   its lines; (3) **clone × (N−1)** — one clone per *additional* period. A 3-year
   ramp = create + EditGroup + 2 clones.
2. **The group is created plain, then ramped by `EditGroup`.** Do **not** try to
   `POST` an already-ramped group. `EditGroup` sets `IsRamped`/`SegmentType`/dates.
3. **Clone is a separate Connect resource**, not a `groupRampAction`:
   `POST /connect/rev/sales-transaction/actions/clone` with
   `{salesTransactionId, recordIds:[<last ramped group id>] (max 1), options:{lineScope}}`.
   `lineScope` ∈ `AllLines` (default) | `RampedLinesOnly`. **Clone only the last
   segment's group.**
4. **Between mutating calls, poll `Quote.CalculationStatus` to a settled state**
   before the next call. Treat an unrecognized status as *stop and look*, never
   "assume done" (see [Status](#status)).
5. **Compound uplift is group + engine, not a line write.** Set the per-segment
   percentage in **`QuoteLineItem.UnitPriceUplift`** (writeable) and the mode in
   **`QuoteLineGroup.RampUpliftType`** (`Standard`|`Compound`) — the mode is
   engine-owned on the *line* and rejected there. The compounding itself is driven
   by the pricing procedure's `PriceRevision` element; see
   [Compound uplift](#compound-uplift).
6. **`RampIdentifier` is the cross-segment linkage — constant per product across
   all segments.** Group the read-back matrix on it. Do **not** use
   `SegmentIdentifier` (unique per line) or `ParentQuoteLineGroupId` (null).
7. **Report from the priced quote — never re-price.** PST already computed net
   prices, subtotals, and totals; read them back.
8. **`org_config.username` for `sf` CLI; `access_token` for REST only** (per
   `AGENTS.md`).

## DO NOT

- **DO NOT** write system-generated / read-only fields on the graph: on the line,
  `RampIdentifier`, `SegmentIdentifier`, `EndQuantity`, `NetUnitPrice`,
  `TotalPrice`; on the Quote, `GrandTotal`, `TotalPrice`, `CalculationStatus`,
  `QuoteNumber`. They are computed — the call fails if you set them.
- **DO NOT** write `RampUpliftType` on `QuoteLineItem`/`OrderItem` via Place — it
  is engine-owned there (rejected as not-writeable even when FLS shows editable).
  Set it on the **`QuoteLineGroup`**; it cascades to the group's ramped lines.
- **DO NOT** use the trial segment type `Trial` — the live enum is **`FreeTrial`**
  (`SegmentType` ∈ `Yearly`, `Custom`, `FreeTrial`, `Prorated`).
- **DO NOT** clone more than one group per call — `recordIds` takes exactly one id
  (the last segment's group).
- **DO NOT** expect a clone to vary quantity or price per period — it copies the
  prior segment as-is. To grow a ramp, set per-segment values (quantity,
  `UnitPriceUplift`) after cloning. Do not fake growth silently; note it.
- **DO NOT** ramp a **bundle** while the CML constraint model is active — a bundle
  re-expands its children on each clone (known issue). Keep ramp demos on
  **standalone** products (`configurationPref.configurationMethod: "Skip"`).
- **DO NOT** treat a null `RampIdentifier` on read-back as a graph mistake — it
  usually means the org's **context definitions are stale**; a Context Definition
  sync fixes it (see `.cursor/skills/context-service/SKILL.md`).
- **DO NOT** claim a build "works" from an offline dry-run — a mutating ramp run
  must be verified against a **live 264 org**, writing only to a confirmed
  **writable** org.

## Entry Conditions

| Situation | Use |
|---|---|
| Build / add a segment to / verify a multi-year **group** ramp quote | This skill |
| Get **compound** per-segment uplift right (the `PriceRevision` engine, `IsCompoundUpliftEnabled`, prerequisites) | [Compound uplift](#compound-uplift) → `.cursor/skills/expression-sets/SKILL.md` |
| Turn on **Advanced Detail Line Pricing** / sync context definitions (a compound prerequisite) | `.cursor/skills/context-service/SKILL.md` |
| Resolve Account / Pricebook / Product2 / PricebookEntry ids | [Discovering ids](#discovering-ids) |
| Build a non-ramp quote → order → asset | `scripts/build_quote_to_asset.py`; `.cursor/skills/txn-data-harness/SKILL.md` |
| The raw Connect endpoint catalog (place, clone, ramp-deal, amend/renew/cancel) | `postman/docs/transaction-management-apis-reference.md`; `.cursor/skills/rlm-business-apis/SKILL.md` |
| A null `RampIdentifier` / stale context definitions | `.cursor/skills/context-service/SKILL.md` |

## The proven build sequence

`<PLACEHOLDER>` values are ids you resolve first (see [Discovering ids](#discovering-ids)).
Windows are contiguous calendar-year spans (`2026-01-01..2026-12-31`,
`2027-01-01..2027-12-31`, …), 12 months per period.

### 1. `placeSalesTransaction` (create) — Quote + group + lines

`POST /connect/rev/sales-transaction/actions/place`. Fields are **siblings of
`attributes`**, not nested under a `fields` key; `@{refX.id}` wires children to
parents created in the same call.

```json
{
  "pricingPref": "System",
  "configurationPref": { "configurationMethod": "Skip" },
  "graph": { "graphId": "rampCreate", "records": [
    { "referenceId": "refQuote", "record": {
        "attributes": { "type": "Quote", "method": "POST" },
        "Name": "<deal name>", "QuoteAccountId": "<ACCOUNT_ID>",
        "Status": "Draft", "Pricebook2Id": "<PRICEBOOK_ID>" } },
    { "referenceId": "refGroup", "record": {
        "attributes": { "type": "QuoteLineGroup", "method": "POST" },
        "Name": "Year 1", "QuoteId": "@{refQuote.id}" } },
    { "referenceId": "refLine0", "record": {
        "attributes": { "type": "QuoteLineItem", "method": "POST" },
        "QuoteId": "@{refQuote.id}", "QuoteLineGroupId": "@{refGroup.id}",
        "Product2Id": "<PRODUCT2_ID>", "PricebookEntryId": "<PBE_ID>",
        "Quantity": 1, "SubscriptionTerm": 12,
        "StartDate": "2026-01-01", "EndDate": "2026-12-31",
        "PeriodBoundary": "AlignToCalendar", "BillingFrequency": "Monthly",
        "BillingTreatmentId": "<TREATMENT_ID>" } }
  ] }
}
```

Add one `refLineN` per product. A ramp line needs **both** `Product2Id` and
`PricebookEntryId` (PBE alone fails). The product must be `Product2.CanRamp=true`.

### 2. `placeSalesTransaction` (EditGroup) — mark period 1 ramped

Same endpoint, with **`groupRampAction: "EditGroup"`**. This flips the group and
stamps `RampIdentifier` on its lines.

```json
{
  "groupRampAction": "EditGroup",
  "pricingPref": "System",
  "graph": { "graphId": "rampEdit", "records": [
    { "referenceId": "q", "record": {
        "attributes": { "type": "Quote", "method": "PATCH", "id": "<QUOTE_ID>" } } },
    { "referenceId": "g", "record": {
        "attributes": { "type": "QuoteLineGroup", "method": "PATCH", "id": "<GROUP_ID>" },
        "StartDate": "2026-01-01", "EndDate": "2026-12-31",
        "SortOrder": 1, "IsRamped": true, "SegmentType": "Yearly" } }
  ] }
}
```

### 3. `cloneSalesTransaction` — add each subsequent period

`POST /connect/rev/sales-transaction/actions/clone`, once per additional period,
each cloning the most recent ramped group:

```json
{ "salesTransactionId": "<QUOTE_ID>",
  "recordIds": [ "<LAST_RAMPED_GROUP_ID>" ],
  "options": { "lineScope": "AllLines" } }
```

The v68 clone response is `{ requestId, salesTransactionId, success, errors }`
(`docs/salesforce/264/dev-guide/articles/connect_responses_clone_sales_transaction_output.htm.md`)
— there is **no** `trackerId`. `success:false` with a populated `errors[]` is a
synchronous failure — stop. On `success:true` the save runs **async**: `requestId`
identifies that process, and the observable gate is `Quote.CalculationStatus` —
poll it to a settled state ([Status](#status)) before the next call. Do **not**
read or clone the next group until it settles; then read back the new group's id
for the next clone.

> **Apex-invocable variant.** Some connectors expose clone as a CLASSIC Apex
> invocable whose args are wrapped in an `inputs` array:
> `{ "inputs": [ { "salesTransactionId": "...", "recordIds": ["..."], "lineScope": "AllLines" } ] }`.
> Same semantics; use whichever the transport exposes.

### <a name="status"></a>Poll `CalculationStatus` between calls

`Quote.CalculationStatus` is read-only and moves through tax/price/save states.
Match against the **live v68 enum** (from `scripts/erd/schema_diff/264-schema.json`),
not a suffix wildcard — several in-flight values are `QueuedFor…`-**prefixed** (they
do not *end* in `Queued`) and `TaxCalculationInProcess` is not `…InProgress`:

- **Settled — success:** `CompletedWithPricing`; `CompletedWithTax` (the org returns
  this where the describe lists `TaxCalculationSuccess` — treat both as success);
  `CompletedWithoutPricing` (settled, but pricing was **skipped** — not a priced
  result, so do not report prices from it).
- **Settled — failure (terminal):** any `…Failed` — `TaxCalculationFailed`,
  `PriceCalculationFailed`, `SaveFailedOrIncomplete`, `ConfigurationFailed`,
  `ReconciliationFailed`, `GroupRampConfigurationFailed`, `PstBaseStepFailed`,
  `ARCStepFailed`, `QuoteRequestFailed`, `CloneFailed`.
- **In-flight (keep polling):** `NotStarted`, `TaxCalculationWaiting`,
  `TaxCalculationInProcess`, `PriceCalculationQueued`, `PriceCalculationInProgress`,
  `Saving`, `ConfigurationInProgress`, `ReconciliationInProgress`,
  `ContextHydrationInProgress`, `ARCInProgress`, `CloneInProgress`, and every
  `QueuedFor…` value (`QueuedForConfiguration`, `QueuedForPricing`,
  `QueuedForPricingAndSaving`, `QueuedForSaving`, `QueuedForARC`, `QueuedForClone`).

**A value in none of these = stop and look**, not "keep polling" or "assume done".

## <a name="compound-uplift"></a>Compound price uplift

Compound uplift makes each period's price uplift on the **prior period's factor**
(not the list price). Working in **percent units** (the units `UnitPriceUplift` and
`ApplUnitPriceUpliftPct` carry):
`applied%(n) = [(1 + applied%(n−1)/100) × (1 + unitUplift%(n)/100) − 1] × 100`,
and `NetUnitPrice(n) = base × (1 + applied%(n)/100)`. The `× 100` converts the
compounded multiplier back to a percentage — e.g. uplifts 5% then 3% give
`applied% = 8.15` (not `0.0815`), so `NetUnitPrice = base × 1.0815`. The first
period is the baseline; a 0% period is a *carryover* (prior cumulative multiplier
preserved).

It needs **all** of:

1. **Revenue Settings → Advanced Detail Line Pricing = ON**, context definition
   synced. Off ⇒ standard (list-based) uplift only. Turning it off *after* compound
   quotes/orders/assets exist corrupts pricing/amendments/renewals. See
   `.cursor/skills/context-service/SKILL.md`.
2. **A group ramp** (this skill) — line ramps can't compound.
3. **`RampUpliftType='Compound'` on the `QuoteLineGroup`** (cascades to lines).
4. **The pricing procedure's ramp `PriceRevision` element has
   `IsCompoundUpliftEnabled=true`** — *this is the engine*. Inspect / diff / author
   it via `.cursor/skills/expression-sets/SKILL.md` →
   [Compound ramp uplift](../expression-sets/SKILL.md#compound-ramp-uplift)
   (there are two `PriceRevision` steps; only the ramp path compounds).
5. **`UnitPriceUplift` (per-period %) set per segment** on each `QuoteLineItem`.

**Unsupported for compound** (264 Help, *Considerations for Ramp Deals*,
`docs/salesforce/264/help/articles/ind.qocal_considerations_ramp_deals.htm.md`):
a SKU using **CPI renewal uplift**, **usage-based pricing**, or **derived pricing**
can't compound — don't build a compound ramp on one; its verification would be
invalid. Also: compound **resets on renewal** (Year 1 of the new term is the new
baseline), and records created **before Winter '27** use standard uplift.

Verify numerically by reading back the segments (below).

## Read-back → the ramp schedule

```bash
sf data query --target-org <sf_alias> -q "SELECT Product2.Name, Product2.ProductCode, \
  SegmentName, IsPrimarySegment, RampIdentifier, StartDate, EndDate, Quantity, \
  UnitPrice, NetUnitPrice, TotalPrice, UnitPriceUplift, ApplUnitPriceUpliftPct, \
  RampUpliftType, QuoteLineGroupId \
  FROM QuoteLineItem WHERE QuoteId='<QUOTE_ID>' ORDER BY StartDate NULLS FIRST"
```

Report: account, products, **TCV** (Σ all line totals across all segments),
per-period subtotal and **% of TCV**, and the ramp-by-product matrix (grouped on
`RampIdentifier`, labelled by `Product2.Name`/`ProductCode`). Sum the
platform-computed **`TotalPrice`** for TCV and subtotals — do **not** derive them
from `Quantity × NetUnitPrice`, which is unreliable for term-priced or prorated
lines. `TotalPrice` is read-only (never *set* it) but is queryable; all numbers
come from the priced quote.

## <a name="discovering-ids"></a>Discovering ids

The ask won't give Salesforce ids — resolve them first. Map spoken product intent
("gen-AI licenses", "premium support") to real SKUs from the catalog; don't invent
SKUs.

```bash
# Account, Pricebook, per-product Product2 + PricebookEntry (a ramp needs BOTH).
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name FROM Account WHERE Name = '<name>'"
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Product2Id, Pricebook2Id, UnitPrice FROM PricebookEntry \
   WHERE Product2.ProductCode = '<SKU>' AND Pricebook2.IsStandard = true"
# Rampable products only:
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name, ProductCode FROM Product2 WHERE CanRamp = true"
```

## Field legality (live 264 / v68.0)

Snapshot — re-verify with a `describe` on the target org. Writeable = createable/updateable on the graph.

| Object | Writeable (set these) | Read-only (never set) |
|---|---|---|
| `QuoteLineGroup` | `IsRamped`, `SegmentType`, `StartDate`, `EndDate`, `SortOrder`, `Type`, `Name`, `RampUpliftType` | — |
| `QuoteLineItem` | `Quantity`, `StartQuantity`, `UnitPrice`, `UnitPriceUplift`, `Discount`, `DiscountAmount`, `StartDate`, `EndDate`, `SegmentType`, `QuoteLineGroupId` | `RampIdentifier`, `SegmentIdentifier`, `EndQuantity`, `NetUnitPrice`, `TotalPrice`, `ApplUnitPriceUpliftPct`; `RampUpliftType` engine-owned via Place |
| `Quote` | `Status`, `TotalPriceOverride`, `AdjustmentDistributionLogic` | `CalculationStatus`, `TotalPrice`, `GrandTotal`, `QuoteNumber` |
| `Product2` | — | `CanRamp` |

`SegmentType` enum: `Yearly`, `Custom`, `FreeTrial`, `Prorated`.
`QuoteLineGroup.Type` enum: `CPQQuoteGroup`, `RampScheduleGroup`, `AssetSwap`,
`AssetUpgrade`, `AssetDowngrade`.

## A headless toolkit is in development

A dependency-free `scripts/ramp_deals/` toolkit (schedule math, payload builders,
status polling, read-back invariants) mirroring `scripts/expression_sets/` is being
built on branch **`feat/ramp-deals-core`** (not yet merged to `264`). Until it
lands, use the raw Connect calls above. When it merges, wire its CLIs into this
skill's routing.

## Examples

**Worked example — a 3-year ramp on a standalone SKU** (substitute your own ids):

1. Resolve ids for one rampable product (`Product2.CanRamp=true`) + its standard
   `PricebookEntry`.
2. `placeSalesTransaction` create → Quote + "Year 1" group + one line (12-month
   window). Poll to `CompletedWithTax`.
3. `placeSalesTransaction` `EditGroup` on the Year-1 group (`IsRamped=true`,
   `SegmentType=Yearly`). Poll.
4. `cloneSalesTransaction` twice (Year 2, Year 3), each cloning the last ramped
   group. Poll after each.
5. For compound uplift: set `RampUpliftType='Compound'` on the group and
   `UnitPriceUplift` per segment, then reprice (needs the `PriceRevision` engine —
   [Compound uplift](#compound-uplift)).
6. Read back; report TCV, per-year subtotal, % of TCV, ramp-by-product matrix.

Expected compound shape for this 3-year ramp (base 360, uplifts 5/3% — baseline +
2 uplifts = 3 periods): 360 → 378 → 389.34 (applied % 0 → 5 → 8.15). A 4-year ramp
would add a 3rd uplift, e.g. +2% → 397.13 (applied % 10.313).

## Validation Checks

- [ ] Group ramp (one `QuoteLineGroup` per period), not a line ramp, if compound
      uplift is in scope.
- [ ] No read-only/system fields written on the graph (see the legality table).
- [ ] `RampUpliftType='Compound'` on the **group**, never on the line; per-segment
      `UnitPriceUplift` set on lines.
- [ ] `CalculationStatus` polled to a settled state between calls; unknown status
      halted, not assumed.
- [ ] Read-back grouped on `RampIdentifier`; every ramped line carries both
      `RampIdentifier` and `SegmentIdentifier` (proves it went through
      `groupRampAction`); TCV reconciles.
- [ ] Compound arithmetic verified against a read-back (applied % compounds on the
      prior factor).
- [ ] Any mutating run executed against a confirmed **writable** live 264 org.

## Related References

- **Compound-uplift engine** (`PriceRevision`, `IsCompoundUpliftEnabled`, ramp vs
  non-ramp path): `.cursor/skills/expression-sets/SKILL.md` →
  [Compound ramp uplift](../expression-sets/SKILL.md#compound-ramp-uplift).
- **Advanced Detail Line Pricing / context definition sync** (compound
  prerequisite; null-`RampIdentifier` fix): `.cursor/skills/context-service/SKILL.md`.
- **Connect endpoint catalog** (place, clone, ramp-deal, amend/renew/cancel):
  `postman/docs/transaction-management-apis-reference.md`;
  `.cursor/skills/rlm-business-apis/SKILL.md`.
- **Non-ramp quote→order→asset builder:** `scripts/build_quote_to_asset.py`;
  `.cursor/skills/txn-data-harness/SKILL.md`.
- **RLM object/field model:** `.cursor/skills/revenue-cloud-data-model/SKILL.md`.
