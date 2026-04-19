# CCI Flows Reference

> **Auto-generated** by `scripts/ai/generate_cci_reference.py` from `cumulusci.yml`.  
> Do not edit manually — re-run the script after changing `cumulusci.yml`.

**52 flows** across **5 groups**.

---

## Data Management - Extract

### `extract_mfg_aaf_with_category_fix`

Extract mfg-aaf from org, then fix Category__r.Code (SFDMU v5 workaround). Equivalent to extract_mfg_aaf_data followed by fix_mfg_aaf_category_extraction.

**Steps:**

1. **task** `extract_mfg_aaf_data`
2. **task** `fix_mfg_aaf_category_extraction`

---

### `run_qb_extracts`

Run all QB data extract tasks (org → CSV). Use --org to specify source org.

**Steps:**

1. **task** `extract_qb_pcm_data`
2. **task** `extract_qb_pricing_data`
3. **task** `extract_qb_product_images_data`
4. **task** `extract_qb_dro_data`
5. **task** `extract_qb_clm_data`
6. **task** `extract_qb_rating_data`
7. **task** `extract_qb_rates_data`
8. **task** `extract_qb_transactionprocessingtypes_data`
9. **task** `extract_qb_guidedselling_data`

---

## Data Management - Idempotency

### `run_qb_idempotency_tests`

Run all QB data idempotency tests (load twice, assert no new records). Use --org to specify target org.

**Steps:**

1. **task** `test_qb_pcm_idempotency`
2. **task** `test_qb_pricing_idempotency`
3. **task** `test_qb_product_images_idempotency`
4. **task** `test_qb_dro_idempotency`
5. **task** `test_qb_clm_idempotency`
6. **task** `test_qb_rating_idempotency`
7. **task** `test_qb_rates_idempotency`
8. **task** `test_qb_transactionprocessingtypes_idempotency`
9. **task** `test_qb_guidedselling_idempotency`

---

## Manufacturing

### `import_mfg_cml`

**Steps:**

1. **task** `import_cml`  `when: project_config.project__custom__manufacturing`
   - `data_dir`: `datasets/constraints/mfg/genSet`
2. **task** `import_cml`  `when: project_config.project__custom__manufacturing`
   - `data_dir`: `datasets/constraints/mfg/fuelCell`
3. **task** `manage_expression_sets`  `when: project_config.project__custom__manufacturing`
   - `operation`: `activate_versions`
   - `version_full_names`: `GeneratorSet_V1,Fuel_Cell_V1`

---

### `prepare_manufacturing`

Full Manufacturing feature setup: deploys core metadata (assets, theme, fields, Apex), assigns Manufacturing permission sets and groups (with propagation sleep), deploys all business process flows and Quick Actions, OmniStudio document generation components, context plan extensions, pricing setup, seed data (PCM, pricing, DRO, CML, tax, billing), guided selling, rebates, advanced account forecasting, revenue settings configuration, UX assembly, and theme activation. Gated by manufacturing=true in prepare_rlm_org (step 30).

**Steps:**

1. **flow** `prepare_mfg_core`
2. **flow** `prepare_mfg_perms`
3. **task** `deploy_mfg_flows_and_actions`  `when: project_config.project__custom__manufacturing`
4. **flow** `prepare_mfg_docgen`
5. **flow** `prepare_mfg_context_plan`
6. **flow** `prepare_mfg_pricing`
7. **flow** `prepare_mfg_data`
8. **task** `update_product_fulfillment_decomp_rules`  `when: project_config.project__custom__dro and project_config.project__custom__manufacturing`
9. **task** `reconfigure_mfg_pricing_discovery`  `when: project_config.project__custom__manufacturing`
10. **flow** `prepare_mfg_visuals`
11. **flow** `prepare_mfg_guided_selling`
12. **flow** `prepare_mfg_rebates`
13. **flow** `prepare_mfg_aaf`
14. **task** `util_sleep`  `when: project_config.project__custom__manufacturing`
   - `seconds`: `30`
15. **task** `configure_mfg_revenue_settings`  `when: project_config.project__custom__manufacturing`
16. **flow** `prepare_mfg_ux`
17. **task** `activate_mfg_theme`  `when: project_config.project__custom__manufacturing`

---

### `prepare_mfg_aaf`

Deploy Manufacturing Advanced Account Forecasting metadata in dependency order: object fields and translations, permission set, then waits before deploying the dimension source and forecast set configuration. Loads AAF seed data last. Gated by manufacturing=true and mfg_aaf=true.

**Steps:**

1. **task** `deploy_mfg_aaf_fields`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
2. **task** `deploy_mfg_aaf_permissions`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
   - `api_names`: `['MFG_AAF']`
4. **task** `util_sleep`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
   - `seconds`: `30`
5. **task** `deploy_mfg_aaf_dim_source`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
6. **task** `deploy_mfg_aaf_forecast_set`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`
7. **task** `insert_badger_aaf_data`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_aaf`

---

### `prepare_mfg_billing`

Load and activate Manufacturing billing seed data (LegalEntity, AccountingPeriod, BillingPolicy, BillingTreatment, BillingTreatmentItem, GeneralLedgerAccount, GeneralLedgerAcctAsgntRule, Product2 billing policy assignments). Activates billing records and deploys billing metadata. Runs when manufacturing=true and billing=true.

**Steps:**

1. **task** `insert_mfg_billing_data`  `when: project_config.project__custom__billing`
2. **task** `activate_flow`  `when: project_config.project__custom__billing`
   - `developer_names`: `RLM_Order_to_Billing_Schedule_Flow`
3. **task** `activate_default_payment_term`  `when: project_config.project__custom__billing`
4. **task** `activate_billing_records`  `when: project_config.project__custom__billing`
5. **task** `deploy_post_billing`  `when: project_config.project__custom__billing`
6. **task** `deploy_billing_template_settings`  `when: project_config.project__custom__billing`

---

### `prepare_mfg_context_plan`

Extend and apply the Manufacturing Sales Transaction context definition. Runs extend_context_sales_transaction_mfg then applies the MFG SalesTransactionContext twice (two-pass pattern required for full attribute population).

**Steps:**

1. **task** `extend_context_sales_transaction_mfg`  `when: project_config.project__custom__manufacturing`
2. **task** `apply_mfg_SalesTransactionContext`  `when: project_config.project__custom__manufacturing`
3. **task** `apply_mfg_SalesTransactionContext`  `when: project_config.project__custom__manufacturing`

---

### `prepare_mfg_core`

Deploy core Manufacturing metadata in dependency order. Step 1 deploys brand assets and IndustriesManufacturing settings (activating SalesAgreement objects) as a committed transaction. Step 2 deploys theme, custom fields, Apex, permissions, and SA settings in a single transaction (SalesAgreement objects now exist). Step 3 conditionally deploys the TSO production PSG (when tso=true). Does not deploy flows — prepare_mfg_perms runs next to assign the Manufacturing PSG before flow deployment.

**Steps:**

1. **task** `deploy_mfg_core_assets`  `when: project_config.project__custom__manufacturing`
2. **task** `deploy_mfg_core`  `when: project_config.project__custom__manufacturing`
3. **task** `deploy_mfg_tso_perms`  `when: project_config.project__custom__manufacturing and project_config.project__custom__tso`

---

### `prepare_mfg_data`

Load all Manufacturing seed data: PCM products, pricing records, DRO fulfillment rules, CML constraint models (GeneratorSet, FuelCell), and conditionally tax and billing records.

**Steps:**

1. **task** `insert_badger_pcm_data`  `when: project_config.project__custom__manufacturing`
2. **task** `insert_badger_pricing_data`  `when: project_config.project__custom__manufacturing`
3. **task** `insert_badger_dro_data`  `when: project_config.project__custom__manufacturing`
4. **flow** `import_mfg_cml`  `when: project_config.project__custom__manufacturing`
5. **flow** `prepare_mfg_tax`  `when: project_config.project__custom__manufacturing and project_config.project__custom__tax`
6. **flow** `prepare_mfg_billing`  `when: project_config.project__custom__manufacturing and project_config.project__custom__billing`

---

### `prepare_mfg_docgen`

Deploy Manufacturing OmniStudio document generation components in dependency order: OmniDataTransforms, OmniIntegrationProcedure, base doc gen OmniScript, Quote Proposal OmniScript, and document templates (Badger_Proposal, Price_Contract). Gated by manufacturing=true and mfg_docgen=true.

**Steps:**

1. **task** `deploy_mfg_omni_datatransforms`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_docgen`
2. **task** `deploy_mfg_omni_integration_procedures`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_docgen`
3. **task** `deploy_mfg_omni_base_docgen_script`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_docgen`
4. **task** `deploy_mfg_omni_quote_script`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_docgen`
5. **task** `deploy_mfg_doc_templates`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_docgen`

---

### `prepare_mfg_dro`

Load Manufacturing DRO seed data and update product fulfillment decomposition rules. Standalone flow; DRO steps are also embedded in prepare_mfg_data and prepare_manufacturing.

**Steps:**

1. **task** `insert_badger_dro_data`  `when: project_config.project__custom__manufacturing`
2. **task** `update_product_fulfillment_decomp_rules`  `when: project_config.project__custom__manufacturing`

---

### `prepare_mfg_guided_selling`

Deploy Manufacturing Guided Selling metadata and load seed data. Deploys AssessmentQuestions, OmniScripts, and ProductDiscovery settings, then inserts guided selling product assignments. Gated by manufacturing=true and mfg_guidedselling=true.

**Steps:**

1. **task** `insert_badger_guidedselling_data`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_guidedselling`
2. **task** `deploy_mfg_guided_selling`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_guidedselling`

---

### `prepare_mfg_perms`

Assign Manufacturing permission sets and permission set groups to the running user. Waits for metadata deployment to settle before assigning. Assigns either the scratch PSG (non-TSO) or production PSG (TSO) based on the tso feature flag. Also grants External Credential Principal Access to RLM_MFG_RCA (Metadata API limitation workaround via Tooling API callout + SetupEntityAccess DML).

**Steps:**

1. **task** `util_sleep`  `when: project_config.project__custom__manufacturing`
   - `seconds`: `30`
2. **task** `assign_permission_sets`  `when: project_config.project__custom__manufacturing`
   - `api_names`: `['RLM_MFG_RCA']`
3. **task** `assign_permission_set_groups`  `when: project_config.project__custom__manufacturing and not project__custom__tso`
   - `api_names`: `['RLM_MFG_scratch']`
4. **task** `assign_permission_set_groups`  `when: project_config.project__custom__manufacturing and project__custom__tso`
   - `api_names`: `['RLM_MFG']`
5. **task** `grant_mfg_ext_credential_access`  `when: project_config.project__custom__manufacturing`

---

### `prepare_mfg_pricing`

Deploy Manufacturing pricing metadata and activate the pricing procedure. Deploys the NGP default pricing recipe, then the MFG_Rev_Mgmt_Default_Pricing_Procedure ExpressionSetDefinition (with live PriceAdjustmentSchedule ID injection), then activates version V1.

**Steps:**

1. **task** `deploy_mfg_pricing_recipe`  `when: project_config.project__custom__manufacturing`
2. **task** `deploy_mfg_pricing_procedure`  `when: project_config.project__custom__manufacturing`
3. **task** `manage_expression_sets`  `when: project_config.project__custom__manufacturing`
   - `operation`: `activate_versions`
   - `version_full_names`: `MFG_Rev_Mgmt_Default_Pricing_Procedure_V1`

---

### `prepare_mfg_rebates`

Deploy Manufacturing rebate metadata (ObjectHierarchyRelationship settings and BatchCalcJobDefinition) then load rebate seed data. Gated by manufacturing=true and mfg_rebates=true.

**Steps:**

1. **task** `deploy_mfg_rebates`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_rebates`
2. **task** `insert_badger_rebates_data`  `when: project_config.project__custom__manufacturing and project_config.project__custom__mfg_rebates`

---

### `prepare_mfg_tax`

Load and activate Manufacturing tax seed data (LegalEntity, TaxPolicy, TaxTreatment, Product2 TaxPolicy assignments). Uses a two-pass SFDMU plan: Pass 1 inserts records in Draft status; Pass 2 activates TaxTreatment and TaxPolicy and sets DefaultTaxTreatmentId. Runs when manufacturing=true and tax=true.

**Steps:**

1. **task** `insert_mfg_tax_data`  `when: project_config.project__custom__tax`
2. **task** `activate_tax_records`  `when: project_config.project__custom__tax`

---

### `prepare_mfg_ux`

Assemble and deploy Manufacturing UX metadata (flexipages, layouts, applications) from templates/flexipages/standalone/manufacturing/, templates/layouts/manufacturing/, and templates/applications/manufacturing/. Output is written to unpackaged/post_manufacturing_ux/ and deployed in a single sf project deploy start call. Passes manufacturing=true so that manufacturing-specific content (SalesAgreement pages, RLM_MFG_* flexipages, manufacturing RLM_Revenue_Cloud variant) is included. Must run after all manufacturing metadata is deployed (step 14 of prepare_manufacturing). Run this flow independently to test manufacturing UX assembly without running the full prepare_rlm_org flow. Gated by manufacturing=true and ux=true in prepare_manufacturing.

**Steps:**

1. **task** `assemble_and_deploy_ux`  `when: project_config.project__custom__manufacturing and project_config.project__custom__ux`
   - `output_path`: `unpackaged/post_manufacturing_ux`
   - `manufacturing`: `True`

---

### `prepare_mfg_visuals`

Deploy Manufacturing 3D Visualization metadata and load product configuration flow assignments. Step 1 deploys unpackaged/post_manufacturing_visualization (LWC, VF page, CSP Trusted Site, RenderDraw flow). Step 2 inserts ProductConfigurationFlow and ProductConfigFlowAssignment records from datasets/sfdmu/mfg/en-US/mfg-configflow. Gated by mfg_visuals=true. Run independently to test visualization deployment before adding to prepare_manufacturing.

**Steps:**

1. **task** `deploy_mfg_visualization`  `when: project_config.project__custom__mfg_visuals`
2. **task** `insert_mfg_configflow_data`  `when: project_config.project__custom__mfg_visuals`

---

## Revenue Lifecycle Management

### `extend_context_definitions`

**Steps:**

1. **task** `extend_context_sales_transaction`
2. **task** `extend_context_product_discovery`
3. **task** `extend_context_cart`  `when: project_config.project__custom__commerce`
4. **task** `extend_context_billing`  `when: project_config.project__custom__billing`
5. **task** `extend_context_collection_plan_segment`  `when: project_config.project__custom__billing`
6. **task** `extend_context_fulfillment_asset`  `when: project_config.project__custom__dro`
7. **task** `extend_context_contracts`  `when: project_config.project__custom__clm`
8. **task** `extend_context_contracts_extraction`  `when: project_config.project__custom__clm`
9. **task** `extend_context_rate_management`  `when: project_config.project__custom__rating`
10. **task** `extend_context_rating_discovery`  `when: project_config.project__custom__rating`
11. **task** `extend_context_asset`

---

### `extract_rating`

Extract rating and rates data from an org into CSV files

**Steps:**

1. **task** `extract_qb_rating_data`
2. **task** `extract_qb_rates_data`

---

### `prepare_agents`

**Steps:**

1. **task** `assign_permission_set_groups`  `when: project_config.project__custom__agents`
   - `api_names`: `['CopilotSalesforceUserPSG', 'CopilotSalesforceAdminPSG']`
2. **task** `deploy_agents_settings`  `when: project_config.project__custom__agents`
3. **task** `deploy_agents`  `when: project_config.project__custom__agents`
4. **task** `assign_permission_sets`  `when: project_config.project__custom__agents`
   - `api_names`: `['RLM_QuotingAgent']`

---

### `prepare_analytics`

**Steps:**

1. **task** `enable_analytics_replication`  `when: project_config.project__custom__analytics`

---

### `prepare_approvals`

**Steps:**

1. **task** `deploy_post_approvals`  `when: project_config.project__custom__quantumbit and project_config.project__custom__approvals`
2. **task** `create_approval_email_templates`  `when: project_config.project__custom__quantumbit and project_config.project__custom__approvals`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__quantumbit and project_config.project__custom__approvals`
   - `api_names`: `['RLM_Approvals']`
4. **task** `insert_qb_approvals_data`  `when: project_config.project__custom__quantumbit and project_config.project__custom__approvals`

---

### `prepare_billing`

**Steps:**

1. **task** `insert_billing_data`  `when: project_config.project__custom__billing and not project_config.project__custom__refresh and project_config.project__custom__qb`
2. **task** `insert_q3_billing_data`  `when: project_config.project__custom__billing and not project_config.project__custom__refresh and project_config.project__custom__q3`
3. **task** `activate_flow`  `when: project_config.project__custom__billing`
   - `developer_names`: `RLM_Order_to_Billing_Schedule_Flow`
4. **task** `activate_default_payment_term`  `when: project_config.project__custom__billing`
5. **task** `activate_billing_records`  `when: project_config.project__custom__billing`
6. **task** `deploy_post_billing`  `when: project_config.project__custom__billing`
7. **task** `deploy_billing_id_settings`  `when: project_config.project__custom__billing and project_config.project__custom__qb`
8. **task** `deploy_billing_template_settings`  `when: project_config.project__custom__billing`

---

### `prepare_billing_portal`

Create Self-Service Billing Portal community and optionally deploy site content. When billing_portal is true, creates the community; when billing_portal_deploy is also true, deploys unpackaged/post_billing_portal and publishes.

**Steps:**

1. **task** `create_billing_portal`  `when: project_config.project__custom__billing_portal`
2. **task** `deploy_post_billing_portal`  `when: project_config.project__custom__billing_portal and project_config.project__custom__billing_portal_deploy`
3. **task** `publish_community`  `when: project_config.project__custom__billing_portal`
   - `name`: `Billing Portal`

---

### `prepare_clm`

**Steps:**

1. **task** `insert_clm_data`  `when: project_config.project__custom__clm and project_config.project__custom__clm_data`

---

### `prepare_constraints`

**Steps:**

1. **task** `insert_qb_transactionprocessingtypes_data`  `when: project_config.project__custom__constraints`
2. **task** `deploy_post_constraints`  `when: project_config.project__custom__constraints`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__tso and project_config.project__custom__constraints`
   - `api_names`: `['RLM_Constraints']`
4. **task** `apply_context_constraint_engine_node_status`  `when: project_config.project__custom__constraints`
5. **task** `enable_constraints_settings`  `when: project_config.project__custom__constraints`
6. **task** `validate_cml`  `when: project_config.project__custom__constraints_data and project_config.project__custom__qb`
   - `cml_dir`: `scripts/cml`
   - `data_dir`: `datasets/constraints/qb/QuantumBitComplete`
7. **task** `import_cml`  `when: project_config.project__custom__constraints_data and project_config.project__custom__qb`
   - `data_dir`: `datasets/constraints/qb/QuantumBitComplete`
   - `dataset_dirs`: `datasets/sfdmu/qb/en-US/qb-pcm`
8. **task** `import_cml`  `when: project_config.project__custom__constraints_data and project_config.project__custom__qb`
   - `data_dir`: `datasets/constraints/qb/Server2`
   - `dataset_dirs`: `datasets/sfdmu/qb/en-US/qb-pcm`
9. **task** `manage_expression_sets`  `when: project_config.project__custom__constraints_data and project_config.project__custom__qb`
   - `operation`: `activate_versions`
   - `version_full_names`: `QuantumBitComplete_V1,Server2_V1`

---

### `prepare_core`

**Steps:**

1. **task** `validate_setup`
2. **task** `assign_permission_set_licenses`
   - `api_names`: `['BREDesigner', 'BRERuntime', 'CorePricingDesignTime', 'DataProcessingEnginePsl', 'DecimalQuantit...`
3. **task** `cleanup_settings_for_dev`
4. **task** `exclude_active_decision_tables`
5. **task** `deploy_pre`
6. **task** `restore_decision_tables`
7. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__clm`
   - `api_names`: `['AIAcceleratorPsl', 'ClauseManagementUser', 'CLMAnalyticsPsl', 'ContractManagementUser', 'Contra...`
8. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__einstein`
   - `api_names`: `['AgentforceServiceAgentBuilderPsl', 'EinsteinGPTCopilotPsl', 'EinsteinGPTPromptTemplatesPsl']`
9. **task** `util_sleep`
   - `seconds`: `30`
10. **task** `assign_permission_set_licenses`
   - `api_names`: `EinsteinAnalyticsPlusPsl`
11. **task** `recalculate_permission_set_groups`
   - `api_names`: `['RLM_QB_AI', 'RLM_RCB', 'RLM_RMI', 'RLM_CFG', 'RLM_CLM', 'RLM_DOC', 'RLM_DRO', 'RLM_NGP', 'RLM_P...`
12. **task** `assign_permission_set_groups_tolerant`
   - `api_names`: `['RLM_QB_AI', 'RLM_RCB', 'RLM_RMI', 'RLM_CFG', 'RLM_CLM', 'RLM_DOC', 'RLM_DRO', 'RLM_NGP', 'RLM_P...`
13. **task** `assign_permission_sets`  `when: project_config.project__custom__tso and project_config.project__custom__psg_debug`
   - `api_names`: `['IndustriesConfiguratorPlatformApi', 'ProductConfigurationRulesDesigner', 'ProductCatalogManagem...`
14. **flow** `extend_context_definitions`
15. **task** `util_sleep`
   - `seconds`: `30`
16. **task** `create_rule_library`  `when: project_config.project__custom__breconfig`
17. **task** `util_sleep`  `when: project_config.project__custom__breconfig`
   - `seconds`: `30`
18. **task** `create_dro_rule_library`  `when: project_config.project__custom__dro and project_config.project__custom__breconfig`
19. **task** `assign_permission_sets`  `when: project_config.project__custom__einstein`
   - `api_names`: `['EinsteinGPTPromptTemplateManager', 'SalesCloudEinsteinAll']`
20. **task** `assign_permission_sets`  `when: project_config.project__custom__billing and project_config.project__custom__psg_debug`
   - `api_names`: `['AnalyticsStoreUser', 'RevenueLifecycleManagementAccountingAdmin', 'RevenueLifecycleManagementBi...`

---

### `prepare_decision_tables`

**Steps:**

1. **task** `activate_decision_tables`

---

### `prepare_docgen`

**Steps:**

1. **task** `create_docgen_library`  `when: project_config.project__custom__docgen`
2. **task** `enable_document_builder_toggle`  `when: project_config.project__custom__docgen`
3. **task** `deploy_docgen_seller_fields`  `when: project_config.project__custom__docgen`
4. **task** `deploy_docgen_qli_fields`  `when: project_config.project__custom__docgen`
5. **task** `deploy_docgen_odt_seed`  `when: project_config.project__custom__docgen`
6. **task** `deploy_post_docgen`  `when: project_config.project__custom__docgen`
7. **task** `activate_docgen_templates`  `when: project_config.project__custom__docgen`
8. **task** `fix_document_template_binaries`  `when: project_config.project__custom__docgen`
9. **task** `apply_context_docgen`  `when: project_config.project__custom__docgen`
10. **task** `assign_permission_sets`  `when: project_config.project__custom__docgen`
   - `api_names`: `['RLM_DocGen']`

---

### `prepare_dro`

**Steps:**

1. **task** `insert_qb_dro_data`  `when: project_config.project__custom__dro and project_config.project__custom__qb`
2. **task** `insert_q3_dro_data_scratch`  `when: org_config.scratch and project_config.project__custom__dro and project_config.project__custom__q3`
3. **task** `insert_q3_dro_data_prod`  `when: not org_config.scratch and project_config.project__custom__dro and project_config.project__custom__q3`
4. **task** `update_product_fulfillment_decomp_rules`  `when: project_config.project__custom__dro`

---

### `prepare_expression_sets`

**Steps:**

1. **task** `deactivate_expression_sets`
2. **task** `ensure_pricing_schedules`
3. **task** `deploy_expression_sets`

---

### `prepare_guidedselling`

**Steps:**

1. **task** `insert_qb_guidedselling_data`  `when: project_config.project__custom__guidedselling and project_config.project__custom__qb`
2. **task** `deploy_post_guidedselling`  `when: project_config.project__custom__guidedselling`

---

### `prepare_payments`

**Steps:**

1. **task** `create_payments_webhook`  `when: project_config.project__custom__payments`
2. **task** `patch_payments_site_for_deploy`  `when: project_config.project__custom__payments`
3. **task** `deploy_post_payments_site`  `when: project_config.project__custom__payments`
4. **task** `revert_payments_site_after_deploy`  `when: project_config.project__custom__payments`
5. **task** `publish_community`  `when: project_config.project__custom__payments`
   - `name`: `Payments Webhook`
6. **task** `deploy_post_payments_settings`  `when: project_config.project__custom__payments`

---

### `prepare_personas`

Deploy persona metadata (profiles, permission set groups, permission sets) from unpackaged/post_personas. Not wired into prepare_rlm_org.

**Steps:**

1. **task** `deploy_post_personas`

---

### `prepare_price_adjustment_schedules`

**Steps:**

1. **task** `activate_price_adjustment_schedules`

---

### `prepare_pricing_data`

**Steps:**

1. **task** `delete_quantumbit_pricing_data`  `when: project_config.project__custom__qb`
2. **task** `insert_quantumbit_pricing_data`  `when: project_config.project__custom__qb`

---

### `prepare_pricing_discovery`

**Steps:**

1. **task** `reconfigure_pricing_discovery`
2. **task** `configure_product_discovery_settings`  `when: project_config.project__custom__qb`

---

### `prepare_prm`

**Steps:**

1. **task** `create_partner_central`  `when: project_config.project__custom__prm`
2. **task** `patch_network_email_for_deploy`  `when: project_config.project__custom__prm and project_config.project__custom__prm_exp_bundle and project_config.project__custom__tso`
3. **task** `deploy_post_prm`  `when: project_config.project__custom__prm and project_config.project__custom__prm_exp_bundle and project_config.project__custom__tso`
5. **task** `revert_network_email_after_deploy`  `when: project_config.project__custom__prm and project_config.project__custom__prm_exp_bundle and project_config.project__custom__tso`
6. **task** `publish_community`  `when: project_config.project__custom__prm`
   - `name`: `rlm`
7. **task** `deploy_sharing_rules`  `when: project_config.project__custom__prm and project_config.project__custom__sharingsettings`
8. **task** `assign_permission_sets`  `when: project_config.project__custom__prm and project_config.project__custom__prm_exp_bundle and project_config.project__custom__tso`
   - `api_names`: `['RLM_PRM']`
9. **task** `insert_quantumbit_prm_data`  `when: project_config.project__custom__prm and project_config.project__custom__qb`
10. **task** `manage_context_definition`  `when: project_config.project__custom__prm`
   - `plan_file`: `datasets/context_plans/PartnerAccount/manifest.json`
   - `developer_name`: `RLM_SalesTransactionContext`
   - `translate_plan`: `True`
   - `activate`: `True`

---

### `prepare_procedureplans`

**Steps:**

1. **task** `deploy_post_procedureplans`  `when: project_config.project__custom__procedureplans`
2. **task** `activate_procedure_plan_expression_sets`  `when: project_config.project__custom__procedureplans`
3. **task** `create_procedure_plan_definition`  `when: project_config.project__custom__procedureplans`
4. **task** `insert_procedure_plan_data`  `when: project_config.project__custom__procedureplans`
5. **task** `activate_procedure_plan_version`  `when: project_config.project__custom__procedureplans`

---

### `prepare_product_data`

**Steps:**

1. **task** `insert_quantumbit_pcm_data`  `when: project_config.project__custom__qb`
2. **task** `insert_q3_data`  `when: project_config.project__custom__q3`
3. **task** `insert_quantumbit_product_image_data`  `when: project_config.project__custom__qb`

---

### `prepare_quantumbit`

**Steps:**

1. **task** `deploy_post_utils`  `when: project_config.project__custom__quantumbit`
2. **flow** `prepare_approvals`
3. **task** `deploy_quantumbit`  `when: project_config.project__custom__quantumbit`
4. **task** `assign_permission_sets`  `when: project_config.project__custom__quantumbit`
   - `api_names`: `['RLM_QuantumBit']`
5. **task** `assign_permission_sets`  `when: project_config.project__custom__quantumbit and project_config.project__custom__calmdelete`
   - `api_names`: `['RLM_CALM_SObject_Access']`

---

### `prepare_ramp_builder`

Deploy Create Ramp Schedule V4 feature into the target org. Deploys QuoteLineGroup custom fields, Lightning Message Channel, all Apex classes, six LWC bundles, the RLM_Create_Ramp_Schedule_V4 screen flow, and the Quote quick action in dependency order. Adds RampMode__c/GroupRampMode__c context attributes to the Sales Transaction context definition mapped to QuoteLineItem, QuoteLineGroup, OrderItem, and OrderItemGroup. After this flow runs, add the "Create Ramp Schedule" action to the Quote page layout (or Dynamic Actions highlights panel) and ensure the flow is Active in Setup.

**Steps:**

1. **task** `deploy_post_ramp_builder`  `when: project_config.project__custom__ramps`
2. **task** `apply_context_ramp_mode`  `when: project_config.project__custom__ramps`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__ramps`
   - `api_names`: `['RLM_RampSchedule']`

---

### `prepare_rating`

**Steps:**

1. **task** `delete_qb_rates_data`  `when: project_config.project__custom__rating and project_config.project__custom__rates and project_config.project__custom__qb and not project_config.project__custom__refresh`
2. **task** `delete_qb_rating_data`  `when: project_config.project__custom__rating and project_config.project__custom__qb and not project_config.project__custom__refresh`
3. **task** `insert_qb_rating_data`  `when: project_config.project__custom__rating and not project_config.project__custom__refresh and project_config.project__custom__qb`
4. **task** `insert_q3_rating_data`  `when: project_config.project__custom__rating and not project_config.project__custom__refresh and project_config.project__custom__q3`
5. **task** `insert_qb_rates_data`  `when: project_config.project__custom__rating and project_config.project__custom__rates and not project_config.project__custom__refresh and project_config.project__custom__qb`
6. **task** `insert_q3_rates_data`  `when: project_config.project__custom__rating and project_config.project__custom__rates and not project_config.project__custom__refresh and project_config.project__custom__q3`
7. **task** `activate_rating_records`  `when: project_config.project__custom__rating and project_config.project__custom__rates`
8. **task** `activate_rates`  `when: project_config.project__custom__rating and project_config.project__custom__rates`

---

### `prepare_revenue_settings`

**Steps:**

1. **task** `configure_revenue_settings`  `when: not (project_config.project__custom__quantumbit or project_config.project__custom__tso)`
2. **task** `configure_revenue_settings`  `when: project_config.project__custom__quantumbit or project_config.project__custom__tso`
   - `manage_assets_flow`: `RLM_ARC_Assets`
3. **task** `configure_core_pricing_setup`

---

### `prepare_rlm_org`

**Steps:**

1. **flow** `prepare_core`
2. **flow** `prepare_decision_tables`
3. **flow** `prepare_expression_sets`
4. **flow** `prepare_payments`
5. **task** `deploy_full`
6. **flow** `prepare_price_adjustment_schedules`
7. **flow** `prepare_scratch`
8. **flow** `prepare_payments`
9. **flow** `prepare_quantumbit`
10. **flow** `prepare_product_data`
11. **flow** `prepare_pricing_data`
12. **flow** `prepare_docgen`
13. **flow** `prepare_dro`
14. **flow** `prepare_tax`
15. **flow** `prepare_billing`
16. **flow** `prepare_analytics`
17. **flow** `prepare_clm`
18. **flow** `prepare_rating`
19. **task** `activate_and_deploy_expression_sets`
20. **flow** `prepare_tso`
21. **flow** `prepare_procedureplans`
22. **flow** `prepare_prm`
23. **flow** `prepare_agents`
24. **flow** `prepare_constraints`
25. **flow** `prepare_guidedselling`
26. **flow** `prepare_revenue_settings`
27. **flow** `prepare_pricing_discovery`
28. **flow** `prepare_ramp_builder`
29. **flow** `prepare_ux`  `when: project_config.project__custom__ux`
30. **flow** `prepare_manufacturing`  `when: project_config.project__custom__manufacturing`
31. **flow** `refresh_all_decision_tables`
32. **task** `stamp_git_commit`
   - `flow_name`: `prepare_rlm_org`

---

### `prepare_scratch`

**Steps:**

1. **task** `insert_scratch_data`  `when: org_config.scratch and not project_config.project__custom__tso`

---

### `prepare_tax`

**Steps:**

1. **task** `create_tax_engine`  `when: project_config.project__custom__tax`
2. **task** `insert_tax_data`  `when: project_config.project__custom__tax and not project_config.project__custom__refresh and project_config.project__custom__qb`
3. **task** `insert_q3_tax_data`  `when: project_config.project__custom__tax and not project_config.project__custom__refresh and project_config.project__custom__q3`
4. **task** `activate_tax_records`  `when: project_config.project__custom__tax`

---

### `prepare_tso`

**Steps:**

1. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__tso`
   - `api_names`: `['AutomatedActionsPsl', 'EinsteinAgentCWUPsl', 'EinsteinAgentPsl', 'EinsteinCopilotReviewMyDayPsl...`
2. **task** `assign_permission_set_groups`  `when: project_config.project__custom__tso`
   - `api_names`: `['CopilotSalesforceUserPSG', 'CopilotSalesforceAdminPSG', 'UnifiedCatalogAdminPsl', 'UnifiedCatal...`
3. **task** `deploy_post_utils`  `when: project_config.project__custom__tso`
4. **task** `deploy_post_tso`  `when: project_config.project__custom__tso`
5. **task** `assign_permission_sets`  `when: project_config.project__custom__tso`
   - `api_names`: `['ERIBasic', 'RLM_UtilitiesPermset', 'OrchestrationProcessManagerPermissionSet', 'EventMonitoring...`
6. **task** `assign_permission_set_groups_tolerant`  `when: project_config.project__custom__tso`
   - `api_names`: `['RLM_TSO']`

---

### `refresh_all_decision_tables`

**Steps:**

1. **task** `sync_pricing_data`
2. **task** `refresh_dt_pricing_discovery`
3. **task** `refresh_dt_asset`  `when: project_config.project__custom__rating`
4. **task** `refresh_dt_rating`  `when: project_config.project__custom__rating`
5. **task** `refresh_dt_rating_discovery`  `when: project_config.project__custom__rating`
6. **task** `refresh_dt_commerce`  `when: project_config.project__custom__commerce`

---

## UX Personalization

### `prepare_ux`

Assemble and deploy all project UX personalization metadata (flexipages, layouts, applications, app menus, profiles) from feature-conditional templates. Runs at step 29 of prepare_rlm_org, after all feature provisioning is complete, ensuring all referenced objects, fields, and components exist before UX metadata is deployed. Step 2 reorders the App Launcher via browser automation — required on Trialforce orgs where the Metadata API AppSwitcher deploy is blocked by managed ConnectedApps.

**Steps:**

1. **task** `assemble_and_deploy_ux`  `when: project_config.project__custom__ux`
2. **task** `reorder_app_launcher`  `when: project_config.project__custom__ux`

---
