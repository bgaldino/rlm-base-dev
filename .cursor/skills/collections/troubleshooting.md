# Collections — Troubleshooting

Read this when something collections-related is empty, zero, refused or missing. Parent:
[SKILL.md](SKILL.md). Each row: symptom, cause, fix.

| Symptom | Cause | Fix |
|---|---|---|
| Pill reads "Status Unavailable"; "Promises to pay could not be read" | The user cannot read `CollectionPlan` (managed billing role sets do not carry it) [Measured: 2026-11-26, 264, scratch, Login As] | `RLM_BillingCollectionsRead` beside the group, with Billing Advanced |
| Assigning the specialist permission fails | It needs Billing Advanced; a Billing-only license refuses it [Measured: 2026-11-26, 264, scratch, Login As] | Assign the Billing Advanced license first |
| A permission set group fails to deploy and keeps its old content | A license-gated permission sits in a group and a holder lacks `BillingAdvancedPsl` [Repo: docs/references/revenue-cloud-permissions.md] | Move it to a standalone set |
| Card shows "Variable does not exist: tmpVar1" | An inline USER_MODE query with a bind on a refused object (Case) [Measured: 2026-11-26, 264, scratch, Login As] | Catch `Exception` and show Unavailable |
| "sObject type 'X' is not supported" | The user cannot read X [Measured: 2026-11-26, 264, scratch, Login As] | Grant read or show Unavailable |
| "No such column 'CurrencyIsoCode'" | Single-currency org: the field does not exist, not a refusal [Measured: 2026-11-26, 264, fresh scratch] | Describe first; drop the currency filter |
| A total reads 0 but data exists | A refused read was coalesced to 0 | Show Unavailable; fix the controller |
| Debit memos total missing | Reading `DebitMemo` needs Manage Debit Memos, not granted ([permissions-and-personas.md](permissions-and-personas.md)) | Label the total as excluding debit memos |
| Dashboard says "Too many records" | A bounded read overflowed | Narrow by account or currency, as the message says |
| Disputed list is empty for a collector | Case OWD is Private; the user sees only owned or shared cases [Measured: 2026-11-26, 264, fresh scratch] | Share or reassign cases; by design |
| Plan seems absent | USER_MODE cannot tell absent from unshared [Measured: 2026-11-26, 264, fresh scratch] | Check sharing before concluding |
| Plan Status is null | The picklist has no values on a fresh build ([object-model.md](object-model.md)) | Add values |
| Write-off returns INVALID_API_INPUT | Reason Code picklist empty [Measured: 2026-11-27, 264, fresh scratch build, API 68.0]; with a value, the outcome is [Open: not measured] | Add a value to the Credit Memo Reason Code |
| Write-off API JSON_PARSER_ERROR "Unrecognized field" | The dev-guide example sends `description`; the field is `reason` [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] | Send `reason` |
| Late-fee flow creates nothing or errors | The Debit Memo create has no field values [Repo: unpackaged/post_collections/flows/RLM_Create_Late_Fee.flow-meta.xml] | [Open: confirm in the UI; fix the flow] |
| Plan never closes | The close flow ships Draft [Repo: unpackaged/post_collections/flows/RLM_Close_Collection_Plan_and_Associated_Cases.flow-meta.xml] | Activate it or close by hand |
| REST create of a plan with `Name` fails | `Name` is an auto-number [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] | Omit it |
| REST create of `PaymentScheduleItem` rejected | Missing `TargetPaymentProcessingDate` or Status "Pending" [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] | Use `TargetPaymentProcessingDate` and Status Draft |
| Fourth promise item accepted by REST | The three-item limit is the flow's [Measured: 2026-11-27, 264, fresh scratch build, API 68.0] | Enforce in your own code |
| Console app missing for a persona | See [permissions-and-personas.md](permissions-and-personas.md) → Test personas; a bare-role persona did not reach the app even with visibility [Open: cause not found] | Use a visible profile; Login As |
| Balance cards missing on an Account page | They sit on `RLM_Collections_Account_Record_Page` inside the Collection Console app only [Repo: templates/applications/conditional/collections/] | Open the account from that app |
| Case Metrics not on any page | Its only target is the home page, which does not include it [Measured: 2026-11-26, 264, scratch, all 82 FlexiPages retrieved] | Add it to a home page |
| Dashboard tab named but missing | `post_billing_ui` not deployed before `assemble_and_deploy_ux` [Repo: unpackaged/post_billing_ui/README.md] | Deploy the bundle first |
| An invoice PDF is blank for a persona | Missing Product2, UnitOfMeasure and Account address reads [Open: not measured for collections personas] | `document-generation` and `billing-operations` |
| Dunning emails do not send | The campaign email path needs Marketing Cloud Growth and Data 360 [Help: ind.billing_collections_dunning_process_setup] | Whether a verified sending domain is also needed [Open: not measured] |
| Any "Open" item above | Not yet measured | Measure it, then tag |

A collections symptom with none of these: describe the object as the user, check sharing, then
read the debug log for the refusal signature
([building-collections-uis.md](building-collections-uis.md)). A build step failing:
`troubleshooting`.
