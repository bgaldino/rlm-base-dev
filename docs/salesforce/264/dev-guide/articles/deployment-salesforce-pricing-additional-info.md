---
page_id: deployment-salesforce-pricing-additional-info
title: Salesforce Pricing Additional Information
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-salesforce-pricing-additional-info.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-c
legacy_page_id: deployment_salesforce_pricing_additional_info.htm
fetched_at: 2026-11-25
---

# Salesforce Pricing Additional Information

Get to know additional deployment information for Salesforce Pricing in Revenue Management, including active or inactive states, object information, and migration considerations.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Attribute Based Adjustment | AttributeBasedAdjustment | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm); [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm); or [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm). |
| Price Adjustment Tier | PriceAdjustmentTier | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm); [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm); or [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm). |
| Bundle Based Adjustment | BundleBasedAdjustment | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm); [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm); or [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm). |
| Product Price Range | ProductPriceRange | [Considerations for Migrating Decision Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm); [Considerations for Migrating Expression Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm); or [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm). |

## Other Information

- 

You need active context definitions for pricing recipes. A pricing recipe is marked as default in an org. A System Admin can access the PricingRecipe object whereas a Pricing Admin can’t access this object internally. You can’t create or update fields of a PricingRecipe object.

- 

You must activate decision tables and pricing procedures.

- 

You need a refresh of the decision table for any new or modified records. For example, any modification in price book entries requires a refresh of the Price Book Entries decision table.

- 

You must migrate the Apex class if Apex is selected for Procedure Plan definitions. See [Customize Your Procedure Plans with Apex Hooks](https://help.salesforce.com/s/articleView?id=ind.pricing_customize_pricing_procedures_with_apex_hooks.htm).

- 

You can’t delete a standard price book. A price book can be deleted after all references are removed. Instead, set the price book to Inactive status.

- 

If you delete a price adjustment schedule, all associated data is deleted without any warning or error messages. The adjustment method and status of a price adjustment schedule aren’t considered for resolution. If you edit or delete an active price adjustment schedule, an error is thrown.

- 

The EffectiveFrom and EffectiveTo field values of a price adjustment tier, attribute-based adjustment, and bundle-based adjustment must be within the EffectiveFrom and EffectiveTo field values.

- 

Product and product selling model must be a part of the product selling model option before you create values in a price book entry.

- 

You can’t delete an inactive or active product selling model. You can delete a draft product selling model by deleting all references. You can’t change status from Active or Inactive to Draft.

- 

You can’t edit a product price range after you’ve created it. Enable price tracking to edit a product price range.

- 

Salesforce Pricing doesn’t consider the Active status of a price book when fetching the values. Also, it doesn’t consider the validity date ranges of a price book.

- 

The pricing term and pricing term unit of a price adjustment tier aren’t considered for resolution.

- 

The IsActive field of a price book entry and price adjustment schedule aren’t considered for resolution.

- 

**[Salesforce Pricing Migration Scenarios](./deployment-salesforce-pricing-migration-scenarios.md)**

Review these considerations to understand the Salesforce Pricing data migration process along with migration order and prerequisites.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-salesforce-pricing-additional-info.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
