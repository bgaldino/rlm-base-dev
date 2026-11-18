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
Force` with configuration rules on (`configurationPref.configurationOptions.executeConfigurationRules:
true`), as a bundle: the
one-time service lines were components of a Term Defined root (`QuoteLineRelationship` to the
root line).

Items tagged `[Measured: 2026-11-12 ...]` in this file and in SKILL.md come from a third scratch org
(release 264, API v68.0) built from this repo with another catalog loaded: a bundle quote placed
with configuration method Force and configuration rules on, its one-time service lines then PATCHed with configuration Skip, ordered
and activated, and later amendments of that contract ordered and activated (two of them adding milestone-billed service quantity).

M12–M15 come from three more scratch orgs (release 264, API v68.0, 2026-11-16 to 2026-11-18)
built from this repo with another catalog loaded: billing policies and treatments loaded by
data plan, orders ordered and activated (one starting in the future, one starting the day it
was placed), and a DRO fulfillment plan run on each. No invoice was run.

## Results

| Row | What was placed | Result |
|---|---|---|
| M1 | A new quote with the Evergreen and the Term Defined line, neither with `BillingFrequency` | Refused on the Term Defined line: *"When the SellingModelType is Evergreen or Term-Defined, BillingFrequency can't be null"*. An earlier request without `PeriodBoundary` on that line was refused first: *"Enter a start proration period with one of these values: AlignToCalendar, Anniversary, DayOfPeriod, or LastDayOfPeriod."* That refused request still created an empty quote header |
| M2 | Evergreen Months line with Monthly, Term Defined Annual line with Annual (both with `PeriodBoundary` Anniversary), one-time line with none; no `BillingTreatmentId` on any line; every treatment in the org had Change Billing Frequency (M10) | Accepted. `BillingTreatmentId` stayed null on every line |
| M3 | PATCH the Term Defined Annual line to Monthly (the same PATCH also set `SubscriptionTerm` to 1, which left the end date and total unchanged) | Without a treatment: refused, *"Add a Billing Treatment to make sure that you can change the Billing Frequency of its related Quote Line Item, and try again."* With `BillingTreatmentId` = *Billing Treatment - USA - Advance* (active, Change Billing Frequency selected): accepted |
| M4 | A one-time line with Monthly and that same treatment | Refused: *"When the SellingModelType is One Time, BillingFrequency must be null or milestone plan"* |
| M5 | With `configurationMethod: Skip` (see Scope): a one-time line with `MilestonePlan` and *Milestone Billing Treatment* in `BillingTreatmentId`; and a PATCH giving an existing one-time line that treatment with no frequency | Both accepted (also standalone, not a component). M11 is a shape where the frequency wasn't kept |
| M6 | PATCH the Term Defined line to Milestone Plan with *Milestone Billing Treatment* | Refused: *"When the SellingModelType is Termed, BillingFrequency can't be Milestone Plan"* |
| M7 | (read back after M2 and M5) | `BillingTerm` was 1 on every line, one-time lines included |
| M8 | `SubscriptionTerm: 12` on the Term Defined Annual line | End date 2038-11-30 from a 2026-12-01 start, total 12 × 3,240. The term counts the selling model's pricing term unit (years here), not months |
| M9 | Describe of the transaction and billing objects | `QuoteLineItem.BillingFrequency`, `OrderItem.BillingFrequency2` and `AssetStatePeriod.BillingFrequency`, each labelled Billing Frequency, API values `MilestonePlan` (label Milestone Plan), `Weekly`, `Monthly`, `Quarterly`, `Semi-Annual`, `Annual`; `Asset` has no billing frequency field. `BillingTerm` (label Billing Term) on the quote line, order product and asset action source. `QuoteLineItem.ProductSellingModelId` is read-only (Place refused it; the price book entry sets it). `Order.PaymentTermId`, `BillingAccount.PaymentTermId` and `BillingScheduleGroup.PaymentTermId` exist; `Quote` has no standard payment-term field, only the repo's `RLM_Payment_Terms__c` |
| M10 | Org state after a full build | Active: `RLM_Order_to_Billing_Schedule_Flow`. Inactive: the standard `o2bsflows` (*Order To Billing Schedule Flow*). Three active policies, 15 active treatments (all with Change Billing Frequency), two active payment terms, no billing milestone plans |
| M11 | One-time service lines as components of a bundle, each with `MilestonePlan` and *Milestone Billing Treatment* in `BillingTreatmentId`, placed with `configurationMethod: Force` and configuration rules on (second org, see Scope) | Place returned success, but `BillingFrequency` was stored blank on those lines; `BillingTreatmentId` was kept. Read the frequency back after placing; a success response doesn't mean it was kept. The save check refuses Milestone Plan on non-One-Time lines and accepts a treatment with a blank frequency, so it neither explains nor rules out a silent drop; cause not established [Platform behaviour, traced in part]. A later Skip PATCH was run on a third org, see Scope and SKILL Quick Rule 4 |
| M12 | Insert `BillingPolicy`, `BillingTreatment` and `BillingTreatmentItem` records by data plan | A policy or treatment inserted without `Status` was refused, so insert them Draft and activate bottom-up in later passes. A rerun of a plan that wrote Draft to records already Active was refused ("Can't change status from Active to Draft"); see SKILL.md → *Billing policies and treatments* for the reload pattern. An event item's `MilestoneStartDate` had to be blank: the field is a restricted picklist whose only value is `OrderProductActivation` |
| M13 | Read the billing schedules of an activated order with Annual and Monthly recurring lines | `BillingSchedule.BillingTermUnit` read `Year` on the Annual lines and `Month` on the Monthly lines (the line field's values are `Annual` and `Monthly`, M9) |
| M14 | Set `IsMilestoneAccomplished` on an event item, on an order whose schedules start in the future, and on one starting today | Future start: refused, *"You can accomplish a milestone only after the billing schedule starts."* Today: accepted, the item moved to Ready for Invoicing. Two orgs |
| M15 | An AutoTask DRO step marking its lines' next event item (SKILL → Marking from a fulfillment AutoTask) | Today-dated order: each line's next event item Ready for Invoicing, two orgs. Future-dated order: every mark deferred, and every item still waiting after the plan completed. Items after a manual step: still waiting, left for a person |

M2 and M3 are the measured basis for the qb-billing README limiting its treatment
requirement to a frequency that differs from the pricing term
[Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`]. In M2 a line whose frequency
matched its pricing term was accepted without one; the treatment was needed only to differ
(M3). Only these two frequency-to-model pairs were run, and every treatment in the org had
Change Billing Frequency selected (M10), so M2 says nothing about a flag-off case.

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

- Where the order product's billing fields come from. Recurring lines did arrive with a frequency
  and a treatment on the order product (Annual or Monthly, the Advance treatment, `BillingTerm` 1;
  one-time lines without a milestone plan had a null frequency and the Advance treatment)
  [Measured: 2026-11-12, 264, scratch; one org]. Not read: whether those were copied from the quote
  line by `createOrdersFromQuote` or derived from the selling model and billing policy, the same for
  period boundary, and how the asset state period gets its frequency. For one-time bundle components, `MilestonePlan` and the milestone
  `BillingTreatmentId`, set by a configuration-Skip Place PATCH after the Force placement,
  were measured as reaching the order product (`OrderItem.BillingFrequency2`,
  `OrderItem.BillingTreatmentId`), and activation made one milestone plan per line
  [Measured: 2026-11-12, 264, scratch; one org].
- Whether the UI defaults `BillingFrequency` from the selling model when a rep adds a line.
  The API didn't (M1).
- `MilestonePlan` on an Evergreen line.
- `MilestonePlan` on a one-time line whose milestone treatment comes only from the product's
  billing policy, with no `BillingTreatmentId` on the line.
- An Evergreen line placed without `PeriodBoundary`.
- A line whose frequency matches its pricing term, when the product's policy treatments have
  Change Billing Frequency off.
- A one-time line with a milestone treatment and no frequency (accepted in M5, and what M11
  left on bundle components): the source creates a plan at activation for a schedule whose
  billing term unit is Milestone Plan on a milestone treatment [Platform behaviour, traced];
  whether this line produces such a schedule is unread, and not confirmed on a live org.
- The cause of the M11 drop (the later Skip PATCH route is measured, Quick Rule 4). The same
  placement with rules off is untried, and the trace found no code in the modules searched that blanks it, and the response-to-line merge was not located (live check).
- A service added by an amendment (a new product on the amendment order) carrying a milestone
  treatment: whether activation creates a plan, with `enableMilestoneBillingForAmend` on (as the
  repo ships) or off, is unmeasured. Read its `BillingSchedule.Category`, `BillingMilestonePlanId`
  and billing schedule group [Dev guide: `sforce_api_objects_billingschedule`], and whether a
  plan made by hand for that order product or quote line links to its schedule.
- Measured, separately: a quantity increase on an already milestone-billed service, with the
  amendment line carrying the milestone treatment and the setting on, got a new active plan on a
  Category Amendment schedule from the amendment date; amendment lines at quantity 0 carried
  `MilestonePlan` from their assets [Measured: 2026-11-12, 264, scratch; one org]. The setting
  off is untried.
- Activation built one plan per order item for service lines placed with `MilestonePlan`
  [Measured: 2026-11-12, 264, scratch; one org]; the open half is a one-time line with no
  frequency (above).
- An approved Net 60 quote through order and invoice: which due date the invoice gets.
- With a billing profile on the account and a payment term on the order, which one the
  invoice uses outside billing arrangements.
- How the shipped approval treats a quote whose `RLM_Payment_Terms__c` is blank.
