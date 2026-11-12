# Billing Setup — Measured on 264

Read this before placing billing fields headlessly or quoting a measured claim from
[SKILL.md](SKILL.md). Each row says what was run; don't widen it.

**Scope.** One scratch org built from this repo (QuantumBit data, release 264, API v68.0),
2026-11-10. Quote lines only: no order was created or activated, and nothing was invoiced.
Lines were placed with Place Sales Transaction
(`POST /services/data/v68.0/connect/rev/sales-transaction/actions/place`,
`configurationMethod: Skip`) on the Standard Price Book. Products:

| Line | Selling model |
|---|---|
| `QB-API` | Evergreen, Months |
| `QB-API-PROD` | Term Defined, Annual |
| `QB-SRV-SOW`, `QB-SRV-IMP`, `QB-TRN-FUND` | One Time |

All five products had *Billing Policy - Advance*. The test quotes were deleted afterwards.

M11 is from a second scratch org (release 264, API v68.0, 2026-11-12) built from this repo with
another catalog loaded. Its quote was placed with Place Sales Transaction, `configurationMethod:
Force` with configuration rules on (`executeConfigurationRules: true`), as a bundle: the
one-time service lines were components of a Term Defined root (`QuoteLineRelationship` to the
root line).

## Results

| Row | What was placed | Result |
|---|---|---|
| M1 | A new quote with the Evergreen and the Term Defined line, neither with `BillingFrequency` | Refused on the Term Defined line: *"When the SellingModelType is Evergreen or Term-Defined, BillingFrequency can't be null"*. An earlier request without `PeriodBoundary` on that line was refused first: *"Enter a start proration period with one of these values: AlignToCalendar, Anniversary, DayOfPeriod, or LastDayOfPeriod."* That refused request still created an empty quote header |
| M2 | Evergreen Months line with Monthly, Term Defined Annual line with Annual (both with `PeriodBoundary` Anniversary), one-time line with none; no `BillingTreatmentId` on any line; every treatment in the org had Change Billing Frequency (M10) | Accepted. `BillingTreatmentId` stayed null on every line |
| M3 | PATCH the Term Defined Annual line to Monthly (the same PATCH also set `SubscriptionTerm` to 1, which left the end date and total unchanged) | Without a treatment: refused, *"Add a Billing Treatment to make sure that you can change the Billing Frequency of its related Quote Line Item, and try again."* With `BillingTreatmentId` = *Billing Treatment - USA - Advance* (active, Change Billing Frequency selected): accepted |
| M4 | A one-time line with Monthly and that same treatment | Refused: *"When the SellingModelType is One Time, BillingFrequency must be null or milestone plan"* |
| M5 | With `configurationMethod: Skip` (see Scope): a one-time line with `MilestonePlan` and *Milestone Billing Treatment* in `BillingTreatmentId`; and a PATCH giving an existing one-time line that treatment with no frequency | Both accepted. M11 is a shape where the frequency wasn't kept |
| M6 | PATCH the Term Defined line to Milestone Plan with *Milestone Billing Treatment* | Refused: *"When the SellingModelType is Termed, BillingFrequency can't be Milestone Plan"* |
| M7 | (read back after M2 and M5) | `BillingTerm` was 1 on every line, one-time lines included |
| M8 | `SubscriptionTerm: 12` on the Term Defined Annual line | End date 2038-11-30 from a 2026-12-01 start, total 12 × 3,240. The term counts the selling model's pricing term unit (years here), not months |
| M9 | Describe of the transaction and billing objects | `QuoteLineItem.BillingFrequency`, `OrderItem.BillingFrequency2` and `AssetStatePeriod.BillingFrequency`, each labelled Billing Frequency, API values `MilestonePlan` (label Milestone Plan), `Weekly`, `Monthly`, `Quarterly`, `Semi-Annual`, `Annual`; `Asset` has no billing frequency field. `BillingTerm` (label Billing Term) on the quote line, order product and asset action source. `QuoteLineItem.ProductSellingModelId` is read-only (Place refused it; the price book entry sets it). `Order.PaymentTermId`, `BillingAccount.PaymentTermId` and `BillingScheduleGroup.PaymentTermId` exist; `Quote` has no standard payment-term field, only the repo's `RLM_Payment_Terms__c` |
| M10 | Org state after a full build | Active: `RLM_Order_to_Billing_Schedule_Flow`. Inactive: the standard `o2bsflows` (*Order To Billing Schedule Flow*). Three active policies, 15 active treatments (all with Change Billing Frequency), two active payment terms, no billing milestone plans |
| M11 | One-time service lines as components of a bundle, each with `MilestonePlan` and *Milestone Billing Treatment* in `BillingTreatmentId`, placed with `configurationMethod: Force` and configuration rules on (second org, see Scope) | Place returned success, but `BillingFrequency` was stored blank on those lines; `BillingTreatmentId` was kept. Read the frequency back after placing; a success response doesn't mean it was kept. The save check refuses Milestone Plan on non-One-Time lines and accepts a treatment with a blank frequency, so it neither explains nor rules out a silent drop; cause not established [Platform behaviour, traced in part] |

M2 and M3 together narrow a statement in the qb-billing README, which says a Term Defined
line needs an explicit `BillingTreatmentId` with Change Billing Frequency
[Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`]. In M2 a line whose frequency
matched its pricing term was accepted without one; the treatment was needed only to differ
(M3). Only these two frequency-to-model pairs were run, and every treatment in the org had
Change Billing Frequency selected (M10), so M2 says nothing about the README's flag-off case.

## Test

Repeat this for the frequencies a plan promises, on the route the demo will use:

1. Find a price book entry per selling model:
   `SELECT Id, Product2Id, ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit FROM PricebookEntry WHERE IsActive = true AND Product2.StockKeepingUnit IN (...)`.
2. Place a quote named `Skill test …` with one `QuoteLineItem` per line: `Product2Id`,
   `PricebookEntryId`, `Quantity`, `UnitPrice`, `StartDate`; for Term Defined and Evergreen
   lines `BillingFrequency` and `PeriodBoundary` (as in M2); and for Term Defined lines
   `SubscriptionTerm` (in pricing term units, M8). Leave
   `ProductSellingModelId` and `AccountId` out; Place refused both as not writable.
3. Read back `BillingFrequency`, `BillingTreatmentId`, `BillingTerm`, `PeriodBoundary`,
   `EndDate` and `TotalPrice`.
4. To prove billing, create the order, activate it, and read `BillingScheduleGroup`
   (`BillingTermUnit`, `BillingTreatmentId`, `PaymentTermId`) and the first invoice. The
   invoice steps are in `rlm-business-apis` → `backdated-asset-lifecycle.md`.
5. Delete the test quote (and order) when done, including empty quotes left by refused
   placements (M1).

## Open: measure before promising

- Whether `createOrdersFromQuote` copies the quote line's `BillingFrequency`,
  `BillingTreatmentId`, `BillingTerm` and period boundary to the order product, and how the
  asset state period gets its frequency.
- Whether the UI defaults `BillingFrequency` from the selling model when a rep adds a line.
  The API didn't (M1).
- `MilestonePlan` on an Evergreen line.
- `MilestonePlan` on a one-time line whose milestone treatment comes only from the product's
  billing policy, with no `BillingTreatmentId` on the line.
- An Evergreen line placed without `PeriodBoundary`.
- A line whose frequency matches its pricing term, when the product's policy treatments have
  Change Billing Frequency off.
- A one-time line with a milestone treatment and no frequency (accepted in M5, and what M11
  left on bundle components): the source says activation builds the plan from the treatment
  alone [Platform behaviour, traced]; not yet confirmed on a live org.
- A route that keeps `MilestonePlan` on a bundle component placed with configuration Force
  (M11): a later PATCH with configuration Skip, or the same placement with rules off.
- A service added by an amendment (a new product on the amendment order, not a change to an
  existing asset) carrying a milestone treatment: does activating the amendment order create
  a billing milestone plan for it, with `enableMilestoneBillingForAmend` on (as the repo
  ships) and off? With the setting off the source gives no plan for an amendment schedule
  [Platform behaviour, traced]; the on case for an added line is unread. Read its `BillingSchedule.Category`, `BillingMilestonePlanId` and billing
  schedule group [Dev guide: `sforce_api_objects_billingschedule`]. Also: does a plan made by
  hand for that order product or quote line link to its billing schedule?
- An approved Net 60 quote through order and invoice: which due date the invoice gets.
- With a billing profile on the account and a payment term on the order, which one the
  invoice uses outside billing arrangements.
- How the shipped approval treats a quote whose `RLM_Payment_Terms__c` is blank.
