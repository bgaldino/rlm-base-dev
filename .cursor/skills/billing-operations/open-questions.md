# Billing Operations — Open Questions

Read this before promising any of these behaviors. Parent: [SKILL.md](SKILL.md). Each item is a
question raised in field work and **not measured here**; where an article covers the area it is
named, but nothing below is a measured fact. Each says what check would settle it. Measure one,
then move it into the sub-file for its stage with a `[Measured: ...]` tag.

## Invoicing

- **On-demand generation size.** A limit of about 200 billing schedules and 200 lines per on-demand
  invoice was reported, with a workaround of splitting by schedule. [Open: generate on demand for an
  account with more than 200 schedules and read the error] [Help: ind.billing_invoice_generation]
- **Invoice Creation API inputs, and the Preview API.** The Preview API was reported to cover a
  single order. [Open: call both with two orders and read what each returns]
- **Custom invoice group key.** Automating the key on schedules from a flow or an API. [Open: set
  the key on two schedules and read the grouping] [Help: ind.billing_schedule_invoice_grouping]
- **Suspend and resume.** What happens to schedules, the next invoice date and already-drafted
  invoices. [Open: suspend mid-term, run an invoice run, resume and read the schedules] [Help:
  ind.billing_suspend_and_resume]
- **Unit price on an invoice line.** Reported to equal line total divided by quantity, and lines in
  the same period reported to merge. [Open: invoice two same-period lines and compare]
- **Billing schedule start.** Reported to follow the order item's start date, with deferral options.
  [Open: activate an order whose start is in the future and read the schedule]
- **Order-to-schedule flow entry conditions.** What stops a schedule from being created for an
  activated order. [Open: activate orders that vary one condition at a time]
- **Invoice email sender.** Reported to be the running user. [Open: run as two users and read the
  sent email]
- **Outbound hooks for invoice delivery.** [Open: list the outbound hooks an org offers for invoice delivery]
- **Reporting and analytics coverage** of billing objects. [Open: list the report types an org
  offers for Invoice, Payment and CreditMemo]

## Credits, memos and tax

- **Tax-only credits and `ManualOverride`** on the credit invoice API. [Open: credit an invoice
  for tax only and send the override] [Dev guide: connect-requests-credit-invoice-input]
- **Credit memo addresses** reported to need tax strategy Calculate, and a change to voiding a
  zero-amount memo. [Open: void a zero-amount memo and create a memo with a tax strategy other than Calculate, then read the results]
- **Card fee as a debit memo** created by a flow on Payment. [Open: build and run the flow]
- **A platform late-fee action** (not the repo's `RLM_Charge_Late_Fee`, covered in
  [collections](../collections/setup-and-operate.md)). [Open: is a platform late-fee action hidden in 264? Read the CollectionPlan quick actions and layout on a fresh 264 build]
- **Chargebacks and disputes.** [Open: record a card chargeback against a payment and read the payment and invoice]

## Payments

- **Payment retries on collection-plan items** and the dunning-email sending domain
  (see [collections](../collections/setup-and-operate.md)). [Open: run a retry on a plan item and send a dunning reminder on a disposable org, then read the results]
- **Payment method sets, the payment link flow and `PaymentRunMatchingValue` routing.** [Open:
  configure a set and run a payment scheduler] [Dev guide: connect-resources-create-payment-scheduler]
- **Reconciling a manual payment against a promise to pay**, and what a batch run does to a promise
  item on an already settled invoice (see [collections](../collections/object-model.md)).
  [Open: create a promise, post a manual payment on its invoice, run the payment batch and read the items]

## Accounting

- **General ledger rules** cannot be targeted at orders (reported), and `TransactionJournal` is
  reported createable. [Open: describe TransactionJournal and try an order-targeted rule]
- **A GL rule criterion on a custom field.** [Open: add the field and try]
- **Closed accounting periods** were reported not to block quote or order creation. [Open: close a
  period, then create a quote and an order dated inside it]
