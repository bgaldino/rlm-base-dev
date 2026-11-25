# Billing Operations — Payments, Refunds, Memos and Collections

Read this when configuring payment collection, application rules, refunds, credit or debit
memos, write-offs or collections. Parent: [SKILL.md](SKILL.md). A read of Help, except
the section *Measured: Line Level application* and the automatic payment schedule note under
*Billing Settings that change behavior*, which record dated live observations.

Licensing: Salesforce Payments (native or bring-your-own gateways) is part of the Revenue
Cloud Billing license with a cost-per-transaction model, and orgs licensed on or before
July 2025 must ask to add it [Help: `ind.billing_payments`]. Collections needs the Billing
license and Marketing Cloud Growth edition for dunning emails
[Help: `ind.billing_collections_dunning_process_setup`]. Confirm licensing before promising.

## Billing Settings that change behavior

From Setup, Billing Settings [Help: `ind.billing_setup_payments_configure`,
`ind.billing_setup_credit_memo_features_enable`]:

- Create Payment Schedules and Payment Schedule Items: automatic, for posted invoices.
  Otherwise create them by hand [Help: `ind.billing_payment_schedules_and_payment_schedule_items`].
  By default this makes one payment schedule and item per posted invoice; invoices of one
  account are grouped into one when the payment schedule treatment's Grouping Source is
  Account, within its Due Date Window, and Billing then records the schedule in the invoice's
  Payment Schedule field [Help: `ind.billing_payments_consolidate_invoices`]. Measured on a
  fresh build whose default treatment (Default Payment Schedule Treatment, trigger
  InvoicePosted) had Grouping Source **Account** and a blank Due Date Window; the repo's data
  plans do not load it. Two invoices of 250 and 1,700 for one account, ingested and posted
  within a second with the same due date, got one Draft payment schedule of 1,950 with one
  Draft item of 1,950, its processing date the invoices' due date. Both invoices'
  `PaymentScheduleId` pointed at it; its `ReferenceEntityId` was blank. A second payment
  schedule created with `ReferenceEntityId` set to one of those invoices was refused (error
  `INVALID_FIELD_FOR_INSERT_UPDATE`, "We can't create this Payment Schedule because its invoice
  is associated with another Payment Schedule that's in Draft or Open status.").
  [Measured: 2026-11-24, 264, fresh build, API 68.0] So, on an org set up like this, a script
  that creates its own schedule after posting must deal with the automatic one first: find it
  through the invoice's `PaymentScheduleId`. Canceling or reusing it was not tried, nor the
  default Invoice grouping, nor invoices posted apart.
- Retry Failed Payments: needs a default payment retry rule set
  [Help: `ind.billing_setup_payment_retry_rules`].
- Application of Payments to Posted Invoices: standalone processed payments apply during
  an invoice run.
- Issue Refunds and Settle Balances: automatic refund when a fully settled invoice is
  amended or canceled.
- Conversion of Negative Invoice Lines to Credit Memo Lines, and application of the
  converted memos to the invoice.
- Apply Credits to Posted Invoices: automatic application of available credit balances,
  with the default flow used to apply the credit memo to invoices.
- Credit, Payment and Refund Application Level: **Line Level** (default) or **Header
  Level**. Decide this early: it changes where balances live and how header tax works
  ([tax.md](tax.md)) [inferred from Help: `ind.billing_setup_header_tax_enable`].
- Rule-Based Credit and Payment Application, with an order and rules (below).
- Level 2 and Level 3 data support, Share Payment Accounts.

## Collect payments

- **Gateway.** Native or third-party (bring your own); saved payment methods per account,
  with a default; externally tokenized methods can be migrated in
  [Help: `ind.billing_setup_third_party_payments`, `ind.billing_saved_payment_methods`,
  `ind.billing_migrate_saved_payment_methods`].
- **Process.** Payment batch runs process payment schedule items through a payment
  scheduler (Billing Batch Schedulers, New Payment Scheduler) and apply the result at the
  application level [Help: `ind.billing_payment_runs_schedule`]. Ad hoc: Payment Sale,
  Authorization, Capture, Authorization Reversal and Tokenize Payment Method APIs
  [Help: `ind.billing_payments_apis`].
- **Consolidation.** Posted invoices of one account can share one payment schedule and
  item, which cuts gateway calls and fees [Help: `ind.billing_payments_consolidate_invoices`].
- **Retries.** A retry rule set holds the default behavior, rules override by error
  category, gateway and raw error code; intervals are Fixed or Staggered; a fixed interval has a
  maximum number of attempts [Help: `ind.billing_retry_failed_payments`,
  `ind.billing_setup_payment_retry_rules`].
- **Reconciliation.** Document AI extracts payment advice and matches it against bank
  proofs, with its own Data 360 setup [Help: `ind.billing_payment_reconciliation`].
- Pay Now links let a customer pay as a guest and save the method
  [Help: `ind.billing_generate_pay_now_payment_links_for_business_accounts`]. The
  self-service portal exists [Help: `ind.billing_self_service_portal`]; not read in detail.

## Application rules

How a payment or credit memo settles an invoice, when more than one invoice is
open [Help: `ind.billing_setup_credit_memos_payments_application_rules`]:

- **Order**: Payments First (default) or credits first.
- **Rules**, in the sequence you select: Match ID (the invoice referenced on the credit
  memo or payment), Match Balance (invoice with the same balance), Prioritize Oldest
  Invoices, Prioritize Highest Balance Invoices. Beyond 2,000 invoices only the first rule
  applies. If both Rule-Based Credit and Payment Application and Apply Credits to Posted
  Invoices are on, the rule-based feature wins.
- Match ID ignores a payment's referenced invoice that is Draft, has zero balance, or
  differs in legal entity, account or currency, and falls to the next rule
  [Help: `ind.billing_rules_based_credits_payments_application`].

Decision: choose Match ID when customers pay with a reference, Match Balance or oldest
otherwise. Ask what the customer's finance team expects for unreferenced cash
[inferred from Help].

## Measured: Line Level application

What the APIs did with Credit, Payment and Refund Application Level set to Line Level. Each is
one observation, so re-measure on the release patch in hand before relying on it; error text
and object names may change between patches. Header Level was not measured.
[Measured: 2026-10-15, 264, harness build, API 68.0, Line Level; repeated 2026-11-24, 264,
fresh build]

- **Apply a payment.** `POST /services/data/v68.0/commerce/billing/payments/{id}/actions/apply` with an invoice id
  as `appliedToId` failed (error `INVALID_FIELD`, "Specify an InvoiceLineId as the appliedToId
  because the Credit Application Level is Invoice Line."). With an invoice line id it created a
  `PaymentLineInvoiceLine` (Type Applied) and no `PaymentLineInvoice`.
- **Credit an invoice.** `POST /services/data/v68.0/commerce/invoicing/invoices/{id}/actions/credit` on a posted
  invoice, copying from the invoice lines, created a `CreditMemoLineInvoiceLine` and no
  `CreditMemoInvApplication`.
- **Balance and test payments.** `Invoice.Balance` rolled up as invoice amount minus applied
  credits minus applied payments (250 less a 50 credit and a 100 payment left 100). A payment
  could be created directly as a record (`Amount`, `Status` Processed, `Type` Sale,
  `ProcessingMode` External, `AccountId`) with no gateway.
- **Payment Schedule Item.** One, on a Payment Schedule with no reference entity, could not
  request more than its payment's balance (error `INVALID_OPERATION`, "The payment
  balance can't be less than requested amount on the Payment Schedule Item. Provide a payment
  with sufficient balance."; the 2026-10-15 record quoted only the first clause). A request
  equal to the balance was accepted.
- **The shipped Apply Payment flow.** The Apply Payment quick action launches the flow
  `RLM_Apply_Payments_on_Invoice`, which calls the subflow `RLM_Apply_Payment_To_Invoice_Lines`.
  The subflow spreads a payment over the invoice's open lines in record Id order, capped at the
  smaller of the payment's balance and the invoice's balance. Copies ship in the
  billing, payments and collections bundles. [Repo: `unpackaged/post_billing/`,
  `unpackaged/post_payments/`, `unpackaged/post_collections/`] Called directly
  (`/actions/custom/flow/RLM_Apply_Payment_To_Invoice_Lines`, inputs `paymentId`, `invoiceId`),
  it applied a 1000 payment to lines of 250, 250 and 1200 as 250, 250 and 500, with no
  header-level rows. A second 1000 payment on the remaining 700 applied 700 and reported
  `unappliedAmount` 0: that output is what is left of the capped amount, not of the payment,
  which kept a balance of 300.

Read-back after any of these: query the line-level junction (`PaymentLineInvoiceLine`,
`CreditMemoLineInvoiceLine`) and confirm the header-level one (`PaymentLineInvoice`,
`CreditMemoInvApplication`) is empty. Rows in the wrong one mean the org is at the other level.

## Credit memos

- Reduce an invoice after an amendment or cancellation: negative invoice lines convert to
  credit memo lines when posted
  [Help: `ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines`].
- Credit specific invoice lines: Create and Apply Credit Memo on a posted invoice
  [Help: `ind.billing_create_and_apply_credit_memos`].
- Credit with no invoice yet: standalone credit memo, then apply
  [Help: `ind.billing_credit_memos_standalone_user_interface_create`].
- Cancel a posted credit: void an unapplied posted memo. Unstick a Pending or Error memo:
  recover it [Help: `ind.billing_credit_memos_void_recover`].

Credit amounts are 0 up to the line balance; tax is
automatic from the credit amount, a typed credit tax amount, or none
[Help: `ind.billing_create_and_apply_credit_memos`]. Voiding a posted credit memo creates
a posted debit memo to offset it for the ledger and carries tax detail
[Help: `ind.billing_credit_memos_void_recover`]. APIs and flow actions cover create standalone,
create and apply, apply and unapply (header and line level) and convert negative invoice
lines to a posted credit memo
[Help: `ind.billing_credit_memos_apis_and_actions`]. What an amendment's credit amounts
are: `asset-lifecycle-changes` and `rlm-business-apis` → `backdated-asset-lifecycle.md`.

## Debit memos

A debit memo adds a charge: undercharge correction, cancellation or suspension fee, late
payment fee. Created in Draft, with a reason code you add to the Reason Code picklist first;
a posted debit memo can become a draft invoice through the Invoice Ingestion API
[Help: `ind.billing_debit_memo_explain`, `ind.billing_debit_memo_create`,
`ind.billing_invoice_creation`]. Orgs created before Winter '26 need the Debit Memos and
Debit Memo Lines tabs set to Default On [Help: `ind.billing_debit_memo_create`].

## Refunds

- **Referenced refund**: triggered by an amendment or cancellation of a fully settled
  invoice; paid to the original payment method; needs the original payment tied to a
  gateway, with both Issue Refunds and Settle Balances and Apply Credits to Posted
  Invoices turned on.
- **Unreferenced refund**: manual, to settle an available credit balance; paid to a saved
  payment method from the request, then the memo, then the billing account or arrangement;
  needs a credit balance, a supported third-party gateway that processes unreferenced
  refunds, and a saved card payment method on the credit memo or billing account.

[Help: `ind.billing_refunds_overview`, `ind.billing_refund_orchestration`,
`ind.billing_unreferenced_refunds`, `ind.billing_issue_unreferenced_refund`]. Header-level
application refunds against the memo; line-level spreads across lines with an open balance,
largest first [Help: `ind.billing_unreferenced_refunds`,
`ind.billing_issue_unreferenced_refund`]. Ask whether the customer wants refunds to cash
automatically or credit balances held [inferred from Help].

## Write-off, disputes, collections

- **Write off** an invoice with a credit memo whose Reason Code you add first (such as bad
  debt); it updates write-off fields on the invoice, and afterwards no further credits or
  payments can be applied or unapplied. Use the Write-Off API or a flow action
  [Help: `ind.billing_write_off_invoices_impact`,
  `ind.billing_write_off_invoices_invoke_action`].
- **Disputes**: Dispute Management is installed from service process templates and
  needs the Revenue Cloud Billing license [Help: `ind.billing_dispute_management_enable`].
- **Collections**: a collection plan per account with an item per overdue invoice; dunning
  orchestration runs Dynamic Revenue Orchestrator templates (reminder, due notice,
  suspension notice, escalation), payment promises can create up to three payment
  schedule items, and uncollectible invoices can be written off
  [Help: `ind.billing_collections`, `ind.billing_dunning_orchestration_enable`,
  `ind.billing_collection_plan_payment_promise_collect`]. Orchestration step design:
  `dro-plans`. Collections and Recovery is a separate Help area (`ind.collections.htm` and its
  children: console app, portal, payment plans, direct debit, risk scores) whose editions page
  lists Financial Services Cloud and Automotive Cloud, not Revenue Cloud
  [Help: `ind.collections_editions_permissions`]; Billing's workflow above is in
  `ind.billing_collections` and `ind.billing_collections_overview`.
- **Invoice aging** components show buckets and overdue counts on Account and Order pages
  [Help: `ind.billing_invoice_aging`]. The repo ships aging, dispute and collections
  components [Repo: `cumulusci.yml` → `deploy_post_billing_ui`].
- **Settlements Central** is one console over invoices, payments, credit memos and debit
  memos [Help: `ind.billing_settlements_central`].

## Read-backs

```sql
SELECT Id, Status, Balance FROM Invoice
SELECT Id, Status, Balance FROM CreditMemo
SELECT Id, Amount, Balance FROM Payment
SELECT Id, Status, RequestedAmount, ProcessedAmount FROM PaymentScheduleItem
SELECT Id, Amount, Balance FROM Refund
SELECT Id, Status, Duedate FROM CollectionPlan
```

Check: an invoice balance falls by exactly the memo or payment applied (at the chosen
level); a voided credit memo has a matching posted debit memo; a write-off sets the
invoice's write-off fields; retries stop at the configured maximum. Timings and volumes:
not measured. Use a sandbox gateway; do not run live payment calls against a customer
gateway to verify.
