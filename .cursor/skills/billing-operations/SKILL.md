---
name: billing-operations
description: >-
  Run and verify Revenue Cloud billing after setup: how billing schedules are created at
  order activation, invoice generation (scheduled batch runs, on-demand, preview, catch-up,
  draft vs posted), invoice documents, tax (tax policies and treatments, tax engines,
  estimated vs actual tax), payments and payment application, refunds, credit and debit
  memos, write-offs, collections and dunning, legal entities, accounting periods and the
  general ledger. Use when planning or reviewing the operate side of a billing build,
  choosing between billing options with a customer, or reading back invoices, tax,
  payments, credits or journals from an org. Billing frequency, policies, treatments,
  milestones and payment terms: billing-setup. Billing schema: revenue-cloud-data-model.
---

# Billing Operations — Invoicing, Tax, Payments, Credits and Accounting

Use this skill after billing is set up (see [billing-setup](../billing-setup/SKILL.md)) and
you must decide, run or check what happens next: schedules, invoices, tax, cash, credits,
the ledger. Every product claim comes from the 264 Help snapshot or the dev guide and is
tagged `[Help: <article_id>]` (id without `.htm.md`), `[Dev guide: <page>]`,
`[Repo: <path>]` or `[inferred]`. **Nothing in this skill was measured by this repo**: it is
a read of Help. Where billing-setup holds a measurement, link it instead of restating it.
Object and field names are in `revenue-cloud-data-model` → `domains/billing.md`.

## Quick Rules

1. **Billing starts at order activation.** One active order-to-billing-schedule flow (or the
   Create Billing Schedules for Orders API) turns an activated order into billing schedules
   and a schedule group. Context definition and mapping come from Billing Settings or a
   custom procedure plan [Help: `ind.billing_schedules_from_orders`,
   `ind.billing_schedules_from_transactions_create`]. Setup and the duplicate-flow trap are
   in billing-setup. Orders need a bill-to contact, billing address and shipping address, or
   activation fails [Help: `ind.billing_setup_enable`].
2. **Invoices come from schedules, not orders.** A run picks schedules whose next billing
   date is on or before the target date and that are ready for invoicing; the invoice date
   is stamped on the invoice and drives tax
   [Help: `ind.billing_understand_target_date_and_billing_period_count`]. Choose scheduled
   batch run, on-demand, or preview by [invoicing.md](invoicing.md).
3. **Draft vs posted is a switch on the run.** Without Post invoices a run leaves invoices
   in Draft; estimated tax is calculated on drafts and actual tax on posted invoices
   [Help: `ind.billing_automate_invoice_run_schedules`, `ind.billing_tax_calculation_results`].
   Deleting a posted invoice is not the correction path; void it, which creates a credit
   memo [Help: `ind.billing_invoices_void`, `ind.billing_invoice_delete`].
4. **Convert synchronous automation before the first run.** Record-triggered flows and Apex
   triggers on billing objects can stop a run or strand invoices in Draft In Progress,
   Posting In Progress or Error [Help: `ind.billing_invoice_run_sync_process`].
5. **Tax is a per-product choice of engine.** A tax policy on the product, its treatment, and
   the treatment's tax engine decide how a line is taxed; engines can be mixed. Pick the
   engine with [tax.md](tax.md).
6. **Cash and credits settle by an application level and a rule order.** Header or line
   level, payments first or credits first, and the match rules are Billing Settings, and
   they change what a balance means [payments-and-credits.md](payments-and-credits.md).
7. **Legal entity is the accounting key.** It is required for financial accounting, it
   selects billing and tax treatments when a policy says Legal Entity, and every
   journal and accounting period hangs on it [Help: `ind.billing_legal_entity_default`]
   ([accounting.md](accounting.md)).
8. **Read back each stage before the next.** Schedules, then invoices, tax, payments,
   credits, journals; queries per stage are in the sub-files and under Validation Checks.

## DO NOT

- **DO NOT** start an invoice batch run while a catch-up bill run is in progress; parallel
  invoicing can leave schedules and invoices inconsistent [Help: `ind.billing_catch_up_bill_runs`].
- **DO NOT** run a catch-up for schedules that already have a draft or posted invoice; they
  are not included [Help: `ind.billing_catch_up_bill_runs`].
- **DO NOT** use the Create Standalone Billing Schedules API for a billing schedule group
  linked to an asset; amend, renew and cancel from the order or asset and use the
  order-to-schedule flow or the orders API [Help: `ind.billing_schedules_standalone_api`].
- **DO NOT** treat the Revenue Standard Tax Engine as a compliance engine: Help calls it
  designed for simple calculations, line-level, with line-level rounding
  [Help: `ind.billing_standard_tax_rate`].
- **DO NOT** write off, void or delete as a shortcut for a wrong amount. Each has its own
  effect on credits, tax and journals ([payments-and-credits.md](payments-and-credits.md)).
- **DO NOT** state a number, amount, count or elapsed time for any stage as fact; this repo
  has not measured them. Say "not measured".
- **DO NOT** promise revenue recognition. The 264 Help area for Billing documents accounting
  periods, ledger accounts and transaction journals, and no revenue recognition schedules
  [inferred from Help's silence; see [accounting.md](accounting.md)].

## Entry Conditions

Read the sub-file for the stage; for anything else, go to the neighbor:

- Schedules, invoices, preview, documents, posting, batch runs: [invoicing.md](invoicing.md).
- Tax engine choice, policies, treatments, estimated vs actual, header tax: [tax.md](tax.md).
- Payments, retries, refunds, credit and debit memos, write-offs, collections:
  [payments-and-credits.md](payments-and-credits.md).
- Legal entities, accounting periods, ledger accounts, journals: [accounting.md](accounting.md).
- Billing frequency, policies, treatments, milestones, payment terms: `billing-setup`.
- Billing objects, fields, relationships: `revenue-cloud-data-model` → `domains/billing.md`.
- Invoice and credit values after amendment, cancellation or a backdated change:
  `asset-lifecycle-changes`; `rlm-business-apis` → `backdated-asset-lifecycle.md`.
- Usage that is rated then billed: `usage-consumption`. Invoice demo volume:
  `txn-data-harness`. Invoice PDF templates: `document-generation`.
- A billing build step fails: `troubleshooting`.

## Sub-files

- [invoicing.md](invoicing.md): read when choosing how invoices are produced (batch,
  on-demand, preview, standalone ingestion), setting a run's dates, grouping or splitting
  invoices, suspending billing, or generating invoice documents.
- [tax.md](tax.md): read when choosing a tax engine, building tax policies and treatments,
  explaining estimated vs actual tax, or importing external tax.
- [payments-and-credits.md](payments-and-credits.md): read when configuring payment
  collection, retries and application rules, issuing refunds, creating credit or debit
  memos, writing off, or running collections.
- [accounting.md](accounting.md): read when setting up legal entities, accounting periods,
  ledger accounts and journal rules, or closing a period.

## What the repo ships for these stages

A snapshot; the files are the source [Repo]:

- Billing flow and settings: `unpackaged/post_billing/` and `prepare_billing` in
  `cumulusci.yml`; detail in billing-setup → `shipped-billing.md`.
- Tax: `datasets/sfdmu/qb/en-US/qb-tax/README.md` (policy, treatment, engine, provider).
- Accounting: `datasets/sfdmu/qb/en-US/qb-accounting/README.md` (legal entities, ledger
  accounts, assignment and journal entry rules).
- Sequence policies: `tasks/rlm_billing.py` (`CreateSequencePolicies`), gapless numbering.
- Invoice email template: `create_default_invoice_email_template` in `cumulusci.yml`.
- Billing UI (aging, split invoices, journals): `scripts/build_billing_ui_module.py`,
  `deploy_post_billing_ui`. Payments metadata: `deploy_post_payments`.
- Backdated billing check: `scripts/backdated_arc/verify_backdated_billing.py`.

Whether any of these has been run end to end for a given stage here: not measured.

## Discovery

Find what an org has before designing (`<sf-alias>` is the SF CLI alias):

```bash
sf data query -o <sf-alias> -q "SELECT Id, Name, Status FROM LegalEntity"
sf data query -o <sf-alias> -q "SELECT Name, Status, TaxEngineName FROM TaxEngine"
sf data query -o <sf-alias> -q "SELECT Name, Status FROM TaxPolicy"
sf data query -o <sf-alias> -q "SELECT Name, Status FROM BillingBatchScheduler"
sf data query -o <sf-alias> -q \
  "SELECT ApiName, IsActive FROM FlowDefinitionView WHERE Label LIKE '%Billing Schedule%'"
```

Field names above and in the sub-files come from the data-model reference; confirm any that
errors with `sf sobject describe -s <Object> -o <sf-alias>`.

## Decisions to ask the customer

Ask these, then pick from the options (Help-grounded consequences in the sub-files):

- **How often, on what date, do you invoice?** Sets scheduler frequency, target date and
  invoice date offset. Options: recurring batch run; on-demand from account or order; both.
- **Do invoices post automatically?** Drafts get estimated tax and can be reviewed; posted
  get actual tax. Options: post in the run; post later by the draft-to-posted action.
- **One invoice per account, or per contract or PO?** Invoice group type on each schedule:
  Default, Billing Schedule, or Custom key.
- **Which tax engine and jurisdictions?** The treatment names the engine per product:
  partner or custom engine, Revenue Standard Tax Engine, or imported tax lines.
- **One legal entity or several?** Treatments, tax, periods and journals are per entity.
- **Who pays how, and what on failure?** Gateway, saved methods, retry rules; native or
  bring-your-own gateway; or manual application only.
- **Credits before or after payments?** Application order and rules (Payments First is the
  default; Match ID, Match Balance, oldest, highest balance).
- **Do you need journals in Salesforce?** They need ledger accounts, rules and a Billing
  license feature; or feed an external accounting system from invoices.
- **Is revenue recognition expected?** Help documents none; confirm the system of record.

## Examples

**"Invoice monthly, post automatically, one invoice per account."** Create an active invoice
scheduler with Post invoices selected, a monthly frequency, target date based on the run
date and an invoice date offset the customer names; leave schedules on the Default invoice
group. Read back the run, the invoices and tax lines ([invoicing.md](invoicing.md)).
Whether this works on the repo's build is not measured.

**"Customer already billed the first year elsewhere."** Import accounts, orders, schedules
and groups, run a catch-up bill run with the target date set to the last date billed, then
start normal invoice runs [Help: `ind.billing_catch_up_bill_runs`]. Not measured here.

**"Simple sales tax in one country, a vendor in another."** Two tax engines: the Revenue
Standard Tax Engine on the simple legal entity's treatments and a partner or custom engine on
the other ([tax.md](tax.md)). Not measured here.

## Validation Checks

Run per stage; each is a read-back, not a measurement of timing or volume:

```bash
# schedules exist after activation (one flow active)
sf data query -o <sf-alias> -q \
  "SELECT Id, ReferenceEntityId, BilledAmount FROM BillingSchedule LIMIT 20"
# invoices from a run
sf data query -o <sf-alias> -q \
  "SELECT Id, Status, Balance, InvoiceBatchRunId FROM Invoice ORDER BY CreatedDate DESC LIMIT 20"
# tax lines on those invoices
sf data query -o <sf-alias> -q \
  "SELECT InvoiceLineId, TaxAmount, TaxCode FROM InvoiceLineTax LIMIT 20"
# journals, when ledger rules are on
sf data query -o <sf-alias> -q "SELECT Id, ActivityDate FROM TransactionJournal LIMIT 20"
```

- Each billing promise has an activated test order whose first invoice has the expected
  period, amount, tax and due date (billing-setup's check, extended to tax and cash).
- Posted and draft invoices carry the tax status the customer expects (estimated vs actual).
- A payment or credit applied to an invoice changes its balance as the configured level
  (header or line) predicts.
- `python3 scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
