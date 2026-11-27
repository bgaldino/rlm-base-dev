# Collections — Object Model

Read this to map a collections concept to an object, field or picklist. Parent:
[SKILL.md](SKILL.md). Schema detail for the billing objects: `revenue-cloud-data-model` →
`domains/billing.md`; confirm any field below with `sf sobject describe -s <Object> -o <sf-alias>`.

## The records

| Concept | Object | Notes |
|---|---|---|
| Collection plan | `CollectionPlan` | One work item for an account's overdue invoices. `Name` is an auto-number, so a record cannot carry a test-name prefix. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] |
| Plan item | `CollectionPlanItem` | One invoice on a plan (`InvoiceId`); Help adds up to 10 invoices per run of the Create Collection Plan Items For Invoices flow [Help: ind.billing_collection_plans_and_plan_items_create]. |
| Reason | `CollectionPlanReason` | The build seeds CPR01 to CPR05 [Repo: scripts/apex/seedCollectionsCaseMatrix.apex]; a fresh build holds 5 and no plans [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. |
| Promise to pay | `PaymentSchedule` (Type PromiseToPay) + `PaymentScheduleItem` | Linked to the plan by `ReferenceEntityId`, `UsageType` CollectionPlan [Repo: unpackaged/post_collections/flows/RLM_Create_Promise_to_Pay.flow-meta.xml]. |
| Dispute | `Case` (and Dispute, a license-gated object) | The repo's collections flow creates a Case [Repo: unpackaged/post_collections_case_flow/flows/RLM_Create_Case_for_Collection.flow-meta.xml]; Dispute Management is a separate Help feature [Help: ind.billing_disputes_overview] [Help: ind.billing_dispute_management_enable]. |
| Follow-up | `Task` (`WhatId` the plan or invoice) | Collector to-dos. |
| Late fee | `DebitMemo` | Intended output of the late-fee action, which has not been run; see [setup-and-operate.md](setup-and-operate.md). |
| Write-off | `CreditMemo` (reason code) + invoice write-off fields | Help: a credit memo whose Reason Code you add first updates the invoice's write-off fields, after which no more credits or payments can be applied or unapplied [Help: ind.billing_write_off_invoices_impact]. |
| Receivable | `Invoice` (`Balance`, `DueDate`, `Status`) | Posted invoices only are receivables; see below. |

## CollectionPlan fields that matter

- **Writable by plain DML, no automation behind them:** `DaysPastDue`, `InitialDueAmount`,
  `PromiseToPayCount`, `IsClosed`, `ClosedDate`. Updating each was accepted and nothing fired. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]
  Help says the same of `DaysPastDue`: it is not calculated, you enter it
  [Help: ind.billing_collection_plans_and_plan_items_create].
- **Read-only:** `TotalInvoiceBalance` is neither createable nor updateable. After two items on two
  250 invoices it rolled up to 500 immediately; `DaysPastDue` and `InitialDueAmount` stayed null.
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]
- **Picklists empty on a fresh build:** `Status` and `CollectionPlanSegment`, and the Credit Memo and
  Debit Memo `ReasonCode`. A null Status is what the platform leaves, and no repo file adds values
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. The Collections and Recovery Help adds Active and Pending to Status
  [Help: ind.collections_add_cpstatus_picklist_values]
  [Open: confirm Billing collections uses the same values].
- **Due date is `Duedate`** (lower-case d). A payment batch run keys on the item's
  `TargetPaymentProcessingDate`, not the plan's `Duedate` or `DaysPastDue`
  [Help: ind.billing_collection_plan_payment_promise_collect].
- `OverdueRiskIndicator` is the only plan field the managed specialist set grants field access to
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0].
- The console's Collection Progress chart needs field permission on `CollectionPlanItem.InitialDueAmount`
  [Help: ind.billing_collections_specialist_console_setup]. No repo permission set grants it:
  `RLM_CollectionsUI` grants only `CollectionPlan.InitialDueAmount`, read
  [Repo: unpackaged/post_collections/permissionsets/RLM_CollectionsUI.permissionset-meta.xml], and the
  managed specialist set grants no `InitialDueAmount` field
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0].

## Promise to pay

- A REST create of a `PaymentSchedule` (Type PromiseToPay, UsageType CollectionPlan,
  `ReferenceEntityId` the plan) and four `PaymentScheduleItem` rows all succeeded: **the platform
  does not enforce three items**. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] The limit is in the shipped flow, which blocks when the
  schedule count equals `MaximumPromisetoPayCount` and creates 1 to 3 items
  [Repo: unpackaged/post_collections/flows/RLM_Create_Promise_to_Pay.flow-meta.xml]
  [Help: ind.billing_collection_plan_payment_promise_collect].
- Item required fields: `PaymentScheduleId`, `RequestedAmount`, `TargetPaymentProcessingDate`,
  `Status`. The date field is `TargetPaymentProcessingDate`. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]
- Item `Status` values: Draft, Ready for Processing, Processing, Processed, Applied, Failed,
  Apply Failed, Canceled, Approval Pending, Deferred Payment, Payment Waived Off. `Pending` is not one.
  [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]
- `PaymentSchedule` has no `Name` column. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]
- A posted invoice also gets an automatic Draft payment schedule (see `billing-operations` →
  `payments-and-credits.md`); do not mistake those for promises: filter on Type.
- A user sees schedules only with Payment Operations or Payment Admin
  [Help: ind.billing_collection_plan_payment_promise_collect]; the specialist set reads and writes
  `PaymentSchedule` and items [Measured: 2026-11-27, 264, fresh scratch build, API 68.0].
- Promise lifecycle after creation (item states on a settled invoice, batch cancel, reconciling a
  manual payment against a promised one): [Open: not measured; create a promise, post a payment on
  the invoice, run the payment batch and read the items].

## Invoice facts a collections figure rests on

- `Invoice` is not insertable by DML and `Balance` is not updateable, so Apex tests cannot build
  invoices; use query-shape assertions or an org with billing runs
  [Measured: 2026-11-26, 264, fresh scratch].
- `Status` values include Draft, Draft In Progress, Pending, Posting In Progress, Posted, Canceled,
  Error, Void In Progress, Voided, Split In Progress. Count receivables as
  `Status = 'Posted' AND Balance > 0`. [Measured: 2026-11-26, 264, fresh scratch]
- `DaysInvoiceOverdue` is platform-calculated and was null on all Posted invoices checked (none was
  overdue); its value on an overdue invoice is [Open: age an invoice past due and read it].

## Case and dispute sharing

- Case org-wide default is Private on a fresh build (`DefaultCaseAccess` None), Account is
  Read/Write, CollectionPlan is internal ReadWrite and external Private. A collector sees only
  cases they own or that are shared, so a disputed list is per user by design.
  [Measured: 2026-11-26, 264, fresh scratch]
- USER_MODE cannot tell an absent record from an unshared one: a plan hidden by sharing reads as
  "no plan". [Measured: 2026-11-26, 264, fresh scratch]
- Account sharing hides names, not rows: `Invoice`, `BillingScheduleGroup` and `BillingArrangement`
  stay visible when Account is Private, and a USER_MODE Account read simply omits the hidden id.
  [Measured: 2026-11-27, 264, scratch, Login As persona with Account read and no View All]
- Whether describe hides license-gated Dispute fields from a user without the Billing license, so
  that user sees a real-looking 0: [Open: describe Dispute as a user without the license].
