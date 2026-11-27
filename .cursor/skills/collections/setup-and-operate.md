# Collections — Setup and Day-to-day Operation

Read this when enabling collections, creating plans and promises, charging a late fee, writing
off, handling disputes, planning dunning, or sequencing a workshop. Parent: [SKILL.md](SKILL.md).
Each claim carries its own tag.

## Setup

1. **Licenses and sets.** Billing and Billing Advanced licenses, the managed specialist set, and
   the repo sets for the personas you need ([permissions-and-personas.md](permissions-and-personas.md)).
2. **Build.** The `collections` flag defaults to true; `prepare_collections` deploys
   `post_collections`, seeds the five reasons and the case matrix and assigns `RLM_CollectionsUI`
   ([repo-collections-tier.md](repo-collections-tier.md)).
3. **Picklists.** Add values to Collection Plan Status (and `CollectionPlanSegment` if used); they
   ship empty ([object-model.md](object-model.md)).
4. **Reason Code values for memos.** The memo Reason Code picklists ship empty
   ([object-model.md](object-model.md)). Write-off needs a credit memo reason and the late-fee action a
   debit memo reason. Setup > Object Manager > Credit Memo > Fields and Relationships > Reason Code,
   add a value such as "Bad Debt" (same for Debit Memo). No headless route to add the value was
   found (no CustomField row, no matching StandardValueSet) [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] [Open: a metadata or Tooling route
   that adds picklist values to these standard fields]
5. **Console.** Specialist console setup: grant field access to `CollectionPlanItem.InitialDueAmount`
   for the Collection Progress chart [Help: ind.billing_collections_specialist_console_setup]. No
   repo set grants it ([object-model.md](object-model.md)), so add it yourself.
6. **Dunning (optional).** In Salesforce Go turn on Dynamic Revenue Orchestrator and Future-Dated
   Steps, turn on Automate Dunning Orchestration in Billing Settings (creates the Billing
   orchestration plan context mapping for `BillingCollectionPlanContext`), install the Dunning
   Orchestration solution (a fulfillment workspace and three email templates; it cannot be
   uninstalled) [Help: ind.billing_dunning_orchestration_enable]. Campaign dunning emails additionally need
   Data 360 and Marketing Cloud Growth with consent data; emails can instead be sent directly from
   the Collection Plan record page [Help: ind.billing_collections_dunning_process_setup]. Whether orchestrated dunning can be
   enabled on a fresh build without Marketing Cloud Growth, and what a reminder step produces:
   [Open: enable it on a disposable org and read the orchestration plan]. Whether reminder emails also need a
   verified sending domain: [Open: send a dunning reminder from a disposable org and read the delivery result].

## Operate

**Create a plan and items.** As the specialist: create the plan (Help also asks for due date, risk
profile and contact data), then add items from the Invoices tab, up to 10 invoices per run; errors go
to the Revenue Transaction Error Logs [Help: ind.billing_collection_plans_and_plan_items_create].
Two items on two 250 invoices rolled `TotalInvoiceBalance` up to 500 at once; nothing set
`DaysPastDue` or `InitialDueAmount`. Enter them yourself. [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]

**Promise to pay.** Launch Create Billing Promise to Pay from the plan: 1 to 3 partial payments, the
sum at most the invoice balance [Help: ind.billing_collection_plan_payment_promise_collect]. The
shipped flow makes a `PaymentSchedule` (Type PromiseToPay, Status Draft, UsageType CollectionPlan),
the items, and increments `PromiseToPayCount` [Repo:
unpackaged/post_collections/flows/RLM_Create_Promise_to_Pay.flow-meta.xml]. Where the three-item
limit lives, and the field and status values for creating the records directly:
[object-model.md](object-model.md).

**Close a plan.** `RLM_Close_Collection_Plan_and_Associated_Cases` is a record-triggered flow on
CollectionPlan update (IsClosed false, DaysPastDue 0) and **ships Draft**, so nothing closes plans
on its own [Repo: unpackaged/post_collections/flows/RLM_Close_Collection_Plan_and_Associated_Cases.flow-meta.xml].
Setting `IsClosed` and `ClosedDate` by DML was accepted and fired no automation
[Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. Activating the flow and its effect on
the plan's cases: [Open: activate it on a disposable org, set DaysPastDue 0, read the cases].

**Charge a late fee.** `CollectionPlan.RLM_Charge_Late_Fee` launches `RLM_Create_Late_Fee`, a screen
flow. As shipped, its Debit Memo create lists AccountId, InvoiceGenerationStatus and Status with no
value, and the entered `Enter_Late_Fee_Amount` is used nowhere [Repo:
unpackaged/post_collections/flows/RLM_Create_Late_Fee.flow-meta.xml]. A REST create of a
`DebitMemo` with `{}` fails with REQUIRED_FIELD_MISSING for AccountId, Status and
InvoiceGenerationStatus [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. The flow itself
was not run, since screen flows have no headless route: [Open: run the quick action in the UI as a
specialist and read the DebitMemo]. The late-fee action was reported reverted and hidden in 264
[Open: read the quick action's metadata and visibility on a fresh 264 build].

**Write off.** `Invoice.RLM_Write_Off_Invoice` launches `RLM_WriteOffInvoices`, which calls the
`writeOffInvoices` action with a reason code and the reason "Bad Debt" [Repo:
unpackaged/post_collections/flows/RLM_WriteOffInvoices.flow-meta.xml]. The API is
`POST /services/data/v68.0/commerce/invoicing/invoices/actions/write-off` with
`{"invoices":[{"invoiceId","reasonCode","reason"}]}` [Measured: 2026-11-27, 264, fresh scratch build,
API 68.0]. The dev-guide example sends `description` [Dev guide: connect-resources-write-off-invoices];
the call rejects it (JSON_PARSER_ERROR, "Unrecognized field") and the field is `reason`
[Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. With reason code "Bad Debt" the call returned INVALID_API_INPUT
because the picklists are empty. The successful write-off and its effect on invoice balance and
write-off fields: [Open: add the reason value (Setup step 4), re-run, read the invoice]. After a
write-off no further credits or payments can be applied or unapplied
[Help: ind.billing_write_off_invoices_impact].

**Disputes.** Dispute Management installs service process templates through Unified Catalog and
needs Billing Settings > Manage Billing Disputes and Service Requests, Omnistudio Metadata, Context
Definitions and sharing for Dispute and Service Catalog Request; the templates cover suspend billing,
update bill-to contact, extend due date, incorrect invoice charge and other inquiries, resolved by a
Resolve Case quick action [Help: ind.billing_disputes_overview,
ind.billing_dispute_management_enable]. The repo's Case-based collections flow and matrix:
[repo-collections-tier.md](repo-collections-tier.md). Chargebacks and card disputes:
[Open: record a card chargeback against a payment and read the payment and invoice].

**Retries and reminders.** Payment retries on collection-plan items and the Send Reminder button:
the repo removed the no-op button; [Open: a working Send Reminder is not built].

## Headless limits

Screen flows (late fee, promise to pay, add plan items) have no REST route; the equivalent
records were created directly. Record-triggered and screen flow behavior therefore
needs a UI run to count as measured.

## Workshop run order

1. Build with `collections` on; add Status values and memo Reason Code values (Setup steps 3 and 4).
2. Create and post two invoices for one account (`txn-data-harness`); they are the receivables.
3. As the specialist, create a plan and add both invoices; read `TotalInvoiceBalance`.
4. Enter `DaysPastDue` and `Duedate`; set a Status value you added.
5. Record a promise on one invoice; apply the payment (`billing-operations`); read the items.
6. Write the other invoice off; read its write-off fields and balance.
7. Close the plan; read `IsClosed`.
8. Open the dashboard as a collector persona and as a bare billing persona; compare
   ([verification.md](verification.md)).
