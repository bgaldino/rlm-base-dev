---
page_id: deployment_product_catalog_management_additional_info.htm
title: Product Catalog Management Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_catalog_management_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Additional Information

Get to know additional deployment information for Product Catalog Management in Revenue
Cloud, including active or inactive states, object information, and migration
considerations.

## Object-Specific Information

| Object Name | Object API | Notes |
| --- | --- | --- |
| Product Qualification | ProductQualification | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Product Disqualification | ProductDisqualification | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Product Category Qualification | ProductCategoryQualification | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |
| Product Category Disqualification | ProductCategoryDisqual | - [Considerations for Migrating Decision   Tables](https://help.salesforce.com/s/articleView?id=ind.bre_decision_table_migration_considerations.htm&language=en_US) - [Considerations for Migrating Expression   Sets](https://help.salesforce.com/s/articleView?id=ind.considerations_for_migrating_expression_sets.htm&language=en_US) - [Migrate Context Definitions](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions_packages.htm&language=en_US) |

## Other Information

- All product data (product, class, product attributes, attributes, picklist, catalog,
  categories, and so on) definitions must be active to appear in the sales channels.
  - These definitions need not be deactivated in the target to propagate updates as part
    of an org-to-org deployment. Exceptions are qualification rules that use decision
    tables, expression sets, and context definitions. The definitions in the target org
    must be deactivated to promote changes.
- Use the Full Index Rebuild to rebuild the entire search index, when enabling the feature
  for the first time, or changing the index settings. Use the Partial Index Rebuild to
  update recent changes to products and categories assignment. For more information about
  indexing products, see [Manage Your Product Index](https://help.salesforce.com/s/articleView?id=ind.product_catalog_index_products.htm&language=en_US "HTML (New Window)").
  - If indexing is enabled in source but not enabled in the target, then while deploying
    the indexing flag (enable indexed product=true), the Full indexing must be run on the
    target org before the feature flag can be enabled.
- Migrating qualification rules records requires refreshing Qualification Rules Decision
  Table definitions (Product and Category Qualification and Disqualification Decision
  Tables).
- Migrating price book Entries requires Decision Table refresh for Product Discovery to
  show list price.
- Core to Near Core Sync Processes—[Configure Product Catalog
  Management Cache](https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_prodoct_catalog_management_cache.htm&language=en_US "HTML (New Window)") in the new org to populate the product details cache, essential
  for large-scale implementations.
- Cross-Module Synchronization—Synchronization of catalog date to Constraint
  Modeling Language (CML) to support constraint rules.
- Incremental Changes and cohesive Sync (Recommended)—Depending on the deployment
  scenario, for example, new or changed product, new or changed price, new price book, new
  or changed rules, and so on.
