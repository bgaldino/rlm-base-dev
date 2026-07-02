---
page_id: deployment_scenarios.htm
title: Deployment Scenarios
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_scenarios.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_overview.htm
fetched_at: 2026-06-09
---

# Deployment Scenarios

Learn about specific deployment scenarios including new environment setup, refreshes, retiring records, deploying patches, and many more.

## Product Catalog Management

Table 1. Product Definition: Full Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| Large Catalog Refresh  Introduce 200+ new SKUs for accessories line | Metadata: [See Additional Deployment Information](./deployment_appendix_C.htm.md "Get to know additional deployment information for each Revenue Cloud feature domain, ensuring successful deployments and migrations.").  Data: bulk product load, product classes, selling models, price book entries, discount schedules, association to categories, catalogs | In the target org: Align baseline metadata.  Validation: Run automated regression tests on bundles and pricing. Validate sample SKUs across categories. |

Table 2. Product Definition: Incremental Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| New Product Launch  Introduce a new product (simple) of type one time, subscription, and usage with standard pricing. | Metadata: product record type, updated page layouts, product catalog management, pricing, usage, and rating metadata  Data: product records, product classifications, attributes, attribute picklists, price book entries, rate card entries, subscription term details | In the target org, a price book and rate card must exist, and billing rules are configured.  Validation: Create a test quote with products, confirm price flows into quote or order, validate subscription billing cycle, validate rates. |
| Bundle Creation  Launch a new product bundle that includes core products, add-ons, and attribute configurations with standard pricing. | Metadata: none  Data: bundle definition, child products, option groups, option attribute configurations, bundle pricing | In the target org, attributes and picklists must be created or updated, child products must be created or updated, and a price book must exist.  Validation: Configure a bundle in a quote, test configuration options, and ensure correct pricing roll up. |
| Update Product Classification Properties  Add new attributes and update existing attribute properties to existing product classification. | Metadata: none  Data: new attributes, new and updated product class attribute assignments. | In the target org, attributes and picklists must be created or updated first.  Validation: Generate a quote with updated product, and validate that product attributes appear correctly. |
| Update Product Classification Hierarchy  Add a new sub-classification, configure attributes, and create a product by using the sub-class. | Metadata: none  Data: new class, class relationship, and class attribute assignments | In the target org, attributes and picklists must be created or updated first.  Validation: Generate a quote with a new product. Validate product attributes correctly appear. |
| Product Retirement  Deactivate legacy products | Metadata: none  Data: Set product status to Inactive. Remove the product from active price books. | Active quotes with retired products must be closed or replaced.  Validation: Attempt to add a retired product to the quote and confirm it's blocked. Make sure that reporting reflects retirement. |
| Update Product Discovery Setup  Change qualification procedure, product discovery flow, and turn on Indexed Product feature. | Metadata: [See Appendix C](./deployment_appendix_C.htm.md "Get to know additional deployment information for each Revenue Cloud feature domain, ensuring successful deployments and migrations.")  Data: Index configuration (searchable, filterable, languages) | In target org, make sure that baseline metadata is created. Run full indexing in the target org before you enable the feature.  Validation: Validate the product discovery setup changes and product indexing process status. Verify by discovering products with term-based and faceted search. |

Table 3. Catalog, Categories & Related Products: Full Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| New Catalog Creation  Introduce a new catalog for a business line. For example, Cloud Services. | Metadata: Catalog object configuration, and Salesforce Configure, Price, Quote (CPQ) page layouts  Data: Create catalog records and linked products | Products must exist before adding to the catalog  Validation: Validate that the catalog is visible in quotes and orders. Confirm that all linked products appear. |
| Large Catalog Expansion  Add 500+ new SKUs across multiple categories. | Metadata: Update catalog metadata if new categories are required.  Data: Bulk product-category relationships, and new catalog entries. | In the target org, make sure that baseline metadata is created.  Validation: Confirm that sample SKUs appear in the correct categories. Perform a regression test of the catalog navigation. |

Table 4. Catalog, Categories & Related Products: Incremental Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| Add New Category  Add the Security Services category under the existing catalog. | Metadata: Update category hierarchy metadata  Data: Create category record, and link products | Parent catalog must exist in the target org.  Validation: Confirm that products appear under the new category in the catalog browser. |
| Category Reorganization  Move products from the Hardware category to the Accessories category. | Metadata: Update category hierarchy and associations.  Data: Update category-to-product mappings. | Validation: Validate that moved products appear only in the new category and that the old category is clean. |
| Product Retirement from Category  Remove retired products from catalog and related category. | Metadata: Update product visibility settings.  Data: Update product-category relationships. | Validation: Validate that the products aren’t visible in the category browser or guided selling. |
| Seasonal Category  Introduce a temporary Holiday Deals category. | Metadata: Configure the category (and time-based visibility if applicable).  Data: Establish product-category relationships with seasonal tag. | Products must exist and be tagged for promotion.  Validation: Confirm that the category is visible during the correct time period only. Verify that the correct products are included. |

Table 5. Qualification Rules: Full Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| Large-Scale Decision Table Migration  Introduce 100+ new eligibility conditions, such as new geographies and pricing models. | Metadata: Qualification Rule framework and Expression Set alignment  Data: Insert decision tables in bulk. | Perform target org metadata baseline alignment and staging of decision tables for verification.  Validation: Regression test eligibility across multiple conditions and customer profiles. |
| Composite Qualification Rule  Combine multiple decision tables and expression sets into a new guided selling path. | Metadata: Create parent qualification rule, and update multiple expression sets.  Data: Populate multiple decision tables with new mappings. | All child rules and data mappings must exist in the target org.  Validation: Test end-to-end guided selling to confirm the composite flow works correctly. |

Table 6. Qualification Rules: Incremental Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| New Qualification Rule with Decision Table  Create a qualification rule to enforce eligibility for product bundles based on region and customer tier. | Metadata: New qualification rule metadata, and context definition setup  Data: Populate decision table entries with region and tier mappings | Product catalog and customer tiers must be available in the target org.  Validation: Create test quotes for each region and tier. Confirm that only eligible products appear. |
| Update Existing Decision Table Entries  Add new conditions to an existing qualification rule such as adding a new country to eligibility. | Metadata: none  Data: Update and add rows in decision tables. | Make sure that new values are aligned with the active product catalog.  Validation: Confirm that the rule returns the correct product eligibility for the new condition. |
| Modify Expression Set  Change logical criteria from OR to AND in the qualification logic. For example, the customer must be an enterprise and have a support contract. | Metadata: Update expression set definition  Data: none | Make sure that the dependent context variable exists.  Validation: Confirm both the positive and negative test cases (eligible vs. non-eligible customers). |
| Context Definition Expansion  Add a new attribute to the context (for example, Industry) for use in qualification rules. | Metadata: Add field reference in context definition  Data: None (until data is mapped into a decision table) | Ensure that the Industry field exists and is populated.  Validation: Test that qualification rules can read Industry context during quote creation. |
| Retirement of Qualification Rule  Deactivate old eligibility rule no longer needed such as a legacy discount program. | Metadata: Update rule status to inactive, and remove references from related expression set.  Data: Remove or disable related decision table entries. | Make sure that the rule isn’t referenced by other bundles or flows.  Validation: Confirm that the retired rule no longer impacts guided selling or product selection. |

## Salesforce Pricing

Table 7. Pricing: Incremental Deployment Scenarios

| Scenario | Impact | Validation and Dependencies |
| --- | --- | --- |
| Pricing Update  Update base license cost by +5% for existing products. | Metadata: None (if there are no new rules)  Data: Update price book entries and adjust discount tiers. | Make sure that no dependent contracts reference the old pricing.  Validation: Generate a quote with the updated product. Confirm that pricing reflects the new value. Confirm no impact to active contracts. |
| Promotional Discount  Introduce a three-month promotional discount for enterprise customers. | Metadata: New time-based pricing rule and approval process update.  Data: Create a discount schedule and promo product entry. | Approval workflow for discount must be active  Validation: Confirm that the discount applies only during the promotion period and verify that approvals trigger correctly. |
