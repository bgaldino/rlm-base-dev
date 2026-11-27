# Collections — Verification

Read this when checking a build, a persona or a figure. Parent: [SKILL.md](SKILL.md). Check as
the user, not as the admin.

## Build read-backs

```bash
sf data query -o <sf-alias> -q "SELECT COUNT() FROM CollectionPlan"
sf data query -o <sf-alias> -q "SELECT Name FROM CollectionPlanReason"
sf data query -o <sf-alias> -q "SELECT Id, Status, Duedate, DaysPastDue, InitialDueAmount, TotalInvoiceBalance, PromiseToPayCount, IsClosed FROM CollectionPlan"
sf data query -o <sf-alias> -q "SELECT CollectionPlanId, InvoiceId FROM CollectionPlanItem"
sf data query -o <sf-alias> -q "SELECT Id, Type, Status, UsageType, ReferenceEntityId FROM PaymentSchedule WHERE Type = 'PromiseToPay'"
sf data query -o <sf-alias> -q "SELECT PaymentScheduleId, RequestedAmount, TargetPaymentProcessingDate, Status FROM PaymentScheduleItem"
sf data query -o <sf-alias> -q "SELECT ApiName, ActiveVersionId FROM FlowDefinitionView WHERE ApiName LIKE 'RLM_%Collection%'"
sf sobject describe -s CollectionPlan -o <sf-alias>   # picklist values for Status and CollectionPlanSegment
```

Expected on a fresh build: 0 plans, 5 reasons, no active version of
`RLM_Close_Collection_Plan_and_Associated_Cases`, empty picklists ([object-model.md](object-model.md)).
[Measured: 2026-11-27, 264, fresh scratch build, API 68.0] The `FlowDefinitionView` view has no `Name` column; use `ApiName`.

## Stage checks

- After adding items: `TotalInvoiceBalance` equals the sum of the items' invoice balances.
- After a promise: one schedule of Type PromiseToPay, 1 to 3 items from the flow, `PromiseToPayCount`
  incremented, and the sum of requested amounts at most the invoice balance.
- After a write-off: the invoice's write-off fields set and a credit memo with the reason code
  [Open: complete a write-off per the setup steps and read the credit memo and the invoice] (see [setup-and-operate.md](setup-and-operate.md)).
- After a payment: balances per `billing-operations` → `verification.md` (`cli verify`).

## Persona checks

For each persona (collector, billing operations, bare managed role, read-only):

1. Login As (the profile must show the app; a Minimum Access profile does not, see
   [permissions-and-personas.md](permissions-and-personas.md)).
2. Open the Collections account page: the pill reads "In Collections" with the collections set and
   "Status Unavailable" with only the bare role [Measured: 2026-11-26, 264, fresh scratch build].
3. Open the dashboard: every section either shows data or says why not; none shows 0 for a section the
   persona cannot read. Debit memos read "not available".
4. Case Metrics for a user who reads Case but not Dispute: Open Billing Cases a real 0, the dispute
   figures "Unavailable" [Measured: 2026-11-26, 264, fresh scratch build]. The metric
   counts only open Cases of Type Billing.
5. Run the same page as the admin only to compare totals; never as the check.

## Refused-read checks

For each figure that can be fed by a refused read: strip the object or field from a test persona,
reload, and confirm "Unavailable" with the persona, a reason, and no zero. Also confirm a totals
label excludes what it could not read.

## Scale checks

With 505 accounts the picker listed the first 500 with a notice and a working name search
[Measured: 2026-11-26, 264, fresh scratch build, live Chrome]. Larger volumes: [Open: not measured; build 10,000
invoices and confirm "Too many records" appears instead of a limit error].
