# Sales Transaction (Quote) — Contracts

> ✅ VERIFIED LIVE against a Revenue Cloud R262 scratch org with the QB demo
> dataset (API v67.0). `lifecycle.py` is a direct transcription of the endpoint
> bodies, response shapes, async barriers, and sequencing rules captured here.

The quote-path lifecycle drives `opportunity_created → quote_placed → order_draft
→ order_activated → usage_upload → invoice_draft → invoice_posted`. Shared
foundations (environment, object describes, terminal-state detection, timing /
sequencing rules, permissions) live in [`contracts-shared.md`](contracts-shared.md);
this file is the per-step wire-format and gotcha record for the PST-via-Quote path.

## Lifecycle steps — endpoints, bodies, responses

Documented-first (DG = v262 dev-guide), then transcribed into `lifecycle.py` after
live verification against the target org.

### 1. Opportunity (optional head)
- **Endpoint:** `POST /services/data/v67.0/sobjects/Opportunity`
- **Body:** `{ Name, AccountId, StageName, CloseDate }` (StageName from discovery).
- **Response:** `{ id, success, errors }` (standard sObject create). VERIFIED shape (standard REST).
- **Async:** none (synchronous).

### 2. Quote — Place Sales Transaction (PST) — ✅ VERIFIED LIVE
- **Endpoint (PRIMARY, works):** `POST /services/data/v67.0/connect/rev/sales-transaction/actions/place`
- **Body:** graph shape (the **documented** form, not the simplified Postman shape).
  Minimal working quote-create payload verified live:
  ```json
  {
    "pricingPref": "System",
    "taxPref": "Skip",
    "graph": {
      "graphId": "createQuote",
      "records": [
        { "referenceId": "refQuote",
          "record": { "attributes": {"method":"POST","type":"Quote"},
                      "Name": "<name>",
                      "QuoteAccountId": "<accountId>",
                      "Pricebook2Id": "<standardPbId>" } },
        { "referenceId": "refQuoteLine0",
          "record": { "attributes": {"type":"QuoteLineItem","method":"POST"},
                      "QuoteId": "@{refQuote.id}",
                      "Product2Id": "<prodId>",
                      "PricebookEntryId": "<pbeId>",
                      "Quantity": "1",
                      "StartDate": "<ISO>", "EndDate": "<ISO>" } }
      ]
    }
  }
  ```
- **Response:** `{ isSuccess, salesTransactionId, errorResponse:[ {errorCode,message,referenceId} ], contextDetails }`.
  On success `salesTransactionId` = the **Quote id** (`0Q0…`), `errorResponse:[]`.
- **Async:** synchronous (response carries the result directly; no polling needed for place).
- **GOTCHAS (verified live, all important):**
  1. **`AccountId` is NOT writable** on the Quote graph record (`createable:false`).
     Use **`QuoteAccountId`** (writable) instead — confirmed by describe. `AccountId`
     is derived (from linked Opportunity or QuoteAccountId). Without an account the
     quote places but downstream `createOrderFromQuote` fails "Select an account".
  2. **Do NOT send `ProductSellingModelId` on QuoteLineItem** — FLS error
     "You do not have the access on field QuoteLineItem : ProductSellingModelId."
     The selling model is carried by the PricebookEntry / dates, not this field.
  3. **Term/subscription products need `StartDate` + `EndDate`** (or Subscription
     Term + unit) on the line, else `END_DATE_MISSING`.
  4. **PST commits the Quote header even when `isSuccess:false`** — a failed place
     left a real orphan Quote with a populated `salesTransactionId`. Confirms the
     plan's "probes leave real artifacts" rule → probe quotes must be tagged and
     cleaned up.

#### Line discounts — ✅ VERIFIED LIVE (survives PST → order → posted invoice)
Set `Discount` (a standard **percent** field on QuoteLineItem, `createable:true`)
on the line record in the place graph. With `pricingPref: "System"` the engine
applies it to the derived net prices, and those flow through to the posted invoice.

Live probe (one quote, example SKU `QB-API-FLEX` @ $450, qty 2, **25%**, 1×Annual term, StartDate 2026-01-15; substitute any term-defined SKU on your standard pricebook). Re-verified `2026-06-23` on `rlm-base__jun17_1`:

| Where | Field | Value | Note |
|-------|-------|-------|------|
| QuoteLineItem | `UnitPrice` / `ListPrice` | 450 | undiscounted |
| QuoteLineItem | `NetUnitPrice` | **337.50** | 450 × 0.75 → 25% applied |
| QuoteLineItem | `NetTotalPrice` | **676.85** | discounted line total (prorated; the platform `PricingTermCount` reads back 1.0027 for a 366-day window, so net total ≈ 2 × 337.50 × 1.0027) |
| QuoteLineItem | `Discount` | **0** | ⚠ engine consumes the input; does **not** round-trip it onto this field |
| Invoice | `Status` / `TotalAmount` | Posted / matches `NetTotalPrice` | discounted amount reached the posted invoice |
| InvoiceLine | `ChargeAmount` | matches | |

**Key gotcha:** verify a discount by the **net prices**, not by reading back
`QuoteLineItem.Discount` (it reads `0` post-place even when applied). `InvoiceLine`
has **no** `NetUnitPrice`/`Amount` columns — use `ChargeAmount`; `Invoice` has no
`NetAmount` — use `TotalAmount`.

#### Bundles — PST auto-expands default-configured bundles (✅ VERIFIED LIVE R262)

Sending one flat input line whose `Product2Id` is a **`ProductClass = 'Bundle'`**
SKU does **not** fail. PST resolves the bundle's component graph server-side and
returns a fully configured set of child `QuoteLineItem`s wired to the parent via
`ParentQuoteLineItemId`, each with its own `ProductSellingModelId`, quantity, and
list/total price. The harness's single input line places the configured bundle
end-to-end — no client-side component graph is needed.

Live probe (R262 scratch org, billing-ready account from the QB demo dataset
— `Infinitech` in QB — example bundle SKU `QB-COMPLETE`, qty 1; substitute any
default-configured bundle on your pricebook):

| Where | Result |
|-------|--------|
| Input PST graph | **1** flat line: `Product2Id = <QB-COMPLETE>` |
| Resulting `QuoteLineItem` rows | **5** — 1 Bundle root (`ParentQuoteLineItemId = null`, `TotalPrice = 0`) + 4 Simple children (`QB-DB`, `QB-API-REQT`, `QB-SRV-OG-PSH`, `QB-API-MGMT`) all linked via `ParentQuoteLineItemId = <root>` |
| `Quote.GrandTotal` | **$91,000** — sum of priced child lines |
| Downstream | `createOrderFromQuote` → activation → 7 `BillingSchedule`s → 1 Asset → Draft invoice → Posted `INV-US-06-2026-000039` |

**Caveats:**

- Only **default-configured** bundles are exercised. Bundles with mandatory slots
  requiring user choice (no default, or required attributes with no default
  value) are expected to fail at PST place — the harness has no way to express
  those choices.
- The YAML's `quantity:` / `discount_percent:` apply to the **root** line only.
  Child quantities and prices come from the bundle definition.
- One BillingSchedule is created per child component slot at activation, **not**
  one per input line. `steps.py:run_activate` derives `expected_count` from
  `count_order_items(orderId)` (a `SELECT COUNT(Id) FROM OrderItem` against the
  freshly-created order) so the BillingSchedule and Asset polls wait for the
  full bundle-expanded fan-out, not just the input-line count.
- Some bundle slots produce a `BillingSchedule` with `TotalAmount = 0` (a $0
  root slot, e.g.). No `InvoiceLine` is created against a $0 schedule, so the
  invoice-correlation poll **must** scan across all schedules in the generate
  call — picking any single id (e.g. `[0]`) risks polling the one that never
  yields a row. See *Invoice correlation* below.

#### Selling models — line date rules (✅ VERIFIED LIVE)

The line's date fields are **selling-model-dependent**, and the model is resolved
from the **PricebookEntry**, not from anything writable on the line. This drove a
real multi-line failure (`INVALID_INPUT` "You can't specify EndDate for evergreen
order products" at `createOrderFromQuote`) before the rule was encoded.

- **`PricebookEntry` binds a single `ProductSellingModelId`.** The engine resolves
  the selling model from the PBE used on the line — **not** from
  `ProductSellingModelOption.IsDefault`. To sell a product under a different model,
  use the PBE bound to that model.
- **`ProductSellingModelId` is unwritable on `QuoteLineItem` even as admin** —
  `PATCH`/place both fail FLS `INVALID_API_INPUT` / "You do not have the access on
  field QuoteLineItem : ProductSellingModelId." You cannot pin the model from the
  line; it comes from the PBE.
- **`SellingModelType` picklist = `{OneTime, TermDefined, Evergreen}`.** EndDate
  rule, verified at `createOrderFromQuote` for all three:

  | `SellingModelType` | `StartDate` | `EndDate` | Behavior |
  |--------------------|-------------|-----------|----------|
  | **TermDefined**    | safe        | **required** | rejects `END_DATE_MISSING` without it |
  | **Evergreen**      | safe        | **rejected** | `INVALID_INPUT` "can't specify EndDate for evergreen order products" |
  | **OneTime**        | safe        | **rejected** | same — only term-defined takes an EndDate |

- **Implementation:** `discovery.py` captures `ProductSellingModel.SellingModelType`
  onto each `Product`; `Product.needs_end_date` is `True` only for `TermDefined`,
  and `place_sales_transaction` sets `EndDate` on the line **only** when
  `needs_end_date`. `StartDate` is always set (safe for all three). A multi-line
  quote mixing a TermDefined and an Evergreen product was live-verified through to a
  Posted invoice (`INV-US-06-2026-000006`, order `00000118`): per-line quantities and
  discounts (QB-API-FLEX x2 @20% → NetUnitPrice 360; QB-API x1 @10% → NetUnitPrice
  1800) both survived.

#### Subscription term fields — per-line, `(count, unit)` (✅ VERIFIED LIVE — Branch A)

`PricingTerm` and `PricingTermCount` on `QuoteLineItem` are **auto-calculated**
from the PBE-bound `ProductSellingModel` and the author-input subscription
fields; the harness **must not** write them. The author-input fields are
**`SubscriptionTerm`** (int) and **`SubscriptionTermUnit`** (picklist —
`{Months, Quarterly, Semi-Annual, Annual}` per `ProductSellingModel.csv`).
`PricingTermUnit` does NOT include `Years` or `Days`; `Years` is accepted as a
config alias that maps to `Annual` and is the only alias supported.

`discovery.py` captures `ProductSellingModel.PricingTerm` and
`PricingTermUnit` onto each `Product` (alongside `selling_model_name`); the
runner resolves a per-line `Term(count, unit)` via the chain
`line override → scenario default → product.default_term → Term(12, "Months")`.
Bare-int config promotes the unit from the PSM; an explicit unit must equal
the PSM's `PricingTermUnit` (the line is bound to a PBE whose SOM already
declares one — incoherent units are rejected at plan time with both values
quoted). Multi-PBE SKUs (one SKU sold under several selling models) require an
explicit `selling_model: "<PSM Name>"` selector; the resolver fails fast with
the candidate names rather than picking arbitrarily.

`place_sales_transaction` writes (per `TermDefined` line only):

- `SubscriptionTerm` = `term.count`
- `SubscriptionTermUnit` = `term.unit`

**`EndDate` is platform-derived — the harness never writes it.** Live-verified
`2026-06-23` against `rlm-base__jun17_1` (R262): a probe sending `StartDate =
2026-01-15`, `SubscriptionTerm = 1`, `SubscriptionTermUnit = Annual`, and **no
`EndDate`** read back `EndDate = 2027-01-14`, `PricingTerm = 1`, and
`PricingTermCount = 1.0`. The platform uses an inclusive
`start + term - 1 day` convention (Jan 15 → Jan 14 next year), which is more
correct than the old harness's `start + term` (Jan 15 → Jan 15) and avoids
overlap if amendments roll forward off the same boundary.

Evergreen and OneTime lines reject any `term` config at parse time and never
write `SubscriptionTerm`/`SubscriptionTermUnit`/`EndDate` (matches the
`createOrderFromQuote` "can't specify EndDate for evergreen order products"
gate above).

#### Proration fields — `billing_frequency` and `period_boundary` (✅ VERIFIED LIVE, 2026-06-23)

When a `Product2` carries a **proration policy** (e.g. `TEST-SUB`,
`QB-LIC-CLOUD`), the line **requires both** `billing_frequency` and
`period_boundary` at place time, or PST fails fast:

```
FIELD_INTEGRITY_EXCEPTION: "When the SellingModelType is Evergreen or
Term-Defined, BillingFrequency can't be null: Billing Frequency"
```

These are **not derivable from the selling model** — they encode how
the platform should slice the billing span — so the harness writes
whatever the line config says and never auto-fills. Both `Evergreen`
and `TermDefined` lines hit this same gate when a proration policy is
attached; SKUs without a policy (e.g. `QB-API-FLEX`) place fine without
either field.

**Evergreen-only sub-rule (`period_boundary: Anniversary` required at
order creation).** An Evergreen line places fine on the quote with any
of the four boundary values, but `createOrderFromQuote` rejects
anything except `Anniversary`:

```
INVALID_INPUT: "Evergreen order products must have an Anniversary
period boundary."
```

Live-verified: `TEST-SUB` @ Evergreen Monthly with `period_boundary:
AlignToCalendar` placed (quote `0Q0WI000003LOtd0AG`) but failed
`createOrderFromQuote`; the same scenario with `period_boundary:
Anniversary` ran end-to-end to Posted `INV-US-06-2026-000086` and
generated `BillingSchedule BS-000000132` (`BillingMethod=Evergreen`,
`BillingTerm=1 Month`, `BillingPeriodAmount=$35`, `EndDate=null`,
`Status=ReadyForInvoicing`, `NextBillingDate=2026-07-23`).
`TermDefined` lines accept all four boundary values
(`AlignToCalendar`, `Anniversary`, `DayOfPeriod`, `LastDayOfPeriod`).

**Authoring rule for scenarios:** for any Evergreen SKU with a
proration policy, pin `period_boundary: Anniversary` plus a matching
`billing_frequency` (e.g. `Monthly` to match `Evergreen Monthly`).
Without both, the run fails at place (no `billing_frequency`) or at
order creation (`AlignToCalendar` on Evergreen).

#### Explicit `EndDate` override — co-term path (✅ ACCEPTED LIVE, prorates)

The harness also exposes an **opt-in** `end_date:` per-line (or scenario-
level) override. When set, the place graph writes a calendar `EndDate`
**alongside** `SubscriptionTerm` / `SubscriptionTermUnit` and the platform
honors the explicit date — recalculating `PricingTermCount` against the
actual span instead of the derived inclusive default. Concretely:

- Input: `StartDate = 2026-01-15`, `SubscriptionTerm = 1`,
  `SubscriptionTermUnit = Annual`, `EndDate = 2027-01-15` (366-day span).
- Readback (live-verified R262): `EndDate = 2027-01-15`,
  `PricingTermCount ≈ 1.0027` (i.e. 366 ÷ 365 — proration drift accepted
  for the explicit-anchor case).

This is the supported way to co-term a multi-line quote (one calendar
anchor, mixed cadences underneath) or land on a fiscal-quarter boundary.
The harness rejects the override on Evergreen / OneTime products at
config-resolve time (same rule as `EndDate`) and requires an accompanying
`term:` so `SubscriptionTerm` is still derivable for billing schedules.
See `scenarios/README.md` → *Explicit `EndDate` overrides* for the YAML
shape and unit grammar.

##### Probed edge cases (live, `rlm-base__jun17_1`, 2026-06-23)

Two ad-hoc PST probes against `QB-API-FLEX` (Term Annual PSM)
clarified what the platform actually does at the boundaries — both
matter when authoring scenarios or reading back results.

**1. `SubscriptionTermUnit` + `EndDate` *without* `SubscriptionTerm`.**
PST accepts it. The line places, `SubscriptionTerm` reads back as
`null`, and `PricingTerm` / `PricingTermCount` auto-calculate from
`StartDate + EndDate + Unit`:

| Input | StartDate | EndDate | SubTerm | SubTermUnit | PricingTerm | PricingTermCount |
|---|---|---|---|---|---|---|
| Unit+EndDate only | 2026-01-15 | 2027-01-15 | `null` | Annual | 1 | 1.0027 |

The harness still **requires** an accompanying `term:` at config time
(raises `ConfigError`): leaving `SubscriptionTerm` null at place time
leaves billing-schedule fan-out under-specified for downstream
activation/invoicing, and silent fallback to `Term(12, Months)` would
be surprising. The platform's tolerance is documented here for
completeness, not exposed as a config shape.

**2. `SubscriptionTerm` and `EndDate` *disagree*.** PST accepts every
combination tried; `EndDate` wins for the auto-calculated
`PricingTermCount` and `SubscriptionTerm` is stored verbatim with no
cross-validation:

| Input | StartDate | EndDate | SubTerm in | SubTermUnit in | SubTerm read | SubTermUnit read | PricingTerm | PricingTermCount |
|---|---|---|---|---|---|---|---|---|
| Term 2y, End 1y | 2026-01-15 | 2027-01-15 | 2 | Annual | 2 | Annual | 1 | 1.0027 |
| Term 1y, End 2y | 2026-01-15 | 2028-01-15 | 1 | Annual | 1 | Annual | 1 | 2.0027 |
| Term 6mo, End 3mo, **wrong unit** | 2026-01-15 | 2026-04-15 | 6 | **Months** | 6 | **Annual** ⚠ | 1 | 0.2493 |

Implications:

- **`EndDate` wins the pricing math.** Pricing is computed as
  `(EndDate − StartDate) / 365` days irrespective of the
  `SubscriptionTerm` value sent in. Treat `EndDate` as the source of
  truth for what the customer will be billed against; treat
  `SubscriptionTerm` as an informational cadence marker (and the
  input billing-schedules read).
- **`SubscriptionTerm` is not validated against the date span.**
  Sending `Term=2, End=1y` does *not* error; the line places with
  `SubscriptionTerm=2` stored but `PricingTermCount=1.0027`. Authors
  who care about both fields agreeing must keep them consistent in
  config (the harness's `end_date.resolve()` is the place to do this).
- **`SubscriptionTermUnit` can be silently coerced.** Row 3 sent
  `Months`; the platform stored `Annual` — apparently snapping to the
  PBE's PSM unit when the input conflicts. The harness's existing
  unit-vs-PSM consistency guard (`runner._resolve_term` raises on
  mismatch) protects against this silently happening through the
  normal config path.

Both probes were against `QB-API-FLEX` (Term Annual SOM) on
`rlm-base__jun17_1` (R262); replicate on a Quarterly / Semi-Annual SOM
before generalizing the "EndDate wins" wording beyond Annual.

#### BillingSchedule fan-out across `end_date` scenarios (✅ VERIFIED LIVE, `rlm-base__jun17_1`, 2026-06-23)

Activated all 9 scenarios from `scenarios/14-end-date-overrides.yaml`
(run `DEMO-20260623T142853Z`, orders 00000156–00000164) and read back
the resulting `BillingSchedule` rows. Key findings:

| # | SKU / PSM | Start → End | Span (d) | Qty | UnitPrice | BillingPeriodAmount | TotalAmount | BillingTerm / Unit |
|---|-----------|-------------|----------|-----|-----------|---------------------|-------------|--------------------|
| 1 | QB-API-FLEX / Annual | 2026-04-01 → 2029-03-31 | 1095 | 1 | 450 | 450 | 1350.00 | 1 Year |
| 2 | QB-API-FLEX / Annual (leap) | 2028-02-29 → 2029-02-28 | 365 | 1 | 450 | 450 | 451.23 | 1 Year |
| 3 | QB-API / Monthly (Aug 31 +1mo) | 2026-08-31 → 2026-09-30 | 30 | 1 | 1500 | 1500 | 1548.39 | 1 Month |
| 4 | QB-API / Monthly (Jan 31 +1mo) | 2027-01-31 → 2027-02-28 | 28 | 1 | 1500 | 1500 | 1548.39 | 1 Month |
| 5 | QB-API / Monthly (90d ramp) | 2026-07-01 → 2026-09-29 | 90 | 1 | 1500 | 1500 | 4450.00 | 1 Month |
| 6 | QB-API / Monthly (3q) | 2026-05-15 → 2027-02-15 | 276 | 1 | 1500 | 1500 | 13553.57 | 1 Month |
| 7 | QB-API-FLEX / Annual (co-term, qty 3) | 2026-06-15 → 2027-12-31 | 564 | 3 | 450 | 1350 | 2087.70 | 1 Year |
| 8 | QB-API-FLEX / Annual (730d) | 2026-10-07 → 2028-10-06 | 730 | 1 | 450 | 450 | 900.00 | 1 Year |
| 9 | QB-API-FLEX / Annual (per-line override) | 2026-09-15 → 2027-06-30 | 288 | 2 | 450 | 900 | 712.60 | 1 Year |

Every schedule: `Status=ReadyForInvoicing`, `BillingType=Advance`,
`BillingTerm=1` (Year for Annual SOMs, Month for Monthly SOMs),
`PricingTermUnit` = PSM unit.

Implications for the harness:

- **One BillingSchedule row per OrderItem at activation.** The 3-year
  Annual deal (#1) is *not* fanned out into three rows at activation
  time — it's a single row spanning the full deal with
  `TotalAmount = 1350` and `BillingPeriodAmount = 450`. Periodic
  fan-out happens lazily through `NextBillingDate` advancing as
  invoices post; the activation-time view is one row regardless of
  span.
- **`BillingTerm` is the *period* length, not the *deal* length.**
  Always `1`, with `BillingTermUnit` taking the PSM's cadence
  (`Year` / `Month`). The deal length lives in
  `BillingScheduleStartDate` → `BillingScheduleEndDate`.
- **`TotalAmount` is prorated against the actual day span** — same
  365-day math as `PricingTermCount` (above), not derived from
  `SubscriptionTerm`. So `EndDate` continues to be the source of
  truth into the billing layer: scenario #2's leap-year span
  (366 days) bills `451.23 ≈ 450 × (366/365)`; scenario #8's exact
  2-year span (730 days) bills `900 = 450 × 2` with no drift.
- **`Quantity` multiplies `BillingPeriodAmount`, not `UnitPrice`.**
  Scenarios #7 (qty 3) and #9 (qty 2) keep `UnitPrice=450` and lift
  the period amount to `1350` / `900` respectively. `TotalAmount`
  layers proration on top of that.
- **Monthly-Advance short-span schedules over-bill the period
  amount.** Scenarios #3 (30-day Sep) and #4 (28-day Feb) both
  produced `TotalAmount = 1548.39` against a `BillingPeriodAmount =
  1500` — i.e. the engine prorated *up* even though the span was
  ≤ one "period" by `BillingTermUnit`. The matching 1548.39 across
  30- and 28-day spans suggests a fixed internal day denominator
  (~30.97) rather than calendar-month days. This is not yet characterized;
  do not generalize Monthly proration math until it is probed against a wider
  span set (e.g. true 31-day month, 60-day span).

Per-line `end_date` override path (scenario #9) only emitted one
`OrderItem` for the qty-2 line. The qty-1 line that pinned its own
`"6mo"` offset wasn't drawn — the `products:` pool randomizes per
transaction, so a `count: 1` scenario does not always exercise both
lines. To live-verify per-line `end_date:` override on the same
quote, run scenario #9 with `count: 3+` until both SKUs land.

Open questions raised by this run (Monthly proration denominator,
Quarterly / Semi-Annual fan-out, per-line override coverage) are
tracked in [`followups.md`](followups.md) → *Billing & invoicing*.

### 3. Order — Create Order from Quote — ✅ VERIFIED LIVE
- **Endpoint (PRIMARY, works):** `POST /services/data/v67.0/actions/standard/createOrderFromQuote`
- **Body:** `{ "inputs": [ { "quoteRecordId": "<quoteId>" } ] }`
- **Response:** an **array**; `[0].isSuccess`, `[0].outputValues.orderId` (`801…`),
  `[0].outputValues.orderNumber`, `[0].errors`. Synchronous.
- **GOTCHA:** the source Quote **must have an account** (`QuoteAccountId`), else
  `[0].errors[0]` = `REQUIRED_FIELD_MISSING` "Select an account."

### 4. Activate Order — ✅ VERIFIED LIVE (mechanism corrected)
- **The documented/Postman `POST .../connect/revenue-management/orders/actions/activate`
  endpoint returns `NOT_FOUND` on this org** (v67.0) — it is NOT the activation route
  here. (Also confirmed `connect/revenue-management` namespace is not resolvable.)
- **Working mechanism:** plain sObject update —
  `PATCH /services/data/v67.0/sobjects/Order/<id>` body `{ "Status": "Activated" }`.
  `Order.Status` picklist is just `["Draft","Activated"]`. This matches how the
  robot E2E suite activates (UI click → poll `Status == Activated`).
- **PRECONDITION (verified + RESOLVED):** activation fails `FAILED_ACTIVATION`
  "Enter the shipping address associated with the account" if the **Order** has no
  shipping address. `createOrderFromQuote` does **not** copy the account's shipping
  address to the order (order ShippingStreet/City/... came back null even though
  the source account had a populated ShippingAddress). **Fix:** before activating, `PATCH` the order
  with `ShippingStreet/ShippingCity/ShippingState/ShippingPostalCode/ShippingCountry`
  (copied from the account). After that, activation succeeds.
- **`PATCH` returns 204 No Content (empty body) on success** — the client must treat
  an empty 2xx body as success, not try to JSON-parse it.
- **RESOLVED — activation auto-generates BillingSchedule AND Asset** (no explicit
  step 5 needed for QB products):
  - `BillingSchedule`: 1 row, `Status=ReadyForInvoicing`, `ReferenceEntityId=<orderId>`,
    `BillingAccountId=<acct>`, `TotalAmount=450`. Poll by `ReferenceEntityId`.
  - `Asset`: no direct order FK, but a deterministic one-hop linkage via
    `AssetActionSource` (see §4d "Asset attribution" below). Poll
    `AssetActionSource.ReferenceEntityItemId IN (SELECT Id FROM OrderItem
    WHERE OrderId = '<orderId>')` filtered to
    `AssetAction.CategoryEnum = 'Initial Sale'`. **Bundle case** (live-verified
    2026-06-23 against a Revenue Cloud R262 scratch org): the example
    `QB-COMPLETE` bundle activates into **5 component assets** (one per
    component OrderItem); the AssetActionSource query returns all 5 in one
    pass. Every Revenue Cloud activation produces LMA assets, so the AAS
    path is the complete attribution picture — no non-LMA escape hatch.
- **Harness checkpoint rule:** `reached_stage = "order_activated"` means the activation
  PATCH succeeded and the derived BillingSchedule + Asset barriers have completed
  (or asset polling returned its explicit warning status). If either poll raises,
  the manifest remains at the prior public stage so retry/resume re-enters
  activation instead of skipping the derived-record gates.

### 4b. Usage consumption — TransactionJournal create (sObject Collections) — ⚠ DOCUMENTED, NEEDS LIVE VERIFICATION

Bound to `unpackaged/post_utils/classes/RLM_UsageUploaderController.cls` (the
canonical in-org TJ writer) and the v262 `TransactionJournal` /
`ProductUsageResource` field docs under `docs/salesforce/262/dev-guide/`.
**Live verification against a scratch org with the QB rating dataset loaded
(`insert_qb_rating_data`) is required before merging behavioral changes here.**

- **Endpoint:** `POST /services/data/v67.0/composite/sobjects`
- **Body (verified shape — chunked at 200 records per call):**
  ```json
  {
    "allOrNone": true,
    "records": [
      {
        "attributes": {"type": "TransactionJournal"},
        "ReferenceRecordId": "<assetId>",
        "AccountId": "<accountId>",
        "UsageResourceId": "<usageResourceId>",
        "QuantityUnitOfMeasureId": "<unitOfMeasureId>",
        "Quantity": 123.45,
        "ActivityDate": "2026-06-22",
        "StartDate": "2026-06-22",
        "EndDate":   "2026-06-22",
        "UsageType": "UsageManagement",
        "Status":    "Pending",
        "UniqueIdentifier": "txn-harness-<run_id>-<assetId>-<targetIdx>-<rowIdx>"
      }
    ]
  }
  ```
- **Response:** standard sObject Collections `[{success, id, errors}, …]` per
  input record.
- **Tag column is `UniqueIdentifier`, NOT `Description`.** `TransactionJournal`
  has no `Description` field per the v262 dev guide. `UniqueIdentifier` is
  `Create+Filter+idLookup`, which is exactly what the harness needs for
  idempotent retry and bulk cleanup (`WHERE UniqueIdentifier LIKE
  'txn-harness-%'`).
- **`UsageType` picklist value used: `UsageManagement`.** Matches
  `RLM_UsageUploaderController.cls` (`buildTransactionJournal`).
- **`Status = Pending` on create.** Becomes `Processed` after the rating job
  completes; that is the verification signal that rating ran end-to-end.
- **`ActivityDate`, `StartDate`, `EndDate` are all set to the same day** for
  single-day usage rows (the QB demo shape). `days_back` spreads
  `ActivityDate` across the last N days but each row still uses one calendar
  day for all three.
- **Idempotent retry contract (lifecycle-side):** before posting, the harness
  pre-queries `SELECT Id, UniqueIdentifier FROM TransactionJournal WHERE
  UniqueIdentifier IN (…)` for the expected ids, excludes already-present
  rows from the POST, and returns `existing_ids ∪ new_ids`. A retry under
  the same `run_id` converges on the complete TJ id set whether the prior
  attempt wrote zero, some, or all rows.
- **Partial-failure isolation:** `allOrNone: true` per chunk. A bad row
  aborts the chunk; the harness raises `LifecycleError("usage", …)` and the
  manifest records zero new ids for that chunk so the retry can reuse the
  same `UniqueIdentifier`s.
- **TODO live-verify on a scratch org:** end-to-end run of
  `scenarios/12-usage-consumption.yaml`, then `SELECT COUNT(Id), Status FROM
  TransactionJournal WHERE UniqueIdentifier LIKE 'txn-harness-%' GROUP BY
  Status` showing the expected `Pending` count before rating and `Processed`
  count after `cli rate`.

### 4c. ProductUsageResource discovery SOQL — ⚠ DOCUMENTED, NEEDS LIVE VERIFICATION

Bound to the v262 `ProductUsageResource` field doc and the seed CSV at
`datasets/sfdmu/qb/en-US/qb-rating/ProductUsageResource.csv`. Live-verify
the binding count against the QB seed once `insert_qb_rating_data` runs.

```sql
SELECT ProductId,
       UsageResourceId,
       UsageResource.Code,
       UsageResource.Name,
       UsageResource.UnitOfMeasureClassId,
       UsageResource.DefaultUnitOfMeasureId,
       UsageResource.DefaultUnitOfMeasure.UnitCode,
       UsageResource.DefaultUnitOfMeasure.Name,
       Status
FROM ProductUsageResource
WHERE ProductId IN (…)
```

- **FK is `ProductId`** (relationship to `Product2`), NOT `Product2Id` — the
  field doc and the seed CSV's `Product.StockKeepingUnit` matcher both
  confirm.
- **User-facing identifier is `UsageResource.Code`** (e.g. `UR-CPUTIME`,
  `UR-DATASTORAGE`, `QB-TOKEN`), not `Name`. The QB seed CSV keys on Code.
- **Do NOT filter by `Status`.** The QB seed loads bindings as `Draft` (per
  `ProductUsageResource.csv`); filtering on `Active` would surface zero
  bindings against the seeded org. If a future pass adds a status filter,
  make it `IN ('Draft','Active')`.
- **Override path (`usage.unit_of_measure` in the YAML):** when a scenario
  pins a UoM code, resolve it via `SELECT Id FROM UnitOfMeasure WHERE
  UnitCode = :code AND UnitOfMeasureClassId = :binding.uom_class_id AND
  Status = 'Active'`. The class-id constraint mirrors
  `RLM_UsageUploaderController.cls:240` — a UoM is only valid against the
  resource if it shares the resource's class.

### 4d. Asset attribution — ✅ VERIFIED LIVE R262 (deterministic via AssetActionSource)

`Asset` has no direct `OrderId`/`OrderItemId` FK, so naive correlation by
account + product + a `CreatedDate >= since` window (the prior approach)
**fails on two real cases**:

1. **Bundles** — a one-line input like `QB-COMPLETE` expands server-side
   into N component OrderItems with different `Product2Id`s. A query keyed
   on the input line's `Product2Id` misses every component asset.
   Live-verified: the example `QB-COMPLETE` bundle produced **5** assets;
   the old account+product+window poll returned **1**.
2. **Concurrency / replay** — peer scenarios on the same account+product
   within the same window were indistinguishable; the old code used a
   process-global claim set to dedupe, but the *first* poller greedy-claimed
   every visible row, leaving peers with empty `asset_ids`.

The data model exposes a one-hop deterministic linkage:

```
Order ─< OrderItem ─< AssetActionSource ─> AssetAction ─> Asset
```

`AssetActionSource.ReferenceEntityItemId` is a polymorphic lookup that, on
the activation event, points at the OrderItem. `AssetAction.CategoryEnum`
distinguishes the activation row (`'Initial Sale'`) from later
amendments/renewals/cancellations on the same OrderItem.

**Locked correlation query (poll_assets):**

```sql
SELECT AssetAction.AssetId
FROM   AssetActionSource
WHERE  ReferenceEntityItemId IN (SELECT Id FROM OrderItem WHERE OrderId = '<orderId>')
  AND  AssetAction.CategoryEnum = 'Initial Sale'
```

**Convergence (no `expected_count` parameter):** assets and bundle
components can land staggered, and `AssetActionSource` writes lag the Asset
write by up to ~1s (live-measured: Asset created 01:28:44, AAS created
01:28:45 on rlm-base scratch org 2026-06-23). The poll returns when the
row count is stable across two consecutive ticks with count ≥ 1, then
extracts ids from the nested subquery envelope
(`row["AssetAction"]["AssetId"]`).

**LMA invariant.** `AssetActionSource` is populated for assets with
`HasLifecycleManagement = true` (Lifecycle-Managed Assets). Every asset
produced via Revenue Cloud activation is LMA, so the AAS path is the
complete picture for this harness — there is no non-LMA escape hatch to
worry about. An empty result therefore only means the AAS write hasn't
landed yet (covered by the stable-count poll) or activation itself didn't
produce assets (a contract violation worth investigating upstream, not a
soft-fail to swallow).

**Bonus correlation (unused — recorded for reference):**
`AsyncOperationTracker` rows with `JobType = 'AssetizationAsyncJob'` carry
`ReferenceEntityId = <orderId>` and reach `Completed` once activation
finishes. Useful as a completion signal, but redundant with the AAS poll
which already converges on row stability.

### 4d.1. Asset → Product2 map (lookup helper)

```sql
SELECT Id, Product2Id FROM Asset WHERE Id IN (…)
```

- Used by the `usage_upload` step to pair each `LineItem` to the correct
  activated Asset by `Product2Id`. `poll_assets` returns ids in
  `AssetActionSource` row order, not input-line order, so a mixed-SKU
  scenario must NOT pair by list index.
- Duplicate-SKU lines (the same Product2 used on two lines) consume the
  asset pool **1:1 in order** (`steps.run_usage` pops the candidate list)
  so each TJ batch lands on a distinct asset.

### 5. Billing Schedule create — ✅ NOT NEEDED for QB (activation auto-generates)
- Verified: activating the order produced a `BillingSchedule` (Status
  `ReadyForInvoicing`) automatically. The explicit create endpoint is a fallback
  only for products/orgs that don't auto-generate; not exercised in the happy path.
- Fallback endpoint (unverified): `POST /services/data/v67.0/commerce/invoicing/billing-schedules/actions/create`
  body `{ billingTransactionIds: [ <orderId> ] }`.

### 6. Invoice generate → post — ✅ VERIFIED LIVE (full chain to Posted)
- **Generate (PRIMARY, works):** `POST /services/data/v67.0/commerce/invoicing/invoices/collection/actions/generate`
  - **Body (verified):** `{ "billingScheduleIds": ["<bsId>"], "action": "Draft", "invoiceDate": "<ISO>", "targetDate": "<ISO>", "correlationId": "<runId>" }`
  - **Response (verified):** `{ requestIdentifier, success, errors }` — **NO `statusURL`**
    (confirms the plan's "cannot assume a tracker URL" finding for *generate*).
- **Post (PRIMARY, works):** `POST /services/data/v67.0/commerce/invoicing/invoices/collection/actions/post`
  - **Body (verified):** `{ "invoiceIds": ["<invId>"], "correlationId": "<runId>" }`
  - **Response (verified):** `{ requestIdentifier, success, errors, statusURL }` —
    **post DOES return `statusURL`** → `/services/data/v67.0/sobjects/AsyncOperationTracker/<id>`.
    ⚠️ **Asymmetry:** generate has no statusURL, post does. Note the capitalization
    is **`statusURL`** (not `statusUrl`).
- **Result (verified):** invoice reached `Posted`, got `InvoiceNumber`
  (`INV-US-06-2026-000001`), `TotalAmount=450`.

#### Invoice correlation — RESOLVED (deterministic; no recency heuristic needed)

`Invoice.ReferenceEntityId` is **null on freshly generated** invoices (the billing
engine does not stamp it for billing-schedule-generated invoices), so the plan's
poll-by-orderId returns 0 rows *as generated*. Investigated three correlation paths
live — all verified on a Revenue Cloud R262 scratch org:

1. **PRIMARY — `InvoiceLine.BillingScheduleId` back-link (deterministic, zero extra writes).**
   We already hold the `billingScheduleId`(s) we passed to `generate`. `InvoiceLine`
   carries **`BillingScheduleId`** (→ BillingSchedule) and exposes the parent via
   `Invoice.*`. Verified query — use `IN (…)` across **every** schedule submitted
   to that generate call, not just one:
   ```sql
   SELECT InvoiceId, Invoice.Status, Invoice.InvoiceNumber
   FROM   InvoiceLine
   WHERE  BillingScheduleId IN ('<bs1>', '<bs2>', ...)
   ```
   → returns the exact invoice. All submitted schedules land on a **single
   Invoice** (single-invoice per generate, verified), so the first row with a
   non-null `InvoiceId` wins. **This is the locked correlation for generate.** No
   account+recency guessing; survives concurrent runs against the same account.
   (`InvoiceLine` also has `ReferenceEntityItemId` → OrderItem/QuoteLineItem and
   `BillingScheduleGroupId` as secondary keys.)

   ⚠ **Do not poll a single `BillingScheduleId =`.** Bundles activate into one
   schedule per child slot; zero-amount slots (e.g. a $0 bundle root) produce
   **no** `InvoiceLine`, so the invoice is real but the single-id query hangs
   until timeout. Live-verified: a default-configured bundle (example:
   `QB-COMPLETE`) activated into 7 schedules; the first was `TotalAmount = 0`
   and yielded no InvoiceLine, but the $91,000 invoice was visible
   immediately via the other six.

2. **`Invoice.ReferenceEntityId` is `updateable=true` → we can stamp it ourselves,
   but ONLY once Posted (Draft rejects it).**
   Verified: `PATCH /sobjects/Invoice/<id> {"ReferenceEntityId":"<orderId>"}` (Order
   is in its `referenceTo`) succeeds (204) on a **Posted** invoice, and **`Invoice
   WHERE ReferenceEntityId = '<orderId>'` then returns the row** — i.e. we can *make*
   order-id lookup work by writing the FK.
   The same PATCH on a **Draft** invoice is **rejected** — HTTP 400
   `INVALID_FIELD_FOR_INSERT_UPDATE` *"Can't change this field's value on Draft
   invoices."* The successful observed write was on an already-Posted invoice.
   So this link must be written **after** `invoice_posted`, not during draft
   tagging.
   The tool splits this out: `tag_invoice` (Description, at draft time) vs.
   `link_invoice_to_order` (ReferenceEntityId, after post). It is purely cosmetic —
   correlation already works via `InvoiceLine.BillingScheduleId` (path 1).

3. **`Invoice.Description` is `updateable=true` and writable even after Posted.**
   Verified: `PATCH {"Description":"DEMO-<run_id>"}` on a **Posted** invoice
   succeeded (`IsInvoiceLocked=false`). So the `run_id` pseudo-tag can be stamped at
   draft time and survives posting → bulk cleanup via
   `... WHERE Description LIKE 'DEMO-%'` works for invoices too.

Dead ends (do not rely on):
- **`Invoice.CorrelationIdentifier`** — the `correlationId` passed to generate/post
  is **NOT** persisted here (came back null), and the field is `create=F update=F`
  (read-only), so we can neither read our id from it nor write it. It is **not** a
  usable correlation carrier despite the promising name.
- **Post `statusURL` → AsyncOperationTracker** *(JobType `InvoiceDraftToPosted`)*
  exists and reaches `Status=Completed`, **but** its `CorrelationIdentifier`,
  `ReferenceEntityId`, `Request`, and `Response` all came back **null** — it is a
  completion *signal* only, carrying no invoice id or correlation. Use it to confirm
  post finished; do not expect to read the invoice id back from it.
- **Generate emits NO AsyncOperationTracker** at all (only post, context, and
  assetization jobs appeared) — so there is no generate tracker to query.

#### Locked correlation strategy
- **generate** → poll `InvoiceLine.BillingScheduleId IN (<all submitted bsIds>)`
  for the InvoiceId (deterministic; works for both single-line and bundle cases —
  see the warning above about single-id polls hanging on $0 bundle slots). Then
  PATCH the invoice's `Description = DEMO-<run_id>` (writable on Draft; survives
  posting). Do **not** PATCH `ReferenceEntityId` here — Draft rejects it.
- **post** → we already hold the invoice id; confirm completion via the returned
  `statusURL` AsyncOperationTracker reaching `Completed` (fallback: poll
  `Invoice.Status = Posted`). **`InvoiceNumber` is assigned at post time — it is
  `null` while Draft**, so read it back after post completes (the manifest's
  human-readable invoice number comes from here, not from generate). Then PATCH
  `ReferenceEntityId = <orderId>` for natural org linkage (Posted-only; cosmetic).
  Because this final PATCH is not required for invoice correctness, the harness
  records `invoice_order_link_status = "failed"` on patch failure instead of
  replaying a completed post.
- **assets** → deterministic via `AssetActionSource` (see §4d). The
  `AsyncOperationTracker` row with `JobType='AssetizationAsyncJob'` and
  `ReferenceEntityId = <orderId>` is a redundant completion signal; the AAS
  poll already converges on row stability without it.

#### Timing observed (single record, indicative only)
- PST place, createOrderFromQuote, Order Status PATCH: effectively synchronous.
- Invoice **generate** is async: invoice row was **not** present at +5s, **was**
  present (Draft) by ~+15s. Post→Posted within ~+12s.
- Both invoice steps need **poll-with-backoff**; do not assume the row exists
  immediately after a `success:true` generate response.
