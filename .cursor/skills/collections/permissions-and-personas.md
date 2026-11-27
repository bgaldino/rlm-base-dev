# Collections — Permissions and Personas

Read this when giving a user collections access, choosing between the managed and the repo
permission sets, or building a test persona. Parent: [SKILL.md](SKILL.md). The repo's
authoritative table is `docs/references/revenue-cloud-permissions.md`.

## Licenses

- The collections user needs the **Billing** and **Billing Advanced** permission set licenses and
  the managed **Billing Collections and Recovery Specialist** set (`BillingCollectionsAndRecoverySpecialist`,
  native `CollectionsAndRecoveryPsl`). The build always assigns the native license
  [Repo: cumulusci.yml] and does not assign the managed set; an admin assigns it
  [Help: ind.billing_collections_specialist_console_setup].
- The `CollectionsAndRecoverySpecialist` **user permission needs Billing Advanced**: a Billing-only
  license refuses it. The billing operations persona (managed Billing Operations set plus
  `RLM_BillingUI`, Billing license only) could not read `CollectionPlan` until it held the
  specialist permission and Billing Advanced. [Measured: 2026-11-26, 264, scratch build, Login As
  personas]
- Promise schedules are visible only with Payment Operations or Payment Admin
  [Help: ind.billing_collection_plan_payment_promise_collect].

## What the managed specialist set grants

- Read: Account, Contact, Invoice [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, ObjectPermissions and FieldPermissions query].
- Create, read, edit, delete: `CollectionPlan`, `CollectionPlanItem`, `CollectionPlanReason`,
  `PaymentSchedule`, `PaymentScheduleItem` [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, ObjectPermissions and FieldPermissions query].
- Full with View All and Modify All: the Fulfillment* orchestration objects,
  `OrchestrationPlanCtxMapping`, `ProductFulfillmentScenario` (this is the dunning side) [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, ObjectPermissions and FieldPermissions query].
- Field grants: only `CollectionPlan.OverdueRiskIndicator` [Measured: 2026-11-27, 264, fresh scratch build, API 68.0, ObjectPermissions and FieldPermissions query].
- **No** Case, Payment, DebitMemo or Task access. The dashboard's reads that the set lacks are:
  Case and Payment object read; `Case.AccountId`, `Subject`, `Description`, `Reason`;
  `CollectionPlan.AccountId`, `Duedate`, `ClosedDate`, `DaysPastDue`; `CollectionPlanItem.InvoiceId`;
  `Task.ActivityDate`, `Task.WhatId`. [Measured: 2026-11-26, 264, fresh scratch, Minimum Access
  persona]
- `Event.WhatId` comes with `Task.WhatId`: the platform adds it whenever the Task field permission is
  granted, so a retrieved set lists both [Repo: docs/references/revenue-cloud-permissions.md].

## The repo's sets

| Set | For | Notes |
|---|---|---|
| `RLM_CollectionsUI` | Collection Plan record page | Ships with the `collections` flag. Not a dashboard grant: it has no access to the dashboard controller. [Repo: unpackaged/post_collections/permissionsets/RLM_CollectionsUI.permissionset-meta.xml] |
| `RLM_CollectionsDashboard` | Collections Dashboard | Tab, controller and the read-only grants above. Self-sufficient beside the specialist set; works with `billing_ui` on and `collections` off. [Repo: unpackaged/post_billing_ui/README.md] |
| `RLM_BillingCollectionsRead` | Billing personas reading collection status | `CollectionPlan` and `CollectionPlanItem` read, `CollectionPlan.AccountId`, the `CollectionsAndRecoverySpecialist` user permission. **Standalone, in no group**: a group holding it fails to deploy while any holder lacks `BillingAdvancedPsl`, and keeps its old content [Repo: docs/references/revenue-cloud-permissions.md]. The three billing personas get it beside their group, with Billing Advanced. [Repo: unpackaged/post_personas/permissionsets/RLM_BillingCollectionsRead.permissionset-meta.xml] |
| `RLM_BillingUI` | Billing UI users | Already grants plan and item read and `CollectionPlan.AccountId` [Repo: docs/references/revenue-cloud-permissions.md]; the plan read still failed without the specialist permission [Measured: 2026-11-26, 264, scratch, Login As]. |

Pick by task:

- Collector who works the dashboard: licenses + managed specialist set + `RLM_CollectionsDashboard`
  (+ `RLM_CollectionsUI` for the record page).
- Billing user who only needs the "In Collections" pill: `RLM_BillingCollectionsRead` + Billing Advanced.
- What else the specialist permission unlocks (collections write actions, the console) is
  [Open: assign the set alone and attempt a collections write action as that user].

## Debit memos

Reading `DebitMemo` needs the **Manage Debit Memos** user permission; there is no narrower grant
[Measured: 2026-11-26, 264, fresh scratch]. By design in this repo, read-only
collections roles do not get it [Repo: unpackaged/post_billing_ui/README.md]. The UI shows debit memos as not available and labels any total as
excluding them.

## Test personas

- A **Minimum Access** profile has no Lightning Experience; to open Lightning pages the persona
  needed a temporary Lightning-only permission set. [Measured: 2026-11-26, 264, scratch, Login As]
- It also cannot see the **Billing - Collections** console app because app visibility comes from the
  profile, so use a profile that shows the app to verify navigation. [Measured: 2026-11-26, 264, scratch, Login As]
- **Login As** needs "Administrators Can Log in as Any User" and works from the Setup user page.
  [Open: Help source for the setting name]
- A Minimum Access persona still reads `CurrencyType`; with the specialist set and
  `RLM_CollectionsDashboard` it also read `Contact.Name` and `DatedConversionRate` in USER_MODE with
  no extra grant [Measured: 2026-11-26, 264, scratch, Login As].
- Headless checks: run USER_MODE Apex as the persona, not as the admin: an admin read
  proves nothing about a persona's grants.

## Where the cards and page are hosted

`RLM_Collections_Account_Record_Page` hosts the balance cards and overrides Account View only inside
the Collection Console app ("Billing - Collections"); anywhere else the standard Account page shows
without them [Repo: templates/applications/conditional/collections/]. A persona with Billing Advanced
and the specialist set reached the app through a permission set's `applicationVisibilities`; a
bare-role persona with the same visibility did not (the URL redirected home). [Measured: 2026-11-26, 264, scratch, Login As] Cause:
[Open: whether the app needs a collections license or permission; assign the app to a bare-role
persona and compare]. A check can use a test-only app that overrides Account View with the same page.
