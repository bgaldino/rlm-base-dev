# Ramped Quotes — The proven build sequence

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`. The API build, step by step (create, EditGroup, clone, compound PATCH). Polling, read-back and id discovery: [verify-and-discover.md](verify-and-discover.md).

`<PLACEHOLDER>` values are ids you resolve first (see [Discovering ids](verify-and-discover.md#discovering-ids)).
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
A term-defined line with a `BillingFrequency` that differs from its selling model's pricing
term needs a `BillingTreatmentId` (Active, Change Billing Frequency selected); a matching
frequency needs none ([billing-setup](../billing-setup/SKILL.md), item 3). Where one is needed,
resolve one for the account currency (see [Discovering ids](verify-and-discover.md#discovering-ids));
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

Per the dev guide the v68 clone response is `{ requestId, salesTransactionId, success, errors }`
(`docs/salesforce/264/dev-guide/articles/connect-responses-clone-sales-transaction-output.md`);
measured clones also returned a `trackerId` key, null in group clones (ramp runs) and in whole-quote clones, and a
`trackerUrl` key, null in whole-quote clones (see
[quote-negotiation-rounds → deep-clone.md](../quote-negotiation-rounds/deep-clone.md#response-and-completion)).
`success:false` with a populated `errors[]` is a
synchronous failure — stop. On `success:true` the save runs **async**. The dev guide says `requestId`
identifies that process; every measured response had `requestId` null, so it can't be the gate there. The
large-transaction clone path wasn't traced. Gate on `Quote.CalculationStatus` —
poll it to a settled state ([Status](verify-and-discover.md#status)) before the next call. Do **not**
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
compound result — the three calls above alone do not. Segments
reparented to the `RampScheduleGroup` by DML priced as Standard until this PATCH sent
`RampUpliftType` [Measured: 2026-11-16, 264, scratch]. `build_quote_to_asset.py --ramp-kind
group` sets neither `RampUpliftType` nor `UnitPriceUplift` [Repo], so send this step yourself.
[Open: whether `RampUpliftType` set on the `RampScheduleGroup` POST takes effect; until tested,
send it in this PATCH] It also needs the fully-configured
`PriceRevision` engine ([Compound uplift](compound-uplift.md)).

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
re-runs pricing on **every** line, so the engine applies the compound uplift. On the graph-request Place
path, `System` prices a request only if it carries at least one line or line-attribute record (an all-delete request is priced only if the header still has lines; a request holding only the Quote
header, such as a lone `RampUpliftType` change, isn't priced); a request carrying a context id is
priced whenever the transaction has lines, and an org setting can skip pricing altogether. `System` delta
pricing, where the org has it on, may also skip lines (see [pitfalls.md](pitfalls.md)) [Platform behaviour, traced]; see the header-only rule in
[transaction-line-editor → runtime behavior](../transaction-line-editor/runtime-behavior.md). Poll `CalculationStatus`
to a settled state, then read back ([Read-back](verify-and-discover.md#read-back--the-ramp-schedule)) and
verify the compounding numerically.

> **Apex-invocable variant.** Some connectors expose clone as a CLASSIC Apex
> invocable whose args are wrapped in an `inputs` array. `lineScope` lives inside the
> Apex-defined **`options`** input (with optional `recordTypeId`), not at the top level
> (`actions-obj-deep-clone-sales-transaction.md`):
> `{ "inputs": [ { "salesTransactionId": "...", "recordIds": ["..."], "options": { "lineScope": "AllLines" } } ] }`.
> Same semantics; use whichever the transport exposes.
