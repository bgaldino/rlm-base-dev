---
page_id: deployment_transaction_management_objects.htm
title: Transaction Management Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_transaction_management_objects.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-06-09
---

# Transaction Management Objects

This table provides the deployment sequence, object types, and API names for
Transaction Management objects in Revenue Cloud.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | App Usage Assignment | AppUsageAssignment | 1 | Order, Quote, Contract, Asset |
| Metadata | Sales Transaction Type | SalesTransactionType | 1 | PricingProcedure |
| Metadata | Quote Template Rich Text Data | QuoteTemplateRichTextData | 1 | None |
| Metadata | Transaction Processing Type | TransactionProcessingType | 1 | None |

#### See Also

- [*Revenue Cloud Developer Guide*: Transaction Management Standard
  Objects](https://developer.salesforce.com/docs/./quote_and_order_capture_standard_objects.htm.md "Revenue Cloud Developer Guide: Transaction Management Standard
         Objects - HTML (New Window)")
- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US "Explore the Revenue Cloud Data Model - HTML (New Window)")
