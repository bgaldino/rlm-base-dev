# Billing Setup — What This Repo Ships

Read this before reusing or changing the repo's billing build. Parent: [SKILL.md](SKILL.md).

**This is a snapshot of `main` that will age.** The flow, the data plan and the settings
file are the source; the commands under [Rediscover](#rediscover) supersede the tables
below.

## The flow

`prepare_billing` is step 13 of `prepare_rlm_org`. Most steps run when the `billing` flag is
on; the data load also needs `qb`, or `q3` with `tax`, and skips on `refresh` builds
[Repo: `cumulusci.yml` → `prepare_billing`]. The steps that shape billing behaviour:

| Step | Task | What it does |
|---|---|---|
| 1 | `deploy_post_billing` | Billing settings and the billing flows from `unpackaged/post_billing` |
| 2 | `insert_billing_data` | The `qb-billing` data plan (policies, treatments, payment terms, accounting) |
| 3 | `insert_q3_billing_data` | q3 builds: maps the q3 products onto the qb-billing policies |
| 5 | `activate_flow` | Activates `RLM_Order_to_Billing_Schedule_Flow` |
| 6, 7 | `activate_default_payment_term`, `activate_billing_records` | Activate the payment terms, then treatment items, treatments and policies |
| 9 | `deploy_billing_id_settings` | Sets the org's default billing treatment (*Billing Treatment - USA - Advance*), default legal entity, tax treatment and GL accounts |

The plan's README has every step and its flag conditions
[Repo: `datasets/sfdmu/qb/en-US/qb-billing/README.md`].

## Policies, treatments and products

From the `qb-billing` CSVs [Repo: `datasets/sfdmu/qb/en-US/qb-billing/`]:

| Policy | Treatment selection | Treatments | Billing Type |
|---|---|---|---|
| Billing Policy - Advance | Legal Entity | One per region (USD, CAD, EUR, GBP, AUD, CHF, JPY), each on its legal entity | Advance |
| Billing Policy - Arrears | Legal Entity | One per region, as above | Arrears |
| Milestone Billing Policy - Software | Default | *Milestone Billing Treatment* (USD, no legal entity) | None |

- Every treatment has Change Billing Frequency selected; the README explains why
  (*CanChangeBillingFrequency gates quote-line creation*).
- The milestone treatment has four items: *Requirements Gathering* 10% (date, 5 days),
  *Design Completion* 20% (date, 1 month), *Software Delivery* 50% (date, 4 months) and
  *Configuration & Deployment* 10% (event). They total 90%.
- `Product2.csv` sets a billing policy on products by SKU: 294 rows to Advance, 7 to
  Arrears, 15 with none. No product gets the milestone policy. Products with no policy bill
  on the org default treatment ([SKILL.md](SKILL.md) → Billing policies and treatments).

## Payment terms

The data plan loads two [Repo: `datasets/sfdmu/qb/en-US/qb-billing/PaymentTerm.csv`,
`PaymentTermItem.csv`]:

| Payment term | Item | Default |
|---|---|---|
| Default Payment Term | Period-Based, 30 days | Yes (set by `activateDefaultPaymentTerm.apex`) |
| Net 45 | Period-Based, 45 days | No |

The approval feature adds `Quote.RLM_Payment_Terms__c`, a restricted picklist on the
`RLM_Payment_Terms` value set: Net 30 (default), Net 45, Net 60, Net 90
[Repo: `unpackaged/post_approvals/globalValueSets/RLM_Payment_Terms.globalValueSet-meta.xml`].
It isn't linked to the `PaymentTerm` records.

## Settings and flows

From `unpackaged/post_billing/` [Repo]:

- `settings/Billing.settings-meta.xml` turns on, among others, milestone plans for amended
  billing schedules (`enableMilestoneBillingForAmend`), invoice email and PDF, dunning, and
  payment schedules. It sets credit, payment and refund application to line level; its
  comment records what that changes.
- `RLM_Order_to_Billing_Schedule_Flow`: record-triggered on Order update when the order is
  Activated and its orchestration submission status is Submitted. On an asynchronous path,
  for orders whose usage type is Revenue Lifecycle Management, it calls
  `createBillingSchedulesFromBillingTransaction`.
- `RLM_Update_Quote_Billing_Info_From_Opportunity_Account`: on quote create, fills the bill-to
  contact and the billing and shipping addresses from the opportunity's account or the quote
  account. It doesn't set a payment term.
- The invoice and payment flows (`RLM_Apply_Payment*`, `RLM_On_Demand_Invoice_Document_Generation`)
  act after invoicing and don't affect schedules.

The Billing UI feature (`billing_ui`) adds `Order.RLM_Billing_Arrangement__c` and
`Order.RLM_Billing_Profile__c` and maps them into the billing context
[Repo: `cumulusci.yml` → `deploy_post_billing_ui`, `apply_context_billing_order`].

## Rediscover

```bash
grep -n -A80 "^  prepare_billing:" cumulusci.yml
cut -d, -f1 datasets/sfdmu/qb/en-US/qb-billing/Product2.csv | sort | uniq -c
cat datasets/sfdmu/qb/en-US/qb-billing/BillingPolicy.csv datasets/sfdmu/qb/en-US/qb-billing/PaymentTerm.csv
git grep -n "RLM_Payment_Terms__c" -- unpackaged force-app templates
```

On an org, run the Discovery queries in [SKILL.md](SKILL.md).
