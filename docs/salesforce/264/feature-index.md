# Release 264 (Winter '27) — Feature Index

**Per-area inventory of features in Winter '27 / Release 264, derived from the Salesforce Help portal snapshot.** Release 264 was promoted to `main` on 2026-09-16; Help snapshots captured 2026-09-04 through 2026-09-07 for ten functional areas (1,131 articles across configurator, transaction_mgmt, billing, pcm, dro, pricing, rating, usage, agents, and approvals). Collections area not captured — still serving 262 content as of 2026-09-07.

> **Pre-GA status:** API v68.0 GA waves 2026-09-05 → 2026-10-10 are in progress as of 2026-09-29. This index derives from Help articles captured during early GA rollout. The feature inventory comes from the Help corpus only. The Winter '27 release notes are published on Help, and their Revenue section is captured under `docs/salesforce/264/release-notes/` (PR #480), but this index has not yet been cross-referenced against them. A live 264 org remains the ground truth for behavioral verification.

## Sources

| File | Description |
|---|---|
| [`help/`](help/) | Salesforce Help snapshot — 1,131 articles captured 2026-09-04 through 2026-09-07 across 10 RC functional areas. Collections not captured — verified still serving 262 content. |
| `release-notes/` (added by PR #480, which merges before this index change) | Winter '27 (264) Revenue release notes — 127 articles under `release-notes.rn_revenue.htm`, captured by `snapshot_revenue_release_notes_264`. Not yet cross-referenced into this index. The notes label no feature Beta or Pilot, so tiers still come from Help titles (e.g. Invoice Risk Scoring (Pilot) appears in Help but not in the notes). |
| *(not captured)* | Solution Overview decks, so features without Help or release-note coverage are unverified. |

## Change Summary

**Corpus comparison (264 vs 262):**
- **Total articles:** 1,131 (264) vs 935 (262) — net +196 articles
- **New in 264:** 301 articles
- **Only in 262:** 105 articles (97 collections + 8 others)
- **Shared articles:** 830 articles (many with material body changes)

**Per-area captured article counts (262 → 264; net change, new IDs, IDs only in 262):**
- Agents: 13 → 17 (net +4; 4 new)
- Approvals: 34 → 43 (net +9; 9 new)
- Billing: 171 → 265 (net +94; 99 new, 5 only in 262 — largest expansion)
- Configurator: 76 → 83 (net +7; 7 new)
- DRO: 70 → 96 (net +26; 27 new, 1 only in 262). The 264 manifest discovered 99 DRO IDs, but 3 failed to capture (see below).
- PCM: 107 → 142 (net +35; 35 new)
- Pricing: 110 → 155 (net +45; 45 new)
- Rating: 35 → 70 (net +35; 35 new — doubled)
- Transaction Mgmt: 170 → 208 (net +38; 40 new, 2 only in 262)
- Usage: 52 → 52 (0 new; 3 articles with material updates)
- Collections: 97 → not captured

---

## New Features in 264 (verified absent from 262 corpus)

| Feature | Area | Description | Articles |
|---|---|---|---|
| **Billing Forecast** | Billing | Estimate upcoming invoice charges before invoices are created. Finance/sales review projected charges. Console uses Tableau Next. Does not apply to milestone or usage charges. | 8 articles including [`ind.billing_forecast.htm`](help/articles/ind.billing_forecast.htm.md), [`ind.billing_forecast_enable.htm`](help/articles/ind.billing_forecast_enable.htm.md), [`ind.billing_forecast_console.htm`](help/articles/ind.billing_forecast_console.htm.md), [`ind.billing_forecast_example.htm`](help/articles/ind.billing_forecast_example.htm.md) |
| **Invoice Risk Scoring (Pilot)** | Billing | Predict risk scores (likelihood of delayed/non-payment) using Data 360 + AI Accelerator. Scores categorized as Low/Medium/High. | 13 articles including [`ind.billing_invoice_risk_score.htm`](help/articles/ind.billing_invoice_risk_score.htm.md), [`ind.billing_invoice_risk_scoring.htm`](help/articles/ind.billing_invoice_risk_scoring.htm.md), [`ind.billing_invoice_risk_scoring_view_scores.htm`](help/articles/ind.billing_invoice_risk_scoring_view_scores.htm.md) |
| **Payment Reconciliation** | Billing | Automate reconciliation of payment advice/proof with bank data using Document AI + vector search + Data 360. | 12 articles including [`ind.billing_payment_reconciliation.htm`](help/articles/ind.billing_payment_reconciliation.htm.md), [`ind.billing_payment_reconciliation_setup.htm`](help/articles/ind.billing_payment_reconciliation_setup.htm.md), [`ind.billing_payment_reconciliation_run.htm`](help/articles/ind.billing_payment_reconciliation_run.htm.md) |
| **Approval Management Agent** | Agentforce | Conversational approval lifecycle — submit, track, summarize, approve/reject from Salesforce/Slack. AI-generated summaries. Three subagents. | 4 articles: [`ind.rev_agent_approval_agent.htm`](help/articles/ind.rev_agent_approval_agent.htm.md), [`ind.rev_agent_topic_approval_management.htm`](help/articles/ind.rev_agent_topic_approval_management.htm.md), [`ind.rev_agent_topic_search_approval_records.htm`](help/articles/ind.rev_agent_topic_search_approval_records.htm.md), [`ind.rev_agent_topic_summarize_multiple_approval_work_items.htm`](help/articles/ind.rev_agent_topic_summarize_multiple_approval_work_items.htm.md) |
| **Compound Price Uplifts for Ramps** | Transaction Mgmt | Create ramp deals with standard or compound price uplifts. | 2 articles: [`ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift_sales_reps.htm.md), [`ind.qocal_ramp_deal_compound_uplift.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift.htm.md) |
| **Invoice Aging** | Billing | Invoice Aging for Account component: invoice counts, overdue invoices, aging buckets, and average and maximum age on Account and Order pages. | 2 articles: [`ind.billing_invoice_aging.htm`](help/articles/ind.billing_invoice_aging.htm.md), [`ind.billing_invoice_aging_component.htm`](help/articles/ind.billing_invoice_aging_component.htm.md) |
| **Billing Start Month and Next Billing Date Override** | Billing | Billing schedule group fields you can update on existing groups. 262 documented billing day of month and the separate period boundary start month, but not these. | 3 articles: [`ind.billing_schedule_group_update.htm`](help/articles/ind.billing_schedule_group_update.htm.md), [`ind.billing_schedule_group_update_billing_start_month.htm`](help/articles/ind.billing_schedule_group_update_billing_start_month.htm.md), [`ind.billing_schedule_group_update_next_billing_date_override.htm`](help/articles/ind.billing_schedule_group_update_next_billing_date_override.htm.md) |
| **Exclude From Billing** | Billing | A billing treatment value that skips billing schedules, groups and invoices for order items not ready to bill, without holding the whole order. | [`ind.billing_treatment_exclude_from_billing.htm`](help/articles/ind.billing_treatment_exclude_from_billing.htm.md) |
| **Partial Search** | PCM | Match an incomplete product code or SKU against any part of the value, ignoring hyphens, spaces and similar characters. | 2 articles: [`ind.product_catalog_partial_search.htm`](help/articles/ind.product_catalog_partial_search.htm.md), [`ind.product_catalog_configure_partial_search.htm`](help/articles/ind.product_catalog_configure_partial_search.htm.md) |
| **Price Book Filtering** | PCM | Return only the products associated with the selected price book, for large catalogs with little price book overlap. | [`ind.product_catalog_turn_on_price_book_filtering.htm`](help/articles/ind.product_catalog_turn_on_price_book_filtering.htm.md) |
| **Custom Dynamic Addition Screen Flow** | Configurator | Replace the default add-products experience for a product classification with your own screen flow during bundle configuration. | [`ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm`](help/articles/ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm.md) |
| **Special Terms on Quotes** | Transaction Mgmt | Insert an active Document Clause Library clause as a quote special term and resolve its placeholder tokens. | [`ind.qocal_add_a_special_term_to_a_quote.htm`](help/articles/ind.qocal_add_a_special_term_to_a_quote.htm.md) |

**Scope:** this index is selective. It names the major feature clusters, and the feature tables link 118 of the 301 new article IDs (they also link 6 shared articles whose content expanded). The count comes from the captured manifests. For the complete list, diff the captured files in [`../262/help/manifest.json`](../262/help/manifest.json) and [`help/manifest.json`](help/manifest.json) (see **How this index was built**). Unlisted new IDs are mostly per-element, per-variable and setup sub-articles of the clusters above (for example the Rating element pages), but some smaller features may remain unclassified.

---

## Expanded / Newly Documented Features (existed in 262)

### Agentforce for Revenue Management

Approval Management Agent moved to **New Features in 264**: the 262 corpus has no approval-agent article, and 264 adds 4.

### Advanced Approvals

| Feature | Status | Description | Articles |
|---|---|---|---|
| Slack Integration | **Expanded** | Post approval notifications to Slack. | [`ind.approvals_slack_channel_notifications.htm`](help/articles/ind.approvals_slack_channel_notifications.htm.md) |
| Serial and Parallel Approvers | **Expanded** (1 → 4 articles) | Multi-stakeholder workflows. | [`ind.approvals_implement_serial_and_parallel_approvers.htm`](help/articles/ind.approvals_implement_serial_and_parallel_approvers.htm.md) |
| Smart / Rule-Based Auto-Approvals | **Expanded** | Automated approval logic. | [`ind.approvals_smart_or_rule_based_approvals.htm`](help/articles/ind.approvals_smart_or_rule_based_approvals.htm.md) |
| Approval Delegation | **Newly documented** (0 → 4 dedicated articles) | Delegate approval responsibilities for temporary coverage. 262 already referenced delegates (delegate notifications in `ind.approvals_email_templates.htm`; "Delegates don’t receive approval notifications in Slack"), so this is not counted as new. 264 adds dedicated setup articles. | 4 articles: [`ind.approvals_approval_delegation.htm`](help/articles/ind.approvals_approval_delegation.htm.md), [`ind.approvals_create_delegation_records.htm`](help/articles/ind.approvals_create_delegation_records.htm.md), [`ind.approvals_turn_on_delegation.htm`](help/articles/ind.approvals_turn_on_delegation.htm.md), [`ind.approvals_delegation_considerations.htm`](help/articles/ind.approvals_delegation_considerations.htm.md) |

### Billing (99 new articles, net +94)

| Feature | Status | Description | Key Articles |
|---|---|---|---|
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

| Feature | Status | Description | Articles |
|---|---|---|---|
| Context Definition Setup | **Expanded** | Set up for constraint engine, custom fields, Apex triggers. | [`ind.product_configurator_set_up_constraint_engine_context_definitions.htm`](help/articles/ind.product_configurator_set_up_constraint_engine_context_definitions.htm.md), [`ind.product_configurator_select_context_attributes.htm`](help/articles/ind.product_configurator_select_context_attributes.htm.md) |
| Rules Engine Transaction Types | **Expanded** | Define which constraint engine to use. | [`ind.product_configurator_specify_which_rule_engine_to_use.htm`](help/articles/ind.product_configurator_specify_which_rule_engine_to_use.htm.md) |

### Dynamic Revenue Orchestration (DRO)

| Feature | Status | Description | Articles |
|---|---|---|---|
| **Time-Aware Fulfillment** | **Expanded** (1 → 12 articles) | DRO decomposes multi-year ramps into FOLIs and FASPs aligned with period effective dates. Prevents overwrites on amendments. | [`ind.dro_time_aware_fulfillment.htm`](help/articles/ind.dro_time_aware_fulfillment.htm.md), [`ind.dro_time_aware_fulfillment_enable.htm`](help/articles/ind.dro_time_aware_fulfillment_enable.htm.md), [`ind.dro_time_aware_fulfillment_migration.htm`](help/articles/ind.dro_time_aware_fulfillment_migration.htm.md), [`ind.dro_time_aware_fulfillment_example_add.htm`](help/articles/ind.dro_time_aware_fulfillment_example_add.htm.md) |
| High Tech Order Orchestration Template | **Expanded** (15 → 21 articles on technical products overall) | Pre-built DRO template. | [`ind.dro_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_hi_tech_order_orchestration_template.htm.md), [`ind.dro_install_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_install_hi_tech_order_orchestration_template.htm.md) |
| Technical Product Catalog | **Expanded** | Build technical product catalog, create products/bundles. | [`ind.dro_technical_product_in_dro.htm`](help/articles/ind.dro_technical_product_in_dro.htm.md), [`ind.dro_creating_a_technical_product.htm`](help/articles/ind.dro_creating_a_technical_product.htm.md), [`ind.dro_technical_bundles.htm`](help/articles/ind.dro_technical_bundles.htm.md) |
| Future-Dated Steps | **Expanded** | Delay step execution relative to the source line start date, the previous step, or a context-definition date field. 262 had Turn On Future Dated Steps; 264 adds a configuration article. | [`ind.dro_configure_steps_for_future_execution.htm`](help/articles/ind.dro_configure_steps_for_future_execution.htm.md) |
| Fulfillment Workspaces | **Expanded** | Clone, configure deep cloning. | [`ind.dro_clone_a_fulfillment_workspace.htm`](help/articles/ind.dro_clone_a_fulfillment_workspace.htm.md), [`ind.dro_configure_fulfillment_workspace_deep_cloning.htm`](help/articles/ind.dro_configure_fulfillment_workspace_deep_cloning.htm.md) |
| Fulfillment Steps | **Expanded** | Define steps, create definition groups, configure scenarios, conditions. | [`ind.dro_define_a_fulfillment_step.htm`](help/articles/ind.dro_define_a_fulfillment_step.htm.md), [`ind.dro_create_a_fulfillment_step_definition_group.htm`](help/articles/ind.dro_create_a_fulfillment_step_definition_group.htm.md), [`ind.dro_custom_scope_step_dependencies.htm`](help/articles/ind.dro_custom_scope_step_dependencies.htm.md) |

### Product Catalog Management (PCM)

| Feature | Status | Description | Articles |
|---|---|---|---|
| Product Selling Model | **Expanded** | Manage, create, assign. | [`ind.product_catalog_product_selling_model.htm`](help/articles/ind.product_catalog_product_selling_model.htm.md), [`ind.product_catalog_create_a_product_selling_model.htm`](help/articles/ind.product_catalog_create_a_product_selling_model.htm.md) |
| Cardinality Management | **Expanded** | Group and local cardinality — manage, edit, override. | [`ind.product_catalog_group_cardinality.htm`](help/articles/ind.product_catalog_group_cardinality.htm.md), [`ind.product_catalog_local_cardinality.htm`](help/articles/ind.product_catalog_local_cardinality.htm.md) |
| Attribute Management | **Expanded** | Create categories/picklists, assign, reorder. | [`ind.product_catalog_dyn_create_attribute_categories.htm`](help/articles/ind.product_catalog_dyn_create_attribute_categories.htm.md), [`ind.product_catalog_assign_attributes_to_a_product_classification.htm`](help/articles/ind.product_catalog_assign_attributes_to_a_product_classification.htm.md) |
| List Price from Cache | **Expanded** | Cache price book list prices with product details. Extends the Product Detail Cache that 262 documented. | [`ind.product_catalog_turn_on_list_price_from_cache.htm`](help/articles/ind.product_catalog_turn_on_list_price_from_cache.htm.md) |
| Product Deep Cloning | **Expanded** | Deep clone products, set up. | [`ind.product_catalog_deep_clone_in_product_catalog_management.htm`](help/articles/ind.product_catalog_deep_clone_in_product_catalog_management.htm.md), [`ind.product_catalog_set_up_product_deep_clone.htm`](help/articles/ind.product_catalog_set_up_product_deep_clone.htm.md) |

### Salesforce Pricing

| Feature | Status | Description | Articles |
|---|---|---|---|
| **Price Adjustment Matrix** | **Expanded** (8 → 12 articles) | Dynamic pricing beyond volume discounts — custom decision tables with criteria/adjustments. | [`ind.pricing_add_the_price_adjustment_matrix_element.htm`](help/articles/ind.pricing_add_the_price_adjustment_matrix_element.htm.md), [`ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`](help/articles/ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm.md) |
| **Price Waterfall** | **Expanded** (39 → 57 articles) | Pricing transparency — detailed breakdown of additions/deductions. | [`ind.pricing_set_up_price_waterfall_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_price_waterfall_salesforce_pricing.htm.md), [`ind.pricing_enable_price_waterfall.htm`](help/articles/ind.pricing_enable_price_waterfall.htm.md), [`ind.pricing_set_price_waterfall_persistence.htm`](help/articles/ind.pricing_set_price_waterfall_persistence.htm.md) |
| Einstein Generative AI for Pricing | **Expanded** (1 → 5 articles) | Automate context tag mapping. | [`ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm.md), [`ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm.md) |
| Discovery Procedure | **Expanded** | Configure, discover pricing factors. | [`ind.pricing_set_up_your_discovery_procedure.htm`](help/articles/ind.pricing_set_up_your_discovery_procedure.htm.md), [`ind.pricing_discovery_procedure_for_pricing.htm`](help/articles/ind.pricing_discovery_procedure_for_pricing.htm.md) |
| Pricing Recipes | **Expanded** | Setup, create, sync decision tables. | [`ind.pricing_pricing_recipes.htm`](help/articles/ind.pricing_pricing_recipes.htm.md), [`ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`](help/articles/ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm.md) |
| Pricing Adjustment Batch Jobs | **Expanded** | Perform, fix/execute failed, view logs. | [`ind.pricing_pricing_adjustment_batch_jobs.htm`](help/articles/ind.pricing_pricing_adjustment_batch_jobs.htm.md), [`ind.pricing_perform_pricing_adjustment_batch_job.htm`](help/articles/ind.pricing_perform_pricing_adjustment_batch_job.htm.md) |

### Rate Management

| Feature | Status | Description | Articles |
|---|---|---|---|
| **Rating Elements (comprehensive)** | **Expanded** (35 → 70 articles, doubled) | Base Rate, Manual Rate Discount, Negotiated Base/Tier/Volume adjustments, Rate Adjustment Matrix, Rounding, Get Rate Cards/Entries. Each element now has dedicated article + variables + "Add" guide. | 35 new element articles including [`ind.rm_element_base_rate.htm`](help/articles/ind.rm_element_base_rate.htm.md), [`ind.rm_element_manual_rate_discount.htm`](help/articles/ind.rm_element_manual_rate_discount.htm.md), [`ind.rm_element_rate_adjustment_matrix.htm`](help/articles/ind.rm_element_rate_adjustment_matrix.htm.md), [`ind.rm_rating_elements.htm`](help/articles/ind.rm_rating_elements.htm.md) |

### Transaction Management

| Feature | Status | Description | Articles |
|---|---|---|---|
| **Ramp Deals** | **Expanded** | Considerations expanded +9,220 chars (+505%). Compound uplifts (new), groups vs lines transition, renewal price uplifts. | [`ind.qocal_considerations_ramp_deals.htm`](help/articles/ind.qocal_considerations_ramp_deals.htm.md), [`ind.qocal_ramp_deals_for_groups_transition.htm`](help/articles/ind.qocal_ramp_deals_for_groups_transition.htm.md), [`ind.qocal_renewal_price_uplifts.htm`](help/articles/ind.qocal_renewal_price_uplifts.htm.md) |
| Quote Line Item CSV Import | **Expanded** (6 → 9 articles) | Import from CSV, custom templates. Requires `Advanced CSV Data Import` permission set. | [`ind.qocal_qli_import_user_import_lines_csv.htm`](help/articles/ind.qocal_qli_import_user_import_lines_csv.htm.md), [`ind.qocal_set_up_quote_line_item_import.htm`](help/articles/ind.qocal_set_up_quote_line_item_import.htm.md) |
| Backdated Asset Transactions | **Expanded** | Backdate transactions, considerations. | [`ind.qocal_backdate_asset_transactions.htm`](help/articles/ind.qocal_backdate_asset_transactions.htm.md), [`ind.qocal_considerations_for_assets_with_backdated_changes.htm`](help/articles/ind.qocal_considerations_for_assets_with_backdated_changes.htm.md) |
| Usage-Based Asset Renewal | **Expanded** | Renew usage-based assets early (new renewal term, renegotiated rates and grants) or after expiry. 262 had one usage-based renewal article and said usage-based assets can't be renewed in ramp contexts. | [`ind.qocal_renew_usage_based_assets_early.htm`](help/articles/ind.qocal_renew_usage_based_assets_early.htm.md), [`ind.qocal_renew_expired_usage_based_assets.htm`](help/articles/ind.qocal_renew_expired_usage_based_assets.htm.md) |
| Tiered Contract Pricing | **Newly documented** | 262 linked to this setup topic from its contract-pricing articles; 264 captures it as a dedicated article. | [`ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm`](help/articles/ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm.md) |
| Zero-Quantity Quote Detail Lines | **Newly documented** | Why zero-quantity detail lines appear when a period's effective quantity is zero. 262 only mentioned zero quantity in amendment and renewal prose. | [`ind.qocal_zero_quantity_considerations.htm`](help/articles/ind.qocal_zero_quantity_considerations.htm.md) |
| Extract Product Mentions | **Newly documented** | Template that extracts products, quantities and attributes from emails, Slack messages or call summaries into quotes. 262 linked to `#qocal_extract_product_mentions` from its foundational setup article; 264 adds dedicated articles. | 2 articles: [`ind.qocal_extract_product_mentions.htm`](help/articles/ind.qocal_extract_product_mentions.htm.md), [`ind.qocal_example_extract_product_mentions.htm`](help/articles/ind.qocal_example_extract_product_mentions.htm.md) |
| Header-Level Action Buttons in STLE | **Expanded** | Choose which Sales Transaction Line Editor actions appear as standalone buttons, button groups or dropdown items. 262 already said to configure the placement and sequence of line-editor action buttons; 264 adds dedicated setup and considerations articles. | 2 articles: [`ind.qocal_configure_placement_of_action_buttons.htm`](help/articles/ind.qocal_configure_placement_of_action_buttons.htm.md), [`ind.qocal_action_button_group_important_considerations.htm`](help/articles/ind.qocal_action_button_group_important_considerations.htm.md) |
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

Of 830 articles captured in both releases, these had the largest absolute body changes, ranked by `body_length` delta in the two manifests:

1. **Considerations for Ramp Deals** ([`ind.qocal_considerations_ramp_deals.htm`](help/articles/ind.qocal_considerations_ramp_deals.htm.md)) — +9,220 chars (+505%)
2. **Best Practices for Apex Pricing Hooks** ([`ind.pricing_apex_hooks_best_practices.htm`](help/articles/ind.pricing_apex_hooks_best_practices.htm.md)) — +8,762 chars (+998%)
3. **Manage Collections for Accounts** ([`ind.billing_collections.htm`](help/articles/ind.billing_collections.htm.md)) — +3,564 chars (+132%)
4. **Configure Your Pricing Procedure** ([`ind.pricing_configure_pricing_procedure.htm`](help/articles/ind.pricing_configure_pricing_procedure.htm.md)) — +3,370 chars (+89%)
5. **Ramp Deal for Groups with Single Ramp Schedule** ([`ind.qocal_ramp_deal_for_groups_create.htm`](help/articles/ind.qocal_ramp_deal_for_groups_create.htm.md)) — -2,574 chars (-67%)
6. **Create Collection Plans and Collection Plan Items** ([`ind.billing_collection_plans_and_plan_items_create.htm`](help/articles/ind.billing_collection_plans_and_plan_items_create.htm.md)) — +2,574 chars (+248%; tied with #5)
7. **Ramp Deals in Revenue Management** ([`ind.qocal_ramp_deals_complex_long_term_multiple_products.htm`](help/articles/ind.qocal_ramp_deals_complex_long_term_multiple_products.htm.md)) — -2,570 chars (-50%)
8. **Create Ramp Deals for Groups with Multiple Ramp Schedules** ([`ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm`](help/articles/ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm.md)) — -2,538 chars (-68%)
9. **Use the Price Revision Element** ([`ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`](help/articles/ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm.md)) — +2,379 chars (+39%)
10. **Honor Precise Time Zones in Asset Lifecycle Dates** ([`ind.qocal_asset_lifecycle_date_time_precision.htm`](help/articles/ind.qocal_asset_lifecycle_date_time_precision.htm.md)) — +2,100 chars (+79%)

---

## Articles in 262 but not in the 264 capture

This covers removals, renames, 264 capture errors, and the uncaptured Collections area. Absence from the capture alone does not prove an article was removed.

### Billing (5 only in 262: 4 replaced or renamed, 1 with no dedicated replacement)

- **Configure Your Custom Metadata Types** (`ind.billing_custom_metadata_types_configure.htm`) — replaced by [`ind.billing_standard_tax_custom_metadata_types_configure.htm`](help/articles/ind.billing_standard_tax_custom_metadata_types_configure.htm.md) (tax-specific)
- **Generate Billing Schedules** (`ind.billing_schedules_create.htm`) — replaced by [`ind.billing_schedules_from_orders.htm`](help/articles/ind.billing_schedules_from_orders.htm.md)
- **Period Boundary and Proration in Billing Cycles** (`ind.billing_understand_period_boundries.htm`) — renamed: the same period-boundary guidance is in [`ind.billing_understand_period_boundaries_and_billing_day_of_month.htm`](help/articles/ind.billing_understand_period_boundaries_and_billing_day_of_month.htm.md)
- **Tax Interface Extension** (`ind.billing_understand_tax_interface_extension.htm`) — renamed: still documented in [`ind.billing_extend_tax_interface.htm`](help/articles/ind.billing_extend_tax_interface.htm.md)
- **Troubleshoot Invoice Batch Run Errors** (`ind.billing_invoice_batch_runs_troubleshooting.htm`) — no dedicated replacement found; invoice batch run errors are still covered in [`ind.billing_invoice_batch_run.htm`](help/articles/ind.billing_invoice_batch_run.htm.md)

### DRO (1 capture error, not a verified removal)

- **Create Custom Context Definition and Map Attribute to Field** (`ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm`). The 264 manifest discovered it but recorded a capture error, so its 264 status is unknown. Two new 264 DRO IDs also errored: `ind.dro_create_a_fulfillment_task_assignment_rule.htm` and `ind.dro_create_a_fulfillment_workspace.htm`. Re-run the DRO snapshot to capture all three.

### Transaction Management (2 only in 262, both reorganized)

- **Divide Subscription Transactions into Segments with Ramp Deals for Lines** (`ind.qocal_ramp_deals.htm`) — reorganized, not removed: 264 still documents Ramp Deals for Lines in [`ind.qocal_ramp_deals_for_groups_transition.htm`](help/articles/ind.qocal_ramp_deals_for_groups_transition.htm.md), which recommends moving to groups but allows both in parallel during migration
- **View Rate Cards for Usage-Based Assets** (`ind.qocal_view_asset_usage_rate_cards.htm`) — reorganized, not removed: asset rate-card visibility (the Usage Rates tab) is in [`ind.qocal_view_and_manage_assets_in_revenue_cloud.htm`](help/articles/ind.qocal_view_and_manage_assets_in_revenue_cloud.htm.md)

### Collections (97 not captured — not verified as removed)

All 97 Collections articles present in 262 are absent from 264 because the Collections area was **verified still serving 262 content** as of 2026-09-07. Collections snapshot intentionally not captured. Expected to be captured once 264-specific content publishes.

---

## Maintenance

### How to re-check this index

1. **Cross-reference the captured Winter '27 release notes** (`release-notes/`, refresh with `cci task run snapshot_revenue_release_notes_264 -o mode refresh`). Update tiers (GA/Beta/Pilot). Add features the notes cover that Help does not.
2. **Check the v68.0 Metadata Coverage Report** (availability not yet checked): if it is available, verify object/field/API changes match it.
3. **Refresh Collections snapshot** once 264 content publishes:
   ```bash
   cci task run snapshot_collections_help_264 -o mode discover
   # byte-diff shared articles against 262 to confirm changed-text signal
   # if ready: cci task run snapshot_collections_help_264
   ```
4. **When Solution Overview decks publish:** Add to Sources table, reconcile descriptions.

### How this index was built

1. Diffing the captured article files (manifest `status: captured`) of 262 and 264: 301 new, 105 only in 262, 830 in both. Discovery counts, which include the three errored 264 DRO IDs, are not used.
2. Grouping new articles by title patterns to identify features.
3. Reading sample articles from each feature group.
4. Computing body-length changes for shared articles.
5. Verifying removed articles to distinguish removals from renames.
6. **Grepping 262 corpus for each feature's key terms** to distinguish truly new from expanded/newly-documented.

Regenerate after corpus refreshes.
