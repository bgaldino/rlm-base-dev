---
page_id: deployment-transaction-management-objects
title: Transaction Management Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-transaction-management-objects.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-a
legacy_page_id: deployment_transaction_management_objects.htm
fetched_at: 2026-11-25
---

# Transaction Management Objects

This table provides the deployment sequence, object types, and API names for Transaction Management objects in Revenue Management.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | App Usage Assignment | AppUsageAssignment | 1 | Order, Quote, Contract, Asset |
| Metadata | Sales Transaction Type | SalesTransactionType | 1 | PricingProcedure |
| Metadata | Quote Template Rich Text Data | QuoteTemplateRichTextData | 1 | None |
| Metadata | Transaction Processing Type | TransactionProcessingType | 1 | None |

**See Also**

- [*Revenue Cloud Developer Guide*: Transaction Management Standard Objects](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_standard_objects.htm)

- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-transaction-management-objects.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
