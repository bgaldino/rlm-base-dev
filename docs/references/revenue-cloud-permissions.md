# Revenue Cloud Permissions Reference

This document describes the Permission Set Licenses (PSLs), Permission Set Groups (PSGs), and individual Permission Sets used by the RLM Base Foundations project, how they map to feature flags, and the order in which they are assigned during `prepare_rlm_org`.

---

## Permission Set Licenses (PSLs)

PSLs are Salesforce-managed licenses that must be assigned to a user before the corresponding permission sets or PSGs can take effect. They are assigned early in `prepare_core` — step 4, then `assign_feature_psls` (steps 1, 2, 3, 4), i.e. build steps 1.4 and 1.8.1–1.8.4 — before any PSGs or permission sets.

### Core RLM PSLs (`rlm_psl_api_names`) -- Always Assigned

Assigned unconditionally at `prepare_core` step 4 → `assign_permission_set_licenses` — build step 1.4 (25 licenses).

| PSL API Name | Capability Area |
|---|---|
| `BREDesigner` | Business Rules Engine design |
| `BRERuntime` | Business Rules Engine execution |
| `CorePricingDesignTime` | Pricing configuration |
| `DataProcessingEnginePsl` | Data processing engine |
| `DecimalQuantityDesigntimePsl` | Decimal quantity design |
| `DecimalQuantityRuntimePsl` | Decimal quantity runtime |
| `DocGenDesignerPsl` | Document generation design |
| `DocumentBuilderUserPsl` | Document builder |
| `DynamicRevenueOrchestratorUserPsl` | Dynamic Revenue Orchestration |
| `IndustriesConfiguratorPsl` | Product configurator |
| `Microsoft365WordPsl` | Word template integration |
| `OmniStudioDesigner` | OmniStudio flow design |
| `ProductCatalogManagementAdministratorPsl` | Product catalog admin |
| `ProductDiscoveryUserPsl` | Product discovery |
| `RatingDesignTimePsl` | Rating/usage design |
| `RatingRunTimePsl` | Rating/usage runtime |
| `RevenueLifecycleManagementUserPsl` | Core RLM user access |
| `RevLifecycleMgmtBillingPsl` | RLM billing |
| `UsageDesignTimePsl` | Usage design |
| `UsageRunTimePsl` | Usage runtime |
| `WalletManagementUserPsl` | Wallet management |
| `BillingAdvancedPsl` | Advanced billing |
| `IndustriesARCPsl` | Asset Recovery |
| `CollectionsAndRecoveryPsl` | Collections |
| `RevPromotionsManagementPsl` | Promotions management |

### `EinsteinAnalyticsPlusPsl` -- `analytics: true`

Assigned at `assign_feature_psls` step 3 → `assign_permission_set_licenses` — build step 1.8.3 — when `analytics` is on
(separate from the AI list because it is required for RLM_RMI PSG functionality, and
`analytics` defaults to true; it is genuinely skipped with `analytics: false`).

### CLM PSLs (`rlm_clm_psl_api_names`) -- `clm: true`

Assigned at `assign_feature_psls` step 1 → `assign_permission_set_licenses` — build step 1.8.1 (11 licenses). Several overlap with core PSLs; Salesforce deduplicates automatically.

| PSL API Name | Capability Area |
|---|---|
| `AIAcceleratorPsl` | AI Accelerator (requires RevenueIntelligence feature) |
| `ClauseManagementUser` | Clause management |
| `CLMAnalyticsPsl` | CLM analytics |
| `ContractManagementUser` | Contract management |
| `ContractsAIUserPsl` | Contracts AI |
| `DocGenDesignerPsl` | Document generation (also in core) |
| `DocumentBuilderUserPsl` | Document builder (also in core) |
| `InsightsCGAnalyticsPsl` | Insights analytics |
| `Microsoft365WordPsl` | Word integration (also in core) |
| `ObligationManagementUser` | Obligation tracking |
| `OmniStudioDesigner` | OmniStudio (also in core) |

### Einstein / AI PSLs (`rlm_ai_psl_api_names`) -- `einstein: true`

Assigned at `assign_feature_psls` step 2 → `assign_permission_set_licenses` — build step 1.8.2 (3 active licenses).

| PSL API Name | Capability Area |
|---|---|
| `AgentforceServiceAgentBuilderPsl` | Agentforce builder |
| `EinsteinGPTCopilotPsl` | Einstein Copilot |
| `EinsteinGPTPromptTemplatesPsl` | Prompt templates |

> Several AI PSLs are commented out because they are unavailable on Enterprise dev scratch orgs (e.g., `RevenueIntelligencePsl`, `MySearchPsl`, `ScoringFrameworkPsl`).

### TSO PSLs (`rlm_tso_psl_api_names`) -- `tso: true`

Assigned in `assign_feature_psls` step 4 (23 licenses; `when tso`). These are Trialforce Source Org-specific licenses for Sales Cloud Unlimited, Einstein features, and engagement tools.

| PSL API Name | Capability Area |
|---|---|
| `AutomatedActionsPsl` | Automated actions |
| `EinsteinAgentCWUPsl` | Einstein Agent |
| `EinsteinAgentPsl` | Einstein Agent |
| `EinsteinCopilotReviewMyDayPsl` | Review My Day |
| `EinsteinDiscoveryInTableauPsl` | Discovery in Tableau |
| `EinsteinGPTCallExplorerPsl` | Call explorer |
| `EinsteinGPTCreateClosePlanPsl` | Close plan creation |
| `EinsteinGPTGetProductPricingPsl` | Product pricing copilot |
| `EinsteinGPTGroundingStructuredDataPsl` | Structured data grounding |
| `EinsteinGPTMeetingFollowUpPsl` | Meeting follow-up |
| `EinsteinGPTSalesCallSummariesPsl` | Sales call summaries |
| `EinsteinGPTSalesEmailsPsl` | Sales emails |
| `EinsteinGPTSalesMiningPsl` | Sales mining |
| `EinsteinGPTSalesSummariesPsl` | Sales summaries |
| `EinsteinGPTSendMeetingRequestPsl` | Meeting requests |
| `EinsteinSalesGenerativeInsightsPsl` | Generative insights |
| `EinsteinSalesRepFeedbackPsl` | Rep feedback |
| `ERIPlatformBasic` | ERI platform |
| `SalesActionFindPastCollaboratorsPsl` | Find collaborators |
| `SalesActionReviewBuyingCommitteePsl` | Buying committee review |
| `SalesCloudUnlimitedAnalyticsAdminPsl` | SCU analytics admin |
| `SalesCloudUnlimitedPsl` | Sales Cloud Unlimited |
| `SalesEngagementBasicPsl` | Sales engagement |

### Tableau PSLs (`rlm_tableaunext_psl_api_names`) -- Not Assigned by Default

Defined as a YAML anchor (`TableauEinsteinUserPsl`) but not assigned in any standard flow. Available for org-specific overrides.

---

## Permission Set Groups (PSGs)

PSGs bundle multiple Salesforce-managed permission sets into capability-area groups. A few PSGs also include a repo-owned permission set from the same folder, which fills a field-access gap in the standard ones (see `RLM_RCB` below). The PSG metadata is deployed at `prepare_core` step 7 → `deploy_pre` (build step 1.7) from `unpackaged/pre/3_permissionsetgroups/`, recalculated at step 9, then assigned to the running user at step 10 (build steps 1.9 and 1.10; `tso` adds a second recalculate/assign pair at 1.11 and 1.12). `RLM_RCB` is force-recalculated once more at `prepare_billing` step 17 (build step 13.17), after the billing settings add the Dispute fields its managed Billing Admin set grants; see the troubleshooting skill → *PSG reads "Updated" but its users lack fields*.

### Core PSGs (`rlm_psg_api_names`) -- Always Assigned

These 11 PSGs are assigned unconditionally. Together they provide admin-level access to all core RLM capabilities.

#### RLM_PSL -- Core Admin Permission Sets (17 permission sets)

The primary lifecycle PSG. Bundles the essential RLM API permission sets for quoting, ordering, contracting, amendments, renewals, and cancellations.

| Permission Set | Purpose |
|---|---|
| `CorePricingAdmin` | Pricing administration |
| `DocumentBuilderUser` | Document builder |
| `PlaceSupplementalOrders` | Supplemental order placement |
| `RevLifecycleManagementCalculatePricesApi` | Calculate Prices API |
| `RevLifecycleManagementCalculateTaxesApi` | Calculate Taxes API |
| `RevLifecycleManagementCoreCPQAssetization` | Core CPQ assetization |
| `RevLifecycleManagementCreateContractApi` | Create Contract API |
| `RevLifecycleManagementCreateOrderFromQuote` | Quote-to-Order conversion |
| `RevLifecycleManagementInitiateAmendmentApi` | Amendment initiation API |
| `RevLifecycleManagementInitiateCancellationApi` | Cancellation initiation API |
| `RevLifecycleManagementInitiateRenewalApi` | Renewal initiation API |
| `RevLifecycleManagementPlaceOrderApi` | Place Order API |
| `RevLifecycleManagementProductAndPriceConfigurationApi` | Product/Price config API |
| `RevLifecycleManagementProductImportApi` | Product Import API |
| `RevLifecycleManagementQuotePricesTaxes` | Quote pricing and taxes |
| `RevLifecycleManagementTaxConfiguration` | Tax configuration |
| `RevLifecycleManagementUsageDesignUser` | Usage design |

#### RLM_RCB -- Revenue Cloud Billing Advanced (19 permission sets)

Billing super-user PSG covering invoicing, payments, credit memos, tax, collections, and accounting. Seventeen are Salesforce-managed. The other two, `RLM_BillingAccountFieldAccess` and `RLM_DeleteInvoices`, are repo-owned and deploy from the same folder.

| Permission Set | Purpose |
|---|---|
| `AnalyticsStoreUser` | Analytics data access |
| `BillingAdvancedPaymentAdministrator` | Payment admin |
| `BillingAdvancedPaymentOperations` | Payment operations |
| `BillingCollectionsAndRecoverySpecialist` | Collections |
| `CollectionsAndRecoveryAdmin` | Collections and recovery admin |
| `DataProcessingEngineUser` | DPE access |
| `DocGenDesigner` | Doc generation |
| `RevenueLifecycleManagementAccountingAdmin` | Accounting admin |
| `RevenueLifecycleManagementBillingAdmin` | Billing admin |
| `RevenueLifecycleManagementBillingCreateInvoiceFromBillingScheduleApi` | Invoice creation API |
| `RevenueLifecycleManagementBillingCreditMemoOperations` | Credit memo ops |
| `RevenueLifecycleManagementBillingCustomerService` | Customer service |
| `RevenueLifecycleManagementBillingInvoiceErrorRecoveryApi` | Invoice error recovery |
| `RevenueLifecycleManagementBillingOperations` | Billing operations |
| `RevenueLifecycleManagementBillingTaxAdmin` | Billing tax admin |
| `RevenueLifecycleManagementBillingVoidPostedInvoiceApi` | Void invoice API |
| `RevenueLifecycleManagementCreateBillingScheduleFromBillingTransactionApi` | Billing schedule API |
| `RLM_BillingAccountFieldAccess` (repo-owned) | Read/edit FLS on `BillingAccount` Shipping Address, Bill Day of Month, Payment Term and Bill To Contact. The standard Billing permission sets omit the first three and make Bill To Contact read-only, so fresh 264 orgs hide them from the Billing Account form even though the standard layout includes them |
| `RLM_DeleteInvoices` (repo-owned) | Enables the **Delete Invoice and Invoice Lines** user permission (`BillingInvoiceSuperUser`), which the managed Billing Admin set leaves off. Without it, only Draft and Canceled invoices can be deleted. Not in the Billing Admin, Billing Operations or Credit Memo Operations persona groups, so only `RLM_RCB` holders get it. The Account Reset's Delete Billing checks for it before deleting posted invoices, and keeps them for a user without it |

#### RLM_NGP -- Salesforce Pricing (4 permission sets)

| Permission Set | Purpose |
|---|---|
| `CorePricingAdmin` | Pricing admin |
| `CorePricingDesignTimeUser` | Pricing design |
| `CorePricingManager` | Pricing management |
| `DecimalQuantityDesigntime` | Decimal quantity |

Which Help persona each pricing set serves, plus record sharing for runtime users:
[`org-enablement-and-permissions.md`](../../.cursor/skills/pricing-setup/org-enablement-and-permissions.md).

#### RLM_CFG -- Revenue Cloud Configurator (3 permission sets)

| Permission Set | Purpose |
|---|---|
| `AdvancedConfiguratorDesigner` | Advanced configurator |
| `IndustriesConfiguratorPlatformApi` | Configurator platform API |
| `ProductConfigurationRulesDesigner` | Configuration rules |

#### RLM_PCM -- Product Catalog Management (3 permission sets)

| Permission Set | Purpose |
|---|---|
| `ProductCatalogManagementAdministrator` | PCM admin |
| `ProductCatalogManagementViewer` | PCM viewer |
| `ProductDetailsApiCache` | Product details API cache |

#### RLM_CLM -- Salesforce Contracts (5 permission sets)

| Permission Set | Purpose |
|---|---|
| `CLMAdminUser` | CLM admin |
| `ClauseDesigner` | Clause design |
| `DocGenDesigner` | Doc generation |
| `Microsoft365WordDesigner` | Word template design |
| `ObligationManager` | Obligation management |

#### RLM_DOC -- Document Generation and Builder (2 permission sets)

| Permission Set | Purpose |
|---|---|
| `DocGenDesigner` | Doc generation design |
| `DocumentBuilderUser` | Document builder |

#### RLM_DRO -- Dynamic Revenue Orchestrator (4 permission sets)

| Permission Set | Purpose |
|---|---|
| `DFODesignerUser` | DFO designer |
| `DFOManagerOperatorUser` | DFO manager/operator |
| `DfoAdminUser` | DFO admin |
| `OrderSubmitUser` | Order submission |

#### RLM_USG -- Usage and Rating Management (9 permission sets)

| Permission Set | Purpose |
|---|---|
| `DecimalQuantityDesigntime` | Decimal quantity |
| `RatingAdmin` | Rating admin |
| `RatingDesignTimeUser` | Rating design |
| `RatingManager` | Rating management |
| `RatingRunTimeUser` | Rating runtime |
| `RevLifecycleManagementUsageDesignUser` | Usage design |
| `UsageManagementDesigner` | Usage management design |
| `UsageManagementRunTimeUser` | Usage management runtime |
| `WalletManagementUser` | Wallet management |

#### RLM_RMI -- Revenue Management Intelligence (2 permission sets)

| Permission Set | Purpose |
|---|---|
| `AnalyticsStoreUser` | Analytics data access |
| `PulseRuntimeUser` | Pulse runtime |

#### RLM_QB_AI -- QuantumBit AI (empty)

Placeholder PSG with no permission sets. AI permission sets are assigned separately via `rlm_ai_ps_api_names` when `einstein: true`.

### RLM_TSO -- Trialforce Source Org PSG -- `tso: true`

Assigned in `prepare_core` step 12 via `assign_permission_set_groups_tolerant` (preceded by a `recalculate_permission_set_groups` at step 11). Contains 50 permission sets spanning Sales Cloud Unlimited, Einstein AI, Tableau, CLM AI, Data Cloud, and engagement features. This is the catch-all PSG for trial/demo orgs that bundles permissions unavailable on Enterprise dev scratch orgs.

<details>
<summary>Full list (50 permission sets)</summary>

`AIAcceleratorPsl`, `AdvancedCsvDataImport`, `AnalyticsQueryService`, `CDPAdmin`, `CGAnalyticsAdmin`, `CLMAnalyticsAdmin`, `CallCoachingIncluded`, `CallCoachingUserPsl`, `ContractsAIClauseDesigner`, `ContractsAIRuntimeUser`, `DataCloudMtrcsVisualizationPsl`, `EinsteinActivityCaptureIncluded`, `EinsteinAgentCWU`, `EinsteinAnalyticsAdmin`, `EinsteinAnalyticsPlusAdmin`, `EinsteinAssistantPsl`, `EinsteinCopilotReviewMyDay`, `EinsteinDiscoveryInTableau`, `EinsteinGPTCallExplorerPsl`, `EinsteinGPTGetProductPricing`, `EinsteinGPTSalesCallSummaries`, `EinsteinGPTSalesEmails`, `EinsteinGPTSalesMiningPsl`, `EinsteinGPTSalesSummaries`, `EinsteinGPTSearchAnswers`, `EinsteinPredictionsManagerAdmin`, `EinsteinReplyRecommendations`, `EinsteinSearchAnswers`, `EinsteinSendMeetingRequestCopilot`, `EinsteinServiceInnovations`, `GenieAdmin`, `HighVelocitySalesCadenceCreatorIncluded`, `HighVelocitySalesQuickCadenceCreatorIncluded`, `HighVelocitySalesUserIncluded`, `InboxIncluded`, `MetadataStudioUser`, `NLPServicePsl`, `PipelineInspectionIncluded`, `PrismBackofficeUser`, `PrismPlaygroundUser`, `QueryForDataPipelines`, `SalesActionReviewBuyingCommittee`, `SalesCloudEinsteinIncluded`, `SalesCloudUnlimitedIncluded`, `SalesMeetingsIncluded`, `TableauEinsteinAdmin`, `TableauEinsteinAnalyst`, `TableauEinsteinIncludedAppBusinessUser`, `TableauIncludedAppManager`, `TableauUser`
</details>

### Copilot/Catalog PSGs (`rlm_tso_psg_api_names` / `rlm_ai_psg_api_names`)

These Salesforce-managed PSGs are assigned in two contexts:

| PSG | Assigned When | Flow Step |
|---|---|---|
| `CopilotSalesforceUserPSG` | `tso: true` OR `agents: true` | `prepare_tso` step 1 / `prepare_agents` step 1 |
| `CopilotSalesforceAdminPSG` | `tso: true` OR `agents: true` | `prepare_tso` step 1 / `prepare_agents` step 1 |
| `UnifiedCatalogAdminPsl` | `tso: true` only | `prepare_tso` step 1 |
| `UnifiedCatalogDesignerPsl` | `tso: true` only | `prepare_tso` step 1 |

---

## Feature-Gated Permission Sets

Individual permission sets defined in project metadata (for example under `force-app/` and `unpackaged/post_*` directories) and assigned conditionally. These grant access to custom fields, Apex classes, or agent configurations specific to each feature.

### Explicitly Assigned Permission Sets

These are assigned via `assign_permission_sets` in their respective flows — to the
**running user** unless the step passes `user_alias`, in which case they land on that
persona user instead. See the persona rows in the flow inventory below.

> ⚠️ **`RLM_UtilitiesPermset` grants a destructive, system-mode entry point, and only
> admins can use it.** It grants `RLM_AccountUtilities`, which is declared `without sharing`,
> so the reset deletes an account's orders, assets, contracts, invoices, collection plans,
> disputes and their cases, quotes, opportunities and usage graph regardless of sharing. The
> Account Reset is for administrators only (owner decision, todo 397, 2026-11-26: "only let
> admins do account resets. It's just for demos, POCs and testing"): the class refuses a user
> without both Modify All Data and View All Data before it reads or changes anything ("Account
> reset is for administrators: it needs the Modify All Data and View All Data permissions.
> Nothing was changed."), and the Reset Account action on `RLM_Account_Record_Page` is hidden
> from such a user by a visibility rule on the same two permissions. The set is therefore
> assigned only to the running admin, not to the salesrep persona. Posted invoices are deleted
> only for an admin who also has **Delete Invoice and Invoice Lines** (`BillingInvoiceSuperUser`,
> from `RLM_DeleteInvoices`). The sharing mode is deliberate: the reset must remove records
> the running user cannot see, or the account is left half-reset, so do not switch the class
> to `with sharing`.

| Permission Set | Feature Flag(s) | Flow / Step | What It Grants |
|---|---|---|---|
| `RLM_QuantumBit` | `quantumbit` | `prepare_quantumbit` step 4 | FLS on custom QB fields (Order, Quote, etc.); on a tso build `deploy_post_tso` replaces it with a copy that adds field permissions and grants to the `BillingSystemExtCredentials` and `SalesforceContractsExtCredentials` principals |
| `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` | `prepare_quantumbit` step 12 | SObject access for CALM Delete operations |
| `RLM_Approvals` | `quantumbit` + `approvals` | `prepare_approvals` step 3 (running user) · `prepare_personas` step 11 (salesrep user, when `personas` is on) | FLS on approval fields (read-only on both stored pricing outputs on quote lines and order products: the pricing engine writes them in system context, and user edit access would let a rep lower the level before submitting) + `RLM_AA_Submit_Approval` Apex class |
| `RLM_DocGen` | `docgen` | `prepare_docgen` step 10 | FLS on seller/docgen fields (Quote, QuoteLineItem) |
| `RLM_Constraints` | `tso` + `constraints` | `prepare_constraints` step 3 | FLS on `RLM_ConstraintEngineNodeStatus__c` (3 objects) |
| `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` | `prepare_prm` step 7 | FLS on partner/channel program fields |
| `RLM_QuotingAgent` | `agents` | `prepare_agents` step 10 | Agent access to `RLM_Revenue_Quote_Management` |
| `RLM_QuotingAssistant` | `agents` | `prepare_agents` step 10 | Agent access to `RLM_Quoting_Assistant` |
| `RLM_BillingEmployeeAgent` | `agents` | `prepare_agents` step 10 | Agent access to `RLM_Billing_Employee_Assistance` |
| `RLM_ApprovalAgent` | `agents` | `prepare_agents` step 10 | Agent access to `RLM_Approval_Agent` |
| `RLM_UtilitiesPermset` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 6 (running user) — **not** assigned to the salesrep persona | `RLM_AccountUtilities` Apex class access. **Destructive** — that invocable deletes account-related orders, assets, contracts, invoices (posted ones only for a user with `BillingInvoiceSuperUser`), credit memos, Draft and Canceled debit memos, collection plans and disputes with their cases, quotes and opportunities, **plus the account's entire usage graph** (usage summaries, ratable summaries, entitlements, entitlement buckets, and rated transaction journals with their record alerts). With Delete Assets it also deletes the assets' rate card entries, usage resource policies and commitment links; a contract it deletes takes its own policies, rate card entries and commitment links. **Admins only**: the class refuses a user without both Modify All Data and View All Data before it reads anything, and the Reset Account action is hidden from them on `RLM_Account_Record_Page`. Assigned on both flows because `deploy_post_utils` ships the whole surface — class, `Account.RLM_Reset_Account` quick action and its flows — to both. |
| `RLM_ExpressionSetManager` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 5 | `RLM_ExpressionSetManagerController` Apex class access; object READ on `ExpressionSet` and READ+EDIT on `ExpressionSetVersion` (controller USER_MODE SOQL; no FLS — the selected fields are `permissionable=false`); `RLM_SessionId` Visualforce page access; **`ApiEnabled`** (broad — required for the `$Api.Session_ID` loopback to work against REST; a Named Credential is the scoped alternative). The controller also reads `ContextDefinition`, `ExpressionSetDefinition`, and the junction, but those are `IsCustomizable=false` platform entities — object perms on them are silently dropped and their read is platform/feature-governed (like `AsyncApexJob`). Grant set verified on a live scratch org (2026-07-22): deploys clean, file==org, all fields non-permissionable. |
| `RLM_DecisionTableManager` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 7 (running user) · **`prepare_personas` step 9 (salesrep persona — non-admin)** | `RLM_DecisionTableManagerController` Apex class access, and nothing else. Deliberately narrow: the controller reads decision-table metadata and queues the platform's own refresh action — it deletes nothing, and Setup's Refresh button is a separate path with a different gate. **The Manager's Refresh still needs Modify All Data and Customize Application**: the controller checks both before it starts the refresh flow [Repo: `canRefreshTables`]. Without that check, Salesforce's own gate on the Refresh Decision Table action, which no permission set can narrow, would still refuse a user with neither permission: a `with sharing` class starting the bulk flow the same way queued nothing for that user [Measured: 2026-11-19, 264, scratch, one org]. Some other paths refreshed for a non-admin when measured, including the repo's contract- and order-activation flows, and the Connect refresh route has a different gate (decision-tables skill, rule 1). So for the salesrep persona the Manager is a read-only freshness view, with Refresh disabled and the reason shown. Object permissions on `DecisionTable` and friends are NOT granted and are not needed; they are setup entities whose read is platform-governed. Assigned to the persona because the component sits on the shared Home page, so withholding it leaves a visible section that errors. |
| `RLM_RebuildSearchIndex` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 8 (running user) — **not** assigned to the salesrep persona | `RLM_RebuildSearchIndex` Apex class access; `RLM_SessionId` Visualforce page access; **`ApiEnabled`** (broad — same `$Api.Session_ID` loopback dependency as `RLM_ExpressionSetManager`, same Named Credential escape hatch). **No object permissions**, because the class runs no SOQL and no DML — its whole surface is one Connect callout to `/connect/pcm/index/deploy`. That callout carries the running user's session, so the endpoint applies that user's own catalog permissions; this set deliberately does not re-grant them, and a user without them gets `isSuccess=false` plus the endpoint's status code surfaced in the component rather than a silent no-op. Withheld from the persona because `ApiEnabled` is a broad system permission and a full catalog index rebuild is an admin operation — the same call already made for `RLM_ExpressionSetManager`. Before this set existed the class was granted in **no** permission set anywhere in the repo. |
| `RLM_UsageUploader` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 9 (running user) · **`prepare_personas` step 14 (salesrep persona — non-admin)** | `RLM_UsageUploaderController` Apex class access. Inserts `TransactionJournal` for usage upload, reads usage-related objects. Controller uses `Security.stripInaccessible(CREATABLE, ...)` for DML security hardening. All 14 SOQL queries reachable from `@AuraEnabled` methods use **`WITH USER_MODE`** — live-verified on the `july28` v67.0 scratch org: deploys clean, all Apex tests pass in-org. `uploadUsage` additionally validates quantity/date inputs and confirms the requested usage resource belongs to the asset's product before inserting. **Object permissions**: `TransactionJournal` CREATE+READ (CREATE is the only incremental grant; READ overlaps with always-assigned `RLM_USG` PSG); READ on `Asset`, `UsageResource`, `ProductUsageResource`, `UnitOfMeasure`, `UnitOfMeasureClass`, `AssetRateCardEntry`, `RateAdjustmentByTier`, `TransactionUsageEntitlement`, `UsageEntitlementBucket`, `ProductUsageResourcePolicy`, `UsageOveragePolicy`, `Account`, `Contact`, `Product2`, `RateCard`, `RateCardEntry` (`ProductUsageResourcePolicy` and `UsageOveragePolicy` back the `getGrantsForAsset` overage lookup — without them its `WITH USER_MODE` query throws and the catch blanks `chargeForOverage`, shown as `N/A`; parent-lookup / relationship-traversal dependencies — `UnitOfMeasureClass` READ is required because `UsageResource.UnitOfMeasureClassId` is a traversal target even though the field itself is non-permissionable; `Contact` READ is required because on orgs with Person Accounts enabled, `Account` READ has an object-permission dependency on `Contact` READ — caught live on the `tcr_803` scratch org; all overlap with `RLM_USG` but retained for standalone functionality). **Field permissions**: FLS grants on every permissionable field the USER_MODE queries select or filter on — TransactionJournal create fields (editable) plus Asset (AccountId, Product2Id, LifecycleStartDate, LifecycleEndDate) and Product2 (UsageModelType) read fields. Most other queried objects (ProductUsageResource, UsageResource, AssetRateCardEntry, RateCardEntry, RateAdjustmentByTier, TransactionUsageEntitlement, UsageEntitlementBucket, ProductUsageResourcePolicy, UsageOveragePolicy) expose **zero permissionable fields** — object-level READ fully covers their queried fields per platform rules, so no `fieldPermissions` rows exist for them. TransactionJournal omits six fields: two required (ActivityDate, Status) and four non-permissionable (AccountId, ReferenceRecordId, UsageResourceId, UsageType). **No `pageAccesses` or `ApiEnabled`** — controller does not call `getApiSessionId()`. Before this set existed the controller was granted in **no** permission set anywhere in the repo, so its LWC component worked only for an admin. An earlier persona `System.runAs` walk saw `getRatesForAsset`'s `AssetRateCardEntry.RateCardEntryId` lookup throw "No such column" for a non-admin user. Not reproduced on 264 (todo 185, 2026-10-29): the salesrep persona, with this set, loads the asset's rate card and tiers and uploads usage from the Account page. Uploading also needs `UnitOfMeasure` row access, which `set_personas_org_wide_defaults` gives (see *Record sharing*). |
| `RLM_UsageOrchestration` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 10 (running user) — **not** assigned to the salesrep persona, deliberately (arbitrary flow launch) | `RLM_UsageOrchestrationController` Apex class access. Starts client-specified autolaunched flows for usage orchestration. **Controller accepts a client-controlled flow API name and launches arbitrary autolaunched flows** — assign only to users who should have this broad capability. **No object or field permissions** (controller performs no SOQL/DML). **No `pageAccesses` or `ApiEnabled`**. Split from `RLM_UsageUploader` per #318 review to isolate the arbitrary-flow-launch capability from the usage-upload capability. Before this set existed the controller was granted in **no** permission set anywhere in the repo. |
| `RLM_UsageDatatables` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 11 (running user) · **`prepare_personas` step 13 (salesrep persona — non-admin)** | Apex class access to `RLM_UsageDataController` plus **READ-only** object and field permissions on usage objects (`TransactionJournal`, `UsageSummary`, `UsageBillingPeriodItem`, `Asset`, `UnitOfMeasure`, `UsageEntitlementAccount`, `UsageEntitlementBucket`, `UsageResource`), `Account`, and `Contact` for the `rlmUsageDataTable` LWC component on Account record pages. For the salesrep persona the Usage Summaries and Liable Summaries tables show the account's data, but the **Usage** table (`TransactionJournal`) shows "No records found", even for journals the persona created: the persona sees `TransactionJournal` rows only with View All on the object, which the build doesn't grant (see *Record sharing*). |
| `RLM_RenewalQuotes` | `tso`, `quantumbit` | `prepare_tso` step 4 / `prepare_quantumbit` step 14 (running user) · **`prepare_personas` step 12 (salesrep persona — non-admin)** | `RLM_RenewalAssetLock` Apex class access, Asset read, the Account read that Asset read depends on and the Contact read that Account read depends on, and nothing else. Generate Renewal Quote and Consolidate Renewals call that invocable to lock the root assets being renewed, so two renewals of them run one at a time; it changes nothing and returns nothing. Its query runs `WITH USER_MODE` and selects only `Id`, so Asset read (with the Account and Contact read the platform requires for it) is the whole object grant and no field permissions are needed. Assigned to the persona because both actions sit on the opportunity page that persona uses, so withholding it leaves visible actions that fault. |
| `DRO_Integrations` | `quantumbit` + `dro` | `prepare_quantumbit` step 15 (running user) | Principal access to the `BillingSystemExtCredentials` external credential (principal `Billing System Principal`), which every named credential in `post_quantumbit` (`BillingSystemNC`, `LogisticsSystemNC`, `OrderFulfillmentSystemNC`, `OrderFulfillmentSystemNCcanned` and `RLM_MockTax`) shares, and nothing else. A DRO callout step on the mock provider (`BillingSystemNC`) failed with `SF_DRO_STEP_API_00124` without the grant [Measured: 2026-11-25, 264, scratch, one org]; a callout through the other three (not the tax credential) would likely fail the same way [inferred], though no shipped provider or Apex uses them. The user who needs it is likely the one who activates the order [inferred; the one measured run had one user, who both activated and held the grant]. Deployed from `unpackaged/post_quantumbit/` beside the credential, so default builds (tso off) get it. Personas get no Billing principal on either build: neither this set nor `RLM_QuantumBit` (which carries the grant on tso builds) is assigned to them. |
| `RLM_BillingUI` | `billing_ui` | `prepare_billing` step 14 (running user) | Apex class access for the Billing UI controllers, `RunFlow`, and **read-only** access to every object their USER_MODE queries read: billing objects (Invoice, Payment and payment schedules, Dispute, Debit/Credit Memo, Refund, Billing Schedule Group, Billing Milestone Plan, Billing Arrangement, Billing Account, Collection Plan, Transaction Journal and others), plus Account, Contact, Case, Product2, Asset State Period, Usage Resource, Unit of Measure, Legal Entity, Tax Treatment and General Ledger Account. `BillingTreatment` and `AttributeDefinition` are read dependencies (of Billing Milestone Plan and of Asset State Period Attribute). The set still grants Asset read, but no Billing UI query reads Asset since the invoice product summary's unused asset-name lookup was removed; whether to keep that grant is pending review. Read FLS on the permissionable fields those queries select, including `Task.ActivityDate` and `Task.WhatId` for the Collections Dashboard's plan tasks (the platform adds `Event.WhatId`; todo 435). Edit FLS on `InvoiceLine.RLM_Attributes__c` (saved by Invoice Product Summary) and on `Order.RLM_Billing_Arrangement__c` / `Order.RLM_Billing_Profile__c` (edited on the billing_ui Order record page). **Not self-sufficient by design:** the billing objects also need a billing role's user permissions (Billing Access, Milestone Billing Access), and the collections objects need the Collections and Recovery Specialist user permission, which the user license allows only with `BillingAdvancedPsl` (the billing personas get it from the standalone `RLM_BillingCollectionsRead` set, below). Without them a user with only this set reads them as "not supported". Those, Invoice edit and Dispute Item edit come from the role, not this set; `CoreCPQUser`, which the asset attribute query needs, comes from `RLM_BillingUIAssetAttributes` (next row). `RLM_BillingUIAccessTest` runs the controllers' reads as each managed billing role (Admin, Operations, Credit Memo Operations) and as Billing Operations plus the Collections and Recovery Specialist, each with this set. The Invoice Batch Run Monitor sits on the Invoice Batch Run page, which the managed Billing Operations set reads and the managed Billing Admin set does not: a Billing Admin persona gets that read from `RLM_BillingInvoiceDocuments` in its group (todo 292). |
| `RLM_BillingUIAssetAttributes` | `billing_ui` | `prepare_billing` step 14 (running user), with `RLM_BillingUI` | `CoreCPQUser` only. Without it the user-mode Asset State Period Attribute query throws `ExternalObjectException` whenever attribute rows exist, and read on every attribute object does not help (measured on 264, todo 447). The user sees the Invoice Product Summary attribute columns come up empty with no error, and the line attribute save fail. It is a broad Revenue Cloud user permission, and it needs a license that allows it (the Billing license does), so it is kept out of `RLM_BillingUI`, which stays assignable to any user. The build assigns it to the running user only; give it to every billing user who works the Billing UI, alongside `RLM_BillingUI`. |
| `RLM_CollectionsDashboard` | `billing_ui` | `prepare_billing` step 14 (running user), with `RLM_BillingUI` | Opens the Collections Dashboard for a collections user who does not hold `RLM_BillingUI`, together with the managed Billing Collections and Recovery Specialist set and nothing else (self-sufficient beside it, so the dashboard works with `billing_ui` on and `collections` off; `RLM_CollectionsUI` is not needed for it). Grants Apex class access to `RLM_CollectionsDashboardController` (the only class the `rlmCollectionsDashboard` component calls), the `RLM_Collections_Dashboard` tab set to Visible, and, read-only, every read the controller makes that the specialist set lacks: object read on `Case` and `Payment`; field read on `Case.AccountId`, `Case.Subject`, `Case.Description`, `Case.Reason`, `CollectionPlan.AccountId`, `CollectionPlan.Duedate`, `CollectionPlan.ClosedDate`, `CollectionPlan.DaysPastDue`, `CollectionPlanItem.InvoiceId`, `Task.ActivityDate` and `Task.WhatId` (the platform adds `Event.WhatId` with `Task.WhatId`, so the file lists it). Measured on 264 (2026-11-26, todo 435) as a Minimum Access user with the Billing and Billing Advanced licenses and only the specialist set and this set. `DebitMemo` is not granted, by owner decision: reading it needs the Manage Debit Memos user permission (measured), a manage permission too broad for a read-only collections role. The dashboard shows anything it could not read as not available, never as $0.00 or an empty "none", and says why: each unavailable card figure, payment promise summary, plan task list, my-plan list, progress panel and worklist tab carries a reason, `refused` (a USER_MODE refusal, "sObject type ... is not supported" or "No such column ...", measured on 264), shown as "You don't have access to ...", or `failed` (any other error, and every failed call), shown as "... could not be loaded. Refresh the page to try again."; the Total Balance says what it excludes and why (debit memos, refused, for this user). (`RLM_BillingUIAccessTest.collectionsUserCannotReadDebitMemos` pins the refusal, `RLM_CollectionsDashboardControllerTest.reasonFor_tellsARefusalFromAFailure` the reasons, `rlmCollectionsDashboard` Jest the display.) The page, its tab and this set ship together in `unpackaged/post_billing_ui`, because the controller and component do; the UX assembler adds the tab to the Billing - Collections console (`standard__CollectionConsole`) when `collections` is on too, so on an existing org deploy `deploy_post_billing_ui` before `assemble_and_deploy_ux`. A tab deployed through the Metadata API is hidden on every profile, so this set is what shows it. `RLM_BillingUIAccessTest.collectionsUserWithoutBillingUiCanRunTheDashboardReads` runs every controller read as that user; `RLM_CollectionsDashboardControllerTest` loads the dashboard as that user, with and without this set. |
| `RLM_CollectionsUI` | `collections` | `prepare_collections` step 5 (running user) | **Read-only** access to `CollectionPlan`, to `BillingAccount` (the page's Billing Account field is a lookup, and its field grant has no effect for a user who cannot read the object; none of the managed collections sets grants `BillingAccount`, so this set does) and to all 18 permissionable `CollectionPlan` fields the Collection Plan record page (`RLM_Collection_Plan_Record_Page`) shows, so the page works with `collections` on and `billing_ui` off: AccountId, BillingAccountId, ClosedDate, CollectionPlanReasonId, CollectionPlanSegment, ContactId, DaysPastDue, Duedate, FirstCallDateTime, FirstEmailDateTime, FirstSmsDateTime, InitialDueAmount, IsClosed, PromiseToPayCount, RiskScore, Status, TotalTaxAmount and UsageType (AccountId, ClosedDate, DaysPastDue and Duedate overlap with `RLM_BillingUI`, which grants them for its controllers). `Name` and `TotalInvoiceBalance` need no grant (not permissionable). Measured on a 264 org: no managed billing role set grants any of the 18. The only other grants of AccountId, ClosedDate, DaysPastDue and Duedate are on five standard profiles (System Administrator, Standard User, Marketing User, Contract Manager and Solution Manager) and in `RLM_BillingUI`, so a Minimum Access user without `RLM_BillingUI` gets them only from this set. **Not self-sufficient by design:** the collections objects need the Billing Advanced license and the Collections and Recovery Specialist set. `RLM_CollectionsUIAccessTest` proves the grant as a Minimum Access user holding the Billing and Billing Advanced licenses plus the specialist set, and that the specialist set alone lacks it; `tests/test_collection_plan_page_fields.py` checks the page against the grants offline. |

### Einstein / AI Permission Sets (`rlm_ai_ps_api_names`) -- `einstein: true`

Assigned by `assign_feature_permission_sets` steps 1–2 — build steps 1.16.1–1.16.2 — when `einstein` is on (`SalesCloudEinsteinAll` additionally requires a non-Developer-Edition org).

| Permission Set | Purpose |
|---|---|
| `EinsteinGPTPromptTemplateManager` | Prompt template management |
| `SalesCloudEinsteinAll` | Sales Cloud Einstein features |

### TSO Permission Sets (`rlm_tso_ps_api_names`) -- `tso: true`

Assigned in `prepare_tso` step 4.

| Permission Set | Purpose |
|---|---|
| `ERIBasic` | ERI platform |
| `RLM_UtilitiesPermset` | Account-reset utilities (`RLM_AccountUtilities` Apex class access; admins only) -- destructive; also clears the account's usage graph |
| `RLM_ExpressionSetManager` | Expression Set Manager component (Apex class, object reads, `RLM_SessionId` page, `ApiEnabled`) |
| `RLM_DecisionTableManager` | Decision Table Manager component (`RLM_DecisionTableManagerController` Apex class access only) |
| `RLM_RebuildSearchIndex` | Rebuild Search Index component (Apex class, `RLM_SessionId` page, `ApiEnabled`; no object perms — the class runs no SOQL/DML) |
| `RLM_UsageUploader` | Usage uploader component (Apex class + WITH USER_MODE SOQL, DML via Security.stripInaccessible; TransactionJournal CREATE + comprehensive field-level READ grants; no page/ApiEnabled) |
| `RLM_UsageOrchestration` | Usage orchestration component (Apex class only; launches client-specified autolaunched flows — broad capability) |
| `RLM_UsageDatatables` | Usage datatables viewer (Apex class + READ-only usage-object permissions for rlmUsageDataTable LWC) |
| `RLM_RenewalQuotes` | Renewal quick actions (`RLM_RenewalAssetLock` Apex class access, Asset, Account and Contact read) |
| `OrchestrationProcessManagerPermissionSet` | Orchestration process manager |
| `EventMonitoringPermSet` | Event monitoring |

### Deploy-Only Permission Sets (Not Explicitly Assigned)

These permission sets are stored as metadata in this repository but are not assigned to the running user via `assign_permission_sets`. Most are deployed by standard `post_*` metadata deploy tasks; some (as noted below) are present only for manual deploy. All are available for manual assignment or assignment via persona PSGs, except `RLM_BillingCollectionsRead`, which is never put in a group (a group with it fails to deploy while any holder lacks `BillingAdvancedPsl`) and is assigned next to the persona group.

| Permission Set | Deployed From | Purpose |
|---|---|---|
| `RLM_QB_Admin_Class_Access` | `unpackaged/post_quantumbit/` | Apex class access for QB admin |
| `RLM_Partner_Community_User_Perm_Set` | `unpackaged/post_prm/` | Partner community user FLS; read on the Quote and QuoteLineItem estimated-tax fields only with `quote_est_tax` and `tax` |
| `RLM_BillingCollectionsRead` | `unpackaged/post_personas/` | Read-only collection plans for the billing personas: assigned to a Billing Operations, Billing Admin or Credit Memo Operations user **next to** their persona group (see *Persona PSGs*). Needs `BillingAdvancedPsl` on the assignee |
| `RLM_BillingInvoiceDocuments` | `unpackaged/post_personas/` | Not assigned to any user by the build: it is a component of the `RLM_Billing_Admin` and `RLM_Billing_Operations` persona groups. Invoice Batch Run read with View All (and its scheduler and run-criteria chain), Access Libraries, and the invoice data mappers' reads (Product2, UnitOfMeasure, three Account fields), for invoice documents; see [Billing personas and invoice documents](#billing-personas-and-invoice-documents) |
| `RLM_BillingAccountFieldAccess` | `unpackaged/pre/3_permissionsetgroups/` | A component of `RLM_RCB` and of the billing persona groups (`RLM_Billing_Admin`, `RLM_Billing_Operations`, `RLM_Credit_Memo_Operations`), not assigned on its own; see the `RLM_RCB` table above |
| `RLM_DeleteInvoices` | `unpackaged/pre/3_permissionsetgroups/` | A component of `RLM_RCB` only, not assigned on its own; see the `RLM_RCB` table above |
| `TwinField_Permissions` | `unpackaged/post_context/` | Twin field FLS for context definitions (present in repo; not deployed by any standard task/flow — deploy manually if needed) |

### Tableau Permission Sets (`rlm_tableaunext_ps_api_names`) -- Not Assigned by Default

Defined as a YAML anchor but not assigned in any standard flow. Available for org-specific overrides.

| Permission Set |
|---|
| `TableauEinsteinAdmin` |
| `TableauEinsteinBusinessUser` |
| `TableauEinsteinAnalyst` |
| `TableauSelfServiceAnalyst` |

---

## Assignment Order in `prepare_rlm_org`

The following table shows the sequence of all permission-related steps across the full `prepare_rlm_org` flow. Step numbers use `X.Y(.Z)` notation: X is the `prepare_rlm_org` step, Y is the step within that sub-flow, and Z is the step within a further-nested sub-flow (e.g. `assign_feature_psls` / `assign_feature_permission_sets` inside `prepare_core`, or `prepare_approvals` inside `prepare_quantumbit`).

**These numbers are checked, not maintained by hand.** `tests/test_doc_build_steps.py` resolves the flow through CumulusCI and asserts both directions: every step number here points at the task named beside it, and every permission-granting step in the flow appears here. That is why the Flow/Task column spells out the whole path down to the task — it is what makes a row verifiable, and the check fails if a row and the flow disagree. Run it after inserting or removing any flow step, because one insertion renumbers every step after it.

| Step | Flow/Task | What is Assigned | Condition |
|---|---|---|---|
| 1.4 | `prepare_core` > `assign_permission_set_licenses` | Core RLM PSLs (25) | Always |
| 1.7 | `prepare_core` > `deploy_pre` | Deploy PSG metadata (`deploy_pre`) | Always |
| 1.8.1 | `prepare_core` > `assign_feature_psls` > `assign_permission_set_licenses` | CLM PSLs (11) | `clm` |
| 1.8.2 | `prepare_core` > `assign_feature_psls` > `assign_permission_set_licenses` | Einstein AI PSLs (3) | `einstein` |
| 1.8.3 | `prepare_core` > `assign_feature_psls` > `assign_permission_set_licenses` | `EinsteinAnalyticsPlusPsl` | `analytics` |
| 1.8.4 | `prepare_core` > `assign_feature_psls` > `assign_permission_set_licenses` | TSO PSLs (23) | `tso` |
| 1.9 | `prepare_core` > `recalculate_permission_set_groups` | Recalculate 11 core PSGs | Always |
| 1.10 | `prepare_core` > `assign_permission_set_groups_tolerant` | Assign 11 core PSGs | Always |
| 1.11 | `prepare_core` > `recalculate_permission_set_groups` | Recalculate `RLM_TSO` PSG | `tso` |
| 1.12 | `prepare_core` > `assign_permission_set_groups_tolerant` | `RLM_TSO` PSG | `tso` |
| 1.16.1 | `prepare_core` > `assign_feature_permission_sets` > `assign_permission_sets` | `EinsteinGPTPromptTemplateManager` | `einstein` |
| 1.16.2 | `prepare_core` > `assign_feature_permission_sets` > `assign_permission_sets` | `SalesCloudEinsteinAll` | `einstein` (non-Developer Edition) |
| 4.8 | `prepare_payments` > `assign_permission_sets` | `RLM_Payments` | `payments` |
| 7.2.3 | `prepare_quantumbit` > `prepare_approvals` > `assign_permission_sets` | `RLM_Approvals` | `quantumbit` + `approvals` |
| 7.4 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_QuantumBit` | `quantumbit` |
| 7.5 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_ExpressionSetManager` | `quantumbit` |
| 7.6 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_UtilitiesPermset` | `quantumbit` |
| 7.7 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_DecisionTableManager` | `quantumbit` |
| 7.8 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_RebuildSearchIndex` | `quantumbit` |
| 7.9 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_UsageUploader` | `quantumbit` |
| 7.10 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_UsageOrchestration` | `quantumbit` |
| 7.11 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_UsageDatatables` | `quantumbit` |
| 7.12 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` |
| 7.14 | `prepare_quantumbit` > `assign_permission_sets` | `RLM_RenewalQuotes` | `quantumbit` |
| 7.15 | `prepare_quantumbit` > `assign_permission_sets` | `DRO_Integrations` | `quantumbit` + `dro` |
| 10.10 | `prepare_docgen` > `assign_permission_sets` | `RLM_DocGen` | `docgen` |
| 13.14 | `prepare_billing` > `assign_permission_sets` | `RLM_BillingUI`, `RLM_BillingUIAssetAttributes`, `RLM_CollectionsDashboard` | `billing_ui` |
| 14.5 | `prepare_collections` > `assign_permission_sets` | `RLM_CollectionsUI` | `collections` |
| 20.1 | `prepare_tso` > `assign_permission_set_groups` | Copilot + Catalog PSGs (4) | `tso` |
| 20.4 | `prepare_tso` > `assign_permission_sets` | TSO permission sets (11) | `tso` |
| 22.7 | `prepare_prm` > `assign_permission_sets` | `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` |
| 22.10.3 | `prepare_prm` > `prepare_prm_pricing` > `assign_permission_sets` | `RLM_PRM_Pricing` | `prm` + `prm_pricing` |
| 23.1 | `prepare_agents` > `assign_permission_set_groups` | Copilot PSGs (2) | `agents` |
| 23.10 | `prepare_agents` > `assign_permission_sets` | `RLM_QuotingAgent`, `RLM_QuotingAssistant`, `RLM_BillingEmployeeAgent`, `RLM_ApprovalAgent` | `agents` |
| 24.3 | `prepare_constraints` > `assign_permission_sets` | `RLM_Constraints` | `tso` + `constraints` |
| 25.1 | `prepare_guidedselling` > `assign_permission_sets` | `OmniStudioAdmin`, `ProductCatalogManagementAdministrator` | `guidedselling` |
| 25.3 | `prepare_guidedselling` > `assign_permission_sets` | `RLM_Guided_Selling` | `guidedselling` |
| 28.3 | `prepare_large_stx` > `assign_permission_sets` | `RLM_LargeSalesTransaction` (running user) | `large_stx` |
| 29.5 | `prepare_personas` > `assign_personas_sales_rep_psg` | `RLM_Sales_Representative` PSG (salesrep user) | `personas` |
| 29.6 | `prepare_personas` > `assign_permission_sets` | `RLM_QuantumBit_Sales_Representative` (salesrep user) | `personas` |
| 29.7 | `prepare_personas` > `assign_permission_sets` | `RLM_LargeSalesTransaction` (salesrep user) | `personas` + `large_stx` |
| 29.9 | `prepare_personas` > `assign_permission_sets` | **`RLM_DecisionTableManager` (salesrep user)** — the Manager sits on the shared Home page that persona sees, so without this it renders a section that errors on class access. Narrow: class access only, deletes nothing | `personas` + (`quantumbit` \| `tso`) |
| 29.10 | `prepare_personas` > `assign_permission_sets` | `RLM_QuantumBitDemoSetup` (salesrep user) | `personas` + `quantumbit` |
| 29.11 | `prepare_personas` > `assign_permission_sets` | `RLM_Approvals` (salesrep user) | `personas` + `quantumbit` + `approvals` |
| 29.12 | `prepare_personas` > `assign_permission_sets` | `RLM_RenewalQuotes` (salesrep user) — Generate Renewal Quote and Consolidate Renewals call `RLM_RenewalAssetLock`. Narrow: class access and Asset/Account/Contact read, changes nothing | `personas` + (`quantumbit` \| `tso`) |
| 29.13 | `prepare_personas` > `assign_permission_sets` | `RLM_UsageDatatables` (salesrep user) — the Account page's View Usage tables (`RLM_UsageDataController`); the Usage (`TransactionJournal`) table stays empty for the persona, see *Record sharing*. Narrow: class access and read on usage objects | `personas` + (`quantumbit` \| `tso`) |
| 29.14 | `prepare_personas` > `assign_permission_sets` | `RLM_UsageUploader` (salesrep user) — the Account page's Add Usage uploader (`RLM_UsageUploaderController`): user-mode `TransactionJournal` create. `RLM_UsageOrchestration` is not given to the persona | `personas` + (`quantumbit` \| `tso`) |
| 31.2 | `prepare_inapp` > `assign_permission_sets` | `RLM_Learning` | `inapp` |
| 36.3 | `prepare_mcp` > `assign_permission_sets` | `RLM_McpSalesTransactions` (running user) — class access to `RLM_CloneSalesTransaction` only, so a non-admin user authorized on the MCP server can call the CLASSIC-bound clone tool. Every other MCP user needs it assigned separately (`sf org assign permset --on-behalf-of`) | `mcp` + `mcp_custom_server` |

---

## Persona PSGs (Optional)

Persona PSGs provide role-based permission groupings for end users. They are deployed by `prepare_personas`, which runs as **step 29 of `prepare_rlm_org`** when the `personas` flag is on (and can also be run standalone via `cci flow run prepare_personas`). Metadata lives in `unpackaged/post_personas/`.

| Persona PSG | Label | Permission Sets |
|---|---|---|
| `RLM_Sales_Representative` | RLM Sales Representative | `BRERuntime`, `CLMRuntimeUser`, `CorePricingRunTimeUser`, `DocGenUser`, `DocumentBuilderUser`, `DROOrderSubmitInitiateUser`, `IndustriesConfiguratorPlatformApi`, `Microsoft365WordUser`, `ObligationUser`, `ProductCatalogManagementViewer`, `ProductDiscoveryUser`, `RatingRunTimeUser`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementCalculateTaxesApi`, `RevLifecycleManagementCoreCPQAssetization`, `RevLifecycleManagementCreateContractApi`, `RevLifecycleManagementCreateOrderFromQuote`, `RevLifecycleManagementInitiateAmendmentApi`, `RevLifecycleManagementInitiateCancellationApi`, `RevLifecycleManagementInitiateRenewalApi`, `RevLifecycleManagementPlaceOrderApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi`, `RevLifecycleManagementQuotePricesTaxes`, `RevLifecycleManagementUsageDesignUser`, `UsageManagementRunTimeUser` |
| `RLM_Sales_Operations` | RLM Sales Operations | `BRERuntime`, `CLMRuntimeUser`, `CorePricingRunTimeUser`, `DocGenUser`, `DocumentBuilderUser`, `DROOrderSubmitInitiateUser`, `IndustriesConfiguratorPlatformApi`, `Microsoft365WordUser`, `ObligationUser`, `ProductCatalogManagementViewer`, `ProductDiscoveryUser`, `RatingRunTimeUser`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementCalculateTaxesApi`, `RevLifecycleManagementCoreCPQAssetization`, `RevLifecycleManagementCreateContractApi`, `RevLifecycleManagementCreateOrderFromQuote`, `RevLifecycleManagementInitiateAmendmentApi`, `RevLifecycleManagementInitiateCancellationApi`, `RevLifecycleManagementInitiateRenewalApi`, `RevLifecycleManagementPlaceOrderApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi`, `RevLifecycleManagementQuotePricesTaxes`, `RevLifecycleManagementUsageDesignUser`, `UsageManagementRunTimeUser` |
| `RLM_Product_and_Pricing_Admin` | RLM Product and Pricing Admin | `AdvancedConfiguratorDesigner`, `BREDesigner`, `BRERuntime`, `CorePricingAdmin`, `CorePricingDesignTimeUser`, `CorePricingManager`, `CorePricingRunTimeUser`, `IndustriesConfiguratorPlatformApi`, `ProductCatalogManagementAdministrator`, `ProductCatalogManagementViewer`, `ProductConfigurationRulesDesigner`, `ProductDetailsApiCache`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi` |
| `RLM_Billing_Admin` | RLM Billing Admin | `RevenueLifecycleManagementBillingAdmin`, `RLM_BillingAccountFieldAccess`, `RLM_BillingInvoiceDocuments` |
| `RLM_Billing_Operations` | RLM Billing Operations | `RevenueLifecycleManagementBillingOperations`, `RLM_BillingAccountFieldAccess`, `RLM_BillingInvoiceDocuments` |
| `RLM_Accounting_Admin` | RLM Accounting Admin | `RevenueLifecycleManagementAccountingAdmin` |
| `RLM_Tax_Admin` | RLM Tax Admin | `RevenueLifecycleManagementBillingTaxAdmin` |
| `RLM_Credit_Memo_Operations` | RLM Credit Memo Operations | `RevenueLifecycleManagementBillingCreditMemoOperations`, `RLM_BillingAccountFieldAccess` |
| `RLM_DRO_Admin` | RLM DRO Admin | `DfoAdminUser` |
| `RLM_Fulfillment_Designer` | RLM Fulfillment Designer | `DFODesignerUser` |
| `RLM_Fulfillment_Manager` | RLM Fulfillment Manager | `DFOManagerOperatorUser` |
| `RLM_Usage_Designer` | RLM Usage Designer | `ProductCatalogManagementViewer`, `RevLifecycleManagementUsageDesignUser` |

**Billing personas and collection plans (owner decision, todo 452).** None of the three billing persona groups (`RLM_Billing_Operations`, `RLM_Billing_Admin`, `RLM_Credit_Memo_Operations`) can read Collection Plan on its own: their managed role sets carry neither Collection Plan read nor the Collections and Recovery Specialist user permission, so the account balance cards show "Status Unavailable" and cannot show promises to pay [Measured: 2026-11-26, 264, scratch, one org, each group with `RLM_BillingUI` and the Billing and Billing Advanced licenses]. A user of any of the three gets the reads from the standalone `RLM_BillingCollectionsRead` set, assigned **next to** the group, plus **`BillingAdvancedPsl`**: the user license refuses that user permission without it. The balance cards also need `RLM_BillingUI` (their Apex classes and reads), which no persona group contains either: a billing persona user who should see the cards is assigned the group, `RLM_BillingUI` and `RLM_BillingCollectionsRead`, with the Billing license and `BillingAdvancedPsl`. A user of the Invoice Product Summary also needs `RLM_BillingUIAssetAttributes` (`CoreCPQUser`, for its Asset State Period Attribute query); the balance cards do not. The set is deliberately in no group: a group containing it fails to deploy ("The user license doesn't allow the permission: CollectionsAndRecoverySpecialist") while any holder lacks Billing Advanced, and keeps its old content [Measured: same org]. The build creates no billing persona users, so assigning the set and the license is the admin's step. Collection Plan's internal org-wide default is Public Read/Write, so these users see every plan [Measured: same org].

### Record sharing

Read, create and edit object permissions above don't grant row access to Private objects (View All and
Modify All do), and some objects need more than their org-wide default. Record access the build adds, and the
one it deliberately doesn't:

- `set_personas_org_wide_defaults` (`prepare_personas` step 1) sets the org-wide defaults the sales
  rep persona relies on: Read for the product and configuration objects, Read/Write for Account,
  Asset, Contract and Order, Read/Read for `UnitOfMeasure`, and internal Read for `UsageSummary` and
  `UsageBillingPeriodItem` (the Account page's usage uploader and View Usage tables read them in
  user mode: at Private the persona's upload fails, and it can't see the summaries, which the rating
  pipeline creates owned by the admin).
- The `ExpressionSet` criteria sharing rule `RLM_Constraint_Models_Read`
  (`unpackaged/post_constraints/sharingRules/`, deployed by `prepare_constraints` step 2 when
  `constraints` is on) shares constraint-model Expression Sets (`UsageType = Constraint`) Read with
  **all internal users**. On a cold constraint solver, the first configuration-rules run redeploys
  the models as the running user, so a non-admin needs to see these rows. Pricing procedures and
  other Expression Sets stay Private, as does access for external (Experience Cloud) users.
- The Docgen Document Template Library membership (`create_docgen_library`, `prepare_docgen`
  step 1, when `docgen` is on): the public group `RLM_DocGen_Template_Users`, seeded with **all
  internal users**, is a member of `DocgenDocumentTemplateLibrary` with the read-only permission
  `RLM DocGen Template Viewer`. Generation reads the template file as the generating user, and only
  library members can read it, so without this only the build admin can generate documents (todo 435).
  Every library permission is off: a member's new version of a library file is refused
  (`INSUFFICIENT_ACCESS_ON_CROSS_REFERENCE_ENTITY`, measured 2026-11-26 on 264). A member also needs the
  **Access Libraries** user permission (`ContentWorkspaces`) to read the files: the Standard User and RLM
  Sales Representative profiles have it, Minimum Access does not. Users of the `RLM_Billing_Admin` and
  `RLM_Billing_Operations` groups get it from `RLM_BillingInvoiceDocuments` (todo 292, see *Billing personas
  and invoice documents*); the other billing persona groups do not get it from this set. Details:
  `docs/guides/docgen-setup.md` → Template Library Access.
- **View All on the invoice batch run objects** (todo 292): holders of `RLM_Billing_Admin` and
  `RLM_Billing_Operations` see every invoice batch run, billing batch scheduler and invoice batch run criteria
  record through `RLM_BillingInvoiceDocuments`, which grants View All on `InvoiceBatchRun`,
  `BillingBatchScheduler` and `InvoiceBatchRunCriteria` (all Private [Measured: 2026-11-26, 264 scratch, EntityDefinition.InternalSharingModel]; the developer guide lists
  no Share object for `InvoiceBatchRunCriteria`, yet its default is still Private). See *Billing personas and invoice
  documents*.
- **Not added: `TransactionJournal` (usage records).** Without View All on `TransactionJournal` the
  sales rep persona sees none of its rows, not even the ones it created; Read isn't enough. The object
  has no owner field, `UserRecordAccess` still reports Read, and a direct retrieve by Id returns
  `NOT_FOUND` (checked live on 264, todo 315). The admin sees the rows through the System Administrator
  profile's View All, and so does a user with the standard Accounts Receivables Admin permission set
  (`RevenueLifecycleManagementAccountingAdmin`, which needs the Billing license), whose grant on the
  object includes View All; the Billing license alone doesn't help. View All would let the sales rep
  persona read every account's usage records, so the persona's View Usage **Usage** table stays empty by
  design. The persona can still upload usage and see the rated summaries.

### Billing personas and invoice documents

What a user of `RLM_Billing_Admin` or `RLM_Billing_Operations` needs to generate invoice PDFs, batch
(**Generate Invoice Documents** on an Invoice Batch Run) and on demand (**Generate Invoice Document** on an
Invoice) (todo 292). The access below was measured headlessly, in check-only and post-deploy test runs, mostly as Minimum
Access users holding the Billing license and each group or its content (the text below names the other users
measured), and, for the invoice document data and the live run, as Login As personas through the UI
[Measured: 2026-11-26, 264, scratch builds]. The Invoice Batch Run reads were checked as the group itself, with
the set in `RLM_Billing_Admin` and `RLM_Billing_Operations`: the group methods ran (each created a user) and the
debug log showed a CHECKED line for each group [Measured: 2026-11-26, 264, scratch, post-deploy test run]. That
run logged the previous wording ("CHECKED: RLM_Billing_Admin is Updated"); the class now logs, for example,
"CHECKED: RLM_Billing_Admin (was Updated); asserting its Invoice Batch Run reads". The batch process create (checked as each managed role set plus `RLM_BillingInvoiceDocuments`
and both DocGen sets, not as the group) was asserted the same way: the debug log shows "CHECKED:
RevenueLifecycleManagementBillingAdmin batch process create asserted (setting ENABLED)" and the same for
RevenueLifecycleManagementBillingOperations, so the test reads the setting row and asserts the insert [Measured: 2026-11-26, 264, scratch, post-deploy test run]. **A live persona run found the empty-PDF gap the invoice document data reads close, and a re-run with the shipped sets plus a test app-visibility set gave complete PDFs (on demand on a Minimum Access persona, batch on a Standard User persona). Batch generation on a Minimum Access persona does not start, even with the shipped sets plus a test app-visibility set (todo 292, open).**

| Need | Why | How the persona gets it |
|---|---|---|
| Billing license (`RevLifecycleMgmtBillingPsl`) | The managed role set in the group requires it | Assigned with the group |
| DocGen Designer license (`DocGenDesignerPsl`), **`DocGenUser`** and **`DocGenDesigner`** | The groups reach no document generation object at all ("Access to entity 'DocumentTemplate' denied", the same for `DocumentGenerationProcess` and `DocGenerationBatchProcess`). `DocGenUser` opens templates (read) and the on-demand `DocumentGenerationProcess` create, but not the batch create: a user-mode insert of `DocGenerationBatchProcess` is refused with `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY: DML operation INSERT not allowed on DocGenerationBatchProcess` (one error: status code and message; a user with no DocGen set gets the same code with "Access to entity 'DocGenerationBatchProcess' denied"), the likely cause of the `INSUFFICIENT_ACCESS` the batch action returned for a billing persona with `DocGenUser`, as reported in todo 292 from an earlier fresh build `[inferred: the action itself was not run here]`. `DocGenDesigner` opens it. Help names DocGen User for generating, so both sets are assigned; they share the one license | **Assigned next to the group** by an admin; the build creates no billing persona users. Not in the group, for the todo 452 reason: existing holders of the billing groups may lack `DocGenDesignerPsl`, and a group gaining a set whose license a holder lacks fails to deploy (measured for `BillingAdvancedPsl` in todo 452). `RLM_Sales_Representative` and `RLM_Sales_Operations` do carry `DocGenUser`; the build's sales rep user holds that license (checked on the measured org) |
| Invoice Batch Run read, with View All | Batch generation runs from the run record. The managed Billing Admin set grants no access to it ("Access to entity 'InvoiceBatchRun' denied"); the managed Billing Operations set reads it. The object is Private [Measured: 2026-11-26, 264 scratch, EntityDefinition.InternalSharingModel], so read alone shows a user only the runs it owns; View All opens every run. Read and View All on `InvoiceBatchRun` require the same on `BillingBatchScheduler`, which requires the same on a run-criteria object (`InvoiceBatchRunCriteria` here); the deploy refuses each step without the next. None of the three objects has a permissionable field, so the set has no field grants on them | `RLM_BillingInvoiceDocuments`, in `RLM_Billing_Admin` and `RLM_Billing_Operations` |
| Access Libraries (`ContentWorkspaces`) | The template file is in the Docgen Document Template Library and is read as the generating user. A library member without this user permission did not read the `DefaultInvoiceTemplate` file (the only file measured; the other library files `[inferred]`); measured as the managed role set plus `RLM_BillingInvoiceDocuments`, and as Minimum Access users without it, through a recreated library group shape or as direct members, headlessly not as a persona group; live as an `RLM_Billing_Admin` persona on Minimum Access (see below). Minimum Access lacks it; Standard User has it. The managed Billing Admin and Billing Operations sets do not carry it (`PermissionsContentWorkspaces` false on both, measured), so the grant is not redundant for these two personas. The other billing persona groups do not get it from this set: the repo's `RLM Tax Admin` profile enables it, the managed Credit Memo Operations set was checked and lacks it (`PermissionsContentWorkspaces` false), and the managed Tax Admin and Accounting Admin sets were not checked for it | `RLM_BillingInvoiceDocuments`, in `RLM_Billing_Admin` and `RLM_Billing_Operations` only |
| Library membership | The default invoice template's file (`DefaultInvoiceTemplate`, and `RLM_InvoiceTemplate`) is in that library | `create_docgen_library` (all internal users, see *Record sharing*). It runs in `prepare_docgen`, under the `docgen` flag, while the groups deploy in `prepare_personas`, under `personas`: a personas build with docgen off has no membership. An org built before that step was added (todo 435) needs `cci task run create_docgen_library --org <alias>` once |
| Invoice document data | The invoice document's data mappers (`BillingDocumentGenerationGetInvoiceDetails` and `BillingDocumentGenerationTransformInvoiceDetails`, for `DefaultInvoiceTemplate`) read as the generating user: Invoice, InvoiceLineRelationship, InvoiceLine, Account (billing and shipping address, phone), Contact, User (company street, city, phone), ContentDocument, Product2 and UnitOfMeasure. A persona missing a read still gets a Success status, not an error, and a PDF that is **empty, or without addresses**: without Product2 and UnitOfMeasure the PDF was empty, and without the Account fields it had data but no addresses [Measured: 2026-11-26, 264, scratch, Login As persona, UI buttons]. Missing reads on Contact, User and ContentDocument were not tested. Product2 and UnitOfMeasure read together fill in the invoice data and lines (either alone does not); the Account billing address, shipping address and phone reads fill in the addresses. The managed Billing Admin set reads Account but not Product2, UnitOfMeasure or those Account fields; the managed Billing Operations set reads Product2 and UnitOfMeasure but not the fields [Measured: 2026-11-26, 264, scratch, check-only probe as Minimum Access users]. Account object read comes from the role sets, so the set adds only the field reads | `RLM_BillingInvoiceDocuments`: Read on Product2 and UnitOfMeasure, read (not edit) on `Account.BillingAddress`, `Account.ShippingAddress` and `Account.Phone` |
| Lightning Experience User and app access | To use the UI buttons, a persona opens the Invoice Batch Run and Invoice records in Lightning from an app it can see (supplied in the live run, not isolated). The build's own sets in the billing groups (`RLM_BillingAccountFieldAccess`, `RLM_BillingInvoiceDocuments`) grant neither the Lightning Experience User user permission nor app or tab visibility, and the build creates no billing persona users, so the profile and any app set are the admin's step. Whether the managed Billing Admin and Billing Operations sets carry them was not checked | Not from the build's own sets: the admin assigns it (profile or a set); the live run used a separate set |

**Live persona run** [Measured: 2026-11-26, 264, scratch, Login As persona, UI buttons]: a Minimum Access persona and a Standard User persona, each holding the Billing and DocGen Designer licenses, `RLM_Billing_Admin` (with this set as it was before the invoice document data reads were added), `DocGenUser` and `DocGenDesigner`, used the UI buttons with `DefaultInvoiceTemplate`.

- **On demand (Generate Invoice Document), Minimum Access persona only** (no Standard User on-demand run was made): status Success; the persona owns the generated file and it is shared with the invoice. Before the invoice document data reads were granted, the PDF was the template frame only (no number, dates, lines or totals), while an admin's PDF of a sibling invoice was complete. Granting Product2 and UnitOfMeasure read filled in the invoice data and lines, and the three Account field reads the addresses; with all of them the persona's PDF matched the admin's. Omnistudio User (`OmniStudioExecution` with its license) changed nothing for this persona.
- **Batch (Generate Invoice Documents on the run), Standard User persona:** completes; the PDF is empty without the data reads and complete with them (addresses, both lines, milestone text).
- **Batch, Minimum Access persona: did not start. [Open]** The `DocGenerationBatchProcess` it creates stays `New` and the run stays In Progress, while an admin's and a Standard User persona's move to `InProgress` at once. Ruled out (the persona held each of these during the attempts): API Enabled; Omnistudio User with its license; and 37 of the 47 user permissions the Standard User profile has and Minimum Access lacks (not counting API Enabled), granted in a permission set. Not tried: the other 10, which a set refused because they depend on object permissions it did not have (View Setup, Export Reports, Import Personal Contacts, Convert Leads, Override Forecasts, Send Email, Mass Email, List Email Send, Transactional Email Send, Remove Direct Message Members), and object access. The cause is not isolated, so a billing persona on Minimum Access cannot run batch generation today; one on Standard User can.
- The platform sets `DocGenerationBatchProcess.Description` itself, so the persona needs no field access on it.
- **Re-run with the shipped sets plus a test app-visibility set** [Measured: 2026-11-26, 264, scratch, Login As persona, UI buttons], after the invoice document data reads were added to this set and every temporary grant was removed. Each persona held only `RLM_Billing_Admin`, `DocGenUser`, `DocGenDesigner` and the licenses, plus a test app-visibility set, which granted only visibility of two apps, tab visibility for Account, Case and Home, and the Lightning Experience User user permission: no object or field permissions, no Access Libraries and no other user permission:
  - on demand, **Minimum Access persona**, fresh invoice: Success, and the PDF is complete (invoice number, dates, billing and shipping address, phone, line, tax, totals);
  - batch, **Standard User persona**: the batch process went to `InProgress` at once and completed in about 90 seconds (1 generated, 0 failed); the PDF is complete (addresses, lines, milestone text);
  - batch, **Minimum Access persona**, holding the same sets (`RLM_Billing_Admin` with the current set, `DocGenUser`, `DocGenDesigner`, the licenses and the test app-visibility set): the batch process stays `New` and the run stays In Progress, as before [Measured: 2026-11-26, 264, scratch, Login As persona, UI buttons]. So a Minimum Access persona's batch does not start with the shipped sets plus a test app-visibility set either.
  - The Minimum Access persona, holding the build's `RLM_Billing_Admin` group, generated a complete PDF from
    `DefaultInvoiceTemplate`, reading the template file through the build's own library membership.
- **Who owns the generated file:** for on-demand generation the persona owns it; for batch generation the file was created by the org's admin user (`ContentVersion.CreatedById`), not the persona (observed once, in the same re-run, Standard User persona).

What `DocGenDesigner` opens beyond `DocGenUser` [Measured: same org; user permissions read from `PermissionSet`,
object access from describe as the user]: `DocGenUser` carries the user permissions DocGen Runtime User,
Context Service Runtime and Manage Content Links; `DocGenDesigner` carries **DocGen Designer**, **Context
Service Admin** and Manage Content Links. Both managed billing role sets (Billing Admin, Billing Operations)
already carry Context Service Admin, so for these two personas Designer's real extras are template authoring
(create and edit on `DocumentTemplate` and `DocumentTemplateContentDoc`) and the batch create (create and edit
on `DocGenerationBatchProcess`). Template authoring is the cost of the batch action. The gate on the batch create is the **DocGen Designer** user permission together with create on the
object: a licensed custom set with only that permission is still refused, an object create grant alone is
refused, and the two together allow the insert, without template edit. Whether the batch action accepts that
narrower pair instead of the managed set was not measured, so the managed set is what is documented.

`RLM_BillingInvoiceDocuments` carries no license, so it can sit in `RLM_Billing_Admin` and `RLM_Billing_Operations`: their holders already have
the Billing license. Billing Advanced is not needed for invoice documents.

`RLM_BillingInvoiceDocumentsAccessTest` (`unpackaged/post_personas/classes/`) checks, as Minimum Access users:

- **as the group itself:** the Invoice Batch Run reads. In a deploy that changes the group or its sets the group
  may not read `Updated`, so the test recalculates it with `Test.calculatePermissionSetGroup`, asserts it then
  reads `Updated`, and assigns and checks it. The recalculation was measured in deploys that changed
  `RLM_BillingInvoiceDocuments`; a deploy that first adds the set to the groups (a first install) was not
  measured with it (an earlier check-only deploy of that kind, with the previous class version, did see both
  groups `Outdated` [Measured: 2026-11-26, 264, scratch, check-only probe]). A group in
  `Failed` status, a recalculation that throws, or one that does not reach `Updated` fails the test; there is
  no skip. A probe test, in a deploy that changed the set, saw both groups `Outdated`; the call succeeded and
  they then read `Updated` [Measured: 2026-11-26, 264, scratch, check-only probe]. The current class passed
  14/14 in a check-only deploy that changed only the set's description [Measured: 2026-11-26, 264, scratch,
  check-only]. (An
  API edit of a group's components also leaves it `Updating` for a while `[seen in the todo 292 log,
  2026-10-28, on RLM_RCB, not on the billing persona groups]`.)
- **as the managed role set plus `RLM_BillingInvoiceDocuments`** (the group's content without its field-access
  set): the Invoice Batch Run reads, and with both DocGen sets the batch create, the on-demand create and
  template read. The batch check covers the create only. A Minimum Access user passes it, while its live batch process stays New (todo 292, open). The batch create is a real user-mode insert, the only check that meets the DocGen Designer
  user-permission gate. With batch document generation turned off (an org setting deployed by `docgen`, not
  `personas`) the platform refuses it with `INVALID_INPUT` "Enable the batch document generation setting."
  [Measured: 2026-11-26, 264, scratch, check-only probe]. With batch on and server-side generation off (client-side mechanism) the persona gets `INVALID_INPUT`
  "Enable the server-side document generation setting." [Measured: 2026-11-26, 264, scratch, check-only probe]; batch on with
  server-side off and the server-side mechanism is refused at deploy. The access check answers before the
  setting check in each of the three measured states: a user with no DocGen set and a user with `DocGenUser` but not `DocGenDesigner`
  got `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` with batch off, with server-side off and with both on, while the
  `DocGenDesigner` persona got `INVALID_INPUT` naming the missing setting in each off state and succeeded with
  both on [Measured: 2026-11-26, 264, scratch, check-only probe]. So the test reads both settings first
  (`IsBatchDocGnrnEnabled` and `IsServerSideDocGenEnabled`). With no setting row (batch document generation
  not configured, e.g. an org where DocGen was never set up `[inferred: no measured org lacked a row]`) the insert is not attempted and the test logs
  "SKIPPED, NOT CHECKED". The measured org had one setting row and Help speaks of "a Document Generation Setting
  record"; one row is not guaranteed, so the test reads the oldest. With a row and both flags on, any refusal fails; with a row and either flag off, only
  `INVALID_INPUT` is a "SKIPPED, NOT CHECKED" WARN line and any other status code fails. An attempted and
  asserted insert logs "CHECKED: <role> batch process create asserted (setting <state>)". With both flags on, the other settings do not stop the insert: it succeeds with the client-side
  generation mechanism and with an hourly batch percentage limit (`batchDocGnrnPctLimitPerHour`) of 0 [Measured: 2026-11-26, 264, scratch, check-only probe]. It decides by status code and setting, never by message text. The Billing
  Operations run-read, group and DocGen methods pass without the set's grants (the managed Operations set and the
  DocGen sets supply that access); the set itself is checked by the metadata tests, the Billing Admin methods and
  both invoice-document-data reads. In both DocGen methods (Admin and
  Operations) the DocGen assertions check the managed DocGen sets assigned next to the group; the Admin one
  depends on the set only through its run reads, which the Admin run-read method already checks;
- **the invoice document data reads**, as the managed role set plus `RLM_BillingInvoiceDocuments`: a USER_MODE
  read of Product2, UnitOfMeasure and the three Account fields (fails for Billing Admin if the set loses any of
  them, for Billing Operations if it loses a field). Passed in a post-deploy test run with the set and groups
  deployed [Measured: 2026-11-26, 264, scratch, post-deploy test run]; the Billing Operations read passing there
  also shows the managed Operations set reads Account;
- **the set's metadata:** exactly Read and View All on the run chain, exactly Read on Product2 and
  UnitOfMeasure, exactly read on the three Account fields, Access Libraries, and membership of
  `RLM_Billing_Admin` and `RLM_Billing_Operations`. The exact-grant tests passed in the same post-deploy test
  run, with all 14 methods of the class.


It does **not** read the template file. That read depends on org data and configuration (the template, its
library, which members an admin left in `RLM_DocGen_Template_Users`), so it cannot gate a deploy. It was
measured as the managed Billing Admin role set plus `RLM_BillingInvoiceDocuments` (and as Minimum Access users
without that set, and a Standard User), not as a persona group, by check-only probes that recreated the build's
group shape inside the test (a read-only library
permission and a public group holding All Internal Users, as library member): a Minimum Access user with the
Billing Admin role set and `RLM_BillingInvoiceDocuments` read the `DefaultInvoiceTemplate` file through it,
and so did a Standard User, also in a copy of the test class [Measured: 2026-11-26, 264, scratch, check-only probe]. Minimum Access users without Access
Libraries read none of it through the same group shape or as direct members; with only that permission added,
a direct member read it [Measured: 2026-11-26, 264, scratch, check-only probe]. Through the build's own group it was shown live: a Minimum Access persona
holding the build's `RLM_Billing_Admin` group generated a complete PDF from `DefaultInvoiceTemplate` through
the build's library membership [Measured: 2026-11-26, 264, scratch, Login As persona, UI buttons].

Nothing in the class fails because Salesforce grants more than today, and it creates no user just to watch
for that. It does fail on an access regression, by design. Each method creates at most one user,
which needs a Salesforce user license, and needs one free seat of each permission set license it assigns: the
Billing license, and `DocGenDesignerPsl` for the DocGen methods. Both seat needs are new to this bundle:
before todo 292 the personas bundle had no Apex, and a deploy that runs local
tests runs every local test in the org, this class included.

Answered by the live persona run: the `DocGenerationBatchProcess.Description` write (the platform sets it);
reading the on-demand output (the persona owns the file, shared with the invoice); bill-to data on the PDF: the
default data mappers read the invoice's Account, not its BillingAccount, so the addresses need the Account field
reads above, now in the set. The persona did not own that Account but could read it, because the personas build
sets Account to internal Read/Write (`set_personas_org_wide_defaults`; Account `InternalSharingModel` ReadWrite
[Measured: 2026-11-26, 264, scratch]); under a Private Account default it would
also need sharing to the Account `[inferred]`. Omnistudio User: not needed for on-demand generation on the
Minimum Access persona, nor for batch generation on the Standard User persona. Still open, or not measured:

- **Batch generation for a Minimum Access persona** (see the live run above): the batch process stays `New`.
- **`DocumentGenerationProcess.RequestText` and `ReferenceObject`:** a Minimum Access persona cannot set them on a
  direct insert ("Operation failed due to fields being inaccessible"); the on-demand action succeeded without
  them, but the Help's route of creating the record in a Flow or Apex as the user does need them.
- **The scheduler's Generate invoice documents option** (Billing Batch Scheduler; release note
  `rn_billing_generate_invoice_documents_batch`), which generates documents during the run: not checked for a
  persona-owned or persona-run scheduler.
- **Credit Memo Operations** (`RLM_Credit_Memo_Operations`) is not covered.
- **`RLM_Billing_Operations` was not run live:** only headless role-set and group checks; the live runs held
  `RLM_Billing_Admin`.
- **A persona opening a batch-generated file,** which the org's admin user created.
- **On-demand generation on a Standard User persona** was not run.

On 264 `DocGenUser` does not carry the DocGen Designer user permission (`PermissionsDocGenDesigner` false,
measured). If a later release adds it, `DocGenDesigner`, and the template authoring that comes with it, may no
longer be needed for the batch create; nothing watches for this.

---

## Feature Flag Quick Reference

| Feature Flag | PSLs Assigned | PSGs Assigned | Permission Sets Assigned |
|---|---|---|---|
| *(always)* | Core RLM (25) | 11 core PSGs | -- |
| `analytics` | `EinsteinAnalyticsPlusPsl` | -- | -- |
| `clm` | CLM (11) | -- | -- |
| `einstein` | AI (3) | -- | `EinsteinGPTPromptTemplateManager`, `SalesCloudEinsteinAll` |
| `tso` | TSO (23) | `RLM_TSO`, Copilot (2), Catalog (2) | `ERIBasic`, `RLM_UtilitiesPermset`, `RLM_ExpressionSetManager`, `RLM_DecisionTableManager`, `RLM_RebuildSearchIndex`, `RLM_UsageUploader`, `RLM_UsageOrchestration`, `RLM_UsageDatatables`, `RLM_RenewalQuotes`, `OrchestrationProcessManagerPermissionSet`, `EventMonitoringPermSet` |
| `quantumbit` | -- | -- | `RLM_QuantumBit`, `RLM_ExpressionSetManager`, `RLM_UtilitiesPermset`, `RLM_DecisionTableManager`, `RLM_RebuildSearchIndex`, `RLM_UsageUploader`, `RLM_UsageOrchestration`, `RLM_UsageDatatables`, `RLM_RenewalQuotes` |
| `quantumbit` + `calmdelete` | -- | -- | `RLM_CALM_SObject_Access` |
| `quantumbit` + `approvals` | -- | -- | `RLM_Approvals` |
| `quantumbit` + `dro` | -- | -- | `DRO_Integrations` |
| `docgen` | -- | -- | `RLM_DocGen` |
| `tso` + `constraints` | -- | -- | `RLM_Constraints` |
| `prm` + `prm_exp_bundle` + `tso` | -- | -- | `RLM_PRM` |
| `agents` | -- | Copilot (2) | `RLM_QuotingAgent`, `RLM_QuotingAssistant`, `RLM_BillingEmployeeAgent`, `RLM_ApprovalAgent` |

---

## Implementation Notes

1. **PSLs before PSGs** -- Salesforce requires the underlying license before any PSG containing those permission sets can take effect. The flow enforces this by assigning PSLs at `prepare_core` steps 4 and 8, then PSGs at steps 10 and 12.

2. **PSG recalculation** -- After deploying PSG metadata (`deploy_pre`), the `recalculate_permission_set_groups` task waits for Salesforce to finish calculating PSG status (`Outdated` -> `Updating` -> `Updated`) before assignment. Without this wait, assignment can fail silently.

3. **Tolerant assignment** -- `assign_permission_set_groups_tolerant` extends the standard CCI `AssignPermissionSetGroups` task to tolerate warnings about permissions unavailable on the target org edition (e.g., Enterprise vs. Unlimited). Used for core PSGs and `RLM_TSO`.

4. **Persona PSGs target end users** -- Deployed by `prepare_personas` (step 29 of `prepare_rlm_org` when the `personas` flag is on; also runnable standalone via `cci flow run prepare_personas`). Designed for end-user role assignment rather than admin provisioning.

5. **Deploy-only permission sets** -- Several permission sets (e.g., agent permission sets) are deployed as metadata but not auto-assigned to the running user. They are available for manual assignment to specific users or inclusion in persona PSGs.
6. **Persona assignments are not admin assignments** -- steps 29.5-29.14 assign to the salesrep user (29.5 through its task's `user_alias: salesrep`, the rest through flow options), so those grants land on a **non-admin** user. `RLM_UtilitiesPermset`, which is destructive, is not among them: the Account Reset is admin-only (todo 397), `prepare_personas` has no step 29.8, and the persona gets no reset grant.
