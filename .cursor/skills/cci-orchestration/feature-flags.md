# CCI Feature Flags Reference

> **Auto-generated** by `scripts/ai/generate_cci_reference.py` from `cumulusci.yml`.  
> Do not edit manually — re-run the script after changing `cumulusci.yml`.

**39 feature flags**, **89 configuration values**, **33 YAML anchors** under `project.custom`.

---

## Feature Flags

Boolean flags that gate task/flow execution via `when:` clauses.

| Flag | Default | Used in `when:` clauses |
|------|---------|------------------------|
| `agents` | `False` | 4 flow step(s) |
| `analytics` | `True` | 1 flow step(s) |
| `approvals` | `True` | 4 flow step(s) |
| `badger` | `True` | 41 flow step(s) |
| `badger_data` | `True` | — |
| `billing` | `True` | 21 flow step(s) |
| `billing_portal` | `False` | 3 flow step(s) |
| `billing_portal_deploy` | `True` | 1 flow step(s) |
| `breconfig` | `False` | 3 flow step(s) |
| `calmdelete` | `True` | 1 flow step(s) |
| `clm` | `False` | 4 flow step(s) |
| `clm_data` | `False` | 1 flow step(s) |
| `commerce` | `False` | 2 flow step(s) |
| `constraints` | `True` | 9 flow step(s) |
| `constraints_data` | `False` | 4 flow step(s) |
| `docgen` | `True` | 10 flow step(s) |
| `dro` | `True` | 7 flow step(s) |
| `einstein` | `False` | 2 flow step(s) |
| `guidedselling` | `False` | 4 flow step(s) |
| `mfg_aaf` | `True` | 7 flow step(s) |
| `mfg_rebates` | `True` | 2 flow step(s) |
| `mfg_visuals` | `True` | 3 flow step(s) |
| `payments` | `True` | 6 flow step(s) |
| `prm` | `True` | 9 flow step(s) |
| `prm_exp_bundle` | `True` | 4 flow step(s) |
| `procedure_plan_definition_version_active` | `False` | — |
| `procedureplans` | `False` | 5 flow step(s) |
| `q3` | `False` | 7 flow step(s) |
| `qb` | `False` | 19 flow step(s) |
| `qbrix` | `False` | — |
| `quantumbit` | `True` | 10 flow step(s) |
| `ramps` | `True` | 3 flow step(s) |
| `rates` | `True` | 5 flow step(s) |
| `rating` | `True` | 13 flow step(s) |
| `refresh` | `False` | 10 flow step(s) |
| `sharingsettings` | `False` | 1 flow step(s) |
| `tax` | `True` | 7 flow step(s) |
| `tso` | `False` | 16 flow step(s) |
| `ux` | `True` | 4 flow step(s) |

---

## Flag Usage Detail

### `agents` (default: `False`)

- `prepare_agents` step 1 → `assign_permission_set_groups`
- `prepare_agents` step 2 → `deploy_agents_settings`
- `prepare_agents` step 3 → `deploy_agents`
- `prepare_agents` step 4 → `assign_permission_sets`

### `analytics` (default: `True`)

- `prepare_analytics` step 1 → `enable_analytics_replication`

### `approvals` (default: `True`)

- `prepare_approvals` step 1 → `deploy_post_approvals`
- `prepare_approvals` step 2 → `create_approval_email_templates`
- `prepare_approvals` step 3 → `assign_permission_sets`
- `prepare_approvals` step 4 → `insert_qb_approvals_data`

### `badger` (default: `True`)

- `prepare_rlm_org` step 30 → `prepare_manufacturing`
- `prepare_manufacturing` step 8 → `update_product_fulfillment_decomp_rules`
- `prepare_manufacturing` step 9 → `reconfigure_mfg_pricing_discovery`
- `prepare_manufacturing` step 15 → `configure_mfg_revenue_settings`
- `prepare_manufacturing` step 17 → `activate_mfg_theme`
- `prepare_mfg_perms` step 2 → `assign_permission_sets`
- `prepare_mfg_perms` step 3 → `assign_permission_set_groups`
- `prepare_mfg_perms` step 4 → `assign_permission_set_groups`
- `prepare_mfg_docgen` step 1 → `deploy_mfg_omni_datatransforms`
- `prepare_mfg_docgen` step 2 → `deploy_mfg_omni_integration_procedures`
- `prepare_mfg_docgen` step 3 → `deploy_mfg_omni_base_docgen_script`
- `prepare_mfg_docgen` step 4 → `deploy_mfg_omni_quote_script`
- `prepare_mfg_docgen` step 5 → `deploy_mfg_doc_templates`
- `prepare_mfg_data` step 1 → `insert_badger_pcm_data`
- `prepare_mfg_data` step 2 → `insert_badger_pricing_data`
- `prepare_mfg_data` step 3 → `insert_badger_dro_data`
- `prepare_mfg_data` step 4 → `import_mfg_cml`
- `prepare_mfg_data` step 5 → `prepare_mfg_tax`
- `prepare_mfg_data` step 6 → `prepare_mfg_billing`
- `prepare_mfg_context_plan` step 1 → `extend_context_sales_transaction_mfg`
- `prepare_mfg_context_plan` step 2 → `apply_mfg_SalesTransactionContext`
- `prepare_mfg_context_plan` step 3 → `apply_mfg_SalesTransactionContext`
- `prepare_mfg_pricing` step 1 → `deploy_mfg_pricing_recipe`
- `prepare_mfg_pricing` step 2 → `deploy_mfg_pricing_procedure`
- `prepare_mfg_pricing` step 3 → `manage_expression_sets`
- `import_mfg_cml` step 1 → `import_cml`
- `import_mfg_cml` step 2 → `import_cml`
- `import_mfg_cml` step 3 → `manage_expression_sets`
- `prepare_mfg_dro` step 1 → `insert_badger_dro_data`
- `prepare_mfg_dro` step 2 → `update_product_fulfillment_decomp_rules`
- `prepare_mfg_guided_selling` step 1 → `insert_badger_guidedselling_data`
- `prepare_mfg_guided_selling` step 2 → `deploy_mfg_guided_selling`
- `prepare_mfg_rebates` step 1 → `deploy_mfg_rebates`
- `prepare_mfg_rebates` step 2 → `insert_badger_rebates_data`
- `prepare_mfg_aaf` step 1 → `deploy_mfg_aaf_fields`
- `prepare_mfg_aaf` step 2 → `deploy_mfg_aaf_permissions`
- `prepare_mfg_aaf` step 3 → `assign_permission_sets`
- `prepare_mfg_aaf` step 4 → `util_sleep`
- `prepare_mfg_aaf` step 5 → `deploy_mfg_aaf_dim_source`
- `prepare_mfg_aaf` step 6 → `deploy_mfg_aaf_forecast_set`
- `prepare_mfg_aaf` step 7 → `insert_badger_aaf_data`

### `billing` (default: `True`)

- `prepare_core` step 20 → `assign_permission_sets`
- `extend_context_definitions` step 4 → `extend_context_billing`
- `extend_context_definitions` step 5 → `extend_context_collection_plan_segment`
- `prepare_billing` step 1 → `insert_billing_data`
- `prepare_billing` step 2 → `insert_q3_billing_data`
- `prepare_billing` step 3 → `activate_flow`
- `prepare_billing` step 4 → `activate_default_payment_term`
- `prepare_billing` step 5 → `activate_billing_records`
- `prepare_billing` step 6 → `deploy_post_billing`
- `prepare_billing` step 7 → `deploy_billing_id_settings`
- `prepare_billing` step 8 → `deploy_billing_template_settings`
- `prepare_billing_portal` step 1 → `create_billing_portal`
- `prepare_billing_portal` step 2 → `deploy_post_billing_portal`
- `prepare_billing_portal` step 3 → `publish_community`
- `prepare_mfg_data` step 6 → `prepare_mfg_billing`
- `prepare_mfg_billing` step 1 → `insert_mfg_billing_data`
- `prepare_mfg_billing` step 2 → `activate_flow`
- `prepare_mfg_billing` step 3 → `activate_default_payment_term`
- `prepare_mfg_billing` step 4 → `activate_billing_records`
- `prepare_mfg_billing` step 5 → `deploy_post_billing`
- `prepare_mfg_billing` step 6 → `deploy_billing_template_settings`

### `billing_portal` (default: `False`)

- `prepare_billing_portal` step 1 → `create_billing_portal`
- `prepare_billing_portal` step 2 → `deploy_post_billing_portal`
- `prepare_billing_portal` step 3 → `publish_community`

### `billing_portal_deploy` (default: `True`)

- `prepare_billing_portal` step 2 → `deploy_post_billing_portal`

### `breconfig` (default: `False`)

- `prepare_core` step 16 → `create_rule_library`
- `prepare_core` step 17 → `util_sleep`
- `prepare_core` step 18 → `create_dro_rule_library`

### `calmdelete` (default: `True`)

- `prepare_quantumbit` step 5 → `assign_permission_sets`

### `clm` (default: `False`)

- `prepare_core` step 7 → `assign_permission_set_licenses`
- `extend_context_definitions` step 7 → `extend_context_contracts`
- `extend_context_definitions` step 8 → `extend_context_contracts_extraction`
- `prepare_clm` step 1 → `insert_clm_data`

### `clm_data` (default: `False`)

- `prepare_clm` step 1 → `insert_clm_data`

### `commerce` (default: `False`)

- `extend_context_definitions` step 3 → `extend_context_cart`
- `refresh_all_decision_tables` step 6 → `refresh_dt_commerce`

### `constraints` (default: `True`)

- `prepare_constraints` step 1 → `insert_qb_transactionprocessingtypes_data`
- `prepare_constraints` step 2 → `deploy_post_constraints`
- `prepare_constraints` step 3 → `assign_permission_sets`
- `prepare_constraints` step 4 → `apply_context_constraint_engine_node_status`
- `prepare_constraints` step 5 → `enable_constraints_settings`
- `prepare_constraints` step 6 → `validate_cml`
- `prepare_constraints` step 7 → `import_cml`
- `prepare_constraints` step 8 → `import_cml`
- `prepare_constraints` step 9 → `manage_expression_sets`

### `constraints_data` (default: `False`)

- `prepare_constraints` step 6 → `validate_cml`
- `prepare_constraints` step 7 → `import_cml`
- `prepare_constraints` step 8 → `import_cml`
- `prepare_constraints` step 9 → `manage_expression_sets`

### `docgen` (default: `True`)

- `prepare_docgen` step 1 → `create_docgen_library`
- `prepare_docgen` step 2 → `enable_document_builder_toggle`
- `prepare_docgen` step 3 → `deploy_docgen_seller_fields`
- `prepare_docgen` step 4 → `deploy_docgen_qli_fields`
- `prepare_docgen` step 5 → `deploy_docgen_odt_seed`
- `prepare_docgen` step 6 → `deploy_post_docgen`
- `prepare_docgen` step 7 → `activate_docgen_templates`
- `prepare_docgen` step 8 → `fix_document_template_binaries`
- `prepare_docgen` step 9 → `apply_context_docgen`
- `prepare_docgen` step 10 → `assign_permission_sets`

### `dro` (default: `True`)

- `prepare_manufacturing` step 8 → `update_product_fulfillment_decomp_rules`
- `prepare_core` step 18 → `create_dro_rule_library`
- `extend_context_definitions` step 6 → `extend_context_fulfillment_asset`
- `prepare_dro` step 1 → `insert_qb_dro_data`
- `prepare_dro` step 2 → `insert_q3_dro_data_scratch`
- `prepare_dro` step 3 → `insert_q3_dro_data_prod`
- `prepare_dro` step 4 → `update_product_fulfillment_decomp_rules`

### `einstein` (default: `False`)

- `prepare_core` step 8 → `assign_permission_set_licenses`
- `prepare_core` step 19 → `assign_permission_sets`

### `guidedselling` (default: `False`)

- `prepare_guidedselling` step 1 → `insert_qb_guidedselling_data`
- `prepare_guidedselling` step 2 → `deploy_post_guidedselling`
- `prepare_mfg_guided_selling` step 1 → `insert_badger_guidedselling_data`
- `prepare_mfg_guided_selling` step 2 → `deploy_mfg_guided_selling`

### `mfg_aaf` (default: `True`)

- `prepare_mfg_aaf` step 1 → `deploy_mfg_aaf_fields`
- `prepare_mfg_aaf` step 2 → `deploy_mfg_aaf_permissions`
- `prepare_mfg_aaf` step 3 → `assign_permission_sets`
- `prepare_mfg_aaf` step 4 → `util_sleep`
- `prepare_mfg_aaf` step 5 → `deploy_mfg_aaf_dim_source`
- `prepare_mfg_aaf` step 6 → `deploy_mfg_aaf_forecast_set`
- `prepare_mfg_aaf` step 7 → `insert_badger_aaf_data`

### `mfg_rebates` (default: `True`)

- `prepare_mfg_rebates` step 1 → `deploy_mfg_rebates`
- `prepare_mfg_rebates` step 2 → `insert_badger_rebates_data`

### `mfg_visuals` (default: `True`)

- `prepare_manufacturing` step 10 → `prepare_mfg_visuals`
- `prepare_mfg_visuals` step 1 → `deploy_mfg_visualization`
- `prepare_mfg_visuals` step 2 → `insert_mfg_configflow_data`

### `payments` (default: `True`)

- `prepare_payments` step 1 → `create_payments_webhook`
- `prepare_payments` step 2 → `patch_payments_site_for_deploy`
- `prepare_payments` step 3 → `deploy_post_payments_site`
- `prepare_payments` step 4 → `revert_payments_site_after_deploy`
- `prepare_payments` step 5 → `publish_community`
- `prepare_payments` step 6 → `deploy_post_payments_settings`

### `prm` (default: `True`)

- `prepare_prm` step 1 → `create_partner_central`
- `prepare_prm` step 2 → `patch_network_email_for_deploy`
- `prepare_prm` step 3 → `deploy_post_prm`
- `prepare_prm` step 5 → `revert_network_email_after_deploy`
- `prepare_prm` step 6 → `publish_community`
- `prepare_prm` step 7 → `deploy_sharing_rules`
- `prepare_prm` step 8 → `assign_permission_sets`
- `prepare_prm` step 9 → `insert_quantumbit_prm_data`
- `prepare_prm` step 10 → `manage_context_definition`

### `prm_exp_bundle` (default: `True`)

- `prepare_prm` step 2 → `patch_network_email_for_deploy`
- `prepare_prm` step 3 → `deploy_post_prm`
- `prepare_prm` step 5 → `revert_network_email_after_deploy`
- `prepare_prm` step 8 → `assign_permission_sets`

### `procedureplans` (default: `False`)

- `prepare_procedureplans` step 1 → `deploy_post_procedureplans`
- `prepare_procedureplans` step 2 → `activate_procedure_plan_expression_sets`
- `prepare_procedureplans` step 3 → `create_procedure_plan_definition`
- `prepare_procedureplans` step 4 → `insert_procedure_plan_data`
- `prepare_procedureplans` step 5 → `activate_procedure_plan_version`

### `q3` (default: `False`)

- `prepare_product_data` step 2 → `insert_q3_data`
- `prepare_dro` step 2 → `insert_q3_dro_data_scratch`
- `prepare_dro` step 3 → `insert_q3_dro_data_prod`
- `prepare_billing` step 2 → `insert_q3_billing_data`
- `prepare_tax` step 3 → `insert_q3_tax_data`
- `prepare_rating` step 4 → `insert_q3_rating_data`
- `prepare_rating` step 6 → `insert_q3_rates_data`

### `qb` (default: `False`)

- `prepare_product_data` step 1 → `insert_quantumbit_pcm_data`
- `prepare_product_data` step 3 → `insert_quantumbit_product_image_data`
- `prepare_pricing_data` step 1 → `delete_quantumbit_pricing_data`
- `prepare_pricing_data` step 2 → `insert_quantumbit_pricing_data`
- `prepare_dro` step 1 → `insert_qb_dro_data`
- `prepare_billing` step 1 → `insert_billing_data`
- `prepare_billing` step 7 → `deploy_billing_id_settings`
- `prepare_prm` step 9 → `insert_quantumbit_prm_data`
- `prepare_tax` step 2 → `insert_tax_data`
- `prepare_rating` step 1 → `delete_qb_rates_data`
- `prepare_rating` step 2 → `delete_qb_rating_data`
- `prepare_rating` step 3 → `insert_qb_rating_data`
- `prepare_rating` step 5 → `insert_qb_rates_data`
- `prepare_constraints` step 6 → `validate_cml`
- `prepare_constraints` step 7 → `import_cml`
- `prepare_constraints` step 8 → `import_cml`
- `prepare_constraints` step 9 → `manage_expression_sets`
- `prepare_guidedselling` step 1 → `insert_qb_guidedselling_data`
- `prepare_pricing_discovery` step 2 → `configure_product_discovery_settings`

### `quantumbit` (default: `True`)

- `prepare_quantumbit` step 1 → `deploy_post_utils`
- `prepare_quantumbit` step 3 → `deploy_quantumbit`
- `prepare_quantumbit` step 4 → `assign_permission_sets`
- `prepare_quantumbit` step 5 → `assign_permission_sets`
- `prepare_approvals` step 1 → `deploy_post_approvals`
- `prepare_approvals` step 2 → `create_approval_email_templates`
- `prepare_approvals` step 3 → `assign_permission_sets`
- `prepare_approvals` step 4 → `insert_qb_approvals_data`
- `prepare_revenue_settings` step 1 → `configure_revenue_settings`
- `prepare_revenue_settings` step 2 → `configure_revenue_settings`

### `ramps` (default: `True`)

- `prepare_ramp_builder` step 1 → `deploy_post_ramp_builder`
- `prepare_ramp_builder` step 2 → `apply_context_ramp_mode`
- `prepare_ramp_builder` step 3 → `assign_permission_sets`

### `rates` (default: `True`)

- `prepare_rating` step 1 → `delete_qb_rates_data`
- `prepare_rating` step 5 → `insert_qb_rates_data`
- `prepare_rating` step 6 → `insert_q3_rates_data`
- `prepare_rating` step 7 → `activate_rating_records`
- `prepare_rating` step 8 → `activate_rates`

### `rating` (default: `True`)

- `extend_context_definitions` step 9 → `extend_context_rate_management`
- `extend_context_definitions` step 10 → `extend_context_rating_discovery`
- `prepare_rating` step 1 → `delete_qb_rates_data`
- `prepare_rating` step 2 → `delete_qb_rating_data`
- `prepare_rating` step 3 → `insert_qb_rating_data`
- `prepare_rating` step 4 → `insert_q3_rating_data`
- `prepare_rating` step 5 → `insert_qb_rates_data`
- `prepare_rating` step 6 → `insert_q3_rates_data`
- `prepare_rating` step 7 → `activate_rating_records`
- `prepare_rating` step 8 → `activate_rates`
- `refresh_all_decision_tables` step 3 → `refresh_dt_asset`
- `refresh_all_decision_tables` step 4 → `refresh_dt_rating`
- `refresh_all_decision_tables` step 5 → `refresh_dt_rating_discovery`

### `refresh` (default: `False`)

- `prepare_billing` step 1 → `insert_billing_data`
- `prepare_billing` step 2 → `insert_q3_billing_data`
- `prepare_tax` step 2 → `insert_tax_data`
- `prepare_tax` step 3 → `insert_q3_tax_data`
- `prepare_rating` step 1 → `delete_qb_rates_data`
- `prepare_rating` step 2 → `delete_qb_rating_data`
- `prepare_rating` step 3 → `insert_qb_rating_data`
- `prepare_rating` step 4 → `insert_q3_rating_data`
- `prepare_rating` step 5 → `insert_qb_rates_data`
- `prepare_rating` step 6 → `insert_q3_rates_data`

### `sharingsettings` (default: `False`)

- `prepare_prm` step 7 → `deploy_sharing_rules`

### `tax` (default: `True`)

- `prepare_tax` step 1 → `create_tax_engine`
- `prepare_tax` step 2 → `insert_tax_data`
- `prepare_tax` step 3 → `insert_q3_tax_data`
- `prepare_tax` step 4 → `activate_tax_records`
- `prepare_mfg_data` step 5 → `prepare_mfg_tax`
- `prepare_mfg_tax` step 1 → `insert_mfg_tax_data`
- `prepare_mfg_tax` step 2 → `activate_tax_records`

### `tso` (default: `False`)

- `prepare_mfg_core` step 4 → `deploy_mfg_tso_perms`
- `prepare_core` step 13 → `assign_permission_sets`
- `prepare_scratch` step 1 → `insert_scratch_data`
- `prepare_tso` step 1 → `assign_permission_set_licenses`
- `prepare_tso` step 2 → `assign_permission_set_groups`
- `prepare_tso` step 3 → `deploy_post_utils`
- `prepare_tso` step 4 → `deploy_post_tso`
- `prepare_tso` step 5 → `assign_permission_sets`
- `prepare_tso` step 6 → `assign_permission_set_groups_tolerant`
- `prepare_prm` step 2 → `patch_network_email_for_deploy`
- `prepare_prm` step 3 → `deploy_post_prm`
- `prepare_prm` step 5 → `revert_network_email_after_deploy`
- `prepare_prm` step 8 → `assign_permission_sets`
- `prepare_constraints` step 3 → `assign_permission_sets`
- `prepare_revenue_settings` step 1 → `configure_revenue_settings`
- `prepare_revenue_settings` step 2 → `configure_revenue_settings`

### `ux` (default: `True`)

- `prepare_rlm_org` step 29 → `prepare_ux`
- `prepare_manufacturing` step 16 → `prepare_mfg_ux`
- `prepare_ux` step 1 → `assemble_and_deploy_ux`
- `prepare_ux` step 2 → `reorder_app_launcher`

### `org_config.scratch` (runtime)

- `prepare_scratch` step 1 → `insert_scratch_data`
- `prepare_dro` step 2 → `insert_q3_dro_data_scratch`
- `prepare_dro` step 3 → `insert_q3_dro_data_prod`

---

## Configuration Values

Non-boolean scalar values under `project.custom` used as YAML anchors for context definitions, dataset paths, sleep durations, etc.

| Key | Value |
|-----|-------|
| `asset_context_base_reference` | `AssetContext__stdctx` |
| `asset_context_default_mapping` | `AssetEntitiesMapping` |
| `asset_context_name` | `RLM_AssetContext` |
| `badger_aaf_dataset` | `datasets/sfdmu/mfg/en-US/mfg-aaf` |
| `badger_billing_dataset` | `datasets/sfdmu/mfg/en-US/mfg-billing` |
| `badger_configflow_dataset` | `datasets/sfdmu/mfg/en-US/mfg-configflow` |
| `badger_dro_dataset` | `datasets/sfdmu/mfg/en-US/mfg-dro` |
| `badger_guidedselling_dataset` | `datasets/sfdmu/mfg/en-US/mfg-guidedselling` |
| `badger_pricing_dataset` | `datasets/sfdmu/mfg/en-US/mfg-pricing` |
| `badger_product_dataset` | `datasets/sfdmu/mfg/en-US/mfg-pcm` |
| `badger_rebates_dataset` | `datasets/sfdmu/mfg/en-US/mfg-rebates` |
| `badger_tax_dataset` | `datasets/sfdmu/mfg/en-US/mfg-tax` |
| `billing_context_base_reference` | `BillingContext__stdctx` |
| `billing_context_default_mapping` | `BSGEntitiesMapping` |
| `billing_context_name` | `RLM_BillingContext` |
| `billing_default_legal_entity_name` | `Default Legal Entity - US` |
| `billing_default_tax_treatment_name` | `Default Tax Policy` |
| `billing_default_treatment_name` | `Billing Treatment - USA - Advance` |
| `cart_context_base_reference` | `CommerceCartContextDefinition__stdctx` |
| `cart_context_default_mapping` | `CommerceCartMapping` |
| `cart_context_name` | `RLM_CommerceCartContext` |
| `collection_plan_segment_context_base_reference` | `CollectionPlanSegmentContext__stdctx` |
| `collection_plan_segment_context_default_mapping` | `CollectionPlanContextMapping` |
| `collection_plan_segment_context_name` | `RLM_CollectionPlanSegmentCtx` |
| `context_definition_label` | `RLM_SalesTransactionContext` |
| `contracts_context_base_reference` | `ContractsContextDefinition__stdctx` |
| `contracts_context_default_mapping` | `OppToCntrPersistenceMapping` |
| `contracts_context_name` | `RLM_ContractsContext` |
| `contracts_extraction_context_base_reference` | `ContractsExtractionContext__stdctx` |
| `contracts_extraction_context_default_mapping` | `DocExtrctPersistenceMapping` |
| `contracts_extraction_context_name` | `RLM_ContractsExtractionContext` |
| `default_context_start_date` | `2020-01-01T00:00:00.000Z` |
| `default_context_ttl` | `30` |
| `fuelCell_mfg_cml` | `datasets/constraints/mfg/fuelCell` |
| `fulfillment_asset_context_base_reference` | `FulfillmentAssetContext__stdctx` |
| `fulfillment_asset_context_default_mapping` | `FulfillAssetEntitiesMapping` |
| `fulfillment_asset_context_name` | `RLM_FulfillmentAssetContext` |
| `genSet_mfg_cml` | `datasets/constraints/mfg/genSet` |
| `locale` | `en_US` |
| `mfg_sales_transaction_context_name` | `MFG_SalesTransactionContext` |
| `procedure_plan_definition_description` | `Procedure Plan Definition for Quote Pricing` |
| `procedure_plan_definition_developer_name` | `RLM_Quote_Pricing_Procedure_Plan` |
| `procedure_plan_definition_name` | `RLM_Quote_Pricing_Procedure_Plan` |
| `procedure_plan_definition_primary_object` | `Quote` |
| `procedure_plan_definition_process_type` | `RevenueCloud` |
| `procedure_plan_definition_version_developer_name` | `RLM_Quote_Pricing_Procedure_Plan` |
| `procedure_plan_definition_version_effective_from` | `2026-01-01T00:00:00.000Z` |
| `procedure_plan_definition_version_effective_to` | `None` |
| `procedure_plan_definition_version_rank` | `1` |
| `procedure_plan_definition_version_read_context_mapping` | `QuoteEntitiesMapping` |
| `procedure_plan_definition_version_save_context_mapping` | `QuoteEntitiesMapping` |
| `procedure_plans_dataset` | `datasets/sfdmu/procedure-plans` |
| `product_dataset` | `qb` |
| `product_discovery_context_base_reference` | `ProductDiscoveryContext__stdctx` |
| `product_discovery_context_default_mapping` | `ProductDiscoveryMapping` |
| `product_discovery_context_name` | `RLM_ProductDiscoveryContext` |
| `q3_billing_dataset` | `datasets/sfdmu/q3/en-US/q3-billing` |
| `q3_dro_dataset` | `datasets/sfdmu/q3/en-US/q3-dro` |
| `q3_product_dataset` | `datasets/sfdmu/q3/en-US/q3-multicurrency` |
| `q3_rates_dataset` | `datasets/sfdmu/q3/en-US/q3-rates` |
| `q3_rating_dataset` | `datasets/sfdmu/q3/en-US/q3-rating` |
| `q3_tax_dataset` | `datasets/sfdmu/q3/en-US/q3-tax` |
| `quantumbit_approvals_dataset` | `datasets/sfdmu/qb/en-US/qb-approvals` |
| `quantumbit_billing_dataset` | `datasets/sfdmu/qb/en-US/qb-billing` |
| `quantumbit_clm_dataset` | `datasets/sfdmu/qb/en-US/qb-clm` |
| `quantumbit_constraints_component_dataset` | `datasets/sfdmu/qb/en-US/qb-constraints-component` |
| `quantumbit_constraints_data_dir` | `datasets/constraints/qb/QuantumBitComplete` |
| `quantumbit_constraints_product_dataset` | `datasets/sfdmu/qb/en-US/qb-constraints-product` |
| `quantumbit_dro_dataset` | `datasets/sfdmu/qb/en-US/qb-dro` |
| `quantumbit_guidedselling_dataset` | `datasets/sfdmu/qb/en-US/qb-guidedselling` |
| `quantumbit_pricing_dataset` | `datasets/sfdmu/qb/en-US/qb-pricing` |
| `quantumbit_prm_dataset` | `datasets/sfdmu/qb/en-US/qb-prm` |
| `quantumbit_product_dataset` | `datasets/sfdmu/qb/en-US/qb-pcm` |
| `quantumbit_product_image_dataset` | `datasets/sfdmu/qb/en-US/qb-product-images` |
| `quantumbit_rates_dataset` | `datasets/sfdmu/qb/en-US/qb-rates` |
| `quantumbit_rating_dataset` | `datasets/sfdmu/qb/en-US/qb-rating` |
| `quantumbit_tax_dataset` | `datasets/sfdmu/qb/en-US/qb-tax` |
| `quantumbit_transactionprocessingtypes_dataset` | `datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes` |
| `rate_management_context_base_reference` | `RateManagementContext__stdctx` |
| `rate_management_context_default_mapping` | `DefaultUsageMapping` |
| `rate_management_context_name` | `RLM_RateManagementContext` |
| `rating_discovery_context_base_reference` | `RatingDiscoveryContext__stdctx` |
| `rating_discovery_context_default_mapping` | `CatalogMapping` |
| `rating_discovery_context_name` | `RLM_RatingDiscoveryContext` |
| `sales_transaction_context_base_reference` | `SalesTransactionContext__stdctx` |
| `sales_transaction_context_default_mapping` | `QuoteEntitiesMapping` |
| `sales_transaction_context_name` | `RLM_SalesTransactionContext` |
| `server2_constraints_data_dir` | `datasets/constraints/qb/Server2` |
| `sleep_default` | `30` |

---

## YAML Anchors (lists/maps)

These `project.custom` entries are YAML anchors (lists or maps) reused throughout the file for permission sets, decision tables, dataset paths, etc.

### `badger_aaf_ps`

*1 items:*

- `MFG_AAF`

### `badger_mfg_ps`

*1 items:*

- `MFG_RCA`

### `badger_mfg_psg`

*1 items:*

- `MFG`

### `badger_mfg_scratch_psg`

*1 items:*

- `MFG_scratch`

### `dt_activation_decision_tables`

*3 items:*

- `RLM_ProductCategoryQualification`
- `RLM_ProductQualification`
- `RLM_CostBookEntries`

### `dt_asset_decision_tables`

*8 items:*

- `Asset_Action_Source_Entries_Decision_Table_V2`
- `Asset_Rate_Card_Entry_Resolution_V2`
- `Asset_Rate_Decision_Table_V2`
- `Asset_Tier_based_Rate_Adjustment_V2`
- `Asset_Volume_based_Rate_Adjustment_V2`
- `Asset_Rate_Adjustment_Resolution_Entries`
- `Asset_Rate_Card_Entry_Resolution_Entries`
- `Commitment_based_Rate_Adjustment`

### `dt_commerce_decision_tables`

*5 items:*

- `Price_Book_Entry_Commerce_V2`
- `Price_Book_Entry_For_Unit_Price_Commerce_V1`
- `Pricebook_Entry_Adjustment_Commerce_V1`
- `Range_Based_Adjustments_Commerce_V1`
- `Slab_Based_Adjustments_Commerce_V1`

### `dt_default_pricing_decision_tables`

*9 items:*

- `Attribute_Based_Adjustment_Decision_Table`
- `Bundle_Based_Adjustment_Decision_Table`
- `Contract_Pricing_Adjustment_Tiers`
- `Contract_Pricing_Entries_Decision_Table`
- `Contract_Pricing_Volume_Tiers`
- `Price_Adjustment_Tier_Decision_Table`
- `Price_Book_Entry_Decision_Table_v2`
- `Tiered_Adjustment_Tier_Decision_Table`
- `StandardTax`

### `dt_pricing_discovery_decision_tables`

*2 items:*

- `Asset_Action_Source_Entries_Decision_Table_V2`
- `Derived_Pricing_Entries_Decision_Table`

### `dt_rating_decision_tables`

*22 items:*

- `Asset_Action_Source_Entries_Decision_Table_V2`
- `Asset_Rate_Card_Entry_Resolution_V2`
- `Asset_Rate_Card_Entry_Resolution_Entries`
- `Asset_Rate_Decision_Table_V2`
- `Asset_Rate_Adjustment_Resolution_Entries`
- `Asset_Tier_based_Rate_Adjustment_V2`
- `Asset_Volume_based_Rate_Adjustment_V2`
- `Attribute_based_Rate_Adjustment_by_Rate_Card_Entry_ID`
- `Binding_Object_Rate_Card_Entry_Resolution_V2`
- `Binding_Object_Rate_Card_Entry_Resolution_Entries_v2`
- `Binding_Object_Rate_Decision_Table_V2`
- `Binding_Object_Rate_Adjustment_Resolution_Entries`
- `Binding_Object_Tier_based_Rate_Adjustment_V2`
- `Binding_Object_Volume_based_Rate_Adjustment_V2`
- `Commitment_based_Rate_Adjustment`
- `Rate_Adjustment_by_Attribute_Entries_2`
- `Rate_Adjustment_by_Tier_Entries_2`
- `Rate_Adjustment_by_Volume_Entries_2`
- `Rate_Card_Entries_2`
- `Tier_based_Rate_Adjustment_by_Rate_Card_Entry_ID`
- `Volume_based_Rate_Adjustment_by_Rate_Card_Entry_ID`
- `Index_Rate_Decision_Table`

### `dt_rating_discovery_decision_tables`

*6 items:*

- `Binding_Object_Rate_Adjustment_Resolution_Entries`
- `Binding_Object_Rate_Card_Entry_Resolution_Entries_v2`
- `Pricebook_Rate_Card_Decision_Table`
- `Rate_Adjustment_by_Attribute_Resolution_Decision_Table`
- `Rate_Adjustment_by_Tier_Resolution_Decision_Table`
- `Rate_Card_Entry_Resolution_Entries_2`

### `ps_aea`

*1 items:*

- `RLM_QuotingAgent`

### `ps_approvals`

*1 items:*

- `RLM_Approvals`

### `ps_calmdelete`

*1 items:*

- `RLM_CALM_SObject_Access`

### `ps_constraints`

*1 items:*

- `RLM_Constraints`

### `ps_docgen`

*1 items:*

- `RLM_DocGen`

### `ps_prm`

*1 items:*

- `RLM_PRM`

### `ps_quantumbit`

*1 items:*

- `RLM_QuantumBit`

### `ps_ramp_builder`

*1 items:*

- `RLM_RampSchedule`

### `psg_tso`

*1 items:*

- `RLM_TSO`

### `rlm_ai_ps_api_names`

*2 items:*

- `EinsteinGPTPromptTemplateManager`
- `SalesCloudEinsteinAll`

### `rlm_ai_psg_api_names`

*2 items:*

- `CopilotSalesforceUserPSG`
- `CopilotSalesforceAdminPSG`

### `rlm_ai_psl_api_names`

*3 items:*

- `AgentforceServiceAgentBuilderPsl`
- `EinsteinGPTCopilotPsl`
- `EinsteinGPTPromptTemplatesPsl`

### `rlm_blng_ps_api_names`

*10 items:*

- `AnalyticsStoreUser`
- `RevenueLifecycleManagementAccountingAdmin`
- `RevenueLifecycleManagementBillingAdmin`
- `RevenueLifecycleManagementBillingCreateInvoiceFromBillingScheduleApi`
- `RevenueLifecycleManagementBillingCreditMemoOperations`
- `RevenueLifecycleManagementBillingInvoiceErrorRecoveryApi`
- `RevenueLifecycleManagementBillingOperations`
- `RevenueLifecycleManagementBillingTaxAdmin`
- `RevenueLifecycleManagementBillingVoidPostedInvoiceApi`
- `RevenueLifecycleManagementCreateBillingScheduleFromBillingTransactionApi`

### `rlm_clm_psl_api_names`

*11 items:*

- `AIAcceleratorPsl`
- `ClauseManagementUser`
- `CLMAnalyticsPsl`
- `ContractManagementUser`
- `ContractsAIUserPsl`
- `DocGenDesignerPsl`
- `DocumentBuilderUserPsl`
- `InsightsCGAnalyticsPsl`
- `Microsoft365WordPsl`
- `ObligationManagementUser`
- `OmniStudioDesigner`

### `rlm_pcm_ps_api_names`

*4 items:*

- `IndustriesConfiguratorPlatformApi`
- `ProductConfigurationRulesDesigner`
- `ProductCatalogManagementAdministrator`
- `ProductCatalogManagementViewer`

### `rlm_psg_api_names`

*11 items:*

- `RLM_QB_AI`
- `RLM_RCB`
- `RLM_RMI`
- `RLM_CFG`
- `RLM_CLM`
- `RLM_DOC`
- `RLM_DRO`
- `RLM_NGP`
- `RLM_PCM`
- `RLM_PSL`
- `RLM_USG`

### `rlm_psl_api_names`

*25 items:*

- `BREDesigner`
- `BRERuntime`
- `CorePricingDesignTime`
- `DataProcessingEnginePsl`
- `DecimalQuantityDesigntimePsl`
- `DecimalQuantityRuntimePsl`
- `DocGenDesignerPsl`
- `DocumentBuilderUserPsl`
- `DynamicRevenueOrchestratorUserPsl`
- `IndustriesConfiguratorPsl`
- `Microsoft365WordPsl`
- `OmniStudioDesigner`
- `ProductCatalogManagementAdministratorPsl`
- `ProductDiscoveryUserPsl`
- `RatingDesignTimePsl`
- `RatingRunTimePsl`
- `RevenueLifecycleManagementUserPsl`
- `RevLifecycleMgmtBillingPsl`
- `UsageDesignTimePsl`
- `UsageRunTimePsl`
- `WalletManagementUserPsl`
- `BillingAdvancedPsl`
- `IndustriesARCPsl`
- `CollectionsAndRecoveryPsl`
- `RevPromotionsManagementPsl`

### `rlm_tableaunext_ps_api_names`

*4 items:*

- `TableauEinsteinAdmin`
- `TableauEinsteinBusinessUser`
- `TableauEinsteinAnalyst`
- `TableauSelfServiceAnalyst`

### `rlm_tableaunext_psl_api_names`

*1 items:*

- `TableauEinsteinUserPsl`

### `rlm_tso_ps_api_names`

*4 items:*

- `ERIBasic`
- `RLM_UtilitiesPermset`
- `OrchestrationProcessManagerPermissionSet`
- `EventMonitoringPermSet`

### `rlm_tso_psg_api_names`

*4 items:*

- `CopilotSalesforceUserPSG`
- `CopilotSalesforceAdminPSG`
- `UnifiedCatalogAdminPsl`
- `UnifiedCatalogDesignerPsl`

### `rlm_tso_psl_api_names`

*23 items:*

- `AutomatedActionsPsl`
- `EinsteinAgentCWUPsl`
- `EinsteinAgentPsl`
- `EinsteinCopilotReviewMyDayPsl`
- `EinsteinDiscoveryInTableauPsl`
- `EinsteinGPTCallExplorerPsl`
- `EinsteinGPTCreateClosePlanPsl`
- `EinsteinGPTGetProductPricingPsl`
- `EinsteinGPTGroundingStructuredDataPsl`
- `EinsteinGPTMeetingFollowUpPsl`
- `EinsteinGPTSalesCallSummariesPsl`
- `EinsteinGPTSalesEmailsPsl`
- `EinsteinGPTSalesMiningPsl`
- `EinsteinGPTSalesSummariesPsl`
- `EinsteinGPTSendMeetingRequestPsl`
- `EinsteinSalesGenerativeInsightsPsl`
- `EinsteinSalesRepFeedbackPsl`
- `ERIPlatformBasic`
- `SalesActionFindPastCollaboratorsPsl`
- `SalesActionReviewBuyingCommitteePsl`
- `SalesCloudUnlimitedAnalyticsAdminPsl`
- `SalesCloudUnlimitedPsl`
- `SalesEngagementBasicPsl`
