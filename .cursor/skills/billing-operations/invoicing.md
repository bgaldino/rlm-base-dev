# Billing Operations — Schedules and Invoicing

Read this when choosing how invoices are produced or setting a run's dates. Parent:
[SKILL.md](SKILL.md). Everything here is a read of Help and is not measured in this repo.

## Where billing schedules come from

- Order to Billing Schedule flow: orders in this org; the repo's route
  [Help: `ind.billing_schedules_from_orders`].
- Create Billing Schedules for Orders API: the same, called from code
  [Help: `ind.billing_schedules_from_transactions_create`].
- Create Standalone Billing Schedules API: external transactions or any object
  [Help: `ind.billing_schedules_standalone_api`].

The standalone API covers original, amended, canceled, renewed, ramped, bundled and
usage-based transactions, and from Summer '26 takes minimal intent-based requests for
changes [Help: `ind.billing_schedules_standalone_api`]. Its context definition is
`BillingContext` or one extended from it [Help: `ind.billing_schedules_from_order_items`].

- A schedule group holds the schedules for one order product or asset; billing day of
  month, next billing date override, addresses, tax treatment and payment term on the group
  can be changed later [Help: `ind.billing_schedule_group_update`].
- Billing needs the order's bill-to contact and addresses at activation
  [Help: `ind.billing_setup_enable`].
- Turning Billing off stops schedule creation for newly activated orders and fails queued
  asynchronous requests and runs [Help: `ind.billing_considerations`].

## Choose how invoices are produced

- Invoice batch run: regular cycle for many accounts (a scheduler; parallel; runs on the
  Data Processing Engine).
- Generate Invoices on an account or order: a person bills one customer now (quick action).
- Invoice Creation API or flow action: another system triggers invoicing for an account,
  order or list of schedules.
- Invoice Ingestion API: invoices exist outside Billing, or come from a debit memo; it
  creates the invoice, lines and tax lines.
- Preview Invoices: show a customer the next invoice; never creates an invoice.

- **Batch run.** A scheduler (App Launcher: Billing Batch Schedulers, New Invoice
  Scheduler) can run once, daily, weekly or monthly, immediately with Start run now, and
  only while Active. Job types are Invoice, Catch-Up Bill Run and Forecast
  [Help: `ind.billing_automate_invoice_run_schedules`, `ind.billing_invoice_batch_run`].
  Limit: 30 active billing batch schedulers, and 2,000 invoice lines per invoice
  [Help: `ind.billing_limits`].
- **On demand.** The Generate Invoices quick action takes a target date and invoices the
  related schedules with next billing date before it and status Ready for Invoicing; it is
  on the Account layout by default and added by hand to Order
  [Help: `ind.billing_invoice_generation_for_accounts_orders`].
- **Ingestion.** A posted debit memo can be turned into a draft invoice; ingested lines
  with tax status Pending or Estimated get estimated tax
  [Help: `ind.billing_invoice_creation`].
- **Preview.** Up to two billing periods and up to 200 schedules, for an order, account or
  schedule group; quotes need a procedure plan and the Invoice Preview API; a PDF needs
  document generation [Help: `ind.billing_preview_invoice`,
  `ind.billing_invoice_preview_create`].

## Dates: invoice date, target date, billing period count

Three controls on a scheduler [Help: `ind.billing_understand_target_date_and_billing_period_count`]:

- **Invoice date**: stamped on the invoice and used for tax. For recurring runs it is the
  target date or run date plus an offset (negative allowed).
- **Target date**: selects schedules whose next billing date is on or before it. With none,
  every schedule matching the filters is invoiced. Recurring runs can base it on the run
  date plus offset or on a calendar day of a month.
- **Billing period count**: 1 to 12 periods per schedule. Use it with a target date when
  schedules have different next billing dates, to avoid billing extra periods. It does not
  apply to milestone or usage schedules.

Decision: a fixed target date is simplest and over-bills schedules with earlier next
billing dates; a period count caps that. Ask which the customer's contracts need
[inferred from Help].

Milestone and usage schedules differ. For milestones the target date picks which
accomplished milestones invoice (the run date when none is set); usage schedules with
liable summaries Ready for Invoicing are always invoiced
[Help: `ind.billing_understand_target_date_and_billing_period_count`]. Both need the
Revenue Cloud Billing license.

## Draft, posted and what a run does

Stages of a run: select schedules and assign grouping keys; process keys in parallel
(finished invoices are usable before the run ends); calculate tax (estimated on draft,
actual on posted); update schedules and groups for the next cycle; write the run summary
[Help: `ind.billing_invoice_batch_run`]. Run status is Completed or Failed; add the status
subtype field to the layout to see the stage. Posting later: Invoice Draft to Posted
Status API, the Post Draft Invoice action, or the batch version for a credit application
[Help: `ind.billing_invoices_apis_and_actions`].

Before the first run, find active record-triggered flows and Apex triggers on billing
objects and make them asynchronous; recovery of stranded invoices is in the same article
[Help: `ind.billing_invoice_run_sync_process`].

## Grouping and splitting

- **Invoice group type** on each schedule: Default (one invoice per billing account,
  bill-to contact, currency, payment term, tax engine, legal entity and saved payment
  method), Billing Schedule (its own invoice), or Custom with a key (contract number,
  purchase order, your value, case-insensitive). The default group is applied first, then
  the key [Help: `ind.billing_schedule_invoice_grouping`].
- **Billing arrangements** bill one transaction to several accounts by percentage; each
  arrangement line makes a separate invoice. Review the Split Invoices tab before posting,
  voiding or deleting [Help: `ind.billing_billing_arrangements`,
  `ind.billing_review_split_invoices`]. Repo UI: `Order.RLM_Billing_Arrangement__c`
  [Repo: `cumulusci.yml` → `deploy_post_billing_ui`].

## Suspend, resume and catch-up

- **Suspend** from an Account or schedule group. Charges are deferred, not waived; a run
  with a target date on or after the resumption date bills the deferred periods. The
  suspension is judged as of the target date, not the run date
  [Help: `ind.billing_suspend_and_resume_overview`,
  `ind.billing_understand_billing_suspensions_and_target_date`].
- **Catch-up bill run** advances next billing date, billed and pending amounts for
  transactions a legacy system already billed. Once frequency, target date required, no
  invoices, tax, memos, payments or documents are created [Help: `ind.billing_catch_up_bill_runs`].

## Invoice documents and delivery

- Turn on server-side and batch document generation in Document Generation Settings, then
  Document Generation in Billing Settings; batch is required for PDFs from a run
  [Help: `ind.billing_setup_document_generation`]. The repo lets Billing default the preview
  and document templates and selects only the email template
  [Repo: `cumulusci.yml` → `deploy_billing_template_id_settings` description].
- Generate for a batch, a single invoice, or per billing profile template
  [Help: `ind.billing_invoice_document_generation_batch_and_single`].
- Email goes after posting and before the due date; preferences resolve billing account,
  then legal entity, then org setting
  [Help: `ind.billing_invoice_pdf_document_delivery_through_email`,
  `ind.billing_invoices_email_prerequisites`].
- Template authoring: `document-generation`.

## Correcting an invoice

Void a posted invoice from the record; tax is voided or adjusted at the engine and the
related credit memo status follows the engine response ([tax.md](tax.md)). Delete is
for Draft or Canceled invoices with Billing Operations User; other statuses need a cloned
Billing Admin set with the Delete Invoice and Invoice Lines permission, and Help warns of
data integrity issues [Help: `ind.billing_invoices_void`, `ind.billing_invoice_delete`].
Gapless numbering for invoices and credit memos is a sequence policy
[Help: `ind.billing_sequential_numbering_for_invoices_configure`]; the repo creates them in
`tasks/rlm_billing.py`.

## Read-backs

```sql
SELECT Id, ReferenceEntityId, BilledAmount FROM BillingSchedule
SELECT Id, Status, Balance, InvoiceBatchRunId FROM Invoice
SELECT InvoiceId, ChargeAmount, TaxProcessingStatus FROM InvoiceLine
SELECT Id, BillingBatchSchedulerId FROM InvoiceBatchRun
```

Confirm each run: invoices exist for the expected schedules only, none stuck in a
`... In Progress` status, schedules' next billing date moved, and no duplicate schedules per
order product (a second active flow). Counts and timings: not measured.
