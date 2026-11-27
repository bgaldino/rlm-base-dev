---
name: collections
description: >-
  Set up, operate, verify and build UIs for Revenue Cloud Billing collections: collection plans
  and plan items, promises to pay, dunning, late fees, disputes as cases, write-offs, the
  specialist permission model and what a non-admin collections persona can read, the repo's
  collections tier (post_collections, the Billing - Collections console, the Collections Dashboard),
  and the traps in reading collections data (refused reads that look like zero, Status picklists
  that ship empty, multi-currency sums, governor limits). Use when running a collections
  workshop, giving a user collections access, reading back plans or promises, debugging a
  collections figure, or writing collections Apex or LWC. Billing runs, payments and credit
  memos: billing-operations. Collections and Recovery (FSC, Automotive) is a different product.
---

# Collections — Plans, Promises, Dunning, Disputes and Write-offs

Use this skill when the work is about collecting what invoices are owed: opening a plan, adding
the overdue invoices, recording a promise to pay, chasing, charging a late fee, handling a
dispute, or writing the balance off. The upstream stages (schedules, invoices, cash application)
are in [billing-operations](../billing-operations/SKILL.md); this skill starts where an invoice is
Posted and unpaid.

**Collections here means Billing collections** (`CollectionPlan` and friends, Help
`ind.billing_collections*`). **Collections and Recovery** (`ind.collections_*`: console, portal,
payment plans, direct debit, risk scores) is a separate Help area whose editions page lists
Financial Services Cloud and Automotive Cloud, not Revenue Cloud
[Help: ind.collections_editions_permissions]. Do not mix their articles.

Tags: `[Help: <article>]` (264 Help snapshot, id without `.htm.md`, no backticks), `[Dev guide: <page>]`,
`[Repo: <path>]`, `[Measured: <date>, <release>, <org shape>]` (an observation on that build;
re-measure on the patch in hand before relying on it), `[Open: <check that would settle it>]`.
Anything untagged is a pointer to a sub-file.

## Quick Rules

1. **A collection plan is a per-account work item; its items are invoices.** Create plans as
   the specialist, add up to 10 invoices at a time from the Invoices tab; failures land in the
   Revenue Transaction Error Logs [Help: ind.billing_collection_plans_and_plan_items_create].
   Object map: [object-model.md](object-model.md).
2. **The platform does not run the plan for you.** `DaysPastDue` is not calculated, and on a
   fresh build the `Status` and `CollectionPlanSegment` picklists have no values, so a plan's
   Status stays null until an admin adds values ([object-model.md](object-model.md)). Plain DML on `DaysPastDue`,
   `PromiseToPayCount`, `IsClosed` and `ClosedDate` is accepted and fires nothing
   [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. The closing flow ships Draft
   [Repo: unpackaged/post_collections/flows/RLM_Close_Collection_Plan_and_Associated_Cases.flow-meta.xml].
3. **Access is not one grant.** The specialist user permission needs the Billing Advanced license
   [Measured: 2026-11-26, 264, fresh scratch build] and the managed specialist set carries no Case,
   Payment, Task or DebitMemo access [Measured: 2026-11-27, 264, fresh scratch build, API 68.0].
   Pick the grants by task in [permissions-and-personas.md](permissions-and-personas.md).
4. **Unreadable is not zero.** A refused read shows "Unavailable"; a failed read says it failed;
   only a feature that is absent (checked by describe) is a real 0
   ([building-collections-uis.md](building-collections-uis.md)).
5. **Promises to pay are payment schedules.** A `PaymentSchedule` of Type PromiseToPay with
   1 to 3 items; where the limit lives is in [object-model.md](object-model.md).
6. **Dunning is orchestration; campaign emails need Marketing Cloud Growth.** Dunning runs DRO
   templates [Help: ind.billing_dunning_orchestration_enable]; the campaign email path needs
   Data 360 and Marketing Cloud, and emails can instead be sent directly from the Collection Plan
   record page [Help: ind.billing_collections_dunning_process_setup]. Not measured here. Step design: `dro-plans`.
7. **Write-off and late fee need Reason Code values that a fresh build lacks.** Add them before a
   workshop run ([object-model.md](object-model.md), [setup-and-operate.md](setup-and-operate.md)).
8. **Collections demos need seed data you create.** Nothing seeds `CollectionPlan` rows; the build
   seeds only the five reasons CPR01 to CPR05 and the case decision matrix
   [Repo: scripts/apex/seedCollectionsCaseMatrix.apex]
   ([repo-collections-tier.md](repo-collections-tier.md)).

## DO NOT

- **DO NOT** show a refused or failed read as 0, "none" or $0.00, or total over it.
- **DO NOT** grant Manage Debit Memos to a read-only collections role to complete a total
  ([permissions-and-personas.md](permissions-and-personas.md)). Label the total as excluding them.
- **DO NOT** put `RLM_BillingCollectionsRead` (or any permission set holding the license-gated
  `CollectionsAndRecoverySpecialist` user permission) in a permission set group: the group fails to
  deploy while any holder lacks `BillingAdvancedPsl`, and keeps its old content
  [Repo: docs/references/revenue-cloud-permissions.md].
- **DO NOT** read `Case.Description` in bulk or in a for loop for a list view; 200 cases at the
  32,000-character maximum take 6.4 MB ([building-collections-uis.md](building-collections-uis.md)).
- **DO NOT** treat every "No such column" as a refusal: a single-currency org has no
  `CurrencyIsoCode` on Invoice or Payment [Measured: 2026-11-26, 264, fresh scratch build].
- **DO NOT** use a filtered `SUM` as a per-currency total in a multi-currency org; it returns the
  corporate-converted amount [Measured: 2026-11-26, 264, fresh scratch build].
- **DO NOT** verify app navigation with a Minimum Access persona
  ([permissions-and-personas.md](permissions-and-personas.md) → Test personas).
- **DO NOT** use `Invoice.DaysInvoiceOverdue` to order or filter: it was null on Posted invoices
  [Measured: 2026-11-26, 264, fresh scratch build]. Derive from `DueDate`.
- **DO NOT** edit `unpackaged/post_ux/`; collections pages and apps come from `templates/`.
- **DO NOT** promise a screen-flow action (late fee, promise to pay) can be driven headlessly;
  no route was found ([setup-and-operate.md](setup-and-operate.md)).
- **DO NOT** state a count, amount or time as fact without a `[Measured]` tag.

## Entry Conditions

- What collections is, which objects, how they relate: [object-model.md](object-model.md).
- Who can see or do what, licenses, test personas, Login As:
  [permissions-and-personas.md](permissions-and-personas.md).
- Turning collections on, creating plans, promises, late fees, write-offs, disputes, dunning, a
  workshop run order: [setup-and-operate.md](setup-and-operate.md).
- What this repo deploys (flag, flows, apps, dashboard, seed): [repo-collections-tier.md](repo-collections-tier.md).
- Writing Apex or LWC that reads collections data: [building-collections-uis.md](building-collections-uis.md).
- Checking a build or a persona, read-backs: [verification.md](verification.md).
- A figure reads zero, a read throws, a page is missing, a picklist is empty:
  [troubleshooting.md](troubleshooting.md).
- Invoices, payments, credit and debit memos, application rules, write-off effects on the
  invoice: `billing-operations` → `payments-and-credits.md`.
- Orchestration steps for dunning: `dro-plans`. Schema: `revenue-cloud-data-model` →
  `domains/billing.md`. Persona deploy and USER_MODE hygiene: `apex-security-hardening`.
- Collections and Recovery (FSC, Automotive): `revenue-cloud-docs`; not this skill.

## Sub-files

- [object-model.md](object-model.md): read when mapping a collections concept to an object,
  field or picklist, or deciding where a promise, dispute, late fee or write-off lives.
- [permissions-and-personas.md](permissions-and-personas.md): read when giving a user
  collections access, choosing between the managed and repo sets, or building a test persona.
- [setup-and-operate.md](setup-and-operate.md): read when enabling collections, creating plans
  and promises, charging a late fee, writing off, handling disputes, planning dunning, or
  sequencing a workshop.
- [repo-collections-tier.md](repo-collections-tier.md): read when asking what the build
  deploys for collections, which apps and pages host which components, or what is not seeded.
- [building-collections-uis.md](building-collections-uis.md): read when writing Apex or LWC that
  reads plans, invoices, cases or payments: refusal signatures, unavailable states, row, heap
  and currency limits.
- [verification.md](verification.md): read when checking a build, a persona or a figure.
- [troubleshooting.md](troubleshooting.md): read when something collections-related is empty,
  zero, refused or missing.

## Examples

**"Give a collections agent access to plans, promises and the dashboard, nothing broader."**
Billing and Billing Advanced licenses, the managed Billing Collections and Recovery Specialist
set, and `RLM_CollectionsDashboard` (self-sufficient beside it); add `RLM_CollectionsUI` for the
plan record page. The managed specialist set is not narrow: it grants Modify All on the Fulfillment*
orchestration objects, so scope it to people who run dunning
[Measured: 2026-11-27, 264, fresh scratch build, API 68.0]. The Collection Progress chart also needs
`CollectionPlanItem.InitialDueAmount` field access, which no repo set grants
([object-model.md](object-model.md)). Debit memos stay "not available"
([permissions-and-personas.md](permissions-and-personas.md)).

**"The On Account card shows Status Unavailable for the billing operations persona."** That
persona cannot read `CollectionPlan`; the pill checks collections first, so no status is
known. Add `RLM_BillingCollectionsRead` beside the group, with Billing Advanced
([troubleshooting.md](troubleshooting.md)).

**"Run a partner workshop on collecting an overdue invoice."** Post invoices, add reason values,
create a plan and two items, record a promise, close or write off, read each stage back
([setup-and-operate.md](setup-and-operate.md) → Workshop run order).

## Validation Checks

```bash
# plans, items, reasons
sf data query -o <sf-alias> -q "SELECT COUNT() FROM CollectionPlan"
sf data query -o <sf-alias> -q "SELECT Id, Status, Duedate, DaysPastDue, TotalInvoiceBalance FROM CollectionPlan"
sf data query -o <sf-alias> -q "SELECT Name FROM CollectionPlanReason"
# promises
sf data query -o <sf-alias> -q "SELECT Id, Type, Status, UsageType FROM PaymentSchedule WHERE Type = 'PromiseToPay'"
```

- Each persona check is run as that user (Login As), not as the admin; a green admin run says
  nothing about access ([verification.md](verification.md)).
- Every figure a UI shows that a refused read can feed has a refused-read check
  ([verification.md](verification.md)).
- `python3 scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
