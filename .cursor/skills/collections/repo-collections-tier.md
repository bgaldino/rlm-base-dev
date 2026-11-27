# Collections — What the Repo Ships

Read this to learn what a build deploys for collections, which apps and pages host which
components, and what is not seeded. Parent: [SKILL.md](SKILL.md). A snapshot of `main`; the files
are the source.

## Flag and flow

- The `collections` flag defaults to true; the build always assigns the native
  `CollectionsAndRecoveryPsl` [Repo: cumulusci.yml].
- `prepare_collections` runs, in order: `deactivate_collections_case_matrix`,
  `deploy_post_collections`, `seed_collections_case_matrix`, `deploy_collections_case_flow`,
  `assign_permission_sets` (`RLM_CollectionsUI`) [Repo: cumulusci.yml].
- Collections pages and apps come from `assemble_and_deploy_ux`, never from `unpackaged/post_ux/`.

## `unpackaged/post_collections`

[Repo: unpackaged/post_collections/]

- Flows: `RLM_Apply_Payment_To_Invoice_Lines`, `RLM_Apply_Payments_on_Invoice`,
  `RLM_Close_Collection_Plan_and_Associated_Cases` (ships Draft), `RLM_Create_Late_Fee`,
  `RLM_Create_Promise_to_Pay`, `RLM_WriteOffInvoices`. Operation notes:
  [setup-and-operate.md](setup-and-operate.md).
- Quick actions `CollectionPlan.RLM_Charge_Late_Fee`, `Invoice.RLM_Write_Off_Invoice`.
- The decision matrix `DetermineCaseReasonAndRelatedAttributes`, the CaseReason and CaseType value
  sets, the omniUiCard `ShowCollectionsPerformanceMetrics2`, the queue `License_Administrators`,
  timeline object definitions, the permission set `RLM_CollectionsUI` and the Apex test class
  `RLM_CollectionsUIAccessTest`.
- `unpackaged/post_collections_case_flow/` is a sibling folder holding the flow
  `RLM_Create_Case_for_Collection`, deployed after the case matrix is seeded
  [Repo: unpackaged/post_collections_case_flow/flows/RLM_Create_Case_for_Collection.flow-meta.xml].

## Apps and pages

[Repo: templates/applications/conditional/collections/]

- Console app `standard__CollectionConsole` (label "Billing - Collections") and
  `RLM_Receivables_Management` ("Billing - Receivables Management").
- `RLM_Collections_Account_Record_Page` hosts the balance cards and overrides Account View only
  inside the Collection Console app ([permissions-and-personas.md](permissions-and-personas.md)). `RLM_Collections_Home_Page` does not include
  `rlmBillingCaseMetrics`, whose only target is the home page, so that component sits on no page
  [Repo: unpackaged/post_billing_ui/lwc/rlmBillingCaseMetrics/rlmBillingCaseMetrics.js-meta.xml].

## Billing UI components (`unpackaged/post_billing_ui/lwc`)

`rlmCollectionsConsole`, `rlmCollectionsDashboard`, `rlmAccountBalanceCard`, `rlmBillingCaseMetrics`,
`rlmOnAccountBilling`, `rlmDisputeDetails`, `rlmCollectionRuleBuilder`.

**Collections Dashboard.** The `RLM_Collections_Dashboard` app page, its tab and the
`RLM_CollectionsDashboard` set deploy with `billing_ui` whether or not `collections` is on; with
`collections` on, the UX assembler adds the tab to the console through
`templates/applications/patches/billing_ui/standard__CollectionConsole.patch.xml`. On an existing
org deploy `post_billing_ui` before `assemble_and_deploy_ux`, or the console names a tab the org does
not have [Repo: unpackaged/post_billing_ui/README.md → Collections Dashboard]. Its design rules:

- Anything unreadable shows as not available with a reason (refused, failed, too many), never zero.
- Every read is bounded; a call stays under 49,250 query rows whatever the data.
- Totals are in one currency at a time; no conversion; My Plans shows each row's own currency.
- Names, never Ids, label Bill To and plan columns; "Not available" for hidden or refused.
- No DebitMemo grant ([permissions-and-personas.md](permissions-and-personas.md)); Send Reminder removed.

Detail and limits: [building-collections-uis.md](building-collections-uis.md); the README's *Known
limitations* section lists the gaps.

## Seed data

Nothing seeds `CollectionPlan` rows. `seed_collections_case_matrix`
(`scripts/apex/seedCollectionsCaseMatrix.apex`) seeds only `CollectionPlanReason` CPR01 to CPR05 and
the case decision matrix. A collections demo creates plans through the UI or the flows.

## Not in the repo

No dunning orchestration (the Salesforce Go solution is installed by hand), no picklist values
([object-model.md](object-model.md)), and no seeded disputes.
