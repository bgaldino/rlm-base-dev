---
name: ramped-quotes
description: >-
  Build and verify multi-year Revenue Cloud group-ramp quotes through the Connect API.
  Use when creating per-period quote groups, cloning ramp segments, checking price
  uplift or compound uplift, or distinguishing group ramps from line ramps.
---

# Ramped Quotes — Build & Verify Multi-Year Group Ramps

Use this skill to build, verify, or report a **multi-year ramped** Revenue Cloud
quote (one commitment segment per period) over the Connect API, and to get the
per-segment **price uplift** — including **compound** uplift — right. It is
consumable by any AI agent (Cursor, Claude Code, Copilot, Codex, Windsurf,
Aider).

> **Pinned to Release 264 / API v68.0.** Field legality (`field-legality.md`) and the enums here are
> live-observed on a 264 org (v68.0); re-verify on the target release at merge
> time. Ramp build is **transaction authoring**; the compound-uplift *engine*
> (the pricing procedure's `PriceRevision` element) belongs to
> `.cursor/skills/expression-sets/SKILL.md` — this skill links to it, not
> duplicates it.

Two distinct ramp mechanisms exist — do not confuse them:

| Mechanism | Shape | Compounds? |
|---|---|---|
| **Group ramp** (this skill) — `placeSalesTransaction` create → `groupRampAction: EditGroup` → clone × (N−1) → add the `RampScheduleGroup` parent (multi-schedule) | one **`QuoteLineGroup`** per period; segments carry `RampIdentifier` | **Yes** — the group holds `RampUpliftType`, so uplift can compound |
| **Line ramp** — `createRampDeal` on a single line (`/connect/revenue-management/sales-transaction-contexts/{lineId}/actions/ramp-deal-create`) | ungrouped segments (`QuoteLineGroupId=null`) | **No**: there's no group to hold the uplift mode, and `RLM_DefaultPricingProcedure` applies **no** `UnitPriceUplift` to line ramps at all (the ramp filter is limited to group ramps; measured 2026-10-28). Prefer group ramps. |
| *(legacy)* `/commerce/sales-transactions/ramp-deals` (v63–66) | quantity/revenue **commitment** ramp on the deprecated `/commerce/` path | out of scope |

**Compound price uplift requires the group ramp.** Build it with the sequence below.

## Quick Rules

1. **A group ramp is a per-period segment structure — and its shape depends on the
   *Multiple Ramp Schedules Per Transaction* setting** (`enableGroupRampMultiSchedulePref`),
   which **this repo enables by default** (`config/project-scratch-def.json`,
   `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`). **ON (repo
   default) ⇒ a two-level structure:** a top-level `QuoteLineGroup` with
   `Type='RampScheduleGroup'` and one **segment subgroup per period** nested under it
   (`ParentQuoteLineGroupId` → the schedule group). **OFF ⇒ a single-level list** of
   period groups (`ParentQuoteLineGroupId` null). Either way the call order is: (1)
   `placeSalesTransaction` **create** — Quote + period-1 group + one `QuoteLineItem`
   per product; (2) `groupRampAction: "EditGroup"` — `IsRamped=true`,
   `SegmentType=Yearly`, which converts the posted group into segment 1 and stamps
   `RampIdentifier` on its lines; (3) **clone × (N−1)** — one clone per
   *additional* period; (4) in multi-schedule mode, add the `RampScheduleGroup` parent
   yourself (measured on 264: neither call creates it, see step 2). A 3-year ramp =
   create + EditGroup + 2 clones + parent. The exact
   two-level graph and resulting ids must be confirmed by read-back on the target org
   (live-verify rule below).
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
   percentage in **`QuoteLineItem.UnitPriceUplift`** (writeable). Set the mode in
   **`RampUpliftType`** (`Standard`|`Compound`) on the ramp **group** — with
   multi-schedule ON (repo default), on the **top-level `RampScheduleGroup`** (it
   cascades to segment subgroups and lines); with it OFF, on the single ramp segment
   group. `RampUpliftType` is engine-owned on the *line* and rejected there. The
   compounding itself is driven by the pricing procedure's `PriceRevision` element;
   see [Compound uplift](#compound-uplift).
6. **`RampIdentifier` is the cross-segment linkage — constant per product across
   all segments.** Group the read-back matrix on it, not `SegmentIdentifier` (unique
   per line). `ParentQuoteLineGroupId` is **not** a linkage key: with multi-schedule
   ON a segment subgroup's `ParentQuoteLineGroupId` points to its top-level
   `RampScheduleGroup`; only with it OFF is it null.
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
  Set it on the ramp **group** — the **top-level `RampScheduleGroup`** in
  multi-schedule mode (repo default), or the single segment group when the setting is
  off; it cascades to every ramped line in the schedule.
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
| The v68 Connect endpoint catalog (place, clone, ramp-deal, amend/renew/cancel) | `docs/salesforce/264/dev-guide/index.md` (tracked 264 dev-guide index — use the `/connect/rev/...` payloads above). `docs/api/transaction-management-apis-reference.md` is a v68-grounded summary of the same routes; prefer the dev-guide page when the two disagree |
| A null `RampIdentifier` / stale context definitions | `.cursor/skills/context-service/SKILL.md` |

## The proven build sequence

`<PLACEHOLDER>` values are ids you resolve first (see [Discovering ids](#discovering-ids)).
Windows are contiguous per-period spans. For **`SegmentType=Yearly`**, send segment 1
through EditGroup as **exactly 365 days** (`StartDate` + 364 days). Help says "exactly 365
days for all segments, fixed" (`ind.qocal_ramp_deal_for_groups_create.htm.md`). Measured on
264 (2026-10-28), though, **clones end each later segment on the calendar anniversary**:
2027-05-01..2028-04-30 is 366 days and works. So only segment 1 can't contain 29 February. If
it did, it would end a day short of the anniversary and the segments would drift; pick another
start or use `Custom`. Later leap years are fine. `build_quote_to_asset.py --ramp-kind group`
refuses such a start. For variable durations use **`SegmentType=Custom`**.

**Multi-schedule mode (repo default).** With `enableGroupRampMultiSchedulePref=true`
(this repo's setting), a group ramp is the **two-level** structure — a top-level
`Type='RampScheduleGroup'` group with the period segments nested under it — and
`RampUpliftType` is set on that **parent** (Quick Rule 5). EditGroup and clone make only the
segments; you add the parent (step 2). After each mutating call,
read the groups back (`SELECT Id, Type, ParentQuoteLineGroupId, IsRamped FROM
QuoteLineGroup WHERE QuoteId='<QUOTE_ID>'`) to get the parent-schedule and
last-segment ids rather than assuming them.

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
        "CurrencyIsoCode": "<ACCOUNT_CURRENCY>",
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
`PricebookEntryId` (PBE alone fails). For **group** ramps the product needs **no
per-product ramp flag** — all subscription (term-defined) products that meet the
requirements are eligible by default (264 Help, *Ramp Deals for Groups Transition*);
`Product2.CanRamp` gates the *line*-ramp path, not this one. Set
`CurrencyIsoCode` on the Quote to the **account currency** — this repo enables
multicurrency (`config/project-scratch-def.json`), so omitting it lets the quote take
the running user's currency and mismatch the PBE/billing-treatment currency (the
proven builder sets it, `scripts/build_quote_to_asset.py`).
`BillingTreatmentId` is **required** for a term-defined line with a `BillingFrequency`:
the Place call fails with no treatment ("Add a Billing Treatment…") *and* if the
referenced treatment has `CanChangeBillingFrequency=false` ("Update the Billing
Treatment…"). Resolve one for the account currency (see [Discovering ids](#discovering-ids));
this mirrors `scripts/build_quote_to_asset.py`.

> **Check the response body after every Place call — a returned Quote id is not
> success.** `place` reports per-record graph failures in an **`errorResponse`** array
> while still returning **HTTP 200** *and* still creating the parent `Quote` (a naive
> "did I get a quote id?" check then proceeds on a quote with no/partial lines, and
> polling it can look settled). Before polling, fail on a top-level `errorCode`, and on
> a dict response fail if `errorResponse` is non-empty **or** `isSuccess === false`.
> This applies to the create call here and the `EditGroup` call in step 2; the proven
> builder does exactly this (`scripts/build_quote_to_asset.py`). (The `clone` call in
> step 3 has its own contract — `success:false` + populated `errors[]` — covered there.)

### 2. `placeSalesTransaction` (EditGroup) — mark period 1 ramped

Same endpoint, with **`groupRampAction: "EditGroup"`**. This flips the group and
stamps `RampIdentifier` on its lines.

**Each `referenceId` must be the record's own Id**, as in the dev guide's example. EditGroup
matches the groups to convert by `referenceId`; with a label such as `"g"` nothing matches and
the call fails with `UNKNOWN_EXCEPTION` *"Index 0 out of bounds for length 0"* (measured on 264,
2026-10-28; `GroupRampActionHandler.handleEditGroup` indexes the empty match list).

**Multi-schedule mode (repo default): add the parent yourself.** Measured on 264, neither
EditGroup nor clone creates the `RampScheduleGroup`, and an order without one fails activation
with *"Specify a ramp schedule group for ramp segment"* (todo 159). After the clones, POST a
`QuoteLineGroup` with `Type: "RampScheduleGroup"` (a Place with the Quote PATCH and that POST),
then set each segment's `ParentQuoteLineGroupId` to it by DML: a Place that reparents a group to
one it creates fails with *"Cyclic dependencies detected"*. `build_quote_to_asset.py
--ramp-kind group` does all of this. Then read the groups back to capture the parent-schedule id
(needed for `RampUpliftType` in step 4) and the segment ids.

```json
{
  "groupRampAction": "EditGroup",
  "pricingPref": "System",
  "graph": { "graphId": "rampEdit", "records": [
    { "referenceId": "<QUOTE_ID>", "record": {
        "attributes": { "type": "Quote", "method": "PATCH", "id": "<QUOTE_ID>" } } },
    { "referenceId": "<GROUP_ID>", "record": {
        "attributes": { "type": "QuoteLineGroup", "method": "PATCH", "id": "<GROUP_ID>" },
        "StartDate": "2026-01-01", "EndDate": "2026-12-31",
        "SortOrder": 1, "IsRamped": true, "SegmentType": "Yearly" } }
  ] }
}
```

The platform rewrites `SortOrder` (measured: 1 became −999999999, the next clone −999999998),
so order segments by `StartDate`, not by the values you sent.

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
for the next clone. The quote can still read as settled from before the call, so also poll
until the new group exists with `IsRamped`, `SortOrder`, `StartDate` and `EndDate` set (as
`build_quote_to_asset.py` does).

### 4. `placeSalesTransaction` (PATCH) — apply compound uplift, then reprice

Cloning copies the prior segment as-is; it does **not** set the uplift. To produce a
compound ramp you must, after the segments exist, PATCH `RampUpliftType='Compound'`
onto the **top-level `RampScheduleGroup`** (multi-schedule; the single segment group
when the setting is off) and the per-segment **`UnitPriceUplift`** onto each segment's
line, in one Place graph, then reprice and poll. This step is what actually yields the
compound result — the three calls above alone do not. It also needs the fully-configured
`PriceRevision` engine ([Compound uplift](#compound-uplift)).

```json
{
  "pricingPref": "Force",
  "graph": { "graphId": "rampCompound", "records": [
    { "referenceId": "q", "record": {
        "attributes": { "type": "Quote", "method": "PATCH", "id": "<QUOTE_ID>" } } },
    { "referenceId": "sg", "record": {
        "attributes": { "type": "QuoteLineGroup", "method": "PATCH", "id": "<RAMP_SCHEDULE_GROUP_ID>" },
        "RampUpliftType": "Compound" } },
    { "referenceId": "l1", "record": {
        "attributes": { "type": "QuoteLineItem", "method": "PATCH", "id": "<SEGMENT_2_LINE_ID>" },
        "UnitPriceUplift": 5 } },
    { "referenceId": "l2", "record": {
        "attributes": { "type": "QuoteLineItem", "method": "PATCH", "id": "<SEGMENT_3_LINE_ID>" },
        "UnitPriceUplift": 3 } }
  ] }
}
```

Segment 1 is the baseline (leave `UnitPriceUplift` 0). `pricingPref: "Force"`
re-runs pricing so the engine applies the compound uplift. Poll `CalculationStatus`
to a settled state, then read back ([Read-back](#read-back--the-ramp-schedule)) and
verify the compounding numerically.

> **Apex-invocable variant.** Some connectors expose clone as a CLASSIC Apex
> invocable whose args are wrapped in an `inputs` array. `lineScope` lives inside the
> Apex-defined **`options`** input (with optional `recordTypeId`), not at the top level
> (`actions_obj_deep_clone_sales_transaction.htm.md`):
> `{ "inputs": [ { "salesTransactionId": "...", "recordIds": ["..."], "options": { "lineScope": "AllLines" } } ] }`.
> Same semantics; use whichever the transport exposes.

### <a name="status"></a>Poll `CalculationStatus` between calls

`Quote.CalculationStatus` is read-only and moves through tax/price/save states.
Match against the **live v68 enum** (from `scripts/erd/schema_diff/264-schema.json`),
not a suffix wildcard — several in-flight values are `QueuedFor…`-**prefixed** (they
do not *end* in `Queued`) and `TaxCalculationInProcess` is not `…InProgress`:

- **Settled — success:** `CompletedWithTax` (the org returns this where the describe
  lists `TaxCalculationSuccess` — treat both as success); `CompletedWithoutPricing`
  (settled, but pricing was **skipped** — not a priced result, so do not report
  prices from it).
- **`CompletedWithPricing` — settled *when tax doesn't run*.** Pricing is done; on
  an org that calculates estimated tax, tax runs next. Which applies depends on the org:
  - **Foundations default build:** estimated tax on quotes and orders is **off**
    (`unpackaged/post_quote_est_tax_settings/`; the `quote_est_tax` flag, with `tax`,
    turns it on). Tax never
    runs, so `CompletedWithPricing` is **terminal**. Live 264.7, 2026-10-14: quotes
    stopped there with no `taxPref`.
  - **Estimated tax on and `taxPref` omitted:** `taxPref` defaults to running tax
    (`connect_requests_place_sales_transaction_input.htm.md`), so `CompletedWithPricing`
    is **still in flight**; wait for `CompletedWithTax`.
  - **`taxPref: "Skip"`:** terminal on any org.
  - The platform also skips tax when any line has a **negative quantity**, so a
    quantity reduction (a negative-quantity line) is terminal at `CompletedWithPricing`
    even with estimated tax on. A price-lowering amendment instead fails with
    `AmountNegative` while estimated tax is on.
  - Robust pollers accept both values as settled; see `E2ECommon.robot`
    `@{QUOTE_CALC_PRICED}`.
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

Read [`compound-uplift.md`](compound-uplift.md) when you apply or verify a **Compound** uplift:
the prerequisites, how the engine compounds on the prior period, and the per-period arithmetic to
check a read-back against. The PATCH payload itself is step 4 above.

## Read-back → the ramp schedule

**Assert the groups first.** A clone after a failed `EditGroup` still returns `success:true`: it
copies a group that was never converted, leaving segments with `IsRamped` and `SortOrder` null that
look like a healthy ramp by count and name. Before reading prices, check:
- every segment group has `IsRamped = true`, a non-null `SortOrder` and a `SegmentType`;
- the segment count is the number of periods;
- in multi-schedule mode (repo default), exactly one group has `Type = 'RampScheduleGroup'`. It is
  the parent, not a segment (observed with `IsRamped = false` and `SortOrder` 0; leave it out of the
  segment checks), and it carries the expected `RampUpliftType`. Every segment's
  `ParentQuoteLineGroupId` must be the `RampScheduleGroup`'s Id. A segment with no parent prices correctly and passes the
  checks above, then fails at order activation with "Specify a ramp schedule group for ramp
  segment".

```bash
sf data query --target-org <sf_alias> -q "SELECT Id, Name, Type, ParentQuoteLineGroupId, \
  IsRamped, SortOrder, SegmentType, RampUpliftType \
  FROM QuoteLineGroup WHERE QuoteId='<QUOTE_ID>' ORDER BY StartDate NULLS FIRST"
```

Then the lines:

```bash
sf data query --target-org <sf_alias> -q "SELECT Product2.Name, Product2.StockKeepingUnit, \
  SegmentName, IsPrimarySegment, RampIdentifier, StartDate, EndDate, Quantity, \
  UnitPrice, NetUnitPrice, TotalPrice, NetTotalPrice, UnitPriceUplift, \
  ApplUnitPriceUpliftPct, RampUpliftType, QuoteLineGroupId \
  FROM QuoteLineItem WHERE QuoteId='<QUOTE_ID>' ORDER BY StartDate NULLS FIRST"
```

Report: account, products, **TCV** (Σ all line totals across all segments),
per-period subtotal and **% of TCV**, and the ramp-by-product matrix (grouped on
`RampIdentifier`, labelled by `Product2.Name`/`StockKeepingUnit`). Sum the
platform-computed **`NetTotalPrice`** for TCV and subtotals — it is the
**post-discount, prorated** line total that propagates to the posted invoice
(`scripts/txn_data_harness/docs/contracts-sales-txn-quote.md`). `TotalPrice` is the
gross list total and **overstates** TCV whenever an uplift, discount, or proration
changes the net; do **not** sum it, and do **not** derive totals from `Quantity ×
NetUnitPrice` (unreliable for term-priced/prorated lines). Both totals are read-only
(never *set* them) but queryable; all numbers come from the priced quote.

## <a name="discovering-ids"></a>Discovering ids

The ask won't give Salesforce ids — resolve them first. Map spoken product intent
("gen-AI licenses", "premium support") to real SKUs from the catalog; don't invent
SKUs.

```bash
# Account — SELECT CurrencyIsoCode: multicurrency is on (repo default), and it drives
# the Quote/PBE/BillingTreatment currency below.
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name, CurrencyIsoCode FROM Account WHERE Name = '<name>'"
# PricebookEntry — a ramp needs BOTH Product2Id and this. Match the SKU on
# Product2.StockKeepingUnit (the repo's SKU field, per scripts/build_quote_to_asset.py
# and scripts/txn_data_harness/discovery.py — NOT ProductCode). Filter to the ACCOUNT
# currency and require BOTH the entry and the product active (IsActive = true AND
# Product2.IsActive = true), and read the selling model: a product can expose several
# (e.g. Evergreen / Term Monthly / Term Annual) and the model dictates which line
# fields are legal, so pick a TermDefined one deliberately (not the first row).
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Product2Id, Pricebook2Id, UnitPrice, \
     ProductSellingModel.Name, ProductSellingModel.SellingModelType \
   FROM PricebookEntry \
   WHERE Product2.StockKeepingUnit = '<SKU>' AND Pricebook2.IsStandard = true \
     AND IsActive = true AND Product2.IsActive = true \
     AND CurrencyIsoCode = '<ACCOUNT_CURRENCY>'"
# Group-ramp eligibility: no per-product ramp flag is required — any subscription
# (term-defined) product that meets the requirements is eligible by default (264
# Help). `Product2.CanRamp` is the LINE-ramp flag, not a group-ramp prerequisite.
# BillingTreatment for <TREATMENT_ID> — REQUIRED on a term-defined line with a
# BillingFrequency. Must be Active, match the ACCOUNT currency, and have
# CanChangeBillingFrequency = true (the Place call rejects a treatment without it).
sf data query --target-org <sf_alias> -q \
  "SELECT Id, Name, CanChangeBillingFrequency FROM BillingTreatment \
   WHERE Status = 'Active' AND CurrencyIsoCode = '<ACCOUNT_CURRENCY>' \
   AND CanChangeBillingFrequency = true ORDER BY Name"
```

## Field legality (live 264 / v68.0)

Read [`field-legality.md`](field-legality.md) when a Place or PATCH call rejects a field, or before
writing a line field: which ramp and pricing fields are writable on input on live 264.

## A headless toolkit is in development

A dependency-free `scripts/ramp_deals/` toolkit (schedule math, payload builders,
status polling, read-back invariants) mirroring `scripts/expression_sets/` is being
built on branch **`feat/ramp-deals-core`** (not yet merged to `main`). Until it
lands, use the raw Connect calls above. When it merges, wire its CLIs into this
skill's routing.

## Examples

**Worked example — a 3-year ramp on a standalone SKU** (substitute your own ids):

1. Resolve ids for one eligible subscription (term-defined) product + its standard,
   active `PricebookEntry` in the account currency (no per-product ramp flag needed
   for group ramps).
2. `placeSalesTransaction` create → Quote + "Year 1" group + one line (365-day
   window; resolve a `BillingTreatmentId`). Poll until settled: `CompletedWithPricing`
   on a default Foundations build, `CompletedWithTax` where estimated tax is on.
3. `placeSalesTransaction` `EditGroup` on the Year-1 group (`IsRamped=true`,
   `SegmentType=Yearly`, each `referenceId` the record's Id). Poll.
4. `cloneSalesTransaction` twice (Year 2, Year 3), each cloning the last ramped
   segment. Poll after each. In multi-schedule mode, then POST the `RampScheduleGroup`
   and reparent the segments to it by DML (step 2 of the sequence), and read the groups
   back to get its id.
5. For compound uplift (step 4 of the sequence): PATCH `RampUpliftType='Compound'`
   on the **top-level `RampScheduleGroup`** and per-segment `UnitPriceUplift`, then
   reprice (`pricingPref:"Force"`) and poll (needs the fully-configured
   `PriceRevision` engine — [Compound uplift](#compound-uplift)).
6. Read back; report TCV, per-year subtotal, % of TCV, ramp-by-product matrix.

Expected compound shape for this 3-year ramp (base 360, uplifts 5/3% — baseline +
2 uplifts = 3 periods): 360 → 378 → 389.34 (applied % 0 → 5 → 8.15). A 4-year ramp
would add a 3rd uplift, e.g. +2% → 397.13 (applied % 10.313).

## Validation Checks

- [ ] Group ramp (per-period segment structure — the two-level `RampScheduleGroup`
      in the repo's multi-schedule default), not a line ramp, if compound uplift is
      in scope.
- [ ] The `Yearly` segment 1 sent to EditGroup is **exactly 365 days** and doesn't contain
      29 February (clones end later segments on calendar anniversaries); `Custom` used for
      variable/calendar durations.
- [ ] `BillingTreatmentId` resolved on each term-defined line (Active, account
      currency, `CanChangeBillingFrequency=true`).
- [ ] No read-only/system fields written on the graph (see [`field-legality.md`](field-legality.md)).
- [ ] `RampUpliftType='Compound'` on the ramp **group** (the top-level
      `RampScheduleGroup` in multi-schedule mode), never on the line; per-segment
      `UnitPriceUplift` set on lines, then repriced with `pricingPref:"Force"`.
- [ ] `CalculationStatus` polled to a settled state between calls; unknown status
      halted, not assumed.
- [ ] Group shape asserted before prices (*Read-back*): segment fields set, one segment per
      period, and in multi-schedule mode one `RampScheduleGroup` parent that every segment points
      at.
- [ ] Read-back grouped on `RampIdentifier`; every ramped line carries both
      `RampIdentifier` and `SegmentIdentifier` (proves it went through
      `groupRampAction`); TCV reconciles.
- [ ] Compound arithmetic verified against a read-back (applied % compounds on the
      prior factor).
- [ ] Any mutating run executed against a confirmed **writable** live 264 org.

## Sub-files

- `compound-uplift.md` — Compound price uplift: prerequisites, how it compounds, and the arithmetic
  to verify. Read it when applying or checking Compound.
- `field-legality.md` — which ramp and pricing line fields are writable on live 264. Read it when a
  call rejects a field.

## Related References

- **Compound-uplift engine** (`PriceRevision`, `IsCompoundUpliftEnabled`, ramp vs
  non-ramp path): `.cursor/skills/expression-sets/SKILL.md` →
  [Compound ramp uplift](../expression-sets/SKILL.md#compound-ramp-uplift).
- **Advanced Detail Line Pricing / context definition sync** (compound
  prerequisite; null-`RampIdentifier` fix): `.cursor/skills/context-service/SKILL.md`.
- **v68 Connect endpoint catalog** (place, clone, ramp-deal, amend/renew/cancel):
  `docs/salesforce/264/dev-guide/index.md` (tracked 264 dev-guide — `/connect/rev/...`).
  `docs/api/transaction-management-apis-reference.md` summarizes the same v68
  routes; prefer the dev-guide page when the two disagree.
- **Non-ramp quote→order→asset builder:** `scripts/build_quote_to_asset.py`;
  `.cursor/skills/txn-data-harness/SKILL.md`.
- **RLM object/field model:** `.cursor/skills/revenue-cloud-data-model/SKILL.md`.
