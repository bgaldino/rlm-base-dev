# Revenue Cloud Permissions Reference

This document describes the Permission Set Licenses (PSLs), Permission Set Groups (PSGs), and individual Permission Sets used by the RLM Base Foundations project, how they map to feature flags, and the order in which they are assigned during `prepare_rlm_org`.

---

## Permission Set Licenses (PSLs)

PSLs are Salesforce-managed licenses that must be assigned to a user before the corresponding permission sets or PSGs can take effect. They are assigned early in `prepare_core` (steps 2, 7, 8, 10) before any PSGs or permission sets.

### Core RLM PSLs (`rlm_psl_api_names`)

Assigned unconditionally at step 2 of `prepare_core`. These cover the foundational RLM capabilities.

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

### CLM PSLs (`rlm_clm_psl_api_names`)

Assigned at step 7 of `prepare_core` when **`clm: true`**.

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

### Einstein / AI PSLs (`rlm_ai_psl_api_names`)

Assigned at step 8 of `prepare_core` when **`einstein: true`**.

| PSL API Name | Capability Area |
|---|---|
| `AgentforceServiceAgentBuilderPsl` | Agentforce builder |
| `EinsteinGPTCopilotPsl` | Einstein Copilot |
| `EinsteinGPTPromptTemplatesPsl` | Prompt templates |

> Several AI PSLs are commented out because they are not available on Enterprise dev scratch orgs (e.g., `EinsteinAnalyticsPlusPsl`, `RevenueIntelligencePsl`, `MySearchPsl`).

### EinsteinAnalyticsPlusPsl

Assigned unconditionally at step 10 of `prepare_core` (separate from the AI list because it is always required for RLM_RMI PSG functionality).

### Tableau PSLs (`rlm_tableaunext_psl_api_names`)

| PSL API Name |
|---|
| `TableauEinsteinUserPsl` |

> These are defined as YAML anchors but are not directly assigned in `prepare_core`. They are available for org-specific overrides.

### TSO PSLs (`rlm_tso_psl_api_names`)

Assigned in `prepare_tso` step 1 when **`tso: true`**. These are Trialforce Source Org-specific licenses for Sales Cloud Unlimited, Einstein features, and engagement tools.

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

---

## Permission Set Groups (PSGs)

PSGs bundle multiple Salesforce-managed permission sets into capability-area groups. They are deployed during `deploy_pre` (step 5 of `prepare_core`) from `unpackaged/pre/3_permissionsetgroups/` and then assigned to the running user.

### Core PSGs (`rlm_psg_api_names`)

These 11 PSGs are recalculated and assigned at steps 11-12 of `prepare_core` (unconditional).

#### RLM_PSL -- Core Admin Permission Sets

The largest core PSG. Bundles the essential RLM API and lifecycle permission sets.

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

#### RLM_RCB -- Revenue Cloud Billing Advanced

Billing-focused PSG with 16 permission sets covering invoicing, payments, credit memos, tax, and collections.

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

#### RLM_NGP -- Salesforce Pricing

| Permission Set | Purpose |
|---|---|
| `CorePricingAdmin` | Pricing admin |
| `CorePricingDesignTimeUser` | Pricing design |
| `CorePricingManager` | Pricing management |
| `DecimalQuantityDesigntime` | Decimal quantity |

#### RLM_CFG -- Revenue Cloud Configurator

| Permission Set | Purpose |
|---|---|
| `AdvancedConfiguratorDesigner` | Advanced configurator |
| `IndustriesConfiguratorPlatformApi` | Configurator platform API |
| `ProductConfigurationRulesDesigner` | Configuration rules |

#### RLM_PCM -- Product Catalog Management

| Permission Set | Purpose |
|---|---|
| `ProductCatalogManagementAdministrator` | PCM admin |
| `ProductCatalogManagementViewer` | PCM viewer |
| `ProductDetailsApiCache` | Product details API cache |

#### RLM_CLM -- Salesforce Contracts

| Permission Set | Purpose |
|---|---|
| `CLMAdminUser` | CLM admin |
| `ClauseDesigner` | Clause design |
| `DocGenDesigner` | Doc generation |
| `Microsoft365WordDesigner` | Word template design |
| `ObligationManager` | Obligation management |

#### RLM_DOC -- Document Generation and Builder

| Permission Set | Purpose |
|---|---|
| `DocGenDesigner` | Doc generation design |
| `DocumentBuilderUser` | Document builder |

#### RLM_DRO -- Dynamic Revenue Orchestrator

| Permission Set | Purpose |
|---|---|
| `DFODesignerUser` | DFO designer |
| `DFOManagerOperatorUser` | DFO manager/operator |
| `DfoAdminUser` | DFO admin |
| `OrderSubmitUser` | Order submission |

#### RLM_USG -- Usage and Rating Management

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

#### RLM_RMI -- Revenue Management Intelligence

| Permission Set | Purpose |
|---|---|
| `AnalyticsStoreUser` | Analytics data access |
| `PulseRuntimeUser` | Pulse runtime |

#### RLM_QB_AI -- QuantumBit AI

Empty PSG (placeholder). AI permission sets are assigned separately via `rlm_ai_ps_api_names` when `einstein: true`.

### TSO PSG (`psg_tso`)

#### RLM_TSO -- Trialforce Source Org

Assigned in `prepare_tso` step 6 when **`tso: true`**. Contains 56 permission sets spanning Sales Cloud Unlimited, Einstein AI, Tableau, CLM AI, Data Cloud, and engagement features. This is the catch-all PSG for trial/demo orgs.

### TSO Copilot/Catalog PSGs (`rlm_tso_psg_api_names`)

Assigned in `prepare_tso` step 2 when **`tso: true`**.

| PSG | Purpose |
|---|---|
| `CopilotSalesforceUserPSG` | Einstein Copilot user |
| `CopilotSalesforceAdminPSG` | Einstein Copilot admin |
| `UnifiedCatalogAdminPsl` | Unified Catalog admin |
| `UnifiedCatalogDesignerPsl` | Unified Catalog designer |

### AI PSGs (`rlm_ai_psg_api_names`)

Assigned in `prepare_agents` step 1 when **`agents: true`**.

| PSG | Purpose |
|---|---|
| `CopilotSalesforceUserPSG` | Einstein Copilot user |
| `CopilotSalesforceAdminPSG` | Einstein Copilot admin |

---

## Feature-Gated Permission Sets

These individual permission sets are deployed and assigned conditionally based on feature flags. Each is deployed from its `unpackaged/post_*` directory and assigned in the corresponding `prepare_*` flow.

| Permission Set | Feature Flag(s) | Flow | Purpose |
|---|---|---|---|
| `RLM_QuantumBit` | `quantumbit` | `prepare_quantumbit` step 4 | Custom field access for QB |
| `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` | `prepare_quantumbit` step 5 | CALM Delete SObject access |
| `RLM_Approvals` | `quantumbit` + `approvals` | `prepare_approvals` step 3 | Advanced approvals |
| `RLM_DocGen` | `docgen` | `prepare_docgen` step 10 | Document generation |
| `RLM_Constraints` | `tso` + `constraints` | `prepare_constraints` step 3 | Constraint builder |
| `RLM_RampSchedule` | `ramps` | `prepare_ramp_builder` step 3 | Ramp scheduling |
| `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` | `prepare_prm` step 8 | Partner portal field access |
| `RLM_QuotingAgent` | `agents` | `prepare_agents` step 4 | Agentforce quoting agent |
| `DRO_Integrations` | `tso` | `prepare_tso` step 4 (via deploy_post_tso) | DRO integrations |
| `RLM_UsageDatatables` | (via deploy_post_utils) | Various | Usage datatable LWC access |
| `RLM_UtilitiesPermset` | `tso` | `prepare_tso` step 5 | Utility features |

### Einstein / AI Permission Sets (`rlm_ai_ps_api_names`)

Assigned at step 19 of `prepare_core` when **`einstein: true`**.

| Permission Set | Purpose |
|---|---|
| `EinsteinGPTPromptTemplateManager` | Prompt template management |
| `SalesCloudEinsteinAll` | Sales Cloud Einstein features |

### Billing Permission Sets (`rlm_blng_ps_api_names`)

Assigned at step 20 of `prepare_core` when **`billing: true`** AND **`psg_debug: true`** (debug-only; in production these are covered by the RLM_RCB PSG).

### PCM Permission Sets (`rlm_pcm_ps_api_names`)

Assigned at step 13 of `prepare_core` when **`tso: true`** AND **`psg_debug: true`** (debug-only).

### Tableau Permission Sets (`rlm_tableaunext_ps_api_names`)

| Permission Set |
|---|
| `TableauEinsteinAdmin` |
| `TableauEinsteinBusinessUser` |
| `TableauEinsteinAnalyst` |
| `TableauSelfServiceAnalyst` |

> Defined as anchors; assigned in TSO-specific flows or org-specific overrides.

### TSO Permission Sets (`rlm_tso_ps_api_names`)

Assigned in `prepare_tso` step 5 when **`tso: true`**.

| Permission Set | Purpose |
|---|---|
| `ERIBasic` | ERI platform |
| `RLM_UtilitiesPermset` | Utility features |
| `OrchestrationProcessManagerPermissionSet` | Orchestration process manager |
| `EventMonitoringPermSet` | Event monitoring |

---

## Assignment Order in `prepare_rlm_org`

The following table shows the sequence of permission-related steps across the full `prepare_rlm_org` flow.

| Step | Flow/Task | What is Assigned | Condition |
|---|---|---|---|
| 1.2 | `prepare_core` | Core RLM PSLs (`rlm_psl_api_names`) | Always |
| 1.5 | `prepare_core` | Deploy pre (includes PSG metadata) | Always |
| 1.7 | `prepare_core` | CLM PSLs (`rlm_clm_psl_api_names`) | `clm: true` |
| 1.8 | `prepare_core` | Einstein AI PSLs (`rlm_ai_psl_api_names`) | `einstein: true` |
| 1.10 | `prepare_core` | `EinsteinAnalyticsPlusPsl` | Always |
| 1.11 | `prepare_core` | Recalculate core PSGs | Always |
| 1.12 | `prepare_core` | Assign core PSGs (`rlm_psg_api_names`) | Always |
| 1.13 | `prepare_core` | PCM permission sets (debug) | `tso` + `psg_debug` |
| 1.19 | `prepare_core` | Einstein AI permission sets | `einstein: true` |
| 1.20 | `prepare_core` | Billing permission sets (debug) | `billing` + `psg_debug` |
| 9.4 | `prepare_quantumbit` | `RLM_QuantumBit` | `quantumbit: true` |
| 9.5 | `prepare_quantumbit` | `RLM_CALM_SObject_Access` | `quantumbit` + `calmdelete` |
| 12.10 | `prepare_docgen` | `RLM_DocGen` | `docgen: true` |
| 20.1 | `prepare_tso` | TSO PSLs | `tso: true` |
| 20.2 | `prepare_tso` | TSO Copilot/Catalog PSGs | `tso: true` |
| 20.5 | `prepare_tso` | TSO permission sets | `tso: true` |
| 20.6 | `prepare_tso` | `RLM_TSO` PSG | `tso: true` |
| 22.8 | `prepare_prm` | `RLM_PRM` | `prm` + `prm_exp_bundle` + `tso` |
| 23.1 | `prepare_agents` | AI Copilot PSGs | `agents: true` |
| 23.4 | `prepare_agents` | `RLM_QuotingAgent` | `agents: true` |
| 24.3 | `prepare_constraints` | `RLM_Constraints` | `tso` + `constraints` |
| 28.3 | `prepare_ramp_builder` | `RLM_RampSchedule` | `ramps: true` |

---

## Persona PSGs (Optional)

Persona PSGs are role-based groupings deployed separately via `cci flow run prepare_personas`. They are **not** wired into `prepare_rlm_org` and must be run independently. Deployed from `unpackaged/post_personas/`.

| Persona PSG | Target Role | Key Permission Sets Included |
|---|---|---|
| `RLM_Sales_Representative` | Sales rep | CLM runtime, configurator, pricing/tax APIs, quote-to-order, doc gen |
| `RLM_Sales_Operations` | Sales ops | (role-specific bundle) |
| `RLM_Product_and_Pricing_Admin` | Product/pricing admin | Advanced configurator, BRE, pricing admin/design/runtime, PCM admin |
| `RLM_Billing_Admin` | Billing admin | Billing admin |
| `RLM_Billing_Operations` | Billing ops | (role-specific bundle) |
| `RLM_Accounting_Admin` | Accounting | (role-specific bundle) |
| `RLM_Tax_Admin` | Tax admin | (role-specific bundle) |
| `RLM_Credit_Memo_Operations` | Credit memo ops | (role-specific bundle) |
| `RLM_DRO_Admin` | DRO admin | DFO admin |
| `RLM_Fulfillment_Designer` | Fulfillment design | (role-specific bundle) |
| `RLM_Fulfillment_Manager` | Fulfillment mgmt | (role-specific bundle) |
| `RLM_Usage_Designer` | Usage design | (role-specific bundle) |

---

## Feature Flag Quick Reference

Summary of which feature flags trigger permission-related assignments.

| Feature Flag | PSLs | PSGs | Permission Sets |
|---|---|---|---|
| *(always)* | Core RLM (25), `EinsteinAnalyticsPlusPsl` | 11 core PSGs | -- |
| `clm: true` | CLM (11) | -- | -- |
| `einstein: true` | AI (3) | -- | `EinsteinGPTPromptTemplateManager`, `SalesCloudEinsteinAll` |
| `tso: true` | TSO (23) | `RLM_TSO`, Copilot/Catalog (4) | `ERIBasic`, `RLM_UtilitiesPermset`, `OrchestrationProcessManagerPermissionSet`, `EventMonitoringPermSet` |
| `quantumbit: true` | -- | -- | `RLM_QuantumBit` |
| `quantumbit` + `calmdelete` | -- | -- | `RLM_CALM_SObject_Access` |
| `quantumbit` + `approvals` | -- | -- | `RLM_Approvals` |
| `docgen: true` | -- | -- | `RLM_DocGen` |
| `constraints: true` (+ `tso`) | -- | -- | `RLM_Constraints` |
| `ramps: true` | -- | -- | `RLM_RampSchedule` |
| `prm` + `prm_exp_bundle` + `tso` | -- | -- | `RLM_PRM` |
| `agents: true` | -- | Copilot PSGs (2) | `RLM_QuotingAgent` |
| `billing` + `psg_debug` | -- | -- | Billing PS (10, debug-only) |
| `tso` + `psg_debug` | -- | -- | PCM PS (4, debug-only) |

---

## Key Implementation Notes

1. **PSLs must be assigned before PSGs** -- Salesforce requires the underlying license before the PSG's permission sets can take effect. The flow enforces this by assigning PSLs at steps 2/7/8/10, then PSGs at step 12.

2. **PSG recalculation** -- After deploying PSG metadata (`deploy_pre`), the `recalculate_permission_set_groups` task waits for Salesforce to finish calculating the PSG status (`Outdated` -> `Updating` -> `Updated`) before assignment. Without this, assignment can fail silently.

3. **Tolerant assignment** -- `assign_permission_set_groups_tolerant` extends the standard CCI task to tolerate warnings about permissions unavailable on the target org edition (e.g., Enterprise vs Unlimited).

4. **Debug-only assignments** -- The `psg_debug` flag gates direct permission set assignments (`rlm_blng_ps_api_names`, `rlm_pcm_ps_api_names`) that are normally covered by their parent PSGs. These are useful for troubleshooting permission issues.

5. **Persona PSGs are independent** -- They are not part of `prepare_rlm_org` and must be deployed/assigned via `prepare_personas` separately. This keeps the core flow focused on admin provisioning.
