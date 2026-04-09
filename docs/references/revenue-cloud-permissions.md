# Revenue Cloud Permissions Reference

This document describes the Permission Set Licenses (PSLs), Permission Set Groups (PSGs), and individual Permission Sets used by the RLM Base Foundations project, how they map to feature flags, and the order in which they are assigned during `prepare_rlm_org`.

---

## Permission Set Licenses (PSLs)

PSLs are Salesforce-managed licenses that must be assigned to a user before the corresponding permission sets or PSGs can take effect. They are assigned early in `prepare_core` (steps 2, 7, 8, 10) before any PSGs or permission sets.

### Core RLM PSLs (`rlm_psl_api_names`) -- Always Assigned

Assigned unconditionally at step 2 of `prepare_core` (25 licenses).

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

### `EinsteinAnalyticsPlusPsl` -- Always Assigned

Assigned unconditionally at step 10 of `prepare_core` (separate from AI list because it is always required for RLM_RMI PSG functionality).

### CLM PSLs (`rlm_clm_psl_api_names`) -- `clm: true`

Assigned at step 7 of `prepare_core` (11 licenses). Several overlap with core PSLs; Salesforce deduplicates automatically.

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

Assigned at step 8 of `prepare_core` (3 active licenses).

| PSL API Name | Capability Area |
|---|---|
| `AgentforceServiceAgentBuilderPsl` | Agentforce builder |
| `EinsteinGPTCopilotPsl` | Einstein Copilot |
| `EinsteinGPTPromptTemplatesPsl` | Prompt templates |

> Several AI PSLs are commented out because they are unavailable on Enterprise dev scratch orgs (e.g., `EinsteinAnalyticsPlusPsl`, `RevenueIntelligencePsl`, `MySearchPsl`, `ScoringFrameworkPsl`).

### TSO PSLs (`rlm_tso_psl_api_names`) -- `tso: true`

Assigned in `prepare_tso` step 1 (23 licenses). These are Trialforce Source Org-specific licenses for Sales Cloud Unlimited, Einstein features, and engagement tools.

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

PSGs bundle multiple Salesforce-managed permission sets into capability-area groups. The PSG metadata is deployed during `deploy_pre` (step 5 of `prepare_core`) from `unpackaged/pre/3_permissionsetgroups/`, recalculated at step 11, then assigned to the running user at step 12.

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

#### RLM_RCB -- Revenue Cloud Billing Advanced (16 permission sets)

Billing super-user PSG covering invoicing, payments, credit memos, tax, collections, and accounting.

| Permission Set | Purpose |
|---|---|
| `AnalyticsStoreUser` | Analytics data access |
| `BillingAdvancedPaymentAdministrator` | Payment admin |
| `BillingAdvancedPaymentOperations` | Payment operations |
| `BillingCollectionsAndRecoverySpecialist` | Collections |
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

#### RLM_NGP -- Salesforce Pricing (4 permission sets)

| Permission Set | Purpose |
|---|---|
| `CorePricingAdmin` | Pricing admin |
| `CorePricingDesignTimeUser` | Pricing design |
| `CorePricingManager` | Pricing management |
| `DecimalQuantityDesigntime` | Decimal quantity |

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

Assigned in `prepare_tso` step 6 via `assign_permission_set_groups_tolerant`. Contains 50 permission sets spanning Sales Cloud Unlimited, Einstein AI, Tableau, CLM AI, Data Cloud, and engagement features. This is the catch-all PSG for trial/demo orgs that bundles permissions unavailable on Enterprise dev scratch orgs.

<details>
<summary>Full list (50 permission sets)</summary>

`AIAcceleratorPsl`, `AdvancedCsvDataImport`, `AnalyticsQueryService`, `CDPAdmin`, `CGAnalyticsAdmin`, `CLMAnalyticsAdmin`, `CallCoachingIncluded`, `CallCoachingUserPsl`, `ContractsAIClauseDesigner`, `ContractsAIRuntimeUser`, `DataCloudMtrcsVisualizationPsl`, `EinsteinActivityCaptureIncluded`, `EinsteinAgentCWU`, `EinsteinAnalyticsAdmin`, `EinsteinAnalyticsPlusAdmin`, `EinsteinAssistantPsl`, `EinsteinCopilotReviewMyDay`, `EinsteinDiscoveryInTableau`, `EinsteinGPTCallExplorerPsl`, `EinsteinGPTGetProductPricing`, `EinsteinGPTSalesCallSummaries`, `EinsteinGPTSalesEmails`, `EinsteinGPTSalesMiningPsl`, `EinsteinGPTSalesSummaries`, `EinsteinGPTSearchAnswers`, `EinsteinPredictionsManagerAdmin`, `EinsteinReplyRecommendations`, `EinsteinSearchAnswers`, `EinsteinSendMeetingRequestCopilot`, `EinsteinServiceInnovations`, `GenieAdmin`, `HighVelocitySalesCadenceCreatorIncluded`, `HighVelocitySalesQuickCadenceCreatorIncluded`, `HighVelocitySalesUserIncluded`, `InboxIncluded`, `MetadataStudioUser`, `NLPServicePsl`, `PipelineInspectionIncluded`, `PrismBackofficeUser`, `PrismPlaygroundUser`, `QueryForDataPipelines`, `SalesActionReviewBuyingCommittee`, `SalesCloudEinsteinIncluded`, `SalesCloudUnlimitedIncluded`, `SalesMeetingsIncluded`, `TableauEinsteinAdmin`, `TableauEinsteinAnalyst`, `TableauEinsteinIncludedAppBusinessUser`, `TableauIncludedAppManager`, `TableauUser`
</details>

### Copilot/Catalog PSGs (`rlm_tso_psg_api_names` / `rlm_ai_psg_api_names`)

These Salesforce-managed PSGs are assigned in two contexts:

| PSG | Assigned When | Flow Step |
|---|---|---|
| `CopilotSalesforceUserPSG` | `tso: true` OR `agents: true` | `prepare_tso` step 2 / `prepare_agents` step 1 |
| `CopilotSalesforceAdminPSG` | `tso: true` OR `agents: true` | `prepare_tso` step 2 / `prepare_agents` step 1 |
| `UnifiedCatalogAdminPsl` | `tso: true` only | `prepare_tso` step 2 |
| `UnifiedCatalogDesignerPsl` | `tso: true` only | `prepare_tso` step 2 |

---

## Feature-Gated Permission Sets

Individual permission sets defined in project metadata (for example under `force-app/` and `unpackaged/post_*` directories) and assigned conditionally. These grant access to custom fields, Apex classes, or agent configurations specific to each feature.

### Explicitly Assigned Permission Sets

These are assigned to the running user via `assign_permission_sets` in their respective flows.

| Permission Set | Feature Flag(s) | Flow / Step | What It Grants |
|---|---|---|---|
| `RLM_QuantumBit` | `quantumbit` | `prepare_quantumbit` step 4 | FLS on custom QB fields (Order, Quote, etc.) |
| `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` | `prepare_quantumbit` step 5 | SObject access for CALM Delete operations |
| `RLM_Approvals` | `quantumbit` + `approvals` | `prepare_approvals` step 3 (called from `prepare_quantumbit` step 2) | FLS on approval fields + `RLM_AA_Submit_Approval` Apex class |
| `RLM_DocGen` | `docgen` | `prepare_docgen` step 10 | FLS on seller/docgen fields (Quote, QuoteLineItem) |
| `RLM_RampSchedule` | `ramps` | `prepare_ramp_builder` step 3 | FLS on ramp fields + 11 ramp Apex classes + RunFlow |
| `RLM_Constraints` | `tso` + `constraints` | `prepare_constraints` step 3 | FLS on `RLM_ConstraintEngineNodeStatus__c` (3 objects) |
| `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` | `prepare_prm` step 8 | FLS on partner/channel program fields |
| `RLM_QuotingAgent` | `agents` | `prepare_agents` step 4 | Agent access to `Revenue_Quote_Management` |
| `RLM_UtilitiesPermset` | `tso` | `prepare_tso` step 5 | `RLM_AccountUtilities` Apex class access |

### Einstein / AI Permission Sets (`rlm_ai_ps_api_names`) -- `einstein: true`

Assigned at step 19 of `prepare_core`.

| Permission Set | Purpose |
|---|---|
| `EinsteinGPTPromptTemplateManager` | Prompt template management |
| `SalesCloudEinsteinAll` | Sales Cloud Einstein features |

### TSO Permission Sets (`rlm_tso_ps_api_names`) -- `tso: true`

Assigned in `prepare_tso` step 5.

| Permission Set | Purpose |
|---|---|
| `ERIBasic` | ERI platform |
| `RLM_UtilitiesPermset` | Utility features (Apex class access) |
| `OrchestrationProcessManagerPermissionSet` | Orchestration process manager |
| `EventMonitoringPermSet` | Event monitoring |

### Debug-Only Permission Sets (`psg_debug: true`)

These are normally covered by their parent PSGs (RLM_RCB, RLM_PCM). The `psg_debug` flag assigns them individually for troubleshooting when PSG recalculation is suspect.

| Anchor | Permission Sets | Condition | Parent PSG |
|---|---|---|---|
| `rlm_pcm_ps_api_names` | `IndustriesConfiguratorPlatformApi`, `ProductConfigurationRulesDesigner`, `ProductCatalogManagementAdministrator`, `ProductCatalogManagementViewer` | `tso` + `psg_debug` | RLM_PCM / RLM_CFG |
| `rlm_blng_ps_api_names` | 10 billing permission sets (same as RLM_RCB minus `DocGenDesigner`, `BillingAdvancedPayment*`, `BillingCollectionsAndRecoverySpecialist`, `DataProcessingEngineUser`, `RevenueLifecycleManagementBillingCustomerService`) | `billing` + `psg_debug` | RLM_RCB |

### Deploy-Only Permission Sets (Not Explicitly Assigned)

These permission sets are stored as metadata in this repository but are not assigned to the running user via `assign_permission_sets`. Most are deployed by standard `post_*` metadata deploy tasks; some (as noted below) are present only for manual deploy. All are available for manual assignment or assignment via persona PSGs.

| Permission Set | Deployed From | Purpose |
|---|---|---|
| `RLM_QB_Admin_Class_Access` | `unpackaged/post_quantumbit/` | Apex class access for QB admin |
| `RLM_UsageDatatables` | `unpackaged/post_utils/` | Read access to usage objects + `RLM_UsageDataController` Apex class for Usage Datatable LWC |
| `RLM_Collection_Plan_Activity` | `unpackaged/post_collections/` | CRUD on `Collection_Plan_Activity__c` custom object (present in repo; not deployed by any standard flow — deploy manually if needed) |
| `RLM_Custom_Sales_Rep_Perm_Set` | `unpackaged/post_personas/` | Custom sales rep permissions (deploy-only; available for manual or future persona PSG assignment) |
| `RLM_Partner_Community_User_Perm_Set` | `unpackaged/post_prm/` | Partner community user FLS |
| `RLM_BillingEmployeeAgent` | `unpackaged/post_agents/` | Agentforce billing employee agent access |
| `RLM_BillingServiceAgent` | `unpackaged/post_agents/` | Agentforce billing service agent access |
| `DRO_Integrations` | `unpackaged/post_tso/` | DRO integration permissions (TSO only) |
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

The following table shows the sequence of all permission-related steps across the full `prepare_rlm_org` flow. Step numbers use `X.Y` notation where X is the `prepare_rlm_org` step and Y is the sub-flow step.

| Step | Flow/Task | What is Assigned | Condition |
|---|---|---|---|
| 1.2 | `prepare_core` | Core RLM PSLs (25) | Always |
| 1.5 | `prepare_core` | Deploy PSG metadata (`deploy_pre`) | Always |
| 1.7 | `prepare_core` | CLM PSLs (11) | `clm` |
| 1.8 | `prepare_core` | Einstein AI PSLs (3) | `einstein` |
| 1.10 | `prepare_core` | `EinsteinAnalyticsPlusPsl` | Always |
| 1.11 | `prepare_core` | Recalculate 11 core PSGs | Always |
| 1.12 | `prepare_core` | Assign 11 core PSGs | Always |
| 1.13 | `prepare_core` | PCM permission sets (4) | `tso` + `psg_debug` |
| 1.19 | `prepare_core` | `EinsteinGPTPromptTemplateManager`, `SalesCloudEinsteinAll` | `einstein` |
| 1.20 | `prepare_core` | Billing permission sets (10) | `billing` + `psg_debug` |
| 9.2.3 | `prepare_quantumbit` > `prepare_approvals` | `RLM_Approvals` | `quantumbit` + `approvals` |
| 9.4 | `prepare_quantumbit` | `RLM_QuantumBit` | `quantumbit` |
| 9.5 | `prepare_quantumbit` | `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` |
| 12.10 | `prepare_docgen` | `RLM_DocGen` | `docgen` |
| 20.1 | `prepare_tso` | TSO PSLs (23) | `tso` |
| 20.2 | `prepare_tso` | Copilot + Catalog PSGs (4) | `tso` |
| 20.5 | `prepare_tso` | TSO permission sets (4) | `tso` |
| 20.6 | `prepare_tso` | `RLM_TSO` PSG | `tso` |
| 22.8 | `prepare_prm` | `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` |
| 23.1 | `prepare_agents` | Copilot PSGs (2) | `agents` |
| 23.4 | `prepare_agents` | `RLM_QuotingAgent` | `agents` |
| 24.3 | `prepare_constraints` | `RLM_Constraints` | `tso` + `constraints` |
| 28.3 | `prepare_ramp_builder` | `RLM_RampSchedule` | `ramps` |

---

## Persona PSGs (Optional)

Persona PSGs provide role-based permission groupings for end users. They are deployed separately via `cci flow run prepare_personas` and are **not** part of `prepare_rlm_org`. Metadata lives in `unpackaged/post_personas/`.

| Persona PSG | Label | Permission Sets |
|---|---|---|
| `RLM_Sales_Representative` | RLM Sales Representative | `BRERuntime`, `CLMRuntimeUser`, `DocGenUser`, `IndustriesConfiguratorPlatformApi`, `Microsoft365WordUser`, `ObligationUser`, `ProductCatalogManagementViewer`, `RatingRunTimeUser`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementCalculateTaxesApi`, `RevLifecycleManagementCreateContractApi`, `RevLifecycleManagementCreateOrderFromQuote`, `RevLifecycleManagementPlaceOrderApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi`, `RevLifecycleManagementQuotePricesTaxes`, `RevLifecycleManagementUsageDesignUser` |
| `RLM_Sales_Operations` | RLM Sales Operations | `AdvancedConfiguratorDesigner`, `BRERuntime`, `CLMRuntimeUser`, `CorePricingRunTimeUser`, `DocGenUser`, `IndustriesConfiguratorPlatformApi`, `ObligationUser`, `OrderSubmitUser`, `ProductCatalogManagementViewer`, `ProductConfigurationRulesDesigner`, `RatingRunTimeUser`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementCalculateTaxesApi`, `RevLifecycleManagementCoreCPQAssetization`, `RevLifecycleManagementCreateContractApi`, `RevLifecycleManagementCreateOrderFromQuote`, `RevLifecycleManagementInitiateAmendmentApi`, `RevLifecycleManagementInitiateCancellationApi`, `RevLifecycleManagementInitiateRenewalApi`, `RevLifecycleManagementPlaceOrderApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi`, `RevLifecycleManagementQuotePricesTaxes`, `RevLifecycleManagementUsageDesignUser` |
| `RLM_Product_and_Pricing_Admin` | RLM Product and Pricing Admin | `AdvancedConfiguratorDesigner`, `BREDesigner`, `BRERuntime`, `CorePricingAdmin`, `CorePricingDesignTimeUser`, `CorePricingManager`, `CorePricingRunTimeUser`, `IndustriesConfiguratorPlatformApi`, `ProductCatalogManagementAdministrator`, `ProductCatalogManagementViewer`, `ProductConfigurationRulesDesigner`, `ProductDetailsApiCache`, `RevLifecycleManagementCalculatePricesApi`, `RevLifecycleManagementProductAndPriceConfigurationApi`, `RevLifecycleManagementProductImportApi` |
| `RLM_Billing_Admin` | RLM Billing Admin | `RevenueLifecycleManagementBillingAdmin` |
| `RLM_Billing_Operations` | RLM Billing Operations | `RevenueLifecycleManagementBillingOperations` |
| `RLM_Accounting_Admin` | RLM Accounting Admin | `RevenueLifecycleManagementAccountingAdmin` |
| `RLM_Tax_Admin` | RLM Tax Admin | `RevenueLifecycleManagementBillingTaxAdmin` |
| `RLM_Credit_Memo_Operations` | RLM Credit Memo Operations | `RevenueLifecycleManagementBillingCreditMemoOperations` |
| `RLM_DRO_Admin` | RLM DRO Admin | `DfoAdminUser` |
| `RLM_Fulfillment_Designer` | RLM Fulfillment Designer | `DFODesignerUser` |
| `RLM_Fulfillment_Manager` | RLM Fulfillment Manager | `DFOManagerOperatorUser` |
| `RLM_Usage_Designer` | RLM Usage Designer | `ProductCatalogManagementViewer`, `RevLifecycleManagementUsageDesignUser` |

---

## Feature Flag Quick Reference

| Feature Flag | PSLs Assigned | PSGs Assigned | Permission Sets Assigned |
|---|---|---|---|
| *(always)* | Core RLM (25), `EinsteinAnalyticsPlusPsl` | 11 core PSGs | -- |
| `clm` | CLM (11) | -- | -- |
| `einstein` | AI (3) | -- | `EinsteinGPTPromptTemplateManager`, `SalesCloudEinsteinAll` |
| `tso` | TSO (23) | `RLM_TSO`, Copilot (2), Catalog (2) | `ERIBasic`, `RLM_UtilitiesPermset`, `OrchestrationProcessManagerPermissionSet`, `EventMonitoringPermSet` |
| `quantumbit` | -- | -- | `RLM_QuantumBit` |
| `quantumbit` + `calmdelete` | -- | -- | `RLM_CALM_SObject_Access` |
| `quantumbit` + `approvals` | -- | -- | `RLM_Approvals` |
| `docgen` | -- | -- | `RLM_DocGen` |
| `ramps` | -- | -- | `RLM_RampSchedule` |
| `tso` + `constraints` | -- | -- | `RLM_Constraints` |
| `prm` + `prm_exp_bundle` + `tso` | -- | -- | `RLM_PRM` |
| `agents` | -- | Copilot (2) | `RLM_QuotingAgent` |
| `billing` + `psg_debug` | -- | -- | 10 billing PS (debug) |
| `tso` + `psg_debug` | -- | -- | 4 PCM PS (debug) |

---

## Implementation Notes

1. **PSLs before PSGs** -- Salesforce requires the underlying license before any PSG containing those permission sets can take effect. The flow enforces this by assigning PSLs at steps 2/7/8/10, then PSGs at step 12.

2. **PSG recalculation** -- After deploying PSG metadata (`deploy_pre`), the `recalculate_permission_set_groups` task waits for Salesforce to finish calculating PSG status (`Outdated` -> `Updating` -> `Updated`) before assignment. Without this wait, assignment can fail silently.

3. **Tolerant assignment** -- `assign_permission_set_groups_tolerant` extends the standard CCI `AssignPermissionSetGroups` task to tolerate warnings about permissions unavailable on the target org edition (e.g., Enterprise vs. Unlimited). Used for core PSGs and `RLM_TSO`.

4. **Debug-only assignments (`psg_debug`)** -- The `psg_debug` flag gates direct permission set assignments that are normally provided by their parent PSGs. Useful for isolating whether a PSG recalculation issue is causing missing permissions.

5. **Persona PSGs are independent** -- Not part of `prepare_rlm_org`. Must be deployed and assigned separately via `cci flow run prepare_personas`. Designed for end-user role assignment rather than admin provisioning.

6. **Deploy-only permission sets** -- Several permission sets (e.g., `RLM_UsageDatatables`, `RLM_Collection_Plan_Activity`, agent permission sets) are deployed as metadata but not auto-assigned to the running user. They are available for manual assignment to specific users or inclusion in persona PSGs.
