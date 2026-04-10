# CCI Flows Reference

> **Auto-generated** by `scripts/ai/generate_cci_reference.py` from `cumulusci.yml`.  
> Do not edit manually — re-run the script after changing `cumulusci.yml`.

**42 flows** across **5 groups**.

---

## Data Management - Extract

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

## RLM Administration

### `stamp_git_commit`

Stamp the git commit hash into the org

**Steps:**

1. **task** `stamp_git_commit`
   - `flow_name`: `prepare_rlm_org`

---

## Revenue Lifecycle Management

### `assign_feature_permission_sets`

Assign feature-gated permission sets after PSGs are updated

**Steps:**

1. **task** `assign_permission_sets`  `when: project_config.project__custom__tso and project_config.project__custom__psg_debug`
   - `api_names`: `['IndustriesConfiguratorPlatformApi', 'ProductConfigurationRulesDesigner', 'ProductCatalogManagem...`
2. **task** `assign_permission_sets`  `when: project_config.project__custom__einstein`
   - `api_names`: `['EinsteinGPTPromptTemplateManager']`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__einstein and not (project_config.project__custom__dev_ed or org_config.name in ["dev", "dev-sb0", "dev-r1"])`
   - `api_names`: `['SalesCloudEinsteinAll']`
4. **task** `assign_permission_sets`  `when: project_config.project__custom__billing and project_config.project__custom__psg_debug`
   - `api_names`: `['AnalyticsStoreUser', 'RevenueLifecycleManagementAccountingAdmin', 'RevenueLifecycleManagementBi...`

---

### `assign_feature_psls`

Assign feature-gated permission set licenses after pre-deploy metadata is in place

**Steps:**

1. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__clm`
   - `api_names`: `['AIAcceleratorPsl', 'ClauseManagementUser', 'CLMAnalyticsPsl', 'ContractManagementUser', 'Contra...`
2. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__einstein`
   - `api_names`: `['AgentforceServiceAgentBuilderPsl', 'EinsteinGPTCopilotPsl', 'EinsteinGPTPromptTemplatesPsl']`
3. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__analytics`
   - `api_names`: `['EinsteinAnalyticsPlusPsl']`
4. **task** `assign_permission_set_licenses`  `when: project_config.project__custom__tso`
   - `api_names`: `['AutomatedActionsPsl', 'EinsteinAgentCWUPsl', 'EinsteinAgentPsl', 'EinsteinCopilotReviewMyDayPsl...`

---

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
4. **task** `insert_qb_approvals_data`  `when: project_config.project__custom__qb and project_config.project__custom__approvals`

---

### `prepare_billing`

**Steps:**

1. **task** `deploy_post_billing`  `when: project_config.project__custom__billing`
2. **task** `insert_billing_data`  `when: project_config.project__custom__billing and not project_config.project__custom__refresh and project_config.project__custom__qb`
3. **task** `insert_q3_billing_data`  `when: project_config.project__custom__billing and not project_config.project__custom__refresh and project_config.project__custom__q3`
4. **task** `create_sequence_policies`  `when: project_config.project__custom__billing and not project_config.project__custom__refresh and project_config.project__custom__qb`
5. **task** `activate_flow`  `when: project_config.project__custom__billing`
   - `developer_names`: `RLM_Order_to_Billing_Schedule_Flow`
6. **task** `activate_default_payment_term`  `when: project_config.project__custom__billing`
7. **task** `activate_billing_records`  `when: project_config.project__custom__billing`
8. **task** `enable_timeline`  `when: project_config.project__custom__billing_ui`
9. **task** `deploy_billing_id_settings`  `when: project_config.project__custom__billing`
10. **task** `deploy_billing_template_settings`  `when: project_config.project__custom__billing`
11. **task** `deploy_post_billing_ui`  `when: project_config.project__custom__billing_ui`
12. **task** `assign_permission_sets`  `when: project_config.project__custom__billing_ui`
   - `api_names`: `['RLM_BillingUI']`
13. **task** `apply_context_billing_order`  `when: project_config.project__custom__billing and project_config.project__custom__billing_ui`

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

1. **task** `insert_qb_transactionprocessingtypes_data`  `when: project_config.project__custom__constraints and project_config.project__custom__quantumbit`
2. **task** `deploy_post_constraints`  `when: project_config.project__custom__constraints`
3. **task** `assign_permission_sets`  `when: project_config.project__custom__constraints`
   - `api_names`: `['RLM_Constraints']`
4. **task** `apply_context_constraint_engine_node_status`  `when: project_config.project__custom__constraints`
5. **task** `enable_constraints_settings`  `when: project_config.project__custom__constraints_data`
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
7. **flow** `assign_feature_psls`
8. **task** `recalculate_permission_set_groups`
   - `api_names`: `['RLM_QB_AI', 'RLM_RCB', 'RLM_RMI', 'RLM_CFG', 'RLM_CLM', 'RLM_DOC', 'RLM_DRO', 'RLM_NGP', 'RLM_P...`
9. **task** `assign_permission_set_groups_tolerant`
   - `api_names`: `['RLM_QB_AI', 'RLM_RCB', 'RLM_RMI', 'RLM_CFG', 'RLM_CLM', 'RLM_DOC', 'RLM_DRO', 'RLM_NGP', 'RLM_P...`
10. **task** `recalculate_permission_set_groups`  `when: project_config.project__custom__tso`
   - `api_names`: `['RLM_TSO']`
11. **task** `assign_permission_set_groups_tolerant`  `when: project_config.project__custom__tso`
   - `api_names`: `['RLM_TSO']`
12. **flow** `extend_context_definitions`
13. **task** `create_rule_library`  `when: project_config.project__custom__breconfig`
14. **task** `create_dro_rule_library`  `when: project_config.project__custom__dro and project_config.project__custom__breconfig`
15. **flow** `assign_feature_permission_sets`

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

1. **task** `manage_fulfillment_scope_cnfg`  `when: project_config.project__custom__dro`
   - `operation`: `upsert`
   - `input_file`: `datasets/tooling/CustomFulfillmentScopeCnfg.json`
2. **task** `insert_qb_dro_data`  `when: project_config.project__custom__dro and project_config.project__custom__qb`
3. **task** `insert_q3_dro_data_scratch`  `when: org_config.scratch and project_config.project__custom__dro and project_config.project__custom__q3`
4. **task** `insert_q3_dro_data_prod`  `when: not org_config.scratch and project_config.project__custom__dro and project_config.project__custom__q3`
5. **task** `update_product_fulfillment_decomp_rules`  `when: project_config.project__custom__dro`

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

### `prepare_large_stx`

**Steps:**

1. **task** `deploy_post_large_stx`  `when: project_config.project__custom__large_stx`

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

Deploy persona metadata (profiles, permission set groups, permission sets) from unpackaged/post_personas and create the Sales Rep scratch user. Gated by the personas feature flag. Wired into `prepare_rlm_org` at step 28, before `prepare_ux`.

**Steps:**

1. **task** `deploy_post_personas`  `when: project_config.project__custom__personas`
2. **task** `create_personas_sales_rep_user`  `when: project_config.project__custom__personas`

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

---

### `prepare_rlm_org`

**Steps:**

1. **flow** `prepare_core`
2. **flow** `prepare_decision_tables`
3. **flow** `prepare_expression_sets`
4. **flow** `prepare_payments`
5. **task** `deploy_full`
6. **flow** `prepare_price_adjustment_schedules`
7. **flow** `prepare_quantumbit`
8. **flow** `prepare_product_data`
9. **flow** `prepare_pricing_data`
10. **flow** `prepare_docgen`
11. **flow** `prepare_dro`
12. **flow** `prepare_tax`
13. **flow** `prepare_billing`
14. **flow** `prepare_analytics`
15. **flow** `prepare_clm`
16. **flow** `prepare_rating`
17. **task** `activate_and_deploy_expression_sets`
18. **flow** `prepare_tso`
19. **flow** `prepare_procedureplans`
20. **flow** `prepare_prm`
21. **flow** `prepare_agents`
22. **flow** `prepare_constraints`
23. **flow** `prepare_guidedselling`
24. **flow** `prepare_revenue_settings`
25. **flow** `prepare_pricing_discovery`
26. **flow** `prepare_ramp_builder`
27. **flow** `prepare_large_stx`  `when: project_config.project__custom__large_stx`
28. **flow** `prepare_personas`  `when: project_config.project__custom__personas`
29. **flow** `prepare_ux`  `when: project_config.project__custom__ux`
30. **flow** `prepare_scratch`
31. **flow** `refresh_all_decision_tables`
32. **flow** `stamp_git_commit`

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

1. **task** `assign_permission_set_groups`  `when: project_config.project__custom__tso`
   - `api_names`: `['CopilotSalesforceUserPSG', 'CopilotSalesforceAdminPSG', 'UnifiedCatalogAdminPsl', 'UnifiedCatal...`
2. **task** `deploy_post_utils`  `when: project_config.project__custom__tso`
3. **task** `deploy_post_tso`  `when: project_config.project__custom__tso`
4. **task** `assign_permission_sets`  `when: project_config.project__custom__tso`
   - `api_names`: `['ERIBasic', 'RLM_UtilitiesPermset', 'OrchestrationProcessManagerPermissionSet', 'EventMonitoring...`

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

### `upsert_fulfillment_scope_cnfg`

Upsert CustomFulfillmentScopeCnfg records from the standard input file. Run manually via 'cci flow run upsert_fulfillment_scope_cnfg --org <alias>'.

**Steps:**

1. **task** `manage_fulfillment_scope_cnfg`
   - `operation`: `upsert`
   - `input_file`: `datasets/tooling/CustomFulfillmentScopeCnfg.json`

---

## UX Personalization

### `apply_ux_drift`

Writes back org-retrieved flexipages into base templates by reverse-applying active feature patches (new_base = org_state - patches), then re-assembles and diffs to verify zero drift. Run capture_ux_drift first to review drift, then run this flow to update templates/ automatically.

**Steps:**

1. **task** `writeback_ux_templates`
   - `dry_run`: `False`
2. **task** `assemble_and_deploy_ux`
   - `deploy`: `False`
3. **task** `diff_ux_templates`

---

### `capture_ux_drift`

Retrieves live flexipages from the target org into unpackaged/post_ux/, then diffs them against what the assembler would produce from current templates/. Reports added, removed, modified, and repositioned flexiPageRegions and writes drift_report.json. Does not modify templates/. After reviewing the report, edit templates/ manually then run assemble_and_deploy_ux to deploy.

**Steps:**

1. **task** `retrieve_ux_from_org`
2. **task** `diff_ux_templates`

---

### `prepare_ux`

Assemble and deploy all project UX personalization metadata (flexipages, layouts, applications, profiles) from feature-conditional templates. Runs at step 29 of prepare_rlm_org, after all feature provisioning is complete, ensuring all referenced objects, fields, and components exist before UX metadata is deployed. Step 2 reorders the App Launcher via browser automation.

**Steps:**

1. **task** `assemble_and_deploy_ux`  `when: project_config.project__custom__ux`
2. **task** `reorder_app_launcher`  `when: project_config.project__custom__ux`

---
