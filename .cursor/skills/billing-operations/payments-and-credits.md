# Billing Operations — Payments, Refunds, Memos and Write-offs

Read this when configuring payment collection, application rules, refunds, credit or debit
memos or write-offs. Collections (plans, promises to pay, dunning, late fees, disputes) is its own
skill: [collections](../collections/SKILL.md). Parent: [SKILL.md](SKILL.md). A read of Help, except
the sections *Measured: Line Level application*, *Measured: unapply* and *Measured: rule-based
application*, and the automatic payment schedule note under *Billing Settings that change
behavior*, which record dated live observations.

Licensing: Salesforce Payments (native or bring-your-own gateways) is part of the Revenue
Cloud Billing license with a cost-per-transaction model, and orgs licensed on or before
July 2025 must ask to add it [Help: ind.billing_payments]. Collections licensing (Billing
Advanced, Marketing Cloud Growth for dunning emails) is in
[collections](../collections/permissions-and-personas.md) and
[collections](../collections/setup-and-operate.md) (Setup, step 6).
Confirm licensing before promising.

## Billing Settings that change behavior

From Setup, Billing Settings [Help: ind.billing_setup_payments_configure] [Help: ind.billing_setup_credit_memo_features_enable]:

- Create Payment Schedules and Payment Schedule Items: automatic, for posted invoices.
  Otherwise create them by hand [Help: ind.billing_payment_schedules_and_payment_schedule_items].
  Of the six `Billing.settings-meta.xml` files, only two set
  `enablePaymentSchedulesAndItemsCreation`: `unpackaged/pre/2_settings`
  sets it false and `unpackaged/post_billing/settings` sets
  it true. No repo file creates a payment schedule treatment or sets its Grouping Source
  [Repo: unpackaged/pre/2_settings/Billing.settings-meta.xml;
  unpackaged/post_billing/settings/Billing.settings-meta.xml].

  Help says: the first time the setting is turned on it creates four default records, Default
  Payment Schedule Policy, Default Payment Schedule Treatment, Default Payment Schedule
  Treatment Detail and Default Payment Schedule Distribution Method
  [Help: ind.billing_setup_payment_schedules_and_payment_schedule_items_enable]; each posted
  invoice then gets a single payment schedule for its whole balance
  [Help: ind.billing_setup_payment_schedules_and_payment_schedule_items_enable]; Grouping
  Source defaults to Invoice, and one account's invoices are grouped into one schedule under
  Grouping Source Account when their due dates fall within the Due Date Window and their
  currency and payment method match [Help: ind.billing_payments_consolidate_invoices].

  Measured on 2026-11-24: the Default Payment Schedule Treatment read Grouping Source
  **Account** and a blank Due Date Window. Two invoices posted for one account with the same due
  date (currency and payment method not recorded) produced one Draft payment schedule, which
  both invoices point to through `PaymentScheduleId`. A second payment schedule with
  `ReferenceEntityId` set to one of those invoices was refused (error
  `INVALID_FIELD_FOR_INSERT_UPDATE`, "We can't create this Payment Schedule because its invoice
  is associated with another Payment Schedule that's in Draft or Open status.").
  [Measured: 2026-11-24, 264, fresh ent-sb0 scratch org, API 68.0] [Open: turn the setting on in a fresh 264 ent-sb0 org with no post_billing deploy and read the Default Payment Schedule Treatment's Grouping Source] [Open: post two invoices for one account with the same due date under Grouping Source Invoice and count the schedules] [Open: under Grouping Source Account, post two invoices whose due dates are N days apart, once under a Due Date Window ≥ N and once under one < N, and count the schedules] [Open: under Grouping Source Account, post two invoices with the same due date and different currencies, then two with different payment methods, and count the schedules] [Open: cancel the automatic Draft schedule, then create one referencing an invoice]
- Retry Failed Payments: needs a default payment retry rule set
  [Help: ind.billing_setup_payment_retry_rules].
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
  ([tax.md](tax.md)) [inferred] [Help: ind.billing_setup_header_tax_enable].
- Rule-Based Credit and Payment Application, with an order and rules (below).
- Level 2 and Level 3 data support, Share Payment Accounts.

## Collect payments

- **Gateway.** Native or third-party (bring your own); saved payment methods per account,
  with a default; externally tokenized methods can be migrated in
  [Help: ind.billing_setup_third_party_payments] [Help: ind.billing_saved_payment_methods] [Help: ind.billing_migrate_saved_payment_methods].
- **Process.** Payment batch runs process payment schedule items through a payment
  scheduler (Billing Batch Schedulers, New Payment Scheduler) and apply the result at the
  application level [Help: ind.billing_payment_runs_schedule]. Ad hoc: Payment Sale,
  Authorization, Capture, Authorization Reversal and Tokenize Payment Method APIs
  [Help: ind.billing_payments_apis].
- **Consolidation.** Posted invoices of one account can share one payment schedule and
  item, which cuts gateway calls and fees [Help: ind.billing_payments_consolidate_invoices].
- **Retries.** A retry rule set holds the default behavior, rules override by error
  category, gateway and raw error code; intervals are Fixed or Staggered; a fixed interval has a
  maximum number of attempts [Help: ind.billing_retry_failed_payments] [Help: ind.billing_setup_payment_retry_rules].
- **Reconciliation.** Document AI extracts payment advice and matches it against bank
  proofs, with its own Data 360 setup [Help: ind.billing_payment_reconciliation].
- Pay Now links let a customer pay as a guest and save the method
  [Help: ind.billing_generate_pay_now_payment_links_for_business_accounts]. The
  self-service portal exists [Help: ind.billing_self_service_portal]; not read in detail.

## Application rules

How a payment or credit memo settles an invoice, when more than one invoice is
open [Help: ind.billing_setup_credit_memos_payments_application_rules]:

- **Order**: Payments First (default) or credits first.
- **Rules**, in the sequence you select: Match ID (the invoice referenced on the credit
  memo or payment), Match Balance (invoice with the same balance), Prioritize Oldest
  Invoices, Prioritize Highest Balance Invoices. Beyond 2,000 invoices only the first rule
  applies. If both Rule-Based Credit and Payment Application and Apply Credits to Posted
  Invoices are on, the rule-based feature wins.
- Match ID ignores a payment's referenced invoice that is Draft, has zero balance, or
  differs in legal entity, account or currency, and falls to the next rule
  [Help: ind.billing_rules_based_credits_payments_application].

**Settings code.** The value is stored coded: the build deploys `ruleBasedCrAndPymtAppln` =
`{"first":"Payments","rules":["EA","OI","HI"]}` (the metadata has no separate enable element)
[Repo: unpackaged/post_billing_id_settings/settings/Billing.settings-meta.xml]
[Repo: scripts/txn_data_harness/docs/contracts-billing-settlement.md]. The response's `appliedRules`
named Match Balance and Prioritize Oldest Invoices
[Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]. That EA is Match Balance and OI is
Prioritize Oldest Invoices [inferred: from the codes and their order; the response carries names, not codes],
and HI is Prioritize Highest Balance Invoices [inferred: from the codes and their order; no call reported a third rule]. The code for Match ID was
not seen. Endpoint behavior:
*Measured: rule-based application* below.

Decision: choose Match ID when customers pay with a reference, Match Balance or oldest
otherwise. Ask what the customer's finance team expects for unreferenced cash
[inferred].

## Measured: Line Level application

What the APIs did with Credit, Payment and Refund Application Level set to Line Level. Each was
observed on the build(s) its tags name, so re-measure on the release patch in hand before relying on it; error text
and object names may change between patches. Header Level was not measured.
[Measured: 2026-10-15, 264, harness build, API 68.0, Line Level]
[Measured: 2026-11-24, 264, fresh ent-sb0 scratch org, API 68.0, Line Level] Details first recorded on 2026-11-24 carry their own tag.

- **Apply a payment.** `POST /services/data/v68.0/commerce/billing/payments/{id}/actions/apply` with an invoice id
  as `appliedToId` failed (error `INVALID_FIELD`, "Specify an InvoiceLineId as the appliedToId
  because the Credit Application Level is Invoice Line."; the error code was first recorded
  [Measured: 2026-11-24, 264, fresh ent-sb0 scratch org, API 68.0]). With an invoice line id the call created a
  `PaymentLineInvoiceLine` (Type Applied) and no `PaymentLineInvoice`.
- **Credit an invoice.** `POST /services/data/v68.0/commerce/invoicing/invoices/{id}/actions/credit` on a posted
  invoice, copying from the invoice lines, created a `CreditMemoLineInvoiceLine` and no
  `CreditMemoInvApplication`.
- **Balance and test payments.** `Invoice.Balance` rolled up as invoice amount minus applied
  credits minus applied payments (250 less a 50 credit and a 100 payment left 100). A payment
  could be created directly as a record (`Amount`, `Status` Processed, `Type` Sale,
  `ProcessingMode` External, `AccountId`) with no gateway.
- **Payment Schedule Item.** One, on a Payment Schedule with no reference entity, could not
  request more than its payment's balance (error `INVALID_OPERATION`, "The payment balance
  can't be less than requested amount on the Payment Schedule Item. Provide a payment with
  sufficient balance."). A request equal to the balance was accepted. The schedule without a
  reference entity, the error code, the text after "requested amount" and the equal request
  were first recorded
  [Measured: 2026-11-24, 264, fresh ent-sb0 scratch org, API 68.0].
- **The shipped Apply Payment flow.** The Apply Payment quick action launches the flow
  `RLM_Apply_Payments_on_Invoice`, which calls the subflow `RLM_Apply_Payment_To_Invoice_Lines`.
  The subflow spreads a payment over the invoice's open lines in record Id order, capped at the
  smaller of the payment's balance and the invoice's balance. Copies ship in the
  billing, payments and collections bundles. [Repo: unpackaged/post_billing/,
  unpackaged/post_payments/, unpackaged/post_collections/] On the 2026-10-15 harness build the subflow spread a
  payment over a three-line invoice with no header-level rows. [Measured: 2026-10-15, 264,
  harness build, API 68.0, Line Level] Called directly
  (`/services/data/v68.0/actions/custom/flow/RLM_Apply_Payment_To_Invoice_Lines`, inputs
  `paymentId`, `invoiceId`), the subflow applied a 1,000 payment to lines of 250, 250 and 1,200 as 250,
  250 and 500. A second 1,000 payment on the remaining 700 applied 700 and reported
  `unappliedAmount` 0, while the payment kept a balance of 300.
  [Measured: 2026-11-24, 264, fresh ent-sb0 scratch org, API 68.0] That output is what was left
  of the capped amount when the lines ran out of balance, not the payment's remaining balance
  [Repo: unpackaged/post_billing/flows/RLM_Apply_Payment_To_Invoice_Lines.flow-meta.xml].

Read-back after any of these: query the line-level junction (`PaymentLineInvoiceLine`,
`CreditMemoLineInvoiceLine`) and confirm the header-level one (`PaymentLineInvoice`,
`CreditMemoInvApplication`) is empty. Rows in the wrong one mean the org is at the other level.

## Measured: unapply

The first measurement was by the harness
[Repo: scripts/txn_data_harness/docs/contracts-billing-settlement.md → Unapply]; the tags below say
which run showed each fact. Header Level unapply, reapplying with the explicit apply action after an
unapply, and voiding a credit memo were not measured.

- **Endpoints.** `POST /services/data/v68.0/commerce/billing/payments/{PaymentId}/paymentlines/{PaymentLineInvoiceLine Id}/actions/unapply`
  (body `{"comments": ...}`) and
  `POST /services/data/v68.0/commerce/invoicing/credit-memo-line-invoice-line/{CreditMemoLineInvoiceLine Id}/actions/unapply`
  (body `{}`). [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]
- **Synchronous and whole-row.** Rows and rollups had changed when the call returned; neither body
  takes an amount. [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]
- **Rows.** The original row stays `Type` Applied with `Amount` unchanged and `UnappliedStatus` set
  to Yes. A new row is added: `Type` Unapplied, the same `Amount`, line and source, `UnappliedStatus`
  NA, and `RelatedPaymentLineInvcLineId` or `RelatedCrMemoLineInvcLineId` naming the original. Read
  back by filtering on those Related fields; do not read the Applied row alone as still in force.
  [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]
- **Balances.** Invoice, line, payment and credit memo balances return to what they were before the
  application, and `Invoice.SettlementLevel` goes back to null when nothing remains applied.
  [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0] Repeated on a run with invoice 300, credit 30 and a payment of 135 applied as two
  line rows (100 and 35): all three rows unapplied, the invoice `Balance` returned to 300 and
  `SettlementLevel` to null. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, Line Level]
- **Twice, and either order.** A second unapply of the same row is HTTP 400
  `INVALID_FIELD_FOR_INSERT_UPDATE` and writes nothing; the credit or the payment can be unapplied
  first. [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]
- **The freed balances do not stay open.** The account's next posted invoice absorbed both the freed
  payment and the memo. [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]

The harness wraps this as `cli unapply` (`txn-data-harness`).

## Measured: rule-based application

`POST /services/data/v68.0/revenue/billing/transactions/actions/apply` with
`{"accountId": ..., optional "targetDate": "YYYY-MM-DD"}`.

- **Synchronous.** The response carries `appliedRules` (Help names, not the settings codes),
  `isSuccess` and `rulesApplicationSummary` (`areAllInvoicesConsidered`, `fetchedCreditMemosCount`,
  `fetchedPaymentsCount`, `totalCreditMemoApplications`, `totalPaymentApplications`). The rows are
  ordinary line-level rows. [Measured: 2026-11-26, 264, scratch, Line Level, API 68.0]
- **Match Balance first.** A payment equal to an open candidate's balance went to that invoice with
  `appliedRules` Match Balance alone. An unmatched payment reported Match Balance then Prioritize
  Oldest Invoices. [Measured: 2026-11-26, 264, scratch, Line Level, API 68.0]
- **Candidates.** Without `targetDate` only invoices posted that UTC day were candidates (inferred
  from calls on one day, not repeated):
  two invoices posted the previous day that matched a payment's balance exactly were skipped, and
  passing their date made them match. [Measured: 2026-11-26, 264, scratch, Line Level, API 68.0]
  The dev guide says `targetDate` selects invoices posted on or after it [Dev guide: connect-resources-rules-application].
- **Nothing open** gives `isSuccess` true, `appliedRules` empty and every count 0. **Nothing
  eligible** (an open payment and a `targetDate` after every invoice) gives `isSuccess` false with
  "We couldn't find eligible invoices to apply rules-based credits and payments" under `errors`, no
  `errorCode`, and a 2xx status, so check `isSuccess`, not the HTTP status. [Measured: 2026-11-26,
  264, scratch, API 68.0]
- **Where an unmatched payment lands is not settled.** Each went to the highest-balance candidate
  posted that day, earliest created among equals, not to the run's own invoice
  [Measured: 2026-11-26, 264, scratch org, Line Level, API 68.0]. On
  2026-11-27 a payment of 135, one of 20 and a credit of 30 (open after an unapply) with seven
  invoices all posted the same UTC day reported Match Balance and Prioritize Oldest Invoices, and all
  three applications went to the invoice (300) the run's own payment and credit had been applied to
  before the unapply, not to the oldest (250 each) or the highest balance (500 each).
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, Line Level] Whether the rule order, the
  prior application or record order decided it: [Open: repeat with invoices posted on different UTC
  days, and with no prior application].
- **Post-time absorption.** Help's worked example has the rules run when invoices post; whether the
  absorption measured at posting follows them: [Open: post an invoice with an open payment and
  compare to a rule-based call on the same data].
- Not measured: ties on Match Balance, Credits First, Match ID, a credit memo alone, Header Level,
  more than 2,000 invoices.

The harness wraps this as `cli apply-rules` (`txn-data-harness`).

## Credit memos

- Reduce an invoice after an amendment or cancellation: negative invoice lines convert to
  credit memo lines when posted
  [Help: ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines].
- Credit specific invoice lines: Create and Apply Credit Memo on a posted invoice
  [Help: ind.billing_create_and_apply_credit_memos].
- Credit with no invoice yet: standalone credit memo, then apply
  [Help: ind.billing_credit_memos_standalone_user_interface_create].
- Cancel a posted credit: void an unapplied posted memo. Unstick a Pending or Error memo:
  recover it [Help: ind.billing_credit_memos_void_recover].

Credit amounts are 0 up to the line balance; tax is
automatic from the credit amount, a typed credit tax amount, or none
[Help: ind.billing_create_and_apply_credit_memos]. Voiding a posted credit memo creates
a posted debit memo to offset it for the ledger and carries tax detail
[Help: ind.billing_credit_memos_void_recover]. APIs and flow actions cover create standalone,
create and apply, apply and unapply (header and line level) and convert negative invoice
lines to a posted credit memo
[Help: ind.billing_credit_memos_apis_and_actions]. What an amendment's credit amounts
are: `asset-lifecycle-changes` and `rlm-business-apis` → `backdated-asset-lifecycle.md`.

## Debit memos

A debit memo adds a charge: undercharge correction, cancellation or suspension fee, late
payment fee. Created in Draft, with a reason code you add to the Reason Code picklist first;
a posted debit memo can become a draft invoice through the Invoice Ingestion API
[Help: ind.billing_debit_memo_explain] [Help: ind.billing_debit_memo_create] [Help: ind.billing_invoice_creation]. Orgs created before Winter '26 need the Debit Memos and
Debit Memo Lines tabs set to Default On [Help: ind.billing_debit_memo_create].

## Refunds

- **Referenced refund**: triggered by an amendment or cancellation of a fully settled
  invoice; paid to the original payment method; needs the original payment tied to a
  gateway, with both Issue Refunds and Settle Balances and Apply Credits to Posted
  Invoices turned on.
- **Unreferenced refund**: manual, to settle an available credit balance; paid to a saved
  payment method from the request, then the memo, then the billing account or arrangement;
  needs a credit balance, a supported third-party gateway that processes unreferenced
  refunds, and a saved card payment method on the credit memo or billing account.

[Help: ind.billing_refunds_overview] [Help: ind.billing_refund_orchestration] [Help: ind.billing_unreferenced_refunds] [Help: ind.billing_issue_unreferenced_refund]. Header-level
application refunds against the memo; line-level spreads across lines with an open balance,
largest first [Help: ind.billing_unreferenced_refunds] [Help: ind.billing_issue_unreferenced_refund]. Ask whether the customer wants refunds to cash
automatically or credit balances held [inferred].

## Write-off, disputes, collections

Collections, dunning, disputes and the write-off and late-fee operations are in the
[collections](../collections/SKILL.md) skill. What stays here is the billing-side effect:

- **Write off** an invoice with a credit memo whose Reason Code you add first (such as bad
  debt); it updates write-off fields on the invoice, and afterwards no further credits or
  payments can be applied or unapplied. Use the Write-Off API or a flow action
  [Help: ind.billing_write_off_invoices_impact] [Help: ind.billing_write_off_invoices_invoke_action]. The Reason Code picklists are empty on a fresh
  build, so the call returns INVALID_API_INPUT until you add a value ([collections](../collections/SKILL.md) →
  `setup-and-operate.md`).
- **Invoice aging** components show buckets and overdue counts on Account and Order pages
  [Help: ind.billing_invoice_aging]. The repo ships aging, dispute and collections
  components [Repo: cumulusci.yml → deploy_post_billing_ui].
- **Settlements Central** is one console over invoices, payments, credit memos and debit
  memos [Help: ind.billing_settlements_central].

## Read-backs

```sql
SELECT Id, Status, Balance FROM Invoice
SELECT Id, Status, Balance FROM CreditMemo
SELECT Id, Amount, Balance FROM Payment
SELECT Id, Status, RequestedAmount, ProcessedAmount FROM PaymentScheduleItem
SELECT Id, Amount, Balance FROM Refund
```

Collection plan read-backs: [collections](../collections/verification.md).

Check: an invoice balance falls by exactly the memo or payment applied (at the chosen
level); a voided credit memo has a matching posted debit memo; a write-off sets the
invoice's write-off fields; retries stop at the configured maximum. Timings and volumes:
not measured. Use a sandbox gateway; do not run live payment calls against a customer
gateway to verify.
