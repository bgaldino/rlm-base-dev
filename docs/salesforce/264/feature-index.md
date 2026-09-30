# Release 264 (Winter '27) — Feature Index

**Per-area inventory of features in Winter '27 / Release 264, derived from the Salesforce Help portal snapshot.** Release 264 was promoted to `main` on 2026-09-16; Help snapshots captured 2026-09-04 through 2026-09-07 for ten functional areas (1,131 articles across configurator, transaction_mgmt, billing, pcm, dro, pricing, rating, usage, agents, and approvals). Collections area not captured — still serving 262 content as of 2026-09-07.

> **Pre-GA status:** API v68.0 GA waves 2026-09-05 → 2026-10-10 are in progress as of 2026-09-29. This index derives from Help articles captured before/during early GA rollout, before official release notes. Feature inventory is Help-corpus-derived. A live 264 org remains the ground truth for behavioral verification.

## Sources

| File | Description |
|---|---|
| [`help/`](help/) | Salesforce Help snapshot — 1,131 articles captured 2026-09-04 through 2026-09-07 across 10 RC functional areas. Collections not captured — verified still serving 262 content. |
| *(none yet)* | Official 264 release notes and Solution Overview decks — not yet published as of 2026-09-29. |

## Change Summary

**Corpus comparison (264 vs 262):**
- **Total articles:** 1,131 (264) vs 935 (262) — net +196 articles
- **New in 264:** 301 articles
- **Only in 262:** 105 articles (97 collections + 8 others)
- **Shared articles:** 830 articles (many with material body changes)

**Per-area article counts (262 → 264):**
- Agents: 13 → 17 (+4)
- Approvals: 34 → 43 (+9)
- Billing: 171 → 265 (+94, largest expansion)
- Configurator: 76 → 83 (+7)
- DRO: 70 → 99 (+29)
- PCM: 107 → 142 (+35)
- Pricing: 110 → 155 (+45)
- Rating: 35 → 70 (+35, doubled)
- Transaction Mgmt: 170 → 208 (+38)
- Usage: 52 → 52 (0 new; 3 articles with material updates)
- Collections: 97 → (not captured)

---

## New Features in 264 (verified absent from 262 corpus)

| Feature | Area | Articles |
|---|---|---|
| **Billing Forecast** | Billing | Estimate upcoming invoice charges before invoices are created. Finance/sales review projected charges. Console uses Tableau Next. Does not apply to milestone or usage charges. | 8 articles: [`ind.billing_forecast.htm`](help/articles/ind.billing_forecast.htm.md), [`ind.billing_forecast_enable.htm`](help/articles/ind.billing_forecast_enable.htm.md), [`ind.billing_forecast_console.htm`](help/articles/ind.billing_forecast_console.htm.md), [`ind.billing_forecast_example.htm`](help/articles/ind.billing_forecast_example.htm.md) |
| **Invoice Risk Scoring (Pilot)** | Billing | Predict risk scores (likelihood of delayed/non-payment) using Data Cloud + AI Accelerator. Scores categorized as Low/Medium/High. | 13 articles including [`ind.billing_invoice_risk_score.htm`](help/articles/ind.billing_invoice_risk_score.htm.md), [`ind.billing_invoice_risk_scoring.htm`](help/articles/ind.billing_invoice_risk_scoring.htm.md), [`ind.billing_invoice_risk_scoring_view_scores.htm`](help/articles/ind.billing_invoice_risk_scoring_view_scores.htm.md) |
| **Payment Reconciliation** | Billing | Automate reconciliation of payment advice/proof with bank data using Document AI + vector search + Data 360. | 12 articles including [`ind.billing_payment_reconciliation.htm`](help/articles/ind.billing_payment_reconciliation.htm.md), [`ind.billing_payment_reconciliation_setup.htm`](help/articles/ind.billing_payment_reconciliation_setup.htm.md), [`ind.billing_payment_reconciliation_run.htm`](help/articles/ind.billing_payment_reconciliation_run.htm.md) |
| **Approval Delegation** | Approvals | Delegate approval responsibilities — temporary coverage during vacation/absence. | 4 articles: [`ind.approvals_approval_delegation.htm`](help/articles/ind.approvals_approval_delegation.htm.md), [`ind.approvals_create_delegation_records.htm`](help/articles/ind.approvals_create_delegation_records.htm.md), [`ind.approvals_turn_on_delegation.htm`](help/articles/ind.approvals_turn_on_delegation.htm.md), [`ind.approvals_delegation_considerations.htm`](help/articles/ind.approvals_delegation_considerations.htm.md) |
| **Compound Price Uplifts for Ramps** | Transaction Mgmt | Create ramp deals with standard or compound price uplifts. | 2 articles: [`ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift_sales_reps.htm.md), [`ind.qocal_ramp_deal_compound_uplift.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift.htm.md) |

---

## Expanded / Newly Documented Features (existed in 262)

### Agentforce for Revenue Management

| Feature | Status | Articles |
|---|---|---|
| Approval Management Agent | **Expanded** (1 → 6 articles) | Conversational approval lifecycle — submit, track, summarize, approve/reject from Salesforce/Slack. AI-generated summaries. Three subagents. | [`ind.rev_agent_approval_agent.htm`](help/articles/ind.rev_agent_approval_agent.htm.md), [`ind.rev_agent_topic_approval_management.htm`](help/articles/ind.rev_agent_topic_approval_management.htm.md), [`ind.rev_agent_topic_search_approval_records.htm`](help/articles/ind.rev_agent_topic_search_approval_records.htm.md), [`ind.rev_agent_topic_summarize_multiple_approval_work_items.htm`](help/articles/ind.rev_agent_topic_summarize_multiple_approval_work_items.htm.md) |

### Advanced Approvals

| Feature | Status | Articles |
|---|---|---|
| Slack Integration | **Expanded** | Post approval notifications to Slack. | [`ind.approvals_slack_channel_notifications.htm`](help/articles/ind.approvals_slack_channel_notifications.htm.md) |
| Serial and Parallel Approvers | **Expanded** (1 → 4 articles) | Multi-stakeholder workflows. | [`ind.approvals_implement_serial_and_parallel_approvers.htm`](help/articles/ind.approvals_implement_serial_and_parallel_approvers.htm.md) |
| Smart / Rule-Based Auto-Approvals | **Expanded** | Automated approval logic. | [`ind.approvals_smart_or_rule_based_approvals.htm`](help/articles/ind.approvals_smart_or_rule_based_approvals.htm.md) |

### Billing (94 net-new articles)

| Feature | Status | Key Articles |
|---|---|---|
| Collections & Dunning | **Expanded** | Collections Specialist Console, dunning orchestration, collection plans/items. | [`ind.billing_collections.htm`](help/articles/ind.billing_collections.htm.md) (+3,564 chars), [`ind.billing_collections_specialist_console.htm`](help/articles/ind.billing_collections_specialist_console.htm.md), [`ind.billing_configure_dunning_orchestration.htm`](help/articles/ind.billing_configure_dunning_orchestration.htm.md) |
| Change Billing Frequency | **Expanded** | Change frequency on new/existing subscriptions. | [`ind.billing_change_billing_pricing_frequencies.htm`](help/articles/ind.billing_change_billing_pricing_frequencies.htm.md), [`ind.billing_change_billing_frequency_examples.htm`](help/articles/ind.billing_change_billing_frequency_examples.htm.md) |
| Refunds & Credit Management | **Expanded** | Issue refunds, unreferenced refunds, rule-based application. | [`ind.billing_refunds_overview.htm`](help/articles/ind.billing_refunds_overview.htm.md), [`ind.billing_unreferenced_refunds.htm`](help/articles/ind.billing_unreferenced_refunds.htm.md), [`ind.billing_setup_credit_memos_payments_application_rules.htm`](help/articles/ind.billing_setup_credit_memos_payments_application_rules.htm.md) |
| Tax Engine Framework | **Expanded** | Create tax engines/providers, extend Revenue Standard Tax Engine. | [`ind.billing_tax_engine_create.htm`](help/articles/ind.billing_tax_engine_create.htm.md), [`ind.billing_extend_revenue_standard_tax_engine.htm`](help/articles/ind.billing_extend_revenue_standard_tax_engine.htm.md), [`ind.billing_tax_policies_and_treatments_create.htm`](help/articles/ind.billing_tax_policies_and_treatments_create.htm.md) |
| Invoice Previews | **Expanded** | Generate previews for orders, accounts, billing schedule groups. | [`ind.billing_preview_invoice.htm`](help/articles/ind.billing_preview_invoice.htm.md), [`ind.billing_invoice_preview_create.htm`](help/articles/ind.billing_invoice_preview_create.htm.md) |
| Invoice Operations | **Expanded** | Delete, write off, review split invoices, convert to async. | [`ind.billing_invoice_delete.htm`](help/articles/ind.billing_invoice_delete.htm.md), [`ind.billing_write_off_invoice_balance.htm`](help/articles/ind.billing_write_off_invoice_balance.htm.md), [`ind.billing_invoice_run_sync_process.htm`](help/articles/ind.billing_invoice_run_sync_process.htm.md) |
| Billing Schedule Management | **Expanded** | Generate from orders, update groups, suspend/resume, APIs. | [`ind.billing_schedules_from_orders.htm`](help/articles/ind.billing_schedules_from_orders.htm.md), [`ind.billing_suspend_and_resume_overview.htm`](help/articles/ind.billing_suspend_and_resume_overview.htm.md), [`ind.billing_catch_up_bill_runs.htm`](help/articles/ind.billing_catch_up_bill_runs.htm.md) |
| General Ledger | **Expanded** | GL account assignment rules, FX gains/losses, legal entity periods. | [`ind.billing_general_ledger_account_assignment_rules_create.htm`](help/articles/ind.billing_general_ledger_account_assignment_rules_create.htm.md), [`ind.billing_foreign_exchange_realized_gains_and_losses.htm`](help/articles/ind.billing_foreign_exchange_realized_gains_and_losses.htm.md) |
| Debit Memos & Policies | **Expanded** | Create debit memos, billing policies/treatments. | [`ind.billing_debit_memo_create.htm`](help/articles/ind.billing_debit_memo_create.htm.md), [`ind.billing_policies_and_treatments_create.htm`](help/articles/ind.billing_policies_and_treatments_create.htm.md) |

### Product Configurator

| Feature | Status | Articles |
|---|---|---|
| Context Definition Setup | **Expanded** | Set up for constraint engine, custom fields, Apex triggers. | [`ind.product_configurator_set_up_constraint_engine_context_definitions.htm`](help/articles/ind.product_configurator_set_up_constraint_engine_context_definitions.htm.md), [`ind.product_configurator_select_context_attributes.htm`](help/articles/ind.product_configurator_select_context_attributes.htm.md) |
| Rules Engine Transaction Types | **Expanded** | Define which constraint engine to use. | [`ind.product_configurator_specify_which_rule_engine_to_use.htm`](help/articles/ind.product_configurator_specify_which_rule_engine_to_use.htm.md) |

### Dynamic Revenue Orchestration (DRO)

| Feature | Status | Articles |
|---|---|---|
| **Time-Aware Fulfillment** | **Expanded** (1 → 12 articles) | DRO decomposes multi-year ramps into FOLIs and FASPs aligned with period effective dates. Prevents overwrites on amendments. | [`ind.dro_time_aware_fulfillment.htm`](help/articles/ind.dro_time_aware_fulfillment.htm.md), [`ind.dro_time_aware_fulfillment_enable.htm`](help/articles/ind.dro_time_aware_fulfillment_enable.htm.md), [`ind.dro_time_aware_fulfillment_migration.htm`](help/articles/ind.dro_time_aware_fulfillment_migration.htm.md), [`ind.dro_time_aware_fulfillment_example_add.htm`](help/articles/ind.dro_time_aware_fulfillment_example_add.htm.md) |
| High Tech Order Orchestration Template | **Expanded** (15 → 21 articles on technical products overall) | Pre-built DRO template. | [`ind.dro_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_hi_tech_order_orchestration_template.htm.md), [`ind.dro_install_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_install_hi_tech_order_orchestration_template.htm.md) |
| Technical Product Catalog | **Expanded** | Build technical product catalog, create products/bundles. | [`ind.dro_technical_product_in_dro.htm`](help/articles/ind.dro_technical_product_in_dro.htm.md), [`ind.dro_creating_a_technical_product.htm`](help/articles/ind.dro_creating_a_technical_product.htm.md), [`ind.dro_technical_bundles.htm`](help/articles/ind.dro_technical_bundles.htm.md) |
| Fulfillment Workspaces | **Expanded** | Clone, configure deep cloning. | [`ind.dro_clone_a_fulfillment_workspace.htm`](help/articles/ind.dro_clone_a_fulfillment_workspace.htm.md), [`ind.dro_configure_fulfillment_workspace_deep_cloning.htm`](help/articles/ind.dro_configure_fulfillment_workspace_deep_cloning.htm.md) |
| Fulfillment Steps | **Expanded** | Define steps, create definition groups, configure scenarios, conditions. | [`ind.dro_define_a_fulfillment_step.htm`](help/articles/ind.dro_define_a_fulfillment_step.htm.md), [`ind.dro_create_a_fulfillment_step_definition_group.htm`](help/articles/ind.dro_create_a_fulfillment_step_definition_group.htm.md), [`ind.dro_custom_scope_step_dependencies.htm`](help/articles/ind.dro_custom_scope_step_dependencies.htm.md) |

### Product Catalog Management (PCM)

| Feature | Status | Articles |
|---|---|---|
| Product Selling Model | **Expanded** | Manage, create, assign. | [`ind.product_catalog_product_selling_model.htm`](help/articles/ind.product_catalog_product_selling_model.htm.md), [`ind.product_catalog_create_a_product_selling_model.htm`](help/articles/ind.product_catalog_create_a_product_selling_model.htm.md) |
| Cardinality Management | **Expanded** | Group and local cardinality — manage, edit, override. | [`ind.product_catalog_group_cardinality.htm`](help/articles/ind.product_catalog_group_cardinality.htm.md), [`ind.product_catalog_local_cardinality.htm`](help/articles/ind.product_catalog_local_cardinality.htm.md) |
| Attribute Management | **Expanded** | Create categories/picklists, assign, reorder. | [`ind.product_catalog_dyn_create_attribute_categories.htm`](help/articles/ind.product_catalog_dyn_create_attribute_categories.htm.md), [`ind.product_catalog_assign_attributes_to_a_product_classification.htm`](help/articles/ind.product_catalog_assign_attributes_to_a_product_classification.htm.md) |
| Product Deep Cloning | **Expanded** | Deep clone products, set up. | [`ind.product_catalog_deep_clone_in_product_catalog_management.htm`](help/articles/ind.product_catalog_deep_clone_in_product_catalog_management.htm.md), [`ind.product_catalog_set_up_product_deep_clone.htm`](help/articles/ind.product_catalog_set_up_product_deep_clone.htm.md) |

### Salesforce Pricing

| Feature | Status | Articles |
|---|---|---|
| **Price Adjustment Matrix** | **Expanded** (8 → 12 articles) | Dynamic pricing beyond volume discounts — custom decision tables with criteria/adjustments. | [`ind.pricing_add_the_price_adjustment_matrix_element.htm`](help/articles/ind.pricing_add_the_price_adjustment_matrix_element.htm.md), [`ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`](help/articles/ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm.md) |
| **Price Waterfall** | **Expanded** (39 → 57 articles) | Pricing transparency — detailed breakdown of additions/deductions. | [`ind.pricing_set_up_price_waterfall_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_price_waterfall_salesforce_pricing.htm.md), [`ind.pricing_enable_price_waterfall.htm`](help/articles/ind.pricing_enable_price_waterfall.htm.md), [`ind.pricing_set_price_waterfall_persistence.htm`](help/articles/ind.pricing_set_price_waterfall_persistence.htm.md) |
| Einstein Generative AI for Pricing | **Expanded** (1 → 5 articles) | Automate context tag mapping. | [`ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm.md), [`ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm.md) |
| Discovery Procedure | **Expanded** | Configure, discover pricing factors. | [`ind.pricing_set_up_your_discovery_procedure.htm`](help/articles/ind.pricing_set_up_your_discovery_procedure.htm.md), [`ind.pricing_discovery_procedure_for_pricing.htm`](help/articles/ind.pricing_discovery_procedure_for_pricing.htm.md) |
| Pricing Recipes | **Expanded** | Setup, create, sync decision tables. | [`ind.pricing_pricing_recipes.htm`](help/articles/ind.pricing_pricing_recipes.htm.md), [`ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`](help/articles/ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm.md) |
| Pricing Adjustment Batch Jobs | **Expanded** | Perform, fix/execute failed, view logs. | [`ind.pricing_pricing_adjustment_batch_jobs.htm`](help/articles/ind.pricing_pricing_adjustment_batch_jobs.htm.md), [`ind.pricing_perform_pricing_adjustment_batch_job.htm`](help/articles/ind.pricing_perform_pricing_adjustment_batch_job.htm.md) |

### Rate Management

| Feature | Status | Articles |
|---|---|---|
| **Rating Elements (comprehensive)** | **Expanded** (35 → 70 articles, doubled) | Base Rate, Manual Rate Discount, Negotiated Base/Tier/Volume adjustments, Rate Adjustment Matrix, Rounding, Get Rate Cards/Entries. Each element now has dedicated article + variables + "Add" guide. | 35 new element articles including [`ind.rm_element_base_rate.htm`](help/articles/ind.rm_element_base_rate.htm.md), [`ind.rm_element_manual_rate_discount.htm`](help/articles/ind.rm_element_manual_rate_discount.htm.md), [`ind.rm_element_rate_adjustment_matrix.htm`](help/articles/ind.rm_element_rate_adjustment_matrix.htm.md), [`ind.rm_rating_elements.htm`](help/articles/ind.rm_rating_elements.htm.md) |

### Transaction Management

| Feature | Status | Articles |
|---|---|---|
| **Ramp Deals** | **Expanded** | Considerations expanded +9,220 chars (+505%). Compound uplifts (new), groups vs lines transition, renewal price uplifts. | [`ind.qocal_considerations_ramp_deals.htm`](help/articles/ind.qocal_considerations_ramp_deals.htm.md), [`ind.qocal_ramp_deals_for_groups_transition.htm`](help/articles/ind.qocal_ramp_deals_for_groups_transition.htm.md), [`ind.qocal_renewal_price_uplifts.htm`](help/articles/ind.qocal_renewal_price_uplifts.htm.md) |
| Quote Line Item CSV Import | **Expanded** (6 → 9 articles) | Import from CSV, custom templates. Requires `Advanced CSV Data Import` permission set. | [`ind.qocal_qli_import_user_import_lines_csv.htm`](help/articles/ind.qocal_qli_import_user_import_lines_csv.htm.md), [`ind.qocal_set_up_quote_line_item_import.htm`](help/articles/ind.qocal_set_up_quote_line_item_import.htm.md) |
| Backdated Asset Transactions | **Expanded** | Backdate transactions, considerations. | [`ind.qocal_backdate_asset_transactions.htm`](help/articles/ind.qocal_backdate_asset_transactions.htm.md), [`ind.qocal_considerations_for_assets_with_backdated_changes.htm`](help/articles/ind.qocal_considerations_for_assets_with_backdated_changes.htm.md) |
| Contract Cotermination | **Expanded** | Coterminate subscription assets with contract end dates. | [`ind.qocal_coterminate_with_contract_end_date.htm`](help/articles/ind.qocal_coterminate_with_contract_end_date.htm.md) |
| Context Service Extension | **Expanded** | Extend/map sales transactions, context definitions, custom fields. | [`ind.qocal_extend_your_transactions_with_custom_field_support.htm`](help/articles/ind.qocal_extend_your_transactions_with_custom_field_support.htm.md), [`ind.qocal_map_custom_fields.htm`](help/articles/ind.qocal_map_custom_fields.htm.md) |
| Transaction Summary | **Expanded** | Customize, turn on auto-refresh. | [`ind.qocal_customize_transaction_summary.htm`](help/articles/ind.qocal_customize_transaction_summary.htm.md), [`ind.qocal_auto_refresh_stle_transaction_summary_help.htm`](help/articles/ind.qocal_auto_refresh_stle_transaction_summary_help.htm.md) |

### Usage Management

**No new articles** (52 → 52), but **3 articles with material updates** (>500 chars):
- **Usage Management Limits** ([`ind.um_usage_management_limits.htm`](help/articles/ind.um_usage_management_limits.htm.md)) — +1,232 chars (+127%)
- **Create Usage Commitment Policy** ([`ind.um_create_usage_commitment_policy.htm`](help/articles/ind.um_create_usage_commitment_policy.htm.md)) — +1,051 chars (+131%)
- **Create Usage Product Grant Binding Policy** ([`ind.um_create_a_usage_product_grant_binding_policy.htm`](help/articles/ind.um_create_a_usage_product_grant_binding_policy.htm.md)) — +533 chars (+43%)

---

## Material Changes to Shared Articles (Top 10)

Of 831 shared articles, these had the largest body changes:

1. **Considerations for Ramp Deals** ([`ind.qocal_considerations_ramp_deals.htm`](help/articles/ind.qocal_considerations_ramp_deals.htm.md)) — +9,220 chars (+505%)
2. **Best Practices for Apex Pricing Hooks** ([`ind.pricing_apex_hooks_best_practices.htm`](help/articles/ind.pricing_apex_hooks_best_practices.htm.md)) — +8,762 chars (+998%)
3. **Manage Collections for Accounts** ([`ind.billing_collections.htm`](help/articles/ind.billing_collections.htm.md)) — +3,564 chars (+132%)
4. **Configure Your Pricing Procedure** ([`ind.pricing_configure_pricing_procedure.htm`](help/articles/ind.pricing_configure_pricing_procedure.htm.md)) — +3,370 chars (+89%)
5. **Ramp Deal for Groups with Single Ramp Schedule** ([`ind.qocal_ramp_deal_for_groups_create.htm`](help/articles/ind.qocal_ramp_deal_for_groups_create.htm.md)) — -2,574 chars (-67%)
6. **Ramp Deals in Revenue Management** ([`ind.qocal_ramp_deals_complex_long_term_multiple_products.htm`](help/articles/ind.qocal_ramp_deals_complex_long_term_multiple_products.htm.md)) — -2,570 chars (-50%)
7. **Create Ramp Deals for Groups with Multiple Ramp Schedules** ([`ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm`](help/articles/ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm.md)) — -2,538 chars (-68%)
8. **Use the Price Revision Element** ([`ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`](help/articles/ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm.md)) — +2,379 chars (+39%)
9. **Honor Precise Time Zones in Asset Lifecycle Dates** ([`ind.qocal_asset_lifecycle_date_time_precision.htm`](help/articles/ind.qocal_asset_lifecycle_date_time_precision.htm.md)) — +2,100 chars (+79%)
10. **Set Dependencies Between Fulfillment Steps** ([`ind.dro_set_dependencies_between_fulfillment_steps.htm`](help/articles/ind.dro_set_dependencies_between_fulfillment_steps.htm.md)) — +1,967 chars (+80%)

---

## Removed / Renamed Articles (264 vs 262)

### Billing (5 removed)

- **Configure Your Custom Metadata Types** (`ind.billing_custom_metadata_types_configure.htm`) — replaced by [`ind.billing_standard_tax_custom_metadata_types_configure.htm`](help/articles/ind.billing_standard_tax_custom_metadata_types_configure.htm.md) (tax-specific)
- **Generate Billing Schedules** (`ind.billing_schedules_create.htm`) — replaced by [`ind.billing_schedules_from_orders.htm`](help/articles/ind.billing_schedules_from_orders.htm.md)
- **Period Boundary and Proration in Billing Cycles** (`ind.billing_understand_period_boundries.htm`) — removed
- **Tax Interface Extension** (`ind.billing_understand_tax_interface_extension.htm`) — superseded by new tax engine framework
- **Troubleshoot Invoice Batch Run Errors** (`ind.billing_invoice_batch_runs_troubleshooting.htm`) — removed

### DRO (1 removed)

- **Create Custom Context Definition and Map Attribute to Field** (`ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm`) — removed (context setup now in configurator articles)

### Transaction Management (2 removed)

- **Divide Subscription Transactions into Segments with Ramp Deals for Lines** (`ind.qocal_ramp_deals.htm`) — superseded by Ramp Deals for Groups
- **View Rate Cards for Usage-Based Assets** (`ind.qocal_view_asset_usage_rate_cards.htm`) — removed

### Collections (97 removed)

All 97 Collections articles present in 262 are absent from 264 because the Collections area was **verified still serving 262 content** as of 2026-09-07. Collections snapshot intentionally not captured. Expected to be captured once 264-specific content publishes.

---

## Maintenance

### How to re-check this index

1. **When 264 release notes publish:** Cross-reference against official notes. Update tiers (GA/Beta/Pilot). Add features not covered by Help.
2. **When v68.0 Metadata Coverage Report publishes:** Verify object/field/API changes match the report.
3. **Refresh Collections snapshot** once 264 content publishes:
   ```bash
   cci task run snapshot_collections_help_264 -o mode discover
   # byte-diff shared articles against 262 to confirm changed-text signal
   # if ready: cci task run snapshot_collections_help_264
   ```
4. **When Solution Overview decks publish:** Add to Sources table, reconcile descriptions.

### How this index was built

1. Diffing 262 and 264 manifest files to identify new (303), removed (104), and shared (831) articles.
2. Grouping new articles by title patterns to identify features.
3. Reading sample articles from each feature group.
4. Computing body-length changes for shared articles.
5. Verifying removed articles to distinguish removals from renames.
6. **Grepping 262 corpus for each feature's key terms** to distinguish truly new from expanded/newly-documented.

Regenerate after corpus refreshes.
