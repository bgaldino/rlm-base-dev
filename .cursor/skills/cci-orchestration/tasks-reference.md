# CCI Tasks Reference

> **Auto-generated** by `scripts/ai/generate_cci_reference.py` from `cumulusci.yml`.  
> Do not edit manually — re-run the script after changing `cumulusci.yml`.

**231 tasks** across **9 groups**.

---

## Data Maintenance

*5 task(s)*

### `delete_badger_pricing_data`

**Description:** Delete all Insert-operation records from the qb-pricing plan (PricebookEntryDerivedPrice, PricebookEntry, BundleBasedAdjustment, AttributeBasedAdjustment, AttributeAdjustmentCondition, PriceAdjustmentTier) in reverse plan order (children first). Shape-agnostic: clears all records of each type regardless of which data shape populated them. Run before insert_quantumbit_pricing_data when layering multiple pricing shapes. Note: CostBookEntry is currently excluded (empty CSV) and will not be deleted.

**Class:** `tasks.rlm_sfdmu.DeleteSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pricing`

---

### `delete_draft_billing_records`

**Description:** Delete all draft billing-related records (BillingTreatmentItem, BillingTreatment, BillingPolicy, PaymentTermItem, PaymentTerm) in dependency order. Use before re-running the billing data plan to avoid duplicates.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/deleteDraftBillingRecords.apex`

---

### `delete_qb_rates_data`

**Description:** Delete all qb-rates data (RateAdjustmentByTier, RateCardEntry, PriceBookRateCard, RateCard) in dependency order. Use before re-running insert_qb_rates_data or test_qb_rates_idempotency to clear duplicates.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/deleteQbRatesData.apex`

---

### `delete_qb_rating_data`

**Description:** Delete all qb-rating data (PUG, PURP, PUR, RatingFrequencyPolicy, UsageGrantRolloverPolicy, etc.) in dependency order. Use before re-running insert_qb_rating_data to clear duplicates.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/deleteQbRatingData.apex`

---

### `delete_quantumbit_pricing_data`

**Description:** Delete all Insert-operation records from the qb-pricing plan (PricebookEntryDerivedPrice, PricebookEntry, BundleBasedAdjustment, AttributeBasedAdjustment, AttributeAdjustmentCondition, PriceAdjustmentTier) in reverse plan order (children first). Shape-agnostic: clears all records of each type regardless of which data shape populated them. Run before insert_quantumbit_pricing_data when layering multiple pricing shapes. Note: CostBookEntry is currently excluded (empty CSV) and will not be deleted.

**Class:** `tasks.rlm_sfdmu.DeleteSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pricing`

---

## Data Management - Extract

*13 task(s)*

### `extract_mfg_aaf_data`

**Description:** Extract mfg-aaf (Advanced Account Forecast) from org to CSV. Output in datasets/sfdmu/extractions/mfg-aaf/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-aaf`

---

### `extract_qb_approvals_data`

**Description:** Extract qb-approvals (ApprovalAlertContentDef) from org to CSV. Output in datasets/sfdmu/extractions/qb-approvals/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-approvals`

---

### `extract_qb_clm_data`

**Description:** Extract qb-clm from org to CSV. Output in datasets/sfdmu/extractions/qb-clm/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-clm`

---

### `extract_qb_dro_data`

**Description:** Extract qb-dro from org to CSV. Output in datasets/sfdmu/extractions/qb-dro/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-dro`

---

### `extract_qb_guidedselling_data`

**Description:** Extract qb-guidedselling from org to CSV. Output in datasets/sfdmu/extractions/qb-guidedselling/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-guidedselling`

---

### `extract_qb_pcm_data`

**Description:** Extract qb-pcm (product catalog) from org to CSV. Output in datasets/sfdmu/extractions/qb-pcm/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pcm`

---

### `extract_qb_pricing_data`

**Description:** Extract qb-pricing from org to CSV. Output in datasets/sfdmu/extractions/qb-pricing/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pricing`

---

### `extract_qb_prm_data`

**Description:** Extract qb-prm (partner relationship management) from org to CSV. Output in datasets/sfdmu/extractions/qb-prm/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-prm`

---

### `extract_qb_product_images_data`

**Description:** Extract qb-product-images from org to CSV. Output in datasets/sfdmu/extractions/qb-product-images/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-product-images`

---

### `extract_qb_rates_data`

**Description:** Extract qb-rates from org to CSV. Output in datasets/sfdmu/extractions/qb-rates/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rates`

---

### `extract_qb_rating_data`

**Description:** Extract qb-rating from org to CSV. Output in datasets/sfdmu/extractions/qb-rating/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rating`

---

### `extract_qb_transactionprocessingtypes_data`

**Description:** Extract qb-transactionprocessingtypes from org to CSV. Output in datasets/sfdmu/extractions/qb-transactionprocessingtypes/<timestamp>. Runs post-process by default; re-import-ready CSVs in <timestamp>/processed/. Use run_post_process false to skip.

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`

---

### `fix_mfg_aaf_category_extraction`

**Description:** Fix Category__r.Code in mfg-aaf extraction output. SFDMU v5 returns #N/A for this custom relationship field; this task queries the org and merges the correct values. Run after extract_mfg_aaf_data. Use extraction_dir to target a specific extraction, or omit to fix the most recent.

**Class:** `tasks.rlm_aaf_category_fix.FixAAFCategoryExtraction`

---

## Data Management - Idempotency

*15 task(s)*

### `test_badger_dro_idempotency`

**Description:** Idempotency test for badger-pricing. Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/mfg-pricing/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-dro`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_badger_pcm_idempotency`

**Description:** Idempotency test for badger-pcm (product catalog). Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/mfg-pcm/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pcm`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_badger_pricing_idempotency`

**Description:** Idempotency test for badger-pricing. Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/mfg-pricing/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pricing`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_badger_testdata_idempotency`

**Description:** Idempotency test for badger-pcm (product catalog). Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/mfg-pcm/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/test`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_qb_approvals_idempotency`

**Description:** Idempotency test for qb-approvals (ApprovalAlertContentDef).

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-approvals`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_clm_idempotency`

**Description:** Idempotency test for qb-clm.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-clm`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_dro_idempotency`

**Description:** Idempotency test for qb-dro. Note: plan uses dynamic_assigned_to_user for load; test runs without it (scratch org user may differ).

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-dro`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_guidedselling_idempotency`

**Description:** Idempotency test for qb-guidedselling.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-guidedselling`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_pcm_idempotency`

**Description:** Idempotency test for qb-pcm (product catalog). Uses extraction roundtrip by default (extract -> post-process -> load) and writes to datasets/sfdmu/extractions/qb-pcm/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pcm`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_qb_pricing_idempotency`

**Description:** Idempotency test for qb-pricing (load twice from source, assert no new records).

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pricing`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_prm_idempotency`

**Description:** Idempotency test for qb-prm (partner relationship management).

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-prm`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_product_images_idempotency`

**Description:** Idempotency test for qb-product-images.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-product-images`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_rates_idempotency`

**Description:** Idempotency test for qb-rates. Runs the plan twice from source CSVs and asserts no record count increase. NOTE: extraction roundtrip is not supported for qb-rates because SFDMU v5 cannot properly extract 2-hop traversal fields in RABT composite keys (RateCardEntry.RateCard.Name extracts as #N/A), breaking FK resolution on re-import.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rates`
- `use_extraction_roundtrip`: `False`

---

### `test_qb_rating_idempotency`

**Description:** Idempotency test for qb-rating. Uses extraction roundtrip (extract -> post-process -> load from processed dir) to validate that extracted CSVs can be re-imported without adding records. Persists extraction output to datasets/sfdmu/extractions/qb-rating/<timestamp>.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rating`
- `use_extraction_roundtrip`: `True`
- `persist_extraction_output`: `True`

---

### `test_qb_transactionprocessingtypes_idempotency`

**Description:** Idempotency test for qb-transactionprocessingtypes.

**Class:** `tasks.rlm_sfdmu.TestSFDMUIdempotency`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`
- `use_extraction_roundtrip`: `False`

---

## E2E Testing

*5 task(s)*

### `robot_e2e`

**Description:** Run the full Quote-to-Order UI test (headless Chrome). Validates the complete sales workflow: Reset Account → Create Opportunity → Create Quote → Browse Catalogs → Add Products → Create Order → Activate Order → Verify Assets. Requires a provisioned org with qb=true (run prepare_rlm_org first).

**Class:** `tasks.rlm_robot_e2e.RunE2ETests`

**Options:**

- `suite`: `robot/rlm-base/tests/e2e/quote_to_order.robot`
- `outputdir`: `robot/rlm-base/results`

---

### `robot_e2e_debug`

**Description:** Run the full Quote-to-Order UI test in headed Chrome with CDP debugging on port 9222. Same flow as robot_e2e but visible browser for development and debugging. Connect via chrome://inspect. Use -o pause_for_recording true to add pause points for DOM inspection.

**Class:** `tasks.rlm_robot_e2e.RunE2ETests`

**Options:**

- `suite`: `robot/rlm-base/tests/e2e/quote_to_order.robot`
- `outputdir`: `robot/rlm-base/results`
- `headed`: `True`

---

### `robot_order_from_quote`

**Description:** Add products via Browse Catalogs, create and activate an Order, and verify Assets (UI automation, headed Chrome). Part 2 of the modular Quote-to-Order flow. If no QUOTE_ID is provided, creates a fresh Quote automatically.

**Class:** `tasks.rlm_robot_e2e.RunE2ETests`

**Options:**

- `suite`: `robot/rlm-base/tests/e2e/order_from_quote.robot`
- `outputdir`: `robot/rlm-base/results`
- `headed`: `True`

---

### `robot_reset_account`

**Description:** Reset the test Account via the RLM_Reset_Account QuickAction (UI automation). Clears transactional data (Opportunities, Quotes, Orders, Assets) so E2E tests can re-run from a clean state. Runs in headed Chrome.

**Class:** `tasks.rlm_robot_e2e.RunE2ETests`

**Options:**

- `suite`: `robot/rlm-base/tests/e2e/reset_account.robot`
- `outputdir`: `robot/rlm-base/results`
- `headed`: `True`

---

### `robot_setup_quote`

**Description:** Reset Account and create an Opportunity + Quote (UI automation, headed Chrome). Part 1 of the modular Quote-to-Order flow. Can be run standalone to prepare a Quote for other tests.

**Class:** `tasks.rlm_robot_e2e.RunE2ETests`

**Options:**

- `suite`: `robot/rlm-base/tests/e2e/setup_quote.robot`
- `outputdir`: `robot/rlm-base/results`
- `headed`: `True`

---

## Manufacturing

*35 task(s)*

### `activate_mfg_docgen_templates`

**Description:** Activate the latest version of each Manufacturing OmniStudio DocumentTemplate (Badger_Proposal, Price_Contract). DocumentTemplates always deploy as inactive. Run after deploy_mfg_doc_templates.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateMfgDocgenTemplates.apex`

---

### `activate_mfg_theme`

**Description:** Activate the Manufacturing Lightning Experience Theme by deploying LightningExperienceSettings with activeThemeName=Badger. Source: unpackaged/post_manufacturing/theme_activation/settings/LightningExperience.settings-meta.xml. Runs last in prepare_manufacturing so the theme activates only after all metadata is in place. Idempotent: deploying the same activeThemeName twice is safe.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing/theme_activation`

---

### `configure_mfg_core_pricing_setup`

**Description:** Configure Salesforce Pricing Setup (CorePricingSetup) page for Manufacturing orgs: set the default Pricing Procedure to the MFG pricing procedure (Robot test). Must run after the MFG Pricing Procedure expression set is deployed and activated.

**Class:** `tasks.rlm_configure_core_pricing_setup.ConfigureCorePricingSetup`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/configure_core_pricing_setup.robot`
- `outputdir`: `robot/rlm-base/results`
- `pricing_procedure`: `MFG Revenue Management Default Pricing Procedure`

---

### `configure_mfg_revenue_settings`

**Description:** Configure Revenue Settings page defaults for Manufacturing (Badger) orgs. Same as configure_revenue_settings but sets pricing_procedure to the MFG pricing procedure (MFG Revenue Management Default Pricing Procedure) deployed via unpackaged/post_manufacturing/mfg_pricingsetup.

**Class:** `tasks.rlm_configure_revenue_settings.ConfigureRevenueSettings`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/configure_revenue_settings.robot`
- `outputdir`: `robot/rlm-base/results`
- `pricing_procedure`: `MFG Revenue Management Default Pricing Procedure`
- `usage_rating_procedure`: `RLM Default Rating Discovery Procedure`
- `create_orders_flow`: `RLM_CreateOrdersFromQuote`

---

### `delete_badger_aaf_data`

**Description:** Delete all Insert-operation records from the mfg-aaf plan (AdvAccountForecastFact, AdvAcctForecastSetPartner) in reverse plan order. Run before insert_badger_aaf_data for a fresh reload.

**Class:** `tasks.rlm_sfdmu.DeleteSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-aaf`

---

### `deploy_mfg_aaf_dim_source`

**Description:** Deploy Manufacturing Advanced Account Forecasting dimension source (Category). Defines the Category dimension used by the forecast set configuration.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_aaf/dim_source`

---

### `deploy_mfg_aaf_fields`

**Description:** Deploy Manufacturing Advanced Account Forecasting object extensions: custom fields on AdvAccountForecastFact and en_US ObjectTranslation for AdvAcctForecastSetPartner.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_aaf/fields`

---

### `deploy_mfg_aaf_forecast_set`

**Description:** Deploy Manufacturing Advanced Account Forecasting forecast set (CategoryForecastSet). Must deploy after dim_source because the forecast set references the Category dimension.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_aaf/forecast_set`

---

### `deploy_mfg_aaf_permissions`

**Description:** Deploy Manufacturing Advanced Account Forecasting permission set (MFG_AAF). Must deploy after aaf/fields so the permission set can reference the custom fields.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_aaf/permissions`

---

### `deploy_mfg_core`

**Description:** Deploy Manufacturing theme, custom fields, Apex, and permissions in a single transaction. Requires deploy_mfg_core_assets to have committed first (activates SalesAgreement objects). Deploys: Lightning Experience theme (BrandingSet, LightningExperienceTheme), custom fields on SalesAgreement, SalesAgreementProduct, SalesAgreementProductSchedule, Quote, QuoteLineItem, and ServiceContract, core Apex classes (RLM_MFG_SalesAgreementRLMOrder, RLM_MFG_ServiceContractQuote), OpenSObject Aura component, SalesAgreement settings, RLM_MFG_RCA permission set, and RLM_MFG_scratch permission set group. Salesforce resolves intra-package ordering internally (fields before PSets, PSets before PSG).

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_core`

---

### `deploy_mfg_core_assets`

**Description:** Deploy Manufacturing brand assets and platform feature settings: ContentAssets (logo variants), StaticResources (product images, Babylon.js 3D libraries), Industries rebates setting, and IndustriesManufacturing settings (enableIndManufacturing, enableRevMgmtForSlsAgr, AAF). Must run as a separate transaction before deploy_mfg_core because the IndustriesManufacturing settings activate the SalesAgreement, SalesAgreementProduct, and SalesAgreementProductSchedule sObject types — these objects must exist in the schema before custom fields and Apex that reference them can deploy. The BrandingSet in deploy_mfg_core also references these ContentAssets.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing/core_assets`

---

### `deploy_mfg_doc_templates`

**Description:** Deploy Manufacturing document templates (Badger_Proposal and Price_Contract). Must deploy after OmniScripts that reference these templates.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_docgen/documentTemplates`

---

### `deploy_mfg_flows_and_actions`

**Description:** Deploy all Manufacturing business process flows and Quick Actions in a single transaction: Sales Agreement creation and activation flows, quote-to-contract flows, DRO work order creation, Service Contract quoting, and the Quick Actions on Account, Contract, Quote, and SalesAgreement that invoke them. Runs after core_setup (SA settings + custom fields + perms) with a propagation sleep, so all SA-DML flows validate cleanly. Requires the IndustriesManufacturing scratch org feature (orgs/dev-mfg.json).

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing/flows_and_actions`

---

### `deploy_mfg_guided_selling`

**Description:** Deploy Manufacturing Guided Selling metadata: AssessmentQuestions for chemicals and power management, Guided Selling OmniScripts, and ProductDiscovery settings.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_guidedselling`

---

### `deploy_mfg_omni_base_docgen_script`

**Description:** Deploy Manufacturing base document generation OmniScript (doc_GenerationCore_English). Orchestrates the core document generation flow for proposals and contracts.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_docgen/base_docgen_omniscript/omniScripts`

---

### `deploy_mfg_omni_datatransforms`

**Description:** Deploy Manufacturing OmniDataTransforms for document generation (Quote/Contract extraction, field mapping, and template name extraction used by the doc gen OmniScript).

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_docgen/omniDataTransforms`

---

### `deploy_mfg_omni_integration_procedures`

**Description:** Deploy Manufacturing OmniIntegrationProcedure for document generation orchestration (doc_Generation_Procedure). Must deploy after OmniDataTransforms.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_docgen/omniIntegrationProcedures`

---

### `deploy_mfg_omni_quote_script`

**Description:** Deploy Manufacturing Quote Proposal OmniScript (doc_QuoteProposal_English). Provides the user-facing UI for generating quote proposal documents.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_docgen/quote_omniscript/omniScripts`

---

### `deploy_mfg_pricing_procedure`

**Description:** Deploy Manufacturing default pricing procedure ExpressionSetDefinition (MFG_Rev_Mgmt_Default_Pricing_Procedure). Performs find-and-replace to inject live PriceAdjustmentSchedule IDs for attribute-based, volume, and bundle adjustments.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_pricing/pricing_procedure`
- `transforms`: `[{'transform': 'find_replace', 'options': {'patterns': [{'xpath': '//ExpressionSetDefinition/versions/variables/value...`

---

### `deploy_mfg_pricing_recipe`

**Description:** Deploy Manufacturing default NGP pricing recipe (NGPDefaultRecipe). Must deploy before deploy_mfg_pricing_procedure because the ExpressionSetDefinition references this recipe.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_pricing/pricing_recipe`

---

### `deploy_mfg_rebates`

**Description:** Deploy Manufacturing rebate metadata: ObjectHierarchyRelationship settings for Opportunity, Quote, SalesAgreement, and TransactionJournal, plus the Aggregate_by_Member_Rebates BatchCalcJobDefinition.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_rebates`

---

### `deploy_mfg_tso_perms`

**Description:** Deploy Manufacturing production permission set group (MFG). Required when tso=true. Deployed separately from core_setup so it can be gated by the tso feature flag.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing/tso_perms`

---

### `deploy_mfg_visualization`

**Description:** Deploy Manufacturing 3D Visualization metadata (LWC renderDraw3DConfigurationPrototype, RenderDraw_Product_Configurator_Flow, X3DVisualization VF page, RenderDraw_SRC CSP Trusted Site). Required when mfg_visuals=true. Source: unpackaged/post_manufacturing_visualization.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_manufacturing_visualization`

---

### `fix_mfg_document_template_binaries`

**Description:** Corrects Manufacturing DocumentTemplate ContentDocument binaries after a batch metadata deploy. Same Salesforce metadata API bug as fix_document_template_binaries: all DocumentTemplates deployed together receive the same ContentDocument binary (first alphabetically — Badger_Proposal wins, Price_Contract gets the wrong binary). Uploads the correct .dt binary from unpackaged/post_manufacturing_docgen/documentTemplates for each template. Run after deploy_mfg_doc_templates + activate_mfg_docgen_templates.

**Class:** `tasks.rlm_docgen.FixDocumentTemplateBinaries`

**Options:**

- `templates_dir`: `unpackaged/post_manufacturing_docgen/documentTemplates`

---

### `grant_mfg_ext_credential_access`

**Description:** Grant External Credential Principal Access to the RLM_MFG_RCA permission set. Salesforce Metadata API does not support externalCredentialPrincipalAccess in PermissionSet deploy or retrieve, so this script uses a Tooling API callout to locate the named principals for BillingSystemExtCredentials and SalesforceContractsExtCredentials, then grants SetupEntityAccess via DML. Idempotent: skips principals already granted.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/grantMfgExternalCredentialAccess.apex`

---

### `insert_badger_aaf_data`

**Description:** Load Manufacturing Advanced Account Forecast data. Syncs Period, Product2, and ProductCategory IDs from the target org, injects PeriodId, ProductId, and CategoryId into AdvAccountForecastFact before SFDMU run.

**Class:** `tasks.rlm_aaf_load.LoadAAFData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-aaf`

---

### `insert_badger_dro_data`

**Description:** Insert Manufacturing DRO fulfillment decomposition seed data. Assigns dynamic user.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-dro`
- `dynamic_assigned_to_user`: `True`

---

### `insert_badger_guidedselling_data`

**Description:** Insert Manufacturing Guided Selling product assignment data.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-guidedselling`

---

### `insert_badger_pcm_data`

**Description:** Insert Manufacturing PCM product data (products, product categories, attributes).

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pcm`

---

### `insert_badger_pricing_data`

**Description:** Insert Manufacturing pricing data (price books, price book entries, price adjustments).

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pricing`

---

### `insert_badger_rebates_data`

**Description:** Insert Manufacturing rebates seed data.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-rebates`

---

### `insert_mfg_billing_data`

**Description:** Insert Manufacturing billing seed data (BillingTreatment, BillingPolicy, PaymentTerm, LegalEntity, AccountingPeriod, GeneralLedgerAccount, GeneralLedgerAcctAsgntRule) and assign BillingPolicy to all MFG products. Required for order activation on badger orgs when billing=true. Source: datasets/sfdmu/mfg/en-US/mfg-billing.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-billing`

---

### `insert_mfg_configflow_data`

**Description:** Insert Manufacturing product configuration flow assignments (ProductConfigurationFlow, ProductConfigFlowAssignment). Maps MFG products to their RenderDraw configuration flows. Required when mfg_visuals=true. Source: datasets/sfdmu/mfg/en-US/mfg-configflow.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-configflow`

---

### `insert_mfg_tax_data`

**Description:** Insert Manufacturing tax seed data (TaxPolicy, TaxTreatment, Product2 TaxPolicy assignments). Activates TaxPolicy and TaxTreatment via a two-pass SFDMU plan. Required for order activation on badger orgs when tax=true. Source: datasets/sfdmu/mfg/en-US/mfg-tax.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-tax`

---

### `insert_test_data`

**Description:** Insert Test Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/test`

---

## Partner Relationship Management

*3 task(s)*

### `deploy_post_prm_tso`

**Description:** Deploy TSO-only PRM experience overlay containing the View Vouchers page (requires Referral and Voucher objects enabled in TSO orgs).

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_prm_tso`

---

### `patch_network_email_for_deploy`

**Description:** Replace the placeholder emailSenderAddress in rlm.network-meta.xml with the Network's actual current EmailSenderAddress (immutable after creation) so deploy_post_prm succeeds. Repo stores a non-PII placeholder; run revert_network_email_after_deploy after deploy.

**Class:** `tasks.rlm_community.PatchNetworkEmailForDeploy`

---

### `revert_network_email_after_deploy`

**Description:** Restore the placeholder emailSenderAddress in rlm.network-meta.xml after deploy_post_prm so the repo never persists the target org's email.

**Class:** `tasks.rlm_community.RevertNetworkEmailAfterDeploy`

---

## Revenue Lifecycle Management

*125 task(s)*

### `activate_and_deploy_expression_sets`

**Description:** Activate and Deploy Expression Sets

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/expressionSetDefinition`
- `transforms`: `[{'transform': 'find_replace', 'options': {'patterns': [{'xpath': '//ExpressionSetDefinition/versions/status[text()="...`

---

### `activate_billing_records`

**Description:** Activate Billing Records

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateBillingRecords.apex`

---

### `activate_decision_tables`

**Description:** Activate selected Decision Tables via API

**Class:** `tasks.rlm_manage_decision_tables.ManageDecisionTables`

**Options:**

- `operation`: `activate`
- `developer_names`: `['RLM_ProductCategoryQualification', 'RLM_ProductQualification', 'RLM_CostBookEntries']`

---

### `activate_default_payment_term`

**Description:** Activate Default Payment Term

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateDefaultPaymentTerm.apex`

---

### `activate_docgen_templates`

**Description:** Activate the latest version of each RLM_ OmniStudio DocumentTemplate. DocumentTemplates always deploy as inactive; this script finds the highest version per template name and sets IsActive = true.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateDocgenTemplates.apex`

---

### `activate_expression_sets`

**Description:** Activate expression set versions via Tooling API

**Class:** `tasks.rlm_manage_expression_sets.ManageExpressionSets`

**Options:**

- `operation`: `activate_versions`
- `metadata_path`: `force-app/main/default/expressionSetDefinition`

---

### `activate_price_adjustment_schedules`

**Description:** Activate Price Adjustment Schedules

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activatePriceAdjustmentSchedules.apex`

---

### `activate_procedure_plan_expression_sets`

**Description:** Activate Procedure Plan expression set versions (RLM_Price_Distribution_Procedure; RLM_DefaultPricingProcedure is activated by the main activate_expression_sets task)

**Class:** `tasks.rlm_manage_expression_sets.ManageExpressionSets`

**Options:**

- `operation`: `activate_versions`
- `version_full_names`: `RLM_Price_Distribution_Procedure_V1`

---

### `activate_procedure_plan_version`

**Description:** Activate the ProcedurePlanDefinitionVersion after sections and options have been inserted

**Class:** `tasks.rlm_create_procedure_plan_def.ActivateProcedurePlanVersion`

**Options:**

- `developerName`: `RLM_Quote_Pricing_Procedure_Plan`

---

### `activate_rates`

**Description:** Activate Rates

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateRateCardEntries.apex`

---

### `activate_rating_records`

**Description:** Activate Rating Records

**Class:** `tasks.rlm_apex_file.FileBasedAnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateRatingRecords.apex`

---

### `activate_tax_records`

**Description:** Activate Tax Records

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/activateTaxRecords.apex`

---

### `apply_context_constraint_engine_node_status`

**Description:** Apply ConstraintEngineNodeStatus mappings to Sales Transaction context

**Class:** `tasks.rlm_context_service.ManageContextDefinition`

**Options:**

- `developer_name`: `RLM_SalesTransactionContext`
- `plan_file`: `datasets/context_plans/ConstraintEngineNodeStatus/manifest.json`
- `translate_plan`: `True`
- `deactivate_before`: `False`
- `activate`: `True`
- `verify`: `True`

---

### `apply_context_docgen`

**Description:** Creates and configures the RLM_QuoteDocGenContext context definition for Context Service document templates. Defines Quote node (AccountName, BillingStreet/City/State/PostalCode, SalesRep, QuoteNumber, CreatedDate, ExpirationDate, GrandTotal) and Line child node (ProductName, Quantity, ListPrice, Discount, NetUnitPrice, NetTotalPrice) mapped via QuoteDocGenMapping to Quote and QuoteLineItem SObjects.

**Class:** `tasks.rlm_context_service.ManageContextDefinition`

**Options:**

- `plan_file`: `datasets/context_plans/DocGen/manifest.json`
- `translate_plan`: `True`
- `deactivate_before`: `False`
- `activate`: `True`
- `verify`: `True`

---

### `apply_context_ramp_mode`

**Description:** Adds RampMode__c (SalesTransactionItem) and GroupRampMode__c (SalesTransactionGroup) context attributes to the Sales Transaction context definition and maps them to QuoteLineItem.RLM_RampMode__c and QuoteLineGroup.RLM_RampMode__c (QuoteEntitiesMapping) and OrderItem.RLM_RampMode__c and OrderItemGroup.RLM_RampMode__c (OrderEntitiesMapping).

**Class:** `tasks.rlm_context_service.ManageContextDefinition`

**Options:**

- `developer_name`: `RLM_SalesTransactionContext`
- `plan_file`: `datasets/context_plans/RampMode/manifest.json`
- `translate_plan`: `True`
- `deactivate_before`: `False`
- `activate`: `True`
- `verify`: `True`

---

### `apply_mfg_SalesTransactionContext`

**Description:** Apply ConstraintEngineNodeStatus mappings to Sales Transaction context for MFG

**Class:** `tasks.rlm_context_service.ManageContextDefinition`

**Options:**

- `developer_name`: `MFG_SalesTransactionContext`
- `plan_file`: `datasets/context_plans/mfg/manifest.json`
- `translate_plan`: `True`
- `deactivate_before`: `False`
- `activate`: `True`
- `verify`: `True`

---

### `assign_permission_set_groups_tolerant`

**Description:** Assign Permission Set Groups with tolerance for permission warnings

**Class:** `tasks.rlm_assign_permission_set_groups.AssignPermissionSetGroupsTolerant`

**Options:**

- `api_names`: API Developer Names of desired Permission Set Groups *(required)*
- `user_alias`: Alias of target user (if not the current running user) 

---

### `cleanup_settings_for_dev`

**Description:** Clean up settings files before deployment (removes fields unsupported in the target org)

**Class:** `tasks.rlm_cleanup_settings.CleanupSettingsForDev`

**Options:**

- `path`: `unpackaged/pre`
- `remove_for_scratch`: `True`

---

### `configure_core_pricing_setup`

**Description:** Configure Salesforce Pricing Setup (CorePricingSetup) page: set the default Pricing Procedure (Robot test). Must run after the Pricing Procedure expression set is deployed and activated.

**Class:** `tasks.rlm_configure_core_pricing_setup.ConfigureCorePricingSetup`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/configure_core_pricing_setup.robot`
- `outputdir`: `robot/rlm-base/results`
- `pricing_procedure`: `RLM Revenue Management Default Pricing Procedure`

---

### `configure_product_discovery_settings`

**Description:** Set the Default Catalog in Product Discovery Settings to 'QuantumBit Software' (Robot test). Must run after QB product catalog data is loaded. Only relevant when qb=true.

**Class:** `tasks.rlm_configure_product_discovery_settings.ConfigureProductDiscoverySettings`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/configure_product_discovery_settings.robot`
- `outputdir`: `robot/rlm-base/results`
- `default_catalog`: `QuantumBit Software`

---

### `configure_revenue_settings`

**Description:** Configure Revenue Settings page defaults: Pricing Procedure, Usage Rating, Instant Pricing toggle, Create Orders from Quote flow, and optionally Manage Assets flow (Robot test). Must run after all data/metadata is deployed and before decision table refresh.

**Class:** `tasks.rlm_configure_revenue_settings.ConfigureRevenueSettings`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/configure_revenue_settings.robot`
- `outputdir`: `robot/rlm-base/results`
- `pricing_procedure`: `RLM Revenue Management Default Pricing Procedure`
- `usage_rating_procedure`: `RLM Default Rating Discovery Procedure`
- `create_orders_flow`: `RLM_CreateOrdersFromQuote`

---

### `create_approval_email_templates`

**Description:** Create Lightning Email Templates for RLM Approval notifications from the dataset CSV. Reads EmailTemplate.csv from datasets/sfdmu/qb/en-US/qb-approvals/ and creates SFX-type (Lightning) EmailTemplate records in the target org, then links them to ApprovalAlertContentDef records. Idempotent: skips templates that already exist. Required before insert_qb_approvals_data. EmailTemplatePage FlexiPages cannot be deployed via Metadata API (platform restriction).

**Class:** `tasks.rlm_create_approval_email_templates.CreateApprovalEmailTemplates`

---

### `create_billing_portal`

**Description:** Create Self-Service Billing Portal community (Experience Cloud site).

**Class:** `cumulusci.tasks.salesforce.CreateCommunity`

**Options:**

- `name`: `Billing Portal`
- `description`: `RLM Self-Service Billing Portal`
- `template`: `Self-Service Billing Portal`
- `url_path_prefix`: `billing`
- `skip_existing`: `True`

---

### `create_docgen_library`

**Description:** Create DocGen Library

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/createDocgenTemplateLibrary.apex`

---

### `create_dro_rule_library`

**Description:** Create DRO Rule Library

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/createDRORuleLibrary.apex`

---

### `create_procedure_plan_definition`

**Description:** Create Procedure Plan Definition via Connect API (idempotent)

**Class:** `tasks.rlm_create_procedure_plan_def.CreateProcedurePlanDefinition`

**Options:**

- `description`: `Procedure Plan Definition for Quote Pricing`
- `developerName`: `RLM_Quote_Pricing_Procedure_Plan`
- `name`: `RLM_Quote_Pricing_Procedure_Plan`
- `primaryObject`: `Quote`
- `processType`: `RevenueCloud`
- `versionActive`: `False`
- `context_definition_label`: `RLM_SalesTransactionContext`
- `versionReadContextMapping`: `QuoteEntitiesMapping`
- `versionSaveContextMapping`: `QuoteEntitiesMapping`
- `versionEffectiveFrom`: `2026-01-01T00:00:00.000Z`
- `versionDeveloperName`: `RLM_Quote_Pricing_Procedure_Plan`
- `versionRank`: `1`
- `versionEffectiveTo`: `None`

---

### `create_rule_library`

**Description:** Create Rule Library

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/createRuleLibrary.apex`

---

### `create_tax_engine`

**Description:** Create Tax Engine

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/createTaxEngine.apex`

---

### `deactivate_decision_tables`

**Description:** Deactivate Decision Tables (required before updating active decision tables)

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/deactivateDecisionTables.apex`

---

### `deactivate_expression_sets`

**Description:** Deactivate expression set versions via Tooling API

**Class:** `tasks.rlm_manage_expression_sets.ManageExpressionSets`

**Options:**

- `operation`: `deactivate_versions`
- `metadata_path`: `force-app/main/default/expressionSetDefinition`

---

### `deploy_agents`

**Description:** Deploy Agentforce Agent Configurations

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents`

---

### `deploy_agents_bots`

**Description:** Deploy Agentforce Agent Bots

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/bots`

---

### `deploy_agents_flows`

**Description:** Deploy Agentforce Agent Flows

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/flows`

---

### `deploy_agents_genAiFunctions`

**Description:** Deploy Agentforce Agent Functions

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/genAiFunctions`

---

### `deploy_agents_genAiPlanners`

**Description:** Deploy Agentforce Agent Planner Bundles

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/genAiPlannerBundles`

---

### `deploy_agents_genAiPlugins`

**Description:** Deploy Agentforce Agent Plugins

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/genAiPlugins`

---

### `deploy_agents_permissionsets`

**Description:** Deploy Agentforce Agent Permissionsets

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/permissionsets`

---

### `deploy_agents_settings`

**Description:** Deploy Agentforce Agent Settings

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_agents/settings`

---

### `deploy_billing_id_settings`

**Description:** Deploy Billing Settings with org-specific record IDs (resolved via XPath transform queries at deploy time)

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_billing_id_settings`
- `transforms`: `[{'transform': 'find_replace', 'options': {'patterns': [{'xpath': '//BillingSettings/defaultBillingTreatment[text()="...`

---

### `deploy_billing_template_settings`

**Description:** Re-enable Invoice Email/PDF toggles to trigger default template auto-creation (cycle step 3)

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_billing_template_settings`

---

### `deploy_context_definitions`

**Description:** Deploy Context Definitions

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/contextDefinitions`

---

### `deploy_decision_tables`

**Description:** Deploy Decision Tables

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/decisionTables`

---

### `deploy_expression_sets`

**Description:** Deploy Expression Sets

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/expressionSetDefinition`
- `transforms`: `[{'transform': 'find_replace', 'options': {'patterns': [{'xpath': '//ExpressionSetDefinition/versions/variables/value...`

---

### `deploy_full`

**Description:** Deploy all metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default`
- `transforms`: `[{'transform': 'find_replace', 'options': {'patterns': [{'xpath': '//ExpressionSetDefinition/versions/variables/value...`

---

### `deploy_org_settings`

**Description:** Deploy Org Settings

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/settings`

---

### `deploy_permissions`

**Description:** Deploy Permission Set Groups

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `force-app/main/default/permissionsetgroups`

---

### `deploy_post_billing_portal`

**Description:** Deploy Billing Portal site metadata (experiences, themes, etc.) from unpackaged/post_billing_portal. Run when billing_portal_deploy is true after create_billing_portal.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_billing_portal`

---

### `deploy_post_collections`

**Description:** Deploy Collections metadata from unpackaged/post_collections (flows, objects, omniUiCard, permissionsets, queues, quickActions, tabs, timelineObjectDefinitions). Flexipages and applications for collections are deployed via assemble_and_deploy_ux (prepare_ux flow) — they are excluded here via .forceignore.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_collections`

---

### `deploy_post_personas`

**Description:** Deploy persona metadata (profiles, permission set groups, permission sets) from unpackaged/post_personas.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_personas`

---

### `deploy_post_ramp_builder`

**Description:** Deploy all Ramp Schedule Builder (Create Ramp Schedule V4) metadata under unpackaged/post_ramp_builder: RLM_RampMode__c (Picklist) on QuoteLineGroup, QuoteLineItem, OrderItemGroup, and OrderItem; RLM_UpliftPercent__c (Percent) on QuoteLineGroup only; Lightning Message Channel (RLM_RampScheduleChannel); Apex classes and test classes (RLM_RampScheduleFlowAction, RLM_RampScheduleService, RLM_RampScheduleValidator, RLM_RampScheduleRequest, RLM_RampScheduleResponse, RLM_RampScheduleFlowException, RLM_RampMigrationQueueable, RLM_RampScheduleStatusController, RLM_QuoteLineItemDiscountUpliftHandler, RLM_QuoteLineItemRampModeHandler, RLM_QuoteLineItemRampHandler, and test classes); RLM_QuoteLineItemRampTrigger trigger; six LWC bundles (rlmRampScheduleFlowModalAction, rlmRampScheduleForm, rlmRampScheduleTrialSection, rlmRampSchedulePreviewTable, rlmRampScheduleStatus, rlmRampRefreshPage); the RLM_Create_Ramp_Schedule_V4 screen flow; the Quote.RLM_Create_Ramp_Schedule_V4 quick action; and the RLM_RampSchedule permission set (grants FLS on all custom fields and class access for all production Apex classes).

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_ramp_builder`

---

### `deploy_pre`

**Description:** Deploy Pre-deployment Metadata

**Class:** `cumulusci.tasks.salesforce.DeployBundles`

**Options:**

- `path`: `unpackaged/pre`

---

### `enable_constraints_settings`

**Description:** Set Default Transaction Type, Asset Context for Product Configurator, and enable Constraints Engine toggle on Revenue Settings (Robot test). Required before CML constraint data import.

**Class:** `tasks.rlm_enable_constraints_settings.EnableConstraintsSettings`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/enable_constraints_settings.robot`
- `outputdir`: `robot/rlm-base/results`
- `default_transaction_type`: `Advanced Configurator`
- `asset_context`: `RLM_AssetContext`

---

### `enable_document_builder_toggle`

**Description:** Enable the Document Builder toggle on Revenue Settings (Robot test with sf org open). Run before deploy_post_docgen when the org does not have Document Builder enabled via metadata.

**Class:** `tasks.rlm_enable_document_builder_toggle.EnableDocumentBuilderToggle`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/enable_document_builder.robot`
- `outputdir`: `robot/rlm-base/results`

---

### `exclude_active_decision_tables`

**Description:** Exclude active decision tables from deployment (TODO: implement proper deactivation)

**Class:** `tasks.rlm_exclude_active_decision_tables.ExcludeActiveDecisionTables`

**Options:**

- `path`: `unpackaged/pre/5_decisiontables`

---

### `export_cml`

**Description:** Export constraint model data (ESDV, ESC, reference objects, blob) from org to local directory

**Class:** `tasks.rlm_cml.ExportCML`

---

### `export_cml_fuelCell`

**Description:** Export constraint model data (ESDV, ESC, reference objects, blob) from org to local directory

**Class:** `tasks.rlm_cml.ExportCML`

**Options:**

- `developer_name`: `Fuel_Cell`
- `version`: `1`
- `output_dir`: `datasets/constraints/mfg/fuelCell`

---

### `export_cml_genSet`

**Description:** Export constraint model data (ESDV, ESC, reference objects, blob) from org to local directory

**Class:** `tasks.rlm_cml.ExportCML`

**Options:**

- `developer_name`: `GeneratorSet`
- `version`: `1`
- `output_dir`: `datasets/constraints/mfg/genSet`

---

### `extend_context_asset`

**Description:** Extend Standard Asset Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_AssetContext`
- `description`: `Extension of Standard Sales Transaction Context Definition`
- `developerName`: `RLM_AssetContext`
- `baseReference`: `AssetContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `AssetEntitiesMapping`
- `activate`: `True`

---

### `extend_context_billing`

**Description:** Extend Standard Billing Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_BillingContext`
- `description`: `Extension of Standard Billing Context Definition`
- `developerName`: `RLM_BillingContext`
- `baseReference`: `BillingContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `BSGEntitiesMapping`
- `activate`: `True`

---

### `extend_context_cart`

**Description:** Extend Standard Cart Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_CommerceCartContext`
- `description`: `Extension of Standard Cart Context Definition`
- `developerName`: `RLM_CommerceCartContext`
- `baseReference`: `CommerceCartContextDefinition__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `CommerceCartMapping`
- `activate`: `True`

---

### `extend_context_collection_plan_segment`

**Description:** Extend Standard Collection Plan Segment Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_CollectionPlanSegmentCtx`
- `description`: `Extension of Standard Collection Plan Segment Context Definition`
- `developerName`: `RLM_CollectionPlanSegmentCtx`
- `baseReference`: `CollectionPlanSegmentContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `CollectionPlanContextMapping`
- `activate`: `True`

---

### `extend_context_contracts`

**Description:** Extend Standard Contracts Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_ContractsContext`
- `description`: `Extension of Standard Contracts Context Definition`
- `developerName`: `RLM_ContractsContext`
- `baseReference`: `ContractsContextDefinition__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `OppToCntrPersistenceMapping`
- `activate`: `True`

---

### `extend_context_contracts_extraction`

**Description:** Extend Standard Contracts Extraction Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_ContractsExtractionContext`
- `description`: `Extension of Standard Contracts Extraction Context Definition`
- `developerName`: `RLM_ContractsExtractionContext`
- `baseReference`: `ContractsExtractionContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `DocExtrctPersistenceMapping`
- `activate`: `True`

---

### `extend_context_fulfillment_asset`

**Description:** Extend Standard Fulfillment Asset Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_FulfillmentAssetContext`
- `description`: `Extension of Standard Fulfillment Asset Context Definition`
- `developerName`: `RLM_FulfillmentAssetContext`
- `baseReference`: `FulfillmentAssetContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `FulfillAssetEntitiesMapping`
- `activate`: `True`

---

### `extend_context_product_discovery`

**Description:** Extend Standard Product Discovery Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_ProductDiscoveryContext`
- `description`: `Extension of Standard Product Discovery Context Definition`
- `developerName`: `RLM_ProductDiscoveryContext`
- `baseReference`: `ProductDiscoveryContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `ProductDiscoveryMapping`
- `activate`: `True`

---

### `extend_context_rate_management`

**Description:** Extend Standard Rate Management Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_RateManagementContext`
- `description`: `Extension of Standard Rate Management Context Definition`
- `developerName`: `RLM_RateManagementContext`
- `baseReference`: `RateManagementContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `DefaultUsageMapping`
- `activate`: `True`

---

### `extend_context_rating_discovery`

**Description:** Extend Standard Rating Discovery Context Definition

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_RatingDiscoveryContext`
- `description`: `Extension of Standard Rating Discovery Context Definition`
- `developerName`: `RLM_RatingDiscoveryContext`
- `baseReference`: `RatingDiscoveryContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `CatalogMapping`
- `activate`: `True`

---

### `extend_context_sales_transaction`

**Description:** Extend Standard Sales Transaction Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `RLM_SalesTransactionContext`
- `description`: `Extension of Standard Sales Transaction Context Definition`
- `developerName`: `RLM_SalesTransactionContext`
- `baseReference`: `SalesTransactionContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `QuoteEntitiesMapping`
- `activate`: `True`

---

### `extend_context_sales_transaction_mfg`

**Description:** Extend Standard Sales Transaction Context

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `MFG_SalesTransactionContext`
- `description`: `Extension of Standard Sales Transaction Context Definition`
- `developerName`: `MFG_SalesTransactionContext`
- `baseReference`: `SalesTransactionContext__stdctx`
- `startDate`: `2020-01-01T00:00:00.000Z`
- `contextTtl`: `30`
- `defaultMapping`: `QuoteEntitiesMapping`
- `activate`: `True`

---

### `extend_standard_context`

**Description:** Extend a standard context definition and optionally apply a plan

**Class:** `tasks.rlm_extend_stdctx.ExtendStandardContext`

**Options:**

- `name`: `None`
- `description`: `None`
- `developerName`: `None`
- `baseReference`: `None`
- `startDate`: `None`
- `contextTtl`: `None`
- `defaultMapping`: `None`
- `activate`: `True`
- `plan_file`: `None`

---

### `extract_badger_pricing_data`

**Description:** Extract Badger Pricing Data

**Class:** `tasks.rlm_sfdmu.ExtractSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/mfg/en-US/mfg-pricing`

---

### `fix_document_template_binaries`

**Description:** Corrects DocumentTemplate ContentDocument binaries after a batch metadata deploy. Salesforce metadata API bug: all DocumentTemplates deployed in a single batch receive the same ContentDocument binary (first alphabetically). This task uploads the correct .dt binary from the repo for each RLM_ template, replacing the wrong ContentDocument content. Run after deploy_post_docgen + activate_docgen_templates.

**Class:** `tasks.rlm_docgen.FixDocumentTemplateBinaries`

---

### `import_cml`

**Description:** Import constraint model metadata, ESC associations, and ConstraintModel blob into org

**Class:** `tasks.rlm_cml.ImportCML`

---

### `insert_billing_data`

**Description:** Insert QuantumBit Billing Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-billing`

---

### `insert_clm_data`

**Description:** Insert CLM Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-clm`

---

### `insert_clm_data_prod`

**Description:** Insert CLM Data to Production

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-clm`

---

### `insert_procedure_plan_data`

**Description:** Insert Procedure Plan data (sections in pass 1, options with expression set links in pass 2)

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/procedure-plans`

---

### `insert_q3_billing_data`

**Description:** Insert Q3 Billing Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-billing`

---

### `insert_q3_data`

**Description:** Insert Q3 Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-multicurrency`

---

### `insert_q3_dro_data_prod`

**Description:** Insert Q3 DRO Data to Production

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-dro`
- `dynamic_assigned_to_user`: `True`

---

### `insert_q3_dro_data_scratch`

**Description:** Insert Q3 DRO Data to Scratch

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-dro`
- `dynamic_assigned_to_user`: `True`

---

### `insert_q3_rates_data`

**Description:** Insert Q3 Rates Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-rates`

---

### `insert_q3_rating_data`

**Description:** Insert Q3 Rating Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-rating`

---

### `insert_q3_tax_data`

**Description:** Insert Q3 Tax Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/q3/en-US/q3-tax`

---

### `insert_qb_approvals_data`

**Description:** Insert QuantumBit Approvals data. Loads ApprovalAlertContentDef records for discount and payment terms approval notifications. Requires post_approvals metadata (Flows, Fields, PathAssistant, PermissionSet) and create_approval_email_templates to be run first. EmailTemplatePage FlexiPages are excluded from deploy (platform restriction).

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-approvals`

---

### `insert_qb_constraints_component_data`

**Description:** Insert QuantumBit Constraints Product Related Component Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-constraints-component`

---

### `insert_qb_constraints_product_data`

**Description:** Insert QuantumBit Constraints Product Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-constraints-product`

---

### `insert_qb_dro_data`

**Description:** Insert QuantumBit DRO Data (scratch and prod; AssignedTo resolved from target org)

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-dro`
- `dynamic_assigned_to_user`: `True`

---

### `insert_qb_guidedselling_data`

**Description:** Insert QuantumBit Guided Selling Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-guidedselling`

---

### `insert_qb_rates_data`

**Description:** Insert QuantumBit Rates Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rates`

---

### `insert_qb_rating_data`

**Description:** Insert QuantumBit Rating Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-rating`

---

### `insert_qb_transactionprocessingtypes_data`

**Description:** Insert QuantumBit Transaction Processing Types Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes`

---

### `insert_quantumbit_pcm_data`

**Description:** Insert QuantumBit Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pcm`

---

### `insert_quantumbit_pricing_data`

**Description:** Insert QuantumBit Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-pricing`

---

### `insert_quantumbit_prm_data`

**Description:** Insert QuantumBit PRM data using a 2-pass SFDMU plan. Pass 1 upserts partner Accounts, ChannelProgram, and ChannelProgramLevel. Pass 2 enables IsPartner on Accounts (not createable, only updateable) and upserts ChannelProgramMember linking partners to program levels.

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-prm`

---

### `insert_quantumbit_product_image_data`

**Description:** Insert QuantumBit Product Image Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-product-images`

---

### `insert_scratch_data`

**Description:** Insert Scratch Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/scratch_data`

---

### `insert_tax_data`

**Description:** Insert QuantumBit Tax Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

**Options:**

- `pathtoexportjson`: `datasets/sfdmu/qb/en-US/qb-tax`

---

### `load_sfdmu_data`

**Description:** Load SFDMU Data

**Class:** `tasks.rlm_sfdmu.LoadSFDMUData`

---

### `manage_context_definition`

**Description:** Modify context definitions via Context Service (connect) endpoints

**Class:** `tasks.rlm_context_service.ManageContextDefinition`

**Options:**

- `context_definition_id`: `None`
- `developer_name`: `None`
- `plan_file`: `None`
- `activate`: `False`
- `dry_run`: `False`

---

### `manage_decision_tables`

**Description:** Decision Table management: list (with UsageType), query, refresh, activate, deactivate, validate_lists (compare org to project list anchors)

**Class:** `tasks.rlm_manage_decision_tables.ManageDecisionTables`

**Options:**

- `operation`: `list`
- `status`: `Active`
- `is_incremental`: `False`
- `sort_by`: `LastSyncDate`
- `sort_order`: `Desc`

---

### `manage_expression_sets`

**Description:** Comprehensive Expression Set management (list, query, manage versions)

**Class:** `tasks.rlm_manage_expression_sets.ManageExpressionSets`

**Options:**

- `operation`: `list`
- `status`: `None`
- `interface_source_type`: `None`
- `process_type`: `None`
- `version_full_name`: `None`
- `version_full_names`: `None`
- `metadata_path`: `force-app/main/default/expressionSetDefinition`
- `sort_by`: `LastModifiedDate`
- `sort_order`: `Desc`

---

### `manage_flows`

**Description:** Comprehensive Flow management (list, query, activate, deactivate)

**Class:** `tasks.rlm_manage_flows.ManageFlows`

**Options:**

- `operation`: `list`
- `status`: `None`
- `process_type`: `None`
- `sort_by`: `LastModifiedDate`
- `sort_order`: `Desc`

---

### `manage_transaction_processing_types`

**Description:** Manage TransactionProcessingType entries via Tooling API

**Class:** `tasks.rlm_manage_transaction_processing_types.ManageTransactionProcessingTypes`

**Options:**

- `operation`: `list`
- `input_file`: `None`
- `key_field`: `DeveloperName`
- `api_version`: `None`
- `dry_run`: `False`

---

### `patch_payments_site_for_deploy`

**Description:** Patch Payments_Webhook.site-meta.xml with the org's actual admin username before deploy. Required because siteAdmin and siteGuestRecordDefaultOwner are immutable after site creation and the committed XML contains a placeholder username.

**Class:** `tasks.rlm_community.PatchPaymentsSiteForDeploy`

---

### `post_process_extraction`

**Description:** Post-process extracted CSVs into import-ready format

**Class:** `cumulusci.tasks.command.Command`

**Options:**

- `command`: `python3 scripts/post_process_extraction.py {extraction_dir} {plan_dir}`

---

### `post_process_extraction_badger_pcm`

**Description:** Post-process extracted CSVs into import-ready format

**Class:** `cumulusci.tasks.command.Command`

**Options:**

- `command`: `python3 scripts/post_process_extraction.py datasets/sfdmu/extractions/mfg-pcm/2026-03-05T165417 datasets/sfdmu/mfg/en...`

---

### `query_billing_state`

**Description:** Query billing record state (PaymentTerm, BillingTreatment, BillingPolicy, BillingTreatmentItem) for validation; check debug logs for output.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/query_billing_state.apex`

---

### `recalculate_permission_set_groups`

**Description:** Recalculate permission set groups and wait for Updated status

**Class:** `tasks.rlm_recalculate_permission_set_groups.RecalculatePermissionSetGroups`

**Options:**

- `api_names`: API Developer Names of Permission Set Groups to recalculate *(required)*
- `timeout_seconds`: `300`
- `poll_seconds`: `10`
- `trigger_recalc`: `True`
- `initial_delay_seconds`: `60`
- `retry_count`: `2`
- `retry_delay_seconds`: `120`
- `post_trigger_delay_seconds`: `90`
- `use_tooling_api`: `False`

---

### `reconfigure_mfg_pricing_discovery`

**Description:** Reconfigure the autoproc Salesforce_Default_Pricing_Discovery_Procedure expression set: fix context definition, set rank and start date, and reactivate. When the autoproc expression set does not exist (e.g. tso=true orgs), activates the fallback RLM_DefaultPricingDiscoveryProcedure instead. Required before decision table refresh.

**Class:** `tasks.rlm_reconfigure_expression_set.ReconfigureExpressionSet`

**Options:**

- `expression_set_name`: `Salesforce_Default_Pricing_Discovery_Procedure`
- `context_definition_name`: `MFG_SalesTransactionContext`
- `rank`: `1`
- `start_date`: `2020-01-01T00:00:00.000Z`
- `fallback_expression_set_name`: `RLM_DefaultPricingDiscoveryProcedure`

---

### `reconfigure_pricing_discovery`

**Description:** Reconfigure the autoproc Salesforce_Default_Pricing_Discovery_Procedure expression set: fix context definition, set rank and start date, and reactivate. When the autoproc expression set does not exist (e.g. tso=true orgs), activates the fallback RLM_DefaultPricingDiscoveryProcedure instead. Required before decision table refresh.

**Class:** `tasks.rlm_reconfigure_expression_set.ReconfigureExpressionSet`

**Options:**

- `expression_set_name`: `Salesforce_Default_Pricing_Discovery_Procedure`
- `context_definition_name`: `RLM_SalesTransactionContext`
- `rank`: `1`
- `start_date`: `2020-01-01T00:00:00.000Z`
- `fallback_expression_set_name`: `RLM_DefaultPricingDiscoveryProcedure`

---

### `refresh_dt_asset`

**Description:** Refresh Asset Decision Tables

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Asset_Action_Source_Entries_Decision_Table_V2', 'Asset_Rate_Card_Entry_Resolution_V2', 'Asset_Rate_Decision_Table_V...`

---

### `refresh_dt_commerce`

**Description:** Refresh Commerce Decision Tables (when commerce flag is true)

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Price_Book_Entry_Commerce_V2', 'Price_Book_Entry_For_Unit_Price_Commerce_V1', 'Pricebook_Entry_Adjustment_Commerce_...`

---

### `refresh_dt_default_pricing`

**Description:** Refresh Default Pricing Decision Tables

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Attribute_Based_Adjustment_Decision_Table', 'Bundle_Based_Adjustment_Decision_Table', 'Contract_Pricing_Adjustment_...`

---

### `refresh_dt_pricing_discovery`

**Description:** Refresh Pricing Discovery Decision Tables

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Asset_Action_Source_Entries_Decision_Table_V2', 'Derived_Pricing_Entries_Decision_Table']`

---

### `refresh_dt_rating`

**Description:** Refresh Rating Decision Tables

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Asset_Action_Source_Entries_Decision_Table_V2', 'Asset_Rate_Card_Entry_Resolution_V2', 'Asset_Rate_Card_Entry_Resol...`

---

### `refresh_dt_rating_discovery`

**Description:** Refresh Rating Discovery Decision Tables

**Class:** `tasks.rlm_refresh_decision_table.RefreshDecisionTable`

**Options:**

- `developerNames`: `['Binding_Object_Rate_Adjustment_Resolution_Entries', 'Binding_Object_Rate_Card_Entry_Resolution_Entries_v2', 'Priceb...`

---

### `restore_decision_tables`

**Description:** Restore skipped decision tables after deploy

**Class:** `tasks.rlm_exclude_active_decision_tables.RestoreDecisionTables`

**Options:**

- `path`: `unpackaged/pre/5_decisiontables`

---

### `revert_payments_site_after_deploy`

**Description:** Restore the placeholder siteAdmin and siteGuestRecordDefaultOwner in Payments_Webhook.site-meta.xml after deploy_post_payments_site so the repo never stores the target org's real username. Run AFTER deploy_post_payments_site.

**Class:** `tasks.rlm_community.RevertPaymentsSiteAfterDeploy`

---

### `stamp_git_commit`

**Description:** Stamps the current git commit hash, branch, timestamp, org definition, dirty-tree flag, and active feature flags into the org as a Custom Metadata Type record (RLM_Build_Info__mdt.Latest). Non-fatal: deploy failures are logged as warnings so this task never breaks a completed flow.

**Class:** `tasks.rlm_stamp_commit.StampGitCommit`

**Options:**

- `flow_name`: `manual`

---

### `sync_pricing_data`

**Description:** Sync Pricing Data

**Class:** `tasks.rlm_sync_pricing_data.SyncPricingData`

---

### `update_product_fulfillment_decomp_rules`

**Description:** Update ProductFulfillmentDecompRule after DRO load. TEMPORARY FIX (260 bug) ExecuteOnRuleId not created on INSERT; re-save triggers ruleset generation. See scripts/apex/updateProductFulfillmentDecompRules.apex.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/updateProductFulfillmentDecompRules.apex`

---

### `validate_billing_structure`

**Description:** Validate that every BillingTreatment has BillingPolicyId set. Run after data load to verify structure before activation.

**Class:** `cumulusci.tasks.apex.anon.AnonymousApexTask`

**Options:**

- `path`: `scripts/apex/validateBillingStructure.apex`

---

### `validate_cml`

**Description:** Validate CML file structure, annotations, and ESC association coverage

**Class:** `tasks.rlm_cml.ValidateCML`

---

### `validate_setup`

**Description:** Validate the local developer setup for rlm-base-dev. Checks Python, CumulusCI, Salesforce CLI, SFDMU plugin version (v5+ required), Node.js, Robot Framework, SeleniumLibrary, webdriver-manager, Chrome/Chromium, ChromeDriver, and urllib3. When auto_fix=true the SFDMU plugin is automatically installed or updated to the required version. Run without an org: cci task run validate_setup

**Class:** `tasks.rlm_validate_setup.ValidateSetup`

**Options:**

- `auto_fix`: `True`
- `required_sfdmu_version`: `5.0.0`
- `fail_on_error`: `True`

---

## UX Personalization

*2 task(s)*

### `assemble_and_deploy_ux`

**Description:** Assembles feature-conditional UX metadata (flexipages, layouts, applications, app menus, profiles) from base templates and YAML patch files in templates/. Writes assembled SFDX-format output to unpackaged/post_ux/ (git-tracked) and deploys in a single sf project deploy start call. Supports granular invocation via metadata_type and metadata_name options for development and debugging.

**Class:** `tasks.rlm_ux_assembly.AssembleAndDeployUX`

---

### `reorder_app_launcher`

**Description:** Applies a priority order to the App Launcher. The Python task queries all AppMenuItem records via the Salesforce REST API (SOQL), builds a priority-ordered ApplicationId list (priority_app_labels first, remaining apps after in their current relative order), and passes the list to a Robot Framework test. The Robot test navigates to the Lightning home page and calls Aura AppLauncherController/saveOrder via synchronous XHR — no modal or DOM scraping required. Required on Trialforce-based orgs where the Metadata API cannot deploy an AppSwitcher containing managed ConnectedApp or Network entries and AppMenuItem.SortOrder is platform read-only via all other APIs.

**Class:** `tasks.rlm_reorder_app_launcher.ReorderAppLauncher`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/reorder_app_launcher.robot`
- `outputdir`: `robot/rlm-base/results`

---

## Uncategorized

*28 task(s)*

### `create_partner_central`

**Description:** Create Partner Central Community

**Class:** `cumulusci.tasks.salesforce.CreateCommunity`

**Options:**

- `name`: `rlm`
- `description`: `RLM Partner Digital Experience`
- `template`: `Partner Central (Enhanced)`
- `url_path_prefix`: `partners`
- `skip_existing`: `True`

---

### `create_payments_webhook`

**Description:** Create Salesforce Payments Webhook

**Class:** `cumulusci.tasks.salesforce.CreateCommunity`

**Options:**

- `name`: `Payments Webhook`
- `description`: `RLM Salesforce Payments Webhook`
- `template`: `Build Your Own (LWR)`
- `url_path_prefix`: `sfpwebhook`
- `skip_existing`: `True`

---

### `deploy_docgen_odt_seed`

**Description:** Seed-insert minimal OmniDataTransform shell records (RLMQuoteExtractBasic, RLMQuoteTransformBasic, RLMQuoteProposalExtract, RLMQuoteProposalTransform) before the full DocGen deploy. Salesforce rejects INSERT of ODTs that reference custom formula fields in inputFieldName (-692085439) but accepts UPDATE of existing records. This step creates the ODT stubs so the subsequent deploy_post_docgen runs as an UPDATE.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/pre_docgen`

---

### `deploy_docgen_qli_fields`

**Description:** Deploy RLM_ProductName__c formula field on QuoteLineItem before the main DocGen metadata deploy. The OmniDataTransform records reference this field in inputFieldName; Salesforce validates field existence on INSERT (fresh org), so it must exist before the ODTs are deployed. QuoteLineItem has no object-meta.xml, so the whole directory is safe to deploy early.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_docgen/objects/QuoteLineItem`

---

### `deploy_docgen_seller_fields`

**Description:** Deploy RLM_Seller_*__c, RLM_Account_Name__c, and RLM_Sales_Rep_Name__c formula fields on Quote before the main DocGen metadata deploy. The OmniDataTransform records reference these custom fields by name; Salesforce validates field existence on INSERT (fresh org), so the fields must exist before the ODTs are deployed. Targets only the Quote fields subdirectory to avoid the Quote object-meta.xml action overrides, which reference flexipages not yet deployed at this stage.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_docgen/objects/Quote/fields`

---

### `deploy_post_approvals`

**Description:** Deploy Advanced Approvals metadata: Quote/QuoteLineItem fields, RLM_Payment_Terms GVS, PathAssistant, quickAction, flows (RLM_Quote_Smart_Approval, RLM_Quote_Approval_Data), Apex class, and permission set. EmailTemplatePage FlexiPages (including RLM_Quote_Record_Page) are excluded via .forceignore — EmailTemplatePage type cannot be deployed via Metadata API (platform restriction); Lightning Email Templates are created separately by create_approval_email_templates.

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_approvals`

---

### `deploy_post_billing`

**Description:** Deploy Billing Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_billing`

---

### `deploy_post_commerce`

**Description:** Deploy Commerce Metadata (e.g. Commerce decision table flows)

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_commerce`

---

### `deploy_post_constraints`

**Description:** Deploy Constraints Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_constraints`

---

### `deploy_post_docgen`

**Description:** Deploy Document Generation Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_docgen`

---

### `deploy_post_guidedselling`

**Description:** Deploy Guided Selling Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_guidedselling`

---

### `deploy_post_payments`

**Description:** Deploy Payments Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_payments`

---

### `deploy_post_payments_settings`

**Description:** Deploy Payments Settings

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_payments_settings`

---

### `deploy_post_payments_site`

**Description:** Deploy Payments site settings only

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_payments/sites`

---

### `deploy_post_prm`

**Description:** Deploy Partner Relationship Management Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_prm`

---

### `deploy_post_procedureplans`

**Description:** Deploy Procedure Plans Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_procedureplans`

---

### `deploy_post_procedureplans_classes`

**Description:** Deploy Procedure Plans Classes

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_procedureplans/classes`

---

### `deploy_post_procedureplans_objects`

**Description:** Deploy Procedure Plans Objects

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_procedureplans/objects`

---

### `deploy_post_procedureplans_permissionsets`

**Description:** Deploy Procedure Plans Permissionsets

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_procedureplans/permissionsets`

---

### `deploy_post_tso`

**Description:** Deploy Trialforce Source Org Metadata (App Launcher now deploys via prepare_ux/assemble_and_deploy_ux)

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_tso`

---

### `deploy_post_utils`

**Description:** Deploy Utils Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_utils`

---

### `deploy_quantumbit`

**Description:** Deploy QuantumBit Metadata

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_quantumbit`

---

### `deploy_sharing_rules`

**Description:** Deploy Sharing Rules

**Class:** `cumulusci.tasks.salesforce.Deploy`

**Options:**

- `path`: `unpackaged/post_sharing`

---

### `enable_analytics_replication`

**Description:** Enable CRM Analytics replication via browser automation (Robot/Selenium, Analytics Settings VF iframe)

**Class:** `tasks.rlm_analytics.EnableAnalyticsReplication`

**Options:**

- `suite`: `robot/rlm-base/tests/setup/enable_analytics.robot`
- `outputdir`: `robot/rlm-base/results`

---

### `ensure_pricing_schedules`

**Description:** Ensure pricing schedules exist before expression sets

**Class:** `tasks.rlm_repair_pricing_schedules.EnsurePricingSchedules`

**Options:**

- `disable_settings_path`: `tasks/resources/pricing_settings_disable`
- `enable_settings_path`: `unpackaged/pre/2_settings`

---

### `robot`

**Options:**

- `suites`: `robot/rlm-base/tests`
- `options`:  

---

### `robot_testdoc`

**Options:**

- `path`: `robot/rlm-base/tests`
- `output`: `robot/rlm-base/doc/rlm-base_tests.html`

---

### `run_tests`

**Options:**

- `required_org_code_coverage_percent`: `75`

---
