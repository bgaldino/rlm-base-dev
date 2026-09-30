# Release 264 (Winter '27) — Feature Index

**Per-area inventory of features in Winter '27 / Release 264, derived from the Salesforce Help portal snapshot.** Release 264 was promoted to `main` on 2026-09-16; Help snapshots captured 2026-09-04 through 2026-09-07 for ten functional areas (1,131 articles across configurator, transaction_mgmt, billing, pcm, dro, pricing, rating, usage, agents, and approvals). Collections area not captured — still serving 262 content as of 2026-09-07.

> **Pre-GA status:** API v68.0 GA waves 2026-09-05 → 2026-10-10 are in progress as of 2026-09-29. This index derives from Help articles captured during early GA rollout. The feature inventory comes from the Help corpus only. The Winter '27 release notes are published on Help, and their Revenue section is captured under `docs/salesforce/264/release-notes/` (PR #480) and cross-referenced below (**Release-Note Cross-Reference**). A live 264 org remains the ground truth for behavioral verification.

## Sources

| File | Description |
|---|---|
| [`help/`](help/) | Salesforce Help snapshot — 1,131 articles captured 2026-09-04 through 2026-09-07 across 10 RC functional areas. Collections not captured — verified still serving 262 content. |
| [`release-notes/`](release-notes/) | Winter '27 (264) Revenue release notes — 127 articles under `release-notes.rn_revenue.htm`, captured by `snapshot_revenue_release_notes_264` and mapped in **Release-Note Cross-Reference**. The notes label no feature Beta or Pilot. Invoice Risk Scoring (Pilot) is labelled only in Help. |
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

| Feature | Area | Release note | Description | Articles |
|---|---|---|---|---|
| **Billing Forecast** | Billing | Yes: [1](release-notes/articles/release-notes.rn_billing_forecast.htm.md) | Estimate upcoming invoice charges before invoices are created. Finance/sales review projected charges. Console uses Tableau Next. Does not apply to milestone or usage charges. | 8 articles including [`ind.billing_forecast.htm`](help/articles/ind.billing_forecast.htm.md), [`ind.billing_forecast_enable.htm`](help/articles/ind.billing_forecast_enable.htm.md), [`ind.billing_forecast_console.htm`](help/articles/ind.billing_forecast_console.htm.md), [`ind.billing_forecast_example.htm`](help/articles/ind.billing_forecast_example.htm.md) |
| **Invoice Risk Scoring (Pilot)** | Billing | None (Help labels it Pilot) | Predict risk scores (likelihood of delayed/non-payment) using Data 360 + AI Accelerator. Scores categorized as Low/Medium/High. | 13 articles including [`ind.billing_invoice_risk_score.htm`](help/articles/ind.billing_invoice_risk_score.htm.md), [`ind.billing_invoice_risk_scoring.htm`](help/articles/ind.billing_invoice_risk_scoring.htm.md), [`ind.billing_invoice_risk_scoring_view_scores.htm`](help/articles/ind.billing_invoice_risk_scoring_view_scores.htm.md) |
| **Payment Reconciliation** | Billing | Yes: [1](release-notes/articles/release-notes.rn_billing_lockbox_reconciliation.htm.md) | Automate reconciliation of payment advice/proof with bank data using Document AI + vector search + Data 360. | 12 articles including [`ind.billing_payment_reconciliation.htm`](help/articles/ind.billing_payment_reconciliation.htm.md), [`ind.billing_payment_reconciliation_setup.htm`](help/articles/ind.billing_payment_reconciliation_setup.htm.md), [`ind.billing_payment_reconciliation_run.htm`](help/articles/ind.billing_payment_reconciliation_run.htm.md) |
| **Approval Agent** | Agentforce | Yes: [1](release-notes/articles/release-notes.rn_rev_agentforce_approvals_agent.htm.md) | Conversational approval lifecycle — submit, track, summarize, approve/reject from Salesforce/Slack. AI-generated summaries. Three subagents. | 4 articles: [`ind.rev_agent_approval_agent.htm`](help/articles/ind.rev_agent_approval_agent.htm.md), [`ind.rev_agent_topic_approval_management.htm`](help/articles/ind.rev_agent_topic_approval_management.htm.md), [`ind.rev_agent_topic_search_approval_records.htm`](help/articles/ind.rev_agent_topic_search_approval_records.htm.md), [`ind.rev_agent_topic_summarize_multiple_approval_work_items.htm`](help/articles/ind.rev_agent_topic_summarize_multiple_approval_work_items.htm.md) |
| **Compound Price Uplifts for Ramps** | Transaction Mgmt | Yes: [1](release-notes/articles/release-notes.rn_transaction_management_ramp_deal_compound_uplift.htm.md), [2](release-notes/articles/release-notes.rn_billing_price_uplifts_for_multiyear_ramp_dealsxml.htm.md), [3](release-notes/articles/release-notes.rn_pricing_reduce_pricing_errors_and_improve_deal_transparency_on_ramp_deals.htm.md) | Create ramp deals with standard or compound price uplifts. | 2 articles: [`ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift_sales_reps.htm.md), [`ind.qocal_ramp_deal_compound_uplift.htm`](help/articles/ind.qocal_ramp_deal_compound_uplift.htm.md) |
| **Invoice Aging** | Billing | Yes: [1](release-notes/articles/release-notes.rn_billing_invoice_aging_summaries.htm.md) | Invoice Aging for Account component: invoice counts, overdue invoices, aging buckets, and average and maximum age on Account and Order pages. | 2 articles: [`ind.billing_invoice_aging.htm`](help/articles/ind.billing_invoice_aging.htm.md), [`ind.billing_invoice_aging_component.htm`](help/articles/ind.billing_invoice_aging_component.htm.md) |
| **Billing Start Month and Next Billing Date Override** | Billing | None (Help only) | Billing schedule group fields you can update on existing groups. 262 documented billing day of month and the separate period boundary start month, but not these. | 3 articles: [`ind.billing_schedule_group_update.htm`](help/articles/ind.billing_schedule_group_update.htm.md), [`ind.billing_schedule_group_update_billing_start_month.htm`](help/articles/ind.billing_schedule_group_update_billing_start_month.htm.md), [`ind.billing_schedule_group_update_next_billing_date_override.htm`](help/articles/ind.billing_schedule_group_update_next_billing_date_override.htm.md) |
| **Exclude From Billing** | Billing | None (Help only) | A billing treatment value that skips billing schedules, groups and invoices for order items not ready to bill, without holding the whole order. | [`ind.billing_treatment_exclude_from_billing.htm`](help/articles/ind.billing_treatment_exclude_from_billing.htm.md) |
| **Prefix Matching and Partial Search** | PCM | Yes: [1](release-notes/articles/release-notes.rn_product_catalog_find_products_with_prefix_matching_and_partial_search.htm.md) | Prefix matching is on by default: a term of at least 3 characters matches the start of a searchable Product Name, Code or SKU (262 said prefix search was unsupported). Partial search is opt-in and matches any part of a Product Code or SKU, ignoring hyphens, spaces and similar characters. | 3 articles: [`ind.product_catalog_search_considerations.htm`](help/articles/ind.product_catalog_search_considerations.htm.md), [`ind.product_catalog_partial_search.htm`](help/articles/ind.product_catalog_partial_search.htm.md), [`ind.product_catalog_configure_partial_search.htm`](help/articles/ind.product_catalog_configure_partial_search.htm.md) |
| **Price Book Filtering** | PCM | Yes: [1](release-notes/articles/release-notes.rn_product_catalog_discover_products_faster_using_price_book_filters.htm.md) | Return only the products associated with the selected price book, for large catalogs with little price book overlap. | [`ind.product_catalog_turn_on_price_book_filtering.htm`](help/articles/ind.product_catalog_turn_on_price_book_filtering.htm.md) |
| **Custom Dynamic Addition Screen Flow** | Configurator | None (Help only) | Replace the default add-products experience for a product classification with your own screen flow during bundle configuration. | [`ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm`](help/articles/ind.product_configurator_set_up_a_custom_dynamic_addition_screen_flow.htm.md) |
| **Special Terms on Quotes** | Transaction Mgmt | Yes: [1](release-notes/articles/release-notes.rn_salesforce_contracts_add_clauses_to_quotes.htm.md) | Insert an active Document Clause Library clause as a quote special term and resolve its placeholder tokens. | [`ind.qocal_add_a_special_term_to_a_quote.htm`](help/articles/ind.qocal_add_a_special_term_to_a_quote.htm.md) |
| **Backdated Asset Transactions** | Transaction Mgmt | Yes: [1](release-notes/articles/release-notes.rn_transaction_management_backdated_arc_for_ramps.htm.md), [2](release-notes/articles/release-notes.rn_transaction_management_backdate_asset_transactions.htm.md) | Backdate asset amendments, renewals and cancellations, with considerations. 262 said "You can't back-date transactions" (`ind.qocal_future_dated_order_amendments_important_considerations.htm`); the 264 release note "Gain Transaction Flexibility with Backdated Asset Changes" introduces it. | 2 articles: [`ind.qocal_backdate_asset_transactions.htm`](help/articles/ind.qocal_backdate_asset_transactions.htm.md), [`ind.qocal_considerations_for_assets_with_backdated_changes.htm`](help/articles/ind.qocal_considerations_for_assets_with_backdated_changes.htm.md) |

**Scope:** this index is selective. It names the major feature clusters, and the feature tables link 118 of the 301 new article IDs (they also link 6 shared articles whose content expanded). The count comes from the captured manifests. For the complete list, diff the captured files in [`../262/help/manifest.json`](../262/help/manifest.json) and [`help/manifest.json`](help/manifest.json) (see **How this index was built**). Unlisted new IDs are mostly per-element, per-variable and setup sub-articles of the clusters above (for example the Rating element pages), but some smaller features may remain unclassified.

---

## Expanded / Newly Documented Features (existed in 262)

### Agentforce for Revenue Management

Approval Agent (the published name; Approval Management is one of its three subagents) moved to **New Features in 264**: the 262 corpus has no approval-agent article, and 264 adds 4.

### Advanced Approvals

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| Slack Integration | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_adv_approvals_slack_notifications.htm.md) | Post approval notifications to Slack. | [`ind.approvals_slack_channel_notifications.htm`](help/articles/ind.approvals_slack_channel_notifications.htm.md) |
| Serial and Parallel Approvers | **Expanded** (3 → 5 approvals articles mention parallel) | None | Multi-stakeholder workflows. 262 already described serial and parallel workflows; 264 adds dedicated types-of-approvals and serial/parallel setup articles. | [`ind.approvals_implement_serial_and_parallel_approvers.htm`](help/articles/ind.approvals_implement_serial_and_parallel_approvers.htm.md) |
| Smart / Rule-Based Auto-Approvals | **Expanded** | None | Automated approval logic. | [`ind.approvals_smart_or_rule_based_approvals.htm`](help/articles/ind.approvals_smart_or_rule_based_approvals.htm.md) |
| Approval Delegation | **Newly documented** (0 → 4 articles with delegation in the ID) | Yes: [1](release-notes/articles/release-notes.rn_adv_approvals_approval_delegation.htm.md) | Delegate approval responsibilities for temporary coverage. 262 already referenced delegates (delegate notifications in `ind.approvals_email_templates.htm`; "Delegates don’t receive approval notifications in Slack"), so this is not counted as new. 264 adds dedicated setup articles. | 4 articles: [`ind.approvals_approval_delegation.htm`](help/articles/ind.approvals_approval_delegation.htm.md), [`ind.approvals_create_delegation_records.htm`](help/articles/ind.approvals_create_delegation_records.htm.md), [`ind.approvals_turn_on_delegation.htm`](help/articles/ind.approvals_turn_on_delegation.htm.md), [`ind.approvals_delegation_considerations.htm`](help/articles/ind.approvals_delegation_considerations.htm.md) |

### Billing (99 new articles, net +94)

| Feature | Status | Release note | Description | Key Articles |
|---|---|---|---|---|
| Collections & Dunning | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_collections_specialist_console.htm.md) | Collections Specialist Console, dunning orchestration, collection plans/items. | [`ind.billing_collections.htm`](help/articles/ind.billing_collections.htm.md) (+3,564 chars), [`ind.billing_collections_specialist_console.htm`](help/articles/ind.billing_collections_specialist_console.htm.md), [`ind.billing_configure_dunning_orchestration.htm`](help/articles/ind.billing_configure_dunning_orchestration.htm.md) |
| Change Billing Frequency | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_change_frequency_arc.htm.md), [2](release-notes/articles/release-notes.rn_billing_weekly_cycle.htm.md) | Change frequency on new/existing subscriptions. | [`ind.billing_change_billing_pricing_frequencies.htm`](help/articles/ind.billing_change_billing_pricing_frequencies.htm.md), [`ind.billing_change_billing_frequency_examples.htm`](help/articles/ind.billing_change_billing_frequency_examples.htm.md) |
| Refunds & Credit Management | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_issue_credits_as_refunds.htm.md) | Issue refunds, unreferenced refunds, rule-based application. Unreferenced refunds are new in 264 (0 → 3 articles mention them). | [`ind.billing_refunds_overview.htm`](help/articles/ind.billing_refunds_overview.htm.md), [`ind.billing_unreferenced_refunds.htm`](help/articles/ind.billing_unreferenced_refunds.htm.md), [`ind.billing_setup_credit_memos_payments_application_rules.htm`](help/articles/ind.billing_setup_credit_memos_payments_application_rules.htm.md) |
| Tax Engine Framework | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_extend_tax_engine.htm.md) | Create tax engines/providers, extend Revenue Standard Tax Engine. | [`ind.billing_tax_engine_create.htm`](help/articles/ind.billing_tax_engine_create.htm.md), [`ind.billing_extend_revenue_standard_tax_engine.htm`](help/articles/ind.billing_extend_revenue_standard_tax_engine.htm.md), [`ind.billing_tax_policies_and_treatments_create.htm`](help/articles/ind.billing_tax_policies_and_treatments_create.htm.md) |
| Invoice Previews | **Expanded** | None | Generate previews for orders, accounts, billing schedule groups. | [`ind.billing_preview_invoice.htm`](help/articles/ind.billing_preview_invoice.htm.md), [`ind.billing_invoice_preview_create.htm`](help/articles/ind.billing_invoice_preview_create.htm.md) |
| Invoice Operations | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_review_split_invoices.htm.md) | Delete, write off, review split invoices, convert to async. | [`ind.billing_invoice_delete.htm`](help/articles/ind.billing_invoice_delete.htm.md), [`ind.billing_write_off_invoice_balance.htm`](help/articles/ind.billing_write_off_invoice_balance.htm.md), [`ind.billing_invoice_run_sync_process.htm`](help/articles/ind.billing_invoice_run_sync_process.htm.md) |
| Billing Schedule Management | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_billing_catch_up_bill_runs.htm.md), [2](release-notes/articles/release-notes.rn_billing_future_dated_suspensions.htm.md), [3](release-notes/articles/release-notes.rn_billing_schedule_timelines.htm.md) | Generate from orders, update groups, suspend/resume, APIs. | [`ind.billing_schedules_from_orders.htm`](help/articles/ind.billing_schedules_from_orders.htm.md), [`ind.billing_suspend_and_resume_overview.htm`](help/articles/ind.billing_suspend_and_resume_overview.htm.md), [`ind.billing_catch_up_bill_runs.htm`](help/articles/ind.billing_catch_up_bill_runs.htm.md) |
| General Ledger | **Expanded** | None | GL account assignment rules, FX gains/losses, legal entity periods. | [`ind.billing_general_ledger_account_assignment_rules_create.htm`](help/articles/ind.billing_general_ledger_account_assignment_rules_create.htm.md), [`ind.billing_foreign_exchange_realized_gains_and_losses.htm`](help/articles/ind.billing_foreign_exchange_realized_gains_and_losses.htm.md) |
| Debit Memos & Policies | **Expanded** | None | Create debit memos, billing policies/treatments. | [`ind.billing_debit_memo_create.htm`](help/articles/ind.billing_debit_memo_create.htm.md), [`ind.billing_policies_and_treatments_create.htm`](help/articles/ind.billing_policies_and_treatments_create.htm.md) |

### Product Configurator

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| Context Definition Setup | **Expanded** | None | Set up for constraint engine, custom fields, Apex triggers. | [`ind.product_configurator_set_up_constraint_engine_context_definitions.htm`](help/articles/ind.product_configurator_set_up_constraint_engine_context_definitions.htm.md), [`ind.product_configurator_select_context_attributes.htm`](help/articles/ind.product_configurator_select_context_attributes.htm.md) |
| Rules Engine Transaction Types | **Expanded** | None | Define which constraint engine to use. | [`ind.product_configurator_specify_which_rule_engine_to_use.htm`](help/articles/ind.product_configurator_specify_which_rule_engine_to_use.htm.md) |

### Dynamic Revenue Orchestration (DRO)

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| **Time-Aware Fulfillment** | **Expanded** (1 → 12 articles mention time-aware) | Yes: [1](release-notes/articles/release-notes.rn_dro_optimize_multiyear_orchestration.htm.md), [2](release-notes/articles/release-notes.rn_dro_backdated_future_dated_amendments.htm.md), [3](release-notes/articles/release-notes.rn_dro_staged_assetization_ramped_products.htm.md) | DRO decomposes multi-year ramps into FOLIs and FASPs aligned with period effective dates. Prevents overwrites on amendments. A Staged Assetize step creates ramp-segment assets during plan execution; it works only for time-aware fulfillment assets. | [`ind.dro_time_aware_fulfillment.htm`](help/articles/ind.dro_time_aware_fulfillment.htm.md), [`ind.dro_ramp_deal_decomposition.htm`](help/articles/ind.dro_ramp_deal_decomposition.htm.md), [`ind.dro_time_aware_fulfillment_enable.htm`](help/articles/ind.dro_time_aware_fulfillment_enable.htm.md), [`ind.dro_time_aware_fulfillment_migration.htm`](help/articles/ind.dro_time_aware_fulfillment_migration.htm.md), [`ind.dro_time_aware_fulfillment_example_add.htm`](help/articles/ind.dro_time_aware_fulfillment_example_add.htm.md) |
| High Tech Order Orchestration Template | **Expanded** (15 → 21 articles mention technical product) | Yes: [1](release-notes/articles/release-notes.rn_dro_hightech_orch_with_salesforce_go.htm.md) | Pre-built DRO template. | [`ind.dro_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_hi_tech_order_orchestration_template.htm.md), [`ind.dro_install_hi_tech_order_orchestration_template.htm`](help/articles/ind.dro_install_hi_tech_order_orchestration_template.htm.md) |
| Technical Product Catalog | **Expanded** | None | Build technical product catalog, create products/bundles. | [`ind.dro_technical_product_in_dro.htm`](help/articles/ind.dro_technical_product_in_dro.htm.md), [`ind.dro_creating_a_technical_product.htm`](help/articles/ind.dro_creating_a_technical_product.htm.md), [`ind.dro_technical_bundles.htm`](help/articles/ind.dro_technical_bundles.htm.md) |
| Future-Dated Steps | **Expanded** | None | Delay step execution relative to the source line start date, the previous step, or a context-definition date field. 262 had Turn On Future Dated Steps; 264 adds a configuration article. | [`ind.dro_configure_steps_for_future_execution.htm`](help/articles/ind.dro_configure_steps_for_future_execution.htm.md) |
| Fulfillment Workspaces | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_dro_clone_fulfillment_workspaces.htm.md) | Clone, configure deep cloning. | [`ind.dro_clone_a_fulfillment_workspace.htm`](help/articles/ind.dro_clone_a_fulfillment_workspace.htm.md), [`ind.dro_configure_fulfillment_workspace_deep_cloning.htm`](help/articles/ind.dro_configure_fulfillment_workspace_deep_cloning.htm.md) |
| Fulfillment Steps | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_dro_custom_fulfillment_scopes.htm.md) | Define steps, create definition groups, configure scenarios, conditions. | [`ind.dro_define_a_fulfillment_step.htm`](help/articles/ind.dro_define_a_fulfillment_step.htm.md), [`ind.dro_create_a_fulfillment_step_definition_group.htm`](help/articles/ind.dro_create_a_fulfillment_step_definition_group.htm.md), [`ind.dro_custom_scope_step_dependencies.htm`](help/articles/ind.dro_custom_scope_step_dependencies.htm.md) |

### Product Catalog Management (PCM)

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| Product Selling Model | **Expanded** | None | Manage, create, assign. | [`ind.product_catalog_product_selling_model.htm`](help/articles/ind.product_catalog_product_selling_model.htm.md), [`ind.product_catalog_create_a_product_selling_model.htm`](help/articles/ind.product_catalog_create_a_product_selling_model.htm.md) |
| Cardinality Management | **Expanded** | None | Group and local cardinality — manage, edit, override. | [`ind.product_catalog_group_cardinality.htm`](help/articles/ind.product_catalog_group_cardinality.htm.md), [`ind.product_catalog_local_cardinality.htm`](help/articles/ind.product_catalog_local_cardinality.htm.md) |
| Attribute Management | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_product_catalog_display_order_attributes.htm.md) | Create categories/picklists, assign, reorder. | [`ind.product_catalog_dyn_create_attribute_categories.htm`](help/articles/ind.product_catalog_dyn_create_attribute_categories.htm.md), [`ind.product_catalog_assign_attributes_to_a_product_classification.htm`](help/articles/ind.product_catalog_assign_attributes_to_a_product_classification.htm.md) |
| List Price from Cache | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_product_catalog_get_faster_product_pricing_with_list_price_caching.htm.md) | Cache price book list prices with product details. Extends the Product Detail Cache that 262 documented. | [`ind.product_catalog_turn_on_list_price_from_cache.htm`](help/articles/ind.product_catalog_turn_on_list_price_from_cache.htm.md) |
| Product Deep Cloning | **Expanded** | None | Deep clone products, set up. | [`ind.product_catalog_deep_clone_in_product_catalog_management.htm`](help/articles/ind.product_catalog_deep_clone_in_product_catalog_management.htm.md), [`ind.product_catalog_set_up_product_deep_clone.htm`](help/articles/ind.product_catalog_set_up_product_deep_clone.htm.md) |

### Salesforce Pricing

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| **Price Adjustment Matrix** | **Expanded** (8 → 12 articles mention it) | None | Dynamic pricing beyond volume discounts — custom decision tables with criteria/adjustments. | [`ind.pricing_add_the_price_adjustment_matrix_element.htm`](help/articles/ind.pricing_add_the_price_adjustment_matrix_element.htm.md), [`ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`](help/articles/ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm.md) |
| **Price Waterfall** | **Expanded** (39 → 57 articles mention it) | None | Pricing transparency — detailed breakdown of additions/deductions. | [`ind.pricing_set_up_price_waterfall_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_price_waterfall_salesforce_pricing.htm.md), [`ind.pricing_enable_price_waterfall.htm`](help/articles/ind.pricing_enable_price_waterfall.htm.md), [`ind.pricing_set_price_waterfall_persistence.htm`](help/articles/ind.pricing_set_price_waterfall_persistence.htm.md) |
| Einstein Generative AI for Pricing | **Expanded** (10 → 14 articles mention Einstein generative AI) | None | Automate context tag mapping. | [`ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_einstein_generative_ai_for_salesforce_pricing.htm.md), [`ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm`](help/articles/ind.pricing_set_up_einstein_generative_ai_for_salesforce_pricing.htm.md) |
| Discovery Procedure | **Expanded** | None | Configure, discover pricing factors. | [`ind.pricing_set_up_your_discovery_procedure.htm`](help/articles/ind.pricing_set_up_your_discovery_procedure.htm.md), [`ind.pricing_discovery_procedure_for_pricing.htm`](help/articles/ind.pricing_discovery_procedure_for_pricing.htm.md) |
| Pricing Recipes | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_pricing_tailor_pricing_rules_for_multiple_industry_clouds.htm.md) | Setup, create, sync decision tables. | [`ind.pricing_pricing_recipes.htm`](help/articles/ind.pricing_pricing_recipes.htm.md), [`ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm`](help/articles/ind.pricing_sync_decision_tables_in_a_pricing_recipe.htm.md) |
| Pricing Adjustment Batch Jobs | **Expanded** | None | Perform, fix/execute failed, view logs. | [`ind.pricing_pricing_adjustment_batch_jobs.htm`](help/articles/ind.pricing_pricing_adjustment_batch_jobs.htm.md), [`ind.pricing_perform_pricing_adjustment_batch_job.htm`](help/articles/ind.pricing_perform_pricing_adjustment_batch_job.htm.md) |

### Rate Management

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| **Rating Elements (comprehensive)** | **Expanded** (Rating area 35 → 70 captured articles, doubled) | None | Base Rate, Manual Rate Discount, Negotiated Base/Tier/Volume adjustments, Rate Adjustment Matrix, Rounding, Get Rate Cards/Entries. New pages are mostly per-element articles, with variables and "Add" pages for many (not all) elements. | 35 new articles including [`ind.rm_element_base_rate.htm`](help/articles/ind.rm_element_base_rate.htm.md), [`ind.rm_element_manual_rate_discount.htm`](help/articles/ind.rm_element_manual_rate_discount.htm.md), [`ind.rm_element_rate_adjustment_matrix.htm`](help/articles/ind.rm_element_rate_adjustment_matrix.htm.md). Shared overview (also in 262): [`ind.rm_rating_elements.htm`](help/articles/ind.rm_rating_elements.htm.md) |

### Transaction Management

| Feature | Status | Release note | Description | Articles |
|---|---|---|---|---|
| **Ramp Deals** | **Expanded** | None | Considerations expanded +9,220 chars (+505%). Compound uplifts (new), groups vs lines transition, renewal price uplifts. | [`ind.qocal_considerations_ramp_deals.htm`](help/articles/ind.qocal_considerations_ramp_deals.htm.md), [`ind.qocal_ramp_deals_for_groups_transition.htm`](help/articles/ind.qocal_ramp_deals_for_groups_transition.htm.md), [`ind.qocal_renewal_price_uplifts.htm`](help/articles/ind.qocal_renewal_price_uplifts.htm.md) |
| Quote Line Item CSV Import | **Expanded** (6 → 10 articles mention quote line item import or import lines) | None | Import from CSV, custom templates. Requires `Advanced CSV Data Import` permission set. | [`ind.qocal_qli_import_user_import_lines_csv.htm`](help/articles/ind.qocal_qli_import_user_import_lines_csv.htm.md), [`ind.qocal_set_up_quote_line_item_import.htm`](help/articles/ind.qocal_set_up_quote_line_item_import.htm.md) |
| Usage-Based Asset Renewal | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_um_renew_active_usage_assets_early.htm.md), [2](release-notes/articles/release-notes.rn_um_renew_ramped_usage_assets_early.htm.md), [3](release-notes/articles/release-notes.rn_um_renew_expired_usage_assets.htm.md) | Renew usage-based assets early (new renewal term, renegotiated rates and grants) or after expiry. 262 had one usage-based renewal article and said usage-based assets can't be renewed in ramp contexts. | [`ind.qocal_renew_usage_based_assets_early.htm`](help/articles/ind.qocal_renew_usage_based_assets_early.htm.md), [`ind.qocal_renew_expired_usage_based_assets.htm`](help/articles/ind.qocal_renew_expired_usage_based_assets.htm.md) |
| Tiered Contract Pricing | **Newly documented** | None | 262 linked to this setup topic from its contract-pricing articles; 264 captures it as a dedicated article. | [`ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm`](help/articles/ind.qocal_use_tiered_volume_and_pricing_in_contract_pricing.htm.md) |
| Zero-Quantity Quote Detail Lines | **Newly documented** | None | Why zero-quantity detail lines appear when a period's effective quantity is zero. 262 only mentioned zero quantity in amendment and renewal prose. | [`ind.qocal_zero_quantity_considerations.htm`](help/articles/ind.qocal_zero_quantity_considerations.htm.md) |
| Extract Product Mentions | **Newly documented** | None | Template that extracts products, quantities and attributes from emails, Slack messages or call summaries into quotes. 262 linked to `#qocal_extract_product_mentions` from its foundational setup article; 264 adds dedicated articles. | 2 articles: [`ind.qocal_extract_product_mentions.htm`](help/articles/ind.qocal_extract_product_mentions.htm.md), [`ind.qocal_example_extract_product_mentions.htm`](help/articles/ind.qocal_example_extract_product_mentions.htm.md) |
| Header-Level Action Buttons in STLE | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_transaction_management_stle_enhance_button_groups.htm.md) | Choose which Sales Transaction Line Editor actions appear as standalone buttons, button groups or dropdown items. 262 already said to configure the placement and sequence of line-editor action buttons; 264 adds dedicated setup and considerations articles. | 2 articles: [`ind.qocal_configure_placement_of_action_buttons.htm`](help/articles/ind.qocal_configure_placement_of_action_buttons.htm.md), [`ind.qocal_action_button_group_important_considerations.htm`](help/articles/ind.qocal_action_button_group_important_considerations.htm.md) |
| Contract Cotermination | **Expanded** | None | Coterminate subscription assets with contract end dates. | [`ind.qocal_coterminate_with_contract_end_date.htm`](help/articles/ind.qocal_coterminate_with_contract_end_date.htm.md) |
| Context Service Extension | **Expanded** | None | Extend/map sales transactions, context definitions, custom fields. | [`ind.qocal_extend_your_transactions_with_custom_field_support.htm`](help/articles/ind.qocal_extend_your_transactions_with_custom_field_support.htm.md), [`ind.qocal_map_custom_fields.htm`](help/articles/ind.qocal_map_custom_fields.htm.md) |
| Transaction Summary | **Expanded** | Yes: [1](release-notes/articles/release-notes.rn_transaction_management_stle_enhance_autorefresh.htm.md) | Customize, turn on auto-refresh. Auto-refresh is new in 264 (0 → 3 articles mention it; release note "Edit Accurate Quotes and Orders in Sales Transaction Line Editor with Autorefresh"). | [`ind.qocal_customize_transaction_summary.htm`](help/articles/ind.qocal_customize_transaction_summary.htm.md), [`ind.qocal_auto_refresh_stle_transaction_summary_help.htm`](help/articles/ind.qocal_auto_refresh_stle_transaction_summary_help.htm.md) |

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

## Release-Note Cross-Reference

The Winter '27 Revenue release notes ([`release-notes/`](release-notes/), 127 articles) contain 22 section pages, 17 reference notes and 88 feature notes. This section maps each feature note to the index row that covers the same capability.

- **37 of the 88 feature notes map onto 27 index rows.** The other 51 have no index row, because the corpus diff did not surface them as a feature cluster. Examples are Large Transactions, Promotions, most of Salesforce Contracts and the billing-portal payment notes. Consider them first when the index is extended.
- **Tier:** no note is labelled Beta or Pilot, so a note's presence is read as GA; confirm on a live org at GA. One note is a Release Update: opt-in now, enforced in Summer '27. Invoice Risk Scoring is Pilot by its Help titles and has no release note. Three other New rows (Billing Start Month and Next Billing Date Override, Exclude From Billing, Custom Dynamic Addition Screen Flow) also have none and rest on Help alone.
- The mapping was done by hand. The license column summarizes the licenses and prerequisites in the note's `Where:` line, with "Revenue Cloud" and "license" dropped. Shared prerequisites follow `+`, alternatives are parenthesized when a prerequisite applies to all of them (a comma separates an alternative that needs no prerequisite), and license conditions or exclusions from later sentences (including `Who:` and `Note:` lines) follow a semicolon. Edition and Lightning Experience limits and the permission sets named in `Who:` lines are left out, so the column is not a setup checklist; read each note for full eligibility.

### Advanced Approvals (3)

| Release note | License or requirement | Index row |
|---|---|---|
| [Extend Slack Approval Notifications to Group and Queue Members](release-notes/articles/release-notes.rn_adv_approvals_slack_notifications.htm.md) | Advanced Approvals enabled | Slack Integration |
| [Keep Approval Workflows Moving with Advanced Approval Delegation](release-notes/articles/release-notes.rn_adv_approvals_approval_delegation.htm.md) | Advanced Approvals enabled | Approval Delegation |
| [Limit Approval Work Item Visibility to Keep Review Steps Confidential](release-notes/articles/release-notes.rn_adv_approvals_work_item_sharing.htm.md) | Advanced Approvals or Flow Approval Processes enabled | *not in index* |

### Agentforce for Revenue Management (1)

| Release note | License or requirement | Index row |
|---|---|---|
| [Accelerate Approval Decisions with Approval Agent](release-notes/articles/release-notes.rn_rev_agentforce_approvals_agent.htm.md) | Advanced Approvals and Agentforce enabled | Approval Agent |

### Billing (24)

| Release note | License or requirement | Index row |
|---|---|---|
| [Accept Regional Payment Methods in the Self-Service Billing Portal Through Native Gateways](release-notes/articles/release-notes.rn_billing_regional_payment_methods.htm.md) | Billing | *not in index* |
| [Add Billing Self-Service Components in LWR Experience Cloud Sites](release-notes/articles/release-notes.rn_billing_self_service_components_lwr.htm.md) | Billing | *not in index* |
| [Advance Migrated Billing Schedules Without Rebilling by Using Catch-Up Bill Runs](release-notes/articles/release-notes.rn_billing_catch_up_bill_runs.htm.md) | Advanced or Billing | Billing Schedule Management |
| [Automate Compound Price Uplifts for Multiyear Ramp Deals](release-notes/articles/release-notes.rn_billing_price_uplifts_for_multiyear_ramp_dealsxml.htm.md) | Advanced | Compound Price Uplifts for Ramps |
| [Bill Every Few Weeks, Months, or Years Instead of Every Term](release-notes/articles/release-notes.rn_billing_term_units.htm.md) | Advanced or Billing | *not in index* |
| [Change Billing Frequency on Active Subscriptions Anytime](release-notes/articles/release-notes.rn_billing_change_frequency_arc.htm.md) | Advanced or Billing | Change Billing Frequency |
| [Extend the Revenue Standard Tax Engine to Match Your Tax Rules](release-notes/articles/release-notes.rn_billing_extend_tax_engine.htm.md) | Advanced or Billing | Tax Engine Framework |
| [Generate Context-Rich Sequence Patterns with Dynamic Fields](release-notes/articles/release-notes.rn_billing_dynamic_sequence_patterns.htm.md) | Billing | *not in index* |
| [Generate Invoice Documents Automatically During Invoice Batch Runs](release-notes/articles/release-notes.rn_billing_generate_invoice_documents_batch.htm.md) | Billing | *not in index* |
| [Generate Invoices Across Accounts for Owned and Billed Charges](release-notes/articles/release-notes.rn_billing_generate_invoices_across_accounts.htm.md) | Billing | *not in index* |
| [Honor Future-Dated Billing Suspensions During Invoicing](release-notes/articles/release-notes.rn_billing_future_dated_suspensions.htm.md) | Advanced or Billing | Billing Schedule Management |
| [Orchestrate Cart-to-Cash Checkout Flow With a Single API Call](release-notes/articles/release-notes.rn_billing_api_updates.htm.md) | Billing | *not in index* |
| [Preview Future Invoice Charges with Billing Forecast](release-notes/articles/release-notes.rn_billing_forecast.htm.md) | Billing; the Billing Forecast Console also needs Tableau Next Consumer | Billing Forecast |
| [Prioritize Collections with Invoice Aging Summaries on Accounts](release-notes/articles/release-notes.rn_billing_invoice_aging_summaries.htm.md) | Billing | Invoice Aging |
| [Prioritize and Act on Overdue Invoices in the Collections Specialist Console](release-notes/articles/release-notes.rn_billing_collections_specialist_console.htm.md) | Billing | Collections & Dunning |
| [Reconcile Payment Advice and Bank Data with Lockbox Processing](release-notes/articles/release-notes.rn_billing_lockbox_reconciliation.htm.md) | Billing | Payment Reconciliation |
| [Refund Available Credit Balances to Customer Accounts](release-notes/articles/release-notes.rn_billing_issue_credits_as_refunds.htm.md) | Billing | Refunds & Credit Management |
| [Review All Impacted Split Invoices Before Posting, Voiding, or Deleting](release-notes/articles/release-notes.rn_billing_review_split_invoices.htm.md) | Billing | Invoice Operations |
| [Save Digital Wallets for Future Invoice Payments](release-notes/articles/release-notes.rn_billing_save_digital_wallets.htm.md) | Billing | *not in index* |
| [Send Level 2 and Level 3 Payment Data Through a Native Payment Gateway](release-notes/articles/release-notes.rn_billing_send_l2_l3_data_native.htm.md) | Billing | *not in index* |
| [Set Invoice Target Dates by Calendar Day or Billing Period Count](release-notes/articles/release-notes.rn_billing_target_date_flexibility.htm.md) | Advanced or Billing | *not in index* |
| [Support Flexible Billing With Weekly Cadences](release-notes/articles/release-notes.rn_billing_weekly_cycle.htm.md) | Advanced or Billing | Change Billing Frequency |
| [Track Ramp Deal Details on Billing Schedules](release-notes/articles/release-notes.rn_billing_track_ramp_deal_details.htm.md) | Advanced | *not in index* |
| [Visualize Billing Schedule Lifecycles with Timelines](release-notes/articles/release-notes.rn_billing_schedule_timelines.htm.md) | Advanced or Billing | Billing Schedule Management |

### Dynamic Revenue Orchestrator (7)

| Release note | License or requirement | Index row |
|---|---|---|
| [Align Fulfillment Dependencies by Using Custom Scopes](release-notes/articles/release-notes.rn_dro_custom_fulfillment_scopes.htm.md) | Advanced | Fulfillment Steps |
| [Automate Multiyear Ramp Deal Orchestration with Sequenced Steps](release-notes/articles/release-notes.rn_dro_optimize_multiyear_orchestration.htm.md) | Advanced | Time-Aware Fulfillment |
| [Clone and Reuse Fulfillment Workspaces](release-notes/articles/release-notes.rn_dro_clone_fulfillment_workspaces.htm.md) | Advanced | Fulfillment Workspaces |
| [Eliminate Fulfillment Delays by Using Staged Assetization for Ramped Products](release-notes/articles/release-notes.rn_dro_staged_assetization_ramped_products.htm.md) | Advanced | Time-Aware Fulfillment |
| [Navigate Orders Easily with the Enhanced Decomposition Viewer](release-notes/articles/release-notes.rn_dro_enhanced_decomposition_viewer.htm.md) | Advanced | *not in index* |
| [Orchestrate Backdated and Future-Dated Contract Changes Automatically](release-notes/articles/release-notes.rn_dro_backdated_future_dated_amendments.htm.md) | Advanced | Time-Aware Fulfillment |
| [Streamline Fulfillment of Ramped Asset Amendments](release-notes/articles/release-notes.rn_dro_fulfill_ramped_asset_amendments.htm.md) | Advanced | *not in index* |

### Large Transactions and Quote Processing (7)

| Release note | License or requirement | Index row |
|---|---|---|
| [Apply Configuration Rules Across 15,000 Line Items](release-notes/articles/release-notes.rn_large_txn_apply_configuration_rules.htm.md) | Growth or Advanced | *not in index* |
| [Generate Documents for Quotes with 15,000 Line Items](release-notes/articles/release-notes.rn_large_txn_generate_documents_for_quotes_with_15_000.htm.md) | Growth or Advanced | *not in index* |
| [Price Quotes and Orders with Up to 15,000 Lines](release-notes/articles/release-notes.rn_large_txn_price_quotes_and_orders.htm.md) | Growth or Advanced | *not in index* |
| [Recover Faster from Quote and Order Calculation Errors](release-notes/articles/release-notes.rn_large_txn_recover_faster_from_quote_and_order_calculation_errors.htm.md) | Growth or Advanced | *not in index* |
| [Speed Up Large Quote Operations with Automatic Context Reuse](release-notes/articles/release-notes.rn_large_txn_speed_up_large_quote_operations_with_automatic_context_reuse.htm.md) | Growth or Advanced | *not in index* |
| [Sync Large Quotes to Opportunities Without Interruption](release-notes/articles/release-notes.rn_large_txn_sync_large_quotes_to_opportunities.htm.md) | Growth or Advanced | *not in index* |
| [Transform Context Data in Large Transactions](release-notes/articles/release-notes.rn_large_txn_transform_context_data_in_large_transactions.htm.md) | Advanced or Billing | *not in index* |

### Product Catalog Management (7)

| Release note | License or requirement | Index row |
|---|---|---|
| [Discover Products Faster by Using Price Book Filters](release-notes/articles/release-notes.rn_product_catalog_discover_products_faster_using_price_book_filters.htm.md) | Growth, Advanced or Billing | Price Book Filtering |
| [Find Products with Prefix Matching and Partial Search](release-notes/articles/release-notes.rn_product_catalog_find_products_with_prefix_matching_and_partial_search.htm.md) | Growth, Advanced or Billing | Prefix Matching and Partial Search |
| [Get Accurate Product Details with Automated Product Cache Management](release-notes/articles/release-notes.rn_product_catalog_get_accurate_product_details_with_automated_product_cache_management.htm.md) | Growth, Advanced or Billing | *not in index* |
| [Get Faster Product Pricing with List Price Caching](release-notes/articles/release-notes.rn_product_catalog_get_faster_product_pricing_with_list_price_caching.htm.md) | Growth, Advanced or Billing | List Price from Cache |
| [Guide Sales Reps Through Product Setup with Dynamic UI Controls](release-notes/articles/release-notes.rn_product_catalog_guide_sales_reps_through_product_setups_with_dynamic_ui_controls.htm.md) | Growth, Advanced or Billing | *not in index* |
| [See Instant Updates in Product Discovery While Building Quotes](release-notes/articles/release-notes.rn_product_catalog_see_instant_updates_in_product_discovery_while_building_quotes.htm.md) | Growth, Advanced or Billing | *not in index* |
| [Simplify Product Configuration with Custom Attribute and Category Ordering](release-notes/articles/release-notes.rn_product_catalog_display_order_attributes.htm.md) | Growth, Advanced or Billing | Attribute Management |

### Product Configurator (5)

| Release note | License or requirement | Index row |
|---|---|---|
| [Enforce Per-Bundle Product Requirements Regardless of Order Size](release-notes/articles/release-notes.rn_product_configurator_instance_quantity.htm.md) | Growth or Advanced | *not in index* |
| [Let Constraint Rules Assign Child Product Quantities in Bundles](release-notes/articles/release-notes.rn_product_configurator_allowQuantityChange.htm.md) | Growth or Advanced | *not in index* |
| [Optimize Performance for Revenue Management (Release Update)](release-notes/articles/release-notes.rn_product_configurator_optimize_performance.htm.md) **(Release Update: opt-in, enforced Summer '27)** | Growth or Advanced | *not in index* |
| [Prevent Constraint Conflicts When Sharing Attributes and Relations](release-notes/articles/release-notes.rn_product_configurator_guardrails_annotation.htm.md) | Growth or Advanced | *not in index* |
| [Updates in Default Product Configurator Flow](release-notes/articles/release-notes.rn_product_configurator_flow_updates.htm.md) | Growth or Advanced | *not in index* |

### Promotions in Revenue Management (1)

| Release note | License or requirement | Index row |
|---|---|---|
| [Increase Sales with Promotions in Revenue Management](release-notes/articles/release-notes.rn_revenue_increase_sales_with_promotions.htm.md) | Advanced | *not in index* |

### Ramp Deals (2)

| Release note | License or requirement | Index row |
|---|---|---|
| [Apply Compound Price Uplifts to Multiyear Ramp Deals to Adjust Pricing Over Time](release-notes/articles/release-notes.rn_transaction_management_ramp_deal_compound_uplift.htm.md) | Growth or Advanced | Compound Price Uplifts for Ramps |
| [Backdate Amendments, Renewals, and Cancellations for Ramp Deals to Adjust Billing](release-notes/articles/release-notes.rn_transaction_management_backdated_arc_for_ramps.htm.md) | Growth or Advanced | Backdated Asset Transactions |

### Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements (1)

| Release note | License or requirement | Index row |
|---|---|---|
| [Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements](release-notes/articles/release-notes.rn_salesforce_cpq_and_advanced_approvals_managed_package.htm.md) | CPQ and Advanced Approvals managed packages (not RLM) | *not in index* |

### Salesforce Contracts (7)

| Release note | License or requirement | Index row |
|---|---|---|
| [Add Clauses to Quotes from Your Clause Library](release-notes/articles/release-notes.rn_salesforce_contracts_add_clauses_to_quotes.htm.md) | Advanced or Salesforce Contracts | Special Terms on Quotes |
| [Apply Contract Governance Policies Consistently with Document Playbooks](release-notes/articles/release-notes.rn_sf_contracts_document_playbooks.htm.md) | Advanced, or Salesforce Contracts + Data 360 | *not in index* |
| [Author Contracts in Government Cloud](release-notes/articles/release-notes.rn_salesforce_contracts_govcloud_support.htm.md) | Advanced or Salesforce Contracts | *not in index* |
| [Protect Sensitive Setup Data by Removing Elevated Permissions from Runtime Users](release-notes/articles/release-notes.rn_sf_contracts_eliminate_privileges_runtime_users.htm.md) | Advanced or Salesforce Contracts | *not in index* |
| [Reduce Contract Risks by Analyzing Every Redline with AI](release-notes/articles/release-notes.rn_sf_contracts_risk_analysis.htm.md) | (Advanced or Salesforce Contracts) + Data 360 + Einstein Foundations | *not in index* |
| [Track Recipient Signing Progress for Document Envelopes](release-notes/articles/release-notes.rn_salesforce_contracts_track_recipient_signing_progress.htm.md) | Advanced or Salesforce Contracts | *not in index* |
| [Use Salesforce Contracts with Lightning Platform Licenses](release-notes/articles/release-notes.rn_sf_contracts_lpp_licenses.htm.md) | Advanced or Salesforce Contracts; either way, users also need Sales Cloud, Sales and Service Cloud, Lightning Platform Starter, or Lightning Platform Plus | *not in index* |

### Salesforce Document Generation (3)

| Release note | License or requirement | Index row |
|---|---|---|
| [Eliminate Manual Template Updates When Clause Content Changes](release-notes/articles/release-notes.rn_salesforce_document_generation_clause_tokens_runtime_resolution.htm.md) | Revenue Events Starter Pack + (Advanced or Billing) | *not in index* |
| [Generate Documents That Include Tables in Rich Text Fields](release-notes/articles/release-notes.rn_salesforce_document_generation_rich_text_tables.htm.md) | Revenue Events Starter Pack + (Advanced or Billing) | *not in index* |
| [Populate Clause Content with Merge and Placeholder Tokens](release-notes/articles/release-notes.rn_salesforce_document_generation_clause_merge_placeholder_tokens.htm.md) | Revenue Events Starter Pack + (Advanced or Billing) | *not in index* |

### Salesforce Pricing (5)

| Release note | License or requirement | Index row |
|---|---|---|
| [Avoid Integration Parsing Errors from Pricing API Decimal Values](release-notes/articles/release-notes.rn_pricing_avoid_integration_parsing_errors_from_pricing_api_decimal_values.htm.md) | Growth or Advanced | *not in index* |
| [Keep Calculated Values in Context with Local List Variables](release-notes/articles/release-notes.rn_pricing_keep_calculated_values_in_context_with_local_list_variables.htm.md) | Growth or Advanced | *not in index* |
| [Prorate with High-Velocity and Short-Term Sales Models](release-notes/articles/release-notes.rn_pricing_prorate_with_short-term_and_high-velocity_sales_models.htm.md) | Growth or Advanced | *not in index* |
| [Reduce Pricing Errors and Improve Deal Transparency on Ramp Deals](release-notes/articles/release-notes.rn_pricing_reduce_pricing_errors_and_improve_deal_transparency_on_ramp_deals.htm.md) | Growth or Advanced | Compound Price Uplifts for Ramps |
| [Tailor Pricing Rules for Multiple Industry Clouds](release-notes/articles/release-notes.rn_pricing_tailor_pricing_rules_for_multiple_industry_clouds.htm.md) | Growth or Advanced | Pricing Recipes |

### Simplify Revenue Cloud Feature Discovery and Setup (2)

| Release note | License or requirement | Index row |
|---|---|---|
| [Configure Billing Features Faster](release-notes/articles/release-notes.rn_billing_features_with_salesforce_go.htm.md) | Advanced or Billing; Invoice Document Delivery needs Billing | *not in index* |
| [Orchestrate High Tech Order Scenarios by Using a Prebuilt Template](release-notes/articles/release-notes.rn_dro_hightech_orch_with_salesforce_go.htm.md) | Advanced or Billing | High Tech Order Orchestration Template |

### Transaction Management (9)

| Release note | License or requirement | Index row |
|---|---|---|
| [Accelerate Transaction Updates with Advanced Filters](release-notes/articles/release-notes.rn_transaction_management_filter_transactions_by_product_name_in_the_sales_transaction_line_editor.htm.md) | Growth or Advanced | *not in index* |
| [Build Focused Quote Line Item and Order Product Pages with Dynamic Forms](release-notes/articles/release-notes.rn_transaction_management_dynamic_forms_for_quote_line_items_and_order_products.htm.md) | Growth or Advanced | *not in index* |
| [Edit Accurate Quotes and Orders in Sales Transaction Line Editor with Autorefresh](release-notes/articles/release-notes.rn_transaction_management_stle_enhance_autorefresh.htm.md) | Growth or Advanced | Transaction Summary |
| [Gain Pricing Flexibility with Price Amendments](release-notes/articles/release-notes.rn_transaction_management_update_quote_and_order_prices_with_price_amendments.htm.md) | Growth or Advanced | *not in index* |
| [Gain Transaction Flexibility with Backdated Asset Changes](release-notes/articles/release-notes.rn_transaction_management_backdate_asset_transactions.htm.md) | Growth or Advanced | Backdated Asset Transactions |
| [Limit a Procedure Plan to a Specific Industry](release-notes/articles/release-notes.rn_transaction_management_prevent_cross_industry_pricing_errors_with_subtype.htm.md) | Growth or Advanced | *not in index* |
| [Maintain Time Zone Accuracy for Asset Lifecycle Changes](release-notes/articles/release-notes.rn_transaction_managment_preserve_original_time_zones_for_asset_lifecycle_changes.htm.md) | Growth or Advanced | *not in index* |
| [Organize Sales Transaction Line Editor Actions into Button Groups for Efficient Editing](release-notes/articles/release-notes.rn_transaction_management_stle_enhance_button_groups.htm.md) | Growth or Advanced | Header-Level Action Buttons in STLE |
| [Sync Quote to Opportunity](release-notes/articles/release-notes.rn_transaction_management_sync_quote_to_opportunity.htm.md) | Growth or Advanced | *not in index* |

### Usage Management (4)

| Release note | License or requirement | Index row |
|---|---|---|
| [Adapt Subscriptions When Customer Needs Change](release-notes/articles/release-notes.rn_um_renew_active_usage_assets_early.htm.md) | Advanced; not in orgs with both Advanced and Billing plus the Usage Management add-on | Usage-Based Asset Renewal |
| [Prevent Usage Summary Failures by Updating Overridden Flows](release-notes/articles/release-notes.rn_um_update_overridden_flows_with_dpe_v4.htm.md) | Advanced | *not in index* |
| [Respond to Growth with Early Ramp Renewal](release-notes/articles/release-notes.rn_um_renew_ramped_usage_assets_early.htm.md) | Advanced | Usage-Based Asset Renewal |
| [Win Back Customers by Restoring Lapsed Subscriptions](release-notes/articles/release-notes.rn_um_renew_expired_usage_assets.htm.md) | Advanced; not in orgs with both Advanced and Billing plus the Usage Management add-on | Usage-Based Asset Renewal |

### Reference notes (17)

New and changed objects, Connect APIs, metadata types, invocable actions and Apex namespace classes. They carry no feature of their own: [`adv_approvals_new_changed_objects`](release-notes/articles/release-notes.rn_adv_approvals_new_changed_objects.htm.md), [`billing_changed_metadata_types`](release-notes/articles/release-notes.rn_billing_changed_metadata_types.htm.md), [`billing_new_changed_connect_rest_apis`](release-notes/articles/release-notes.rn_billing_new_changed_connect_rest_apis.htm.md), [`billing_new_changed_invocable_actions`](release-notes/articles/release-notes.rn_billing_new_changed_invocable_actions.htm.md), [`contracts_new_connect_rest_apis`](release-notes/articles/release-notes.rn_contracts_new_connect_rest_apis.htm.md), [`dro_new_and_changed_objects`](release-notes/articles/release-notes.rn_dro_new_and_changed_objects.htm.md), [`new_changed_billing_objects`](release-notes/articles/release-notes.rn_new_changed_billing_objects.htm.md), [`product_catalog_changed_connect_rest_api_response_body`](release-notes/articles/release-notes.rn_product_catalog_changed_connect_rest_api_response_body.htm.md), [`product_configurator_changed_connect_rest_api_request_body`](release-notes/articles/release-notes.rn_product_configurator_changed_connect_rest_api_request_body.htm.md), [`product_configurator_changed_object`](release-notes/articles/release-notes.rn_product_configurator_changed_object.htm.md), [`revenue_promotions_new_changed_objects`](release-notes/articles/release-notes.rn_revenue_promotions_new_changed_objects.htm.md), [`runtime_industries_cpq_namespace`](release-notes/articles/release-notes.rn_runtime_industries_cpq_namespace.htm.md), [`salesforce_contracts_newandchanged_objects`](release-notes/articles/release-notes.rn_salesforce_contracts_newandchanged_objects.htm.md), [`salesforce_pricing_new_changed_connect_rest_apis`](release-notes/articles/release-notes.rn_salesforce_pricing_new_changed_connect_rest_apis.htm.md), [`transaction_management_changed_connect_rest_apis`](release-notes/articles/release-notes.rn_transaction_management_changed_connect_rest_apis.htm.md), [`transaction_management_new_invocable_action_in_transaction_management`](release-notes/articles/release-notes.rn_transaction_management_new_invocable_action_in_transaction_management.htm.md), [`um_new_and_changes_objects`](release-notes/articles/release-notes.rn_um_new_and_changes_objects.htm.md).

---

## Maintenance

### How to re-check this index

1. **Refresh the release notes** (`cci task run snapshot_revenue_release_notes_264 -o mode refresh`) and re-map any new or retitled feature notes in **Release-Note Cross-Reference**. Update tiers if a note gains a Beta or Pilot label. Promote unmapped notes to index rows as the index is extended.
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
7. **Status-column counts** (`a → b`) are case-insensitive counts of captured 262 and 264 articles whose body contains the stated phrase as a substring (so `technical product` also matches `technical products`), or whose article ID does where the row says so. "Mention it" means the feature name; area counts use the per-area manifest totals.
8. **Release-note mapping:** each release-note article is a section page when another article names it as `parent_article`, a reference note when its title starts with New or Changed or ends in Namespace, and a feature note otherwise. Each feature note was then matched by hand to the index row describing the same capability.

Regenerate after corpus refreshes.
