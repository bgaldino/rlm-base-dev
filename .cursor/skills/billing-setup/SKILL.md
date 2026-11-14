---
name: billing-setup
description: >-
  Decide and set up how Revenue Cloud bills what was sold: billing frequency
  and how it relates to the selling model on quote, order and asset lines;
  billing policies, treatments and treatment items (in advance, in arrears,
  excluded); milestone billing for services, including what to decide when a
  source names no milestones; payment terms, where they live and how the
  shipped quote approval reads them; and what this repo's billing build ships.
  Use when planning or reviewing the billing side of a build, placing quote
  lines that need a billing frequency, or explaining why a line is refused for
  its billing fields. Billing schema: revenue-cloud-data-model. Invoice values
  on amendments and cancellations: asset-lifecycle-changes and rlm-business-apis.
---

# Billing Setup — Frequency, Treatments, Milestones and Payment Terms

Use this skill when a commercial source says how customers are billed ("annually in
advance", "services in milestones", "Net 45") and you have to turn that into Revenue Cloud
records and line values. It covers the decisions and the line rules the platform enforces.
The objects themselves are in `revenue-cloud-data-model` → `domains/billing.md`. Claims are
tagged `[Help: <article>]`, `[Dev guide: <page>]`, `[Repo: <path>]` and `[Measured: Mn]`.
Each `Mn` is a row in [measured-264.md](measured-264.md), measured on 264 on 2026-11-10;
read the row's scope before generalising it.

## Quick Rules

1. **Billing frequency is a line field, separate from the pricing term.** The selling
   model sets how a line is priced; `BillingFrequency` sets how often it is billed. When the two
   differ, Billing prorates the line total over whole and partial billing periods
   [Help: `ind.billing_change_billing_frequency_examples`]. The field is
   `QuoteLineItem.BillingFrequency`, `OrderItem.BillingFrequency2` (also labelled Billing
   Frequency) and `AssetStatePeriod.BillingFrequency`; `Asset` has none [Measured: M9].
2. **Set the frequency on every Term Defined and Evergreen line you place through the API.**
   Place Sales Transaction refused a Term Defined line without one rather than default it
   from the selling model [Measured: M1]. The configurator's pricing step fills
   the frequency only for a Months (Monthly) or Annual (Annual) term unit; other units get
   no automatic value, so set it explicitly [Platform behaviour, traced]. Place with Skip gave no
   fill (M1) [Measured: 2026-11-10, 264, scratch]. Whether Skip skips that step is not
   traced. A frequency that matches the pricing term (Monthly on a Months model, Annual on an
   Annual model) needed no billing treatment on the line, in an org where every treatment had
   Change Billing Frequency selected [Measured: M2]; item 3 gives the traced rule for when a
   treatment is required. With the
   flag off on the product's treatments, the repo's data-plan README reports the line can't be
   created at all [Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`].
3. **A frequency that differs from the pricing term needs a billing treatment on the line.**
   Changing a Term Defined Annual line to Monthly was refused until the line had one
   [Measured: M3]. Help also requires that treatment to have Change Billing Frequency
   (`CanChangeBillingFrequency`) selected [Help: `ind.billing_change_billing_pricing_frequencies`]. The flag
   defaults to false [Dev guide: `sforce_api_objects_billingtreatment`].
   The complete rule: a treatment on the quote or order line is required only when the
   line's frequency differs from the pricing term unit of its selling model (Annual on a Months
   model); a frequency equal to the term unit, or a milestone plan, needs none. When one is
   required it must be Active and have Change Billing Frequency selected, or the line is
   refused; the check reads the line's own treatment and does not fall back to the billing
   policy. The check is skipped when Billing is not enabled in the org [Platform behaviour,
   traced]. Item 2's caveat (a matching frequency needed no treatment) is the equal-frequency half
   of this rule. Other docs link here instead of restating it.
4. **One-time lines take no frequency, or Milestone Plan (API value `MilestonePlan`).**
   Monthly on a one-time line was refused, Milestone Plan with a milestone treatment was
   accepted, and Milestone Plan on a Term Defined line was refused [Measured: M4–M6]. Bill services in milestones on a one-time selling model.
   A source that bills a one-time charge periodically is an owner decision, not a field
   fix. Options: Milestone Plan with a milestone treatment (accepted on a one-time line, above) and
   one date-based milestone per instalment [Help: `ind.billing_milestone_treatment_and_item_create`],
   periodic invoicing that way unmeasured;
   or sell it on a recurring selling model with a term equal to the number of instalments
   [inferred, not measured]. Don't force a recurring frequency onto the one-time line.
   On bundle components placed with configuration method Force and configuration rules on, Place stored the
   frequency blank and kept the treatment, with success; read the frequency back [Measured: M11].
   The save check explains the refusals, not the drop: Milestone Plan is legal only on One-Time
   lines, and a treatment with a blank frequency is accepted. Why Place blanked the frequency on a
   component is not established [Platform behaviour, traced in part]. Skip kept it on a standalone line (M5). To keep it on
   components, place first, then send a second Place PATCH of the component lines with
   configuration Skip, `BillingFrequency` `MilestonePlan` and the milestone `BillingTreatmentId`:
   both were kept, no price moved, the frequency and the milestone treatment were on the order
   products after `createOrdersFromQuote` (`OrderItem.BillingFrequency2` `MilestonePlan`,
   `OrderItem.BillingTreatmentId`) and activation built one plan per line
   [Measured: 2026-11-12, 264, scratch]. One org and one bundle; the cause of the
   drop stays open. Read the frequency back after each Place.
5. **In advance or in arrears is the treatment item's Billing Type, not a line field.**
   Advance bills on the billing date on or before the start date; Arrears on the first one
   after it; None is for milestone billing
   [Help: `ind.billing_policies_and_treatments_create`]. The product's billing policy picks
   the treatment ([Billing treatments](#billing-policies-and-treatments)).
6. **Payment terms live on the order, not the quote.** `Order.PaymentTermId` feeds the
   billing schedules and the invoice due date. An order without one falls back to its
   billing profile, then the account's default billing profile, then the org's default
   payment term [Help: `ind.billing_payment_terms`] [Help: `ind.billing_billing_profiles_create`]. `Quote` has no standard payment-term
   field [Measured: M9]. The shipped approval reads a custom quote picklist that nothing
   copies to the order ([Payment terms](#payment-terms)).
7. **Billing starts at order activation.** One active flow creates billing schedules and
   groups when an order is activated; more than one active flow duplicates them
   [Help: `ind.billing_setup_clone_order_to_schedule_flow`]. The repo activates
   `RLM_Order_to_Billing_Schedule_Flow` [Repo: `cumulusci.yml` → `prepare_billing` step 5].

## DO NOT

- **DO NOT** activate a second order-to-billing-schedule flow beside the repo's. Duplicate
  billing schedules follow (Quick Rule 7).
- **DO NOT** put a recurring frequency (Monthly, Annual) on a one-time line, or Milestone
  Plan on a Term Defined line. Both were refused (Quick Rule 4).
- **DO NOT** assume an approved quote payment term reaches the invoice. Nothing in the repo
  sets `Order.PaymentTermId` from the quote ([Payment terms](#payment-terms)).
- **DO NOT** invent milestone names, percentages or dates for a source that names none.
  Record them as decisions in the plan ([Milestone billing](#milestone-billing-for-services)).
- **DO NOT** edit an active billing treatment's currency, or deactivate the default
  treatment of an active policy. Both are refused
  [Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`]
  [Help: `ind.billing_policies_and_treatments_create`].

## Entry Conditions

| Situation | Use |
|---|---|
| Map a source's billing rules (cadence, advance or arrears, milestones, payment terms) onto Revenue Cloud | This skill |
| Place quote lines headlessly and they are refused for `BillingFrequency` or billing treatment | This skill → [measured-264.md](measured-264.md) |
| What billing records, settings and flows this repo deploys | This skill → [shipped-billing.md](shipped-billing.md) |
| Billing object fields and relationships | `revenue-cloud-data-model` → `domains/billing.md` |
| Selling models and proration (how a line is priced) | `pricing-setup`; catalog design: `product-catalog-modeling` |
| Payment terms as an approval dimension, the Finance chain | `advanced-approvals` |
| Invoice and credit values after an amendment or cancellation | `asset-lifecycle-changes`; `rlm-business-apis` → `backdated-asset-lifecycle.md` |
| Changing the billing frequency of an active asset | `rlm-business-apis` → `backdated-asset-lifecycle.md` → *Changing billing frequency* |
| Loading or editing the billing data plans | `sfdmu-data-plans`, then the plan's README |
| A billing build step fails | `troubleshooting` |

## Sub-files

- [shipped-billing.md](shipped-billing.md): read before reusing or changing what the repo
  builds. It has the `prepare_billing` steps, the policies, treatments and payment terms the
  data plan loads, the billing settings, and the queries that show what an org actually has.
- [measured-264.md](measured-264.md): read before placing lines headlessly or before
  quoting a measured claim. It has every measured result with its scope, the test that
  produced it, and the open questions.

## Discovery

Find what an org has before you design against it (`<sf-alias>` is the SF CLI alias):

```bash
sf data query -o <sf-alias> -q "SELECT Name, Status, BillingTreatmentSelection, DefaultBillingTreatment.Name FROM BillingPolicy"
sf data query -o <sf-alias> -q "SELECT Name, Status, BillingPolicy.Name, LegalEntity.Name, IsMilestoneBilling, CanChangeBillingFrequency, ExcludeFromBilling FROM BillingTreatment"
sf data query -o <sf-alias> -q "SELECT BillingTreatment.Name, Name, BillingType, MilestoneType, Percentage, ProcessingOrder, Status FROM BillingTreatmentItem ORDER BY BillingTreatment.Name, ProcessingOrder"
sf data query -o <sf-alias> -q "SELECT Name, Status, IsDefault, (SELECT Type, Period, PeriodUnit FROM PaymentTermItems) FROM PaymentTerm"
sf data query -o <sf-alias> -q "SELECT BillingPolicy.Name, COUNT(Id) n FROM Product2 GROUP BY BillingPolicy.Name"
sf data query -o <sf-alias> -q "SELECT ApiName, IsActive FROM FlowDefinitionView WHERE Label LIKE '%Billing Schedule%'"
```

## Billing frequency

A line's frequency is one of Weekly, Monthly, Quarterly, Semi-Annual, Annual or Milestone
Plan; the API values match the labels except `MilestonePlan` [Measured: M9]. On a new sale it is chosen on the quote line or the order product
[Help: `ind.billing_change_billing_pricing_frequencies`].

| Selling model | Frequency the API accepted | Billing treatment on the line |
|---|---|---|
| Term Defined, Evergreen | Required (the refusal names both; run on Term Defined, M1); the pricing term's own cadence (two models run) | Not needed, with the flag on every treatment [Measured: M2] |
| Term Defined, Evergreen | A different cadence | Needed (run on Term Defined, M3), with Change Billing Frequency (Help) |
| One Time | Blank, or `MilestonePlan` with a milestone treatment on the line (not kept in M11: bundle components placed with configuration Force, rules on) | Optional with a blank frequency [Measured: M2, M5] |

`MilestonePlan` on an Evergreen line wasn't tested (the save check refuses it on Term Defined and Evergreen lines).

The save check, as read, skips a blank frequency on insert and refuses a blank only when a
saved line's frequency is changed and the result is blank; it applies only when billing is enabled. M1 refused a new Term
Defined line with a blank frequency anyway; that is measured and the source read doesn't explain it.
A save error on a line can hide the rule message. On the synchronous path, a refused line save is
what comes back, and configuration messages from that call aren't written as error logs (traced in
part; the asynchronous path wasn't traced), so read the response rather than the error log
[Platform behaviour, traced in part]. Amend, renew and cancel lines have further rules not read.

- **Combining periods:** `BillingTerm` bills several frequency units as one period, for
  example Monthly with a term of 3. It defaults to 1 [Help: `ind.billing_multiple_term_billing`]
  [Measured: M7]. That article calls the field Billing Term Unit; its API name is
  `BillingTerm` [Measured: M9].
- **Period alignment:** `PeriodBoundary`, `PeriodBoundaryDay` and `PeriodBoundaryStartMonth`
  anchor the periods (anniversary, calendar, a fixed day or start month). Not every
  combination is valid for every frequency [Help: `ind.billing_field_combination_requirements`].
  A Term Defined line placed without `PeriodBoundary` was refused [Measured: M1].
- **Rounding:** an Evergreen line priced yearly and billed monthly can bill a few cents
  less over the year ($100 a year billed as 12 × $8.33) [Help: `ind.billing_frequency_change_flow_impact`].
- **Later changes:** on an active subscription, only a zero-quantity field amendment changes
  the frequency, never a renewal or cancellation, and Weekly can't change to or from another
  frequency [Help: `ind.billing_frequency_change_flow_impact`]. The API steps are in
  `rlm-business-apis` → `backdated-asset-lifecycle.md`.

## Billing policies and treatments

A **billing policy** is assigned to products (`Product2.BillingPolicyId`) and groups
**billing treatments**. A non-milestone treatment has one **treatment item**,
which holds the Billing Type (Advance, Arrears, None)
[Help: `ind.billing_policies_and_treatments_create`].

How an order product gets its treatment, when it doesn't have one already
[Help: `ind.billing_treatment_resolution`]:

| Policy's Billing Treatment Selection | Treatment assigned |
|---|---|
| Default or Manual | The policy's default treatment |
| Legal Entity | The treatment whose legal entity matches the order product's (or the org default legal entity); otherwise the policy's default |
| (product has no policy) | The org's default billing treatment; with none, the billing calculation fails |

Only active policies and treatments count. Activate bottom-up: treatment item, then
treatment, then policy [Help: `ind.billing_policies_and_treatments_create`].

**Exclude From Billing = Yes** on a treatment skips billing schedules and invoices for the
order items that carry it, without holding up the rest of the order. Switch it back, or give
the item a billable treatment, and reprocess the order when they are ready
[Help: `ind.billing_policies_and_treatments`].

## Milestone billing for services

A milestone treatment has Enable milestone billing (`IsMilestoneBilling`) selected and one
treatment item per milestone; Configure Milestones creates up to 20 at once. Each item is date-based (an offset from the
billing schedule start) or event-based (someone marks it accomplished), and carries a
percentage or a flat amount [Help: `ind.billing_milestone_treatment_and_item_create`]
[Help: `ind.billing_milestone_create`]. Order activation creates a billing milestone plan
from the treatment and links it to the order product's billing schedule. To edit that plan,
set it back to Draft [Help: `ind.billing_milestone_usecase`]. A schedule whose billing term unit is Milestone
Plan, with no plan attached, of category Original (or Amendment with the amend setting on), on a
milestone treatment, gets its plan created at activation from the treatment's items, one for one,
and activated; if a plan with the same reference item exists it is updated rather than duplicated;
you don't author the plan [Platform behaviour, traced]. Activating an order whose service lines carried
`MilestonePlan` and a milestone treatment built one active plan per order item, its reference
amount the line total, with the treatment's items plus a platform remainder item for the
unassigned share; each schedule's billing term unit was Milestone Plan, starting on the order's
start date, with the next billing date at the first date-based item's offset
[Measured: 2026-11-12, 264, scratch]. One org and one treatment. Whether a
one-time line with a milestone treatment and no frequency produces such a schedule is unread.

**Marking an event milestone done.** An event-based plan item waits in Waiting for Milestone
Accomplishment until someone selects Milestone accomplished on it
(`BillingMilestonePlanItem.IsMilestoneAccomplished`, updateable); saving moves it to Ready for
Invoicing, and after activation that field is the only one you can edit on event items [Help:
`ind.billing_milestone_usecase`, `ind.billing_milestone_create`,
`ind.billing_milestone_treatment_and_item_create`] [Dev guide:
`sforce_api_objects_billingmilestoneplanitem`]. The invoice run's target date then decides which
accomplished milestones are invoiced [Help:
`ind.billing_understand_target_date_and_billing_period_count`]. Help names no link from
fulfillment steps to billing milestones [inferred from Help's silence], so a source milestone tied
to a delivery step needs a decided way to be marked: a billing user, or automation such as a
fulfillment AutoTask flow that sets the field [inferred, not measured]. Without one the
item stays waiting and is not invoiced [inferred from Help]. A DRO Milestone step completed by
itself with nobody acting [Measured: 2026-11-13, 264, scratch, one org], and Help names no
action it takes [inferred from Help's silence], so don't count on a Milestone step to mark a
billing milestone; each event item needs its own marking point after the step it names
[inferred]. DRO step behavior: [dro-plans](../dro-plans/examples-and-grounding.md). Where an
amendment makes a new milestone plan (dro-plans measured a full new plan on amendment), a marking
flow scoped to the original order may not reach its event items; select plan items by asset or
contract, or have the amendment's own fulfillment mark them [inferred]. Decide who marks an event
already past when the amendment activates [inferred, unmeasured].

**When a source names no milestones,** Revenue Cloud still needs, for each milestone:
- a name;
- date-based or event-based, and for a date, the offset and its unit;
- a percentage or a flat amount;
- for an event milestone, who or what marks it accomplished (above).

Any share left after the items is a remainder item that the platform adds, invoiced with the
final milestone [Help: `ind.billing_milestone_usecase`]. Ask the source's owner for these;
until they answer, list them as open decisions in the plan. Meanwhile build the milestone
route with a placeholder treatment (the repo's example below), assert only that activation creates
the plans, and don't assert amounts or names; don't fall back to one-time billing. The repo's milestone treatment
(four items, 10/20/50/10 percent) is an example, not a default for services
([shipped-billing.md](shipped-billing.md)).

Amendments, renewals and cancellations of milestone-billed assets have their own rules:
by default no new milestone plan is made for amend or renew orders. Turning on *Support
Milestone Plans for Amended Billing Schedules* makes or links one for amendment schedules
(Help says nothing about renewals with it on), and a cancellation cancels the date-based milestones
due on or after the cancellation date (event-based ones once the original order's event
milestone is invoiced and posted). Billing then issues a credit memo for the part not
invoiced [Help: `ind.billing_milestone_amended_renewed_canceled_assets`].
A plan is created from treatment for an amendment schedule only when that setting is on and
the amendment's treatment (or, without one, the original group's) is a milestone treatment; a
preconfigured plan carried on the amendment, which Help says is linked, wasn't traced. A
non-milestone amend treatment gives an ordinary schedule. With the setting off, no plan is made for the
amendment schedule; original schedules aren't gated by it [Platform behaviour, traced].
The repo turns that setting on (`enableMilestoneBillingForAmend`)
[Repo: `unpackaged/post_billing/settings/Billing.settings-meta.xml`].

For amending an asset that has a milestone plan, the same article lists four cases, keyed on
what the amendment carries. It doesn't say which of them hold with the setting off.

| The amendment has | Result |
|---|---|
| A milestone treatment | A new plan based on the amendment, linked to the amendment billing schedule; dates and amounts recalculated from the amendment start date. A quantity increase on a milestone-billed service, with the amendment line carrying the milestone treatment and the setting on, got a new active plan on a Category Amendment schedule from the amendment date [Measured: 2026-11-12, 264, scratch; one org] |
| A non-milestone treatment | A one-time billing schedule and no plan |
| A preconfigured or negotiated milestone plan | That plan, linked to the amendment billing schedule |
| No billing treatment | A new plan from the original billing schedule group's treatment; the original plan isn't reused |

**A service that an amendment adds** (a new product on the amendment, not a change to a
milestone-billed asset) is none of those cases. The amend rule above was read for amendment
schedules; the source read doesn't separate an added product. Whether activating the amendment
order gives such a line a milestone plan, with the setting on or off, hasn't been measured
([measured-264.md](measured-264.md) → Open). Help also documents creating a plan by hand for an
order product or quote line item [Help: `ind.billing_milestone_create`]; whether one made for the
added line links to its billing schedule is part of the same open item. Until it is measured,
record milestone billing for amendment-added services as an open decision in the plan.

## Payment terms

A **payment term** (`PaymentTerm`) has one Standard **payment term item**: Period-Based
(invoice date plus a period) or Derive End of Month and Add Period. Only active terms
apply. The order's payment term carries to its billing schedules and sets each invoice's
due date [Help: `ind.billing_payment_terms`] [Help: `ind.billing_payment_terms_usecase`].
Help states two fallbacks for an order without one. The payment-terms article names the org
default. The billing-profiles article says a transaction missing values takes them from its
billing profile (`BillingAccount.PaymentTermId`), then from the account's default billing
profile, and only then from the org default [Help: `ind.billing_billing_profiles_create`].

**As an approval input,** the shipped quote approval reads `Quote.RLM_Payment_Terms__c`, a
custom picklist (Net 30 default, Net 45, Net 60, Net 90), and routes any value other than
Net 30 to the Finance chain [Repo: `unpackaged/post_approvals/flows/RLM_Quote_Smart_Approval.flow-meta.xml`].
How that chain behaves is in `advanced-approvals`. Two gaps sit between the approval and
billing [Repo: `unpackaged/post_approvals`, `datasets/sfdmu/qb/en-US/qb-billing`]:

1. Nothing copies the picklist to `Order.PaymentTermId`.
2. The data plan loads only *Default Payment Term* (30 days, the org default) and *Net 45*;
   Net 60 and Net 90 have no `PaymentTerm` record.

So, by Help's rules above, an approved Net 60 quote's order is due on its billing
profile's term, or the org default, unless something sets the order's payment term. That is inferred; it hasn't been run
through an invoice ([measured-264.md](measured-264.md) → Open).

To make an approved term reach the invoice, create a `PaymentTerm` for each picklist value
and set `Order.PaymentTermId` from the quote when the order is created.

## Amendments, cancellations and invoices

Quote and order values on a change are not the invoice. For where change values land, read
`asset-lifecycle-changes`. For invoices and credit memos after a backdated change, and
frequency changes on active assets, read `rlm-business-apis` → `backdated-asset-lifecycle.md`.
For milestone-billed assets, and services an amendment adds, see the milestone section above.

**Notice periods on until-cancelled lines.** The 264 Help snapshot names no notice-period
setting for billing or cancellation: its only notice terms are collections reminders and
contract-document key terms, neither of which gates a cancellation. A source that requires
notice before an until-cancelled line stops needs a decision, not a setting. Options:
a validation on cancellation quotes comparing the cancellation date with the notice
window, or a process rule outside the product. Record which, and the window's start
(request date or quote date) [inferred, not measured].

## Examples

**"Subscriptions billed annually in advance."** Give each subscription product a policy
whose treatment item is Billing Type Advance; in this repo that is *Billing Policy -
Advance*. Then:
- keep Change Billing Frequency selected on the policy's treatments (Quick Rule 2);
- on an Annual selling model, place lines with `BillingFrequency` Annual and no treatment
  on the line;
- on a Monthly selling model, place Annual with a treatment that has Change Billing
  Frequency selected.

Check the first invoice's period against the period-boundary examples
[Help: `ind.billing_field_combination_requirements`].

**"Services billed in milestones" with no milestones named.** Sell the service on a
one-time selling model and place the line with `BillingFrequency` `MilestonePlan` and the
milestone treatment in `BillingTreatmentId` [Measured: M5]. Leaving the treatment to the
product's policy wasn't placed. Put the milestone names,
types, offsets and shares in the plan as open decisions, and test the plan's milestones
after order activation.

**"Net 60 needs Finance approval."** The shipped approval already routes it. For billing,
add a `Net 60` payment term with a 60-day Period-Based item, activate it, and set the
order's `PaymentTermId` when the order is created from the quote.

## Validation Checks

- The Discovery queries show active policies, treatments with active items, the payment
  terms the source names, and one active order-to-billing-schedule flow.
- A test quote places with the frequencies the plan promises, through the route the demo
  uses ([measured-264.md](measured-264.md) → Test).
- For each billing promise, an activated test order has billing schedules with the expected
  frequency, treatment and payment term, and the first invoice has the expected period,
  amount and due date.
- `python scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
