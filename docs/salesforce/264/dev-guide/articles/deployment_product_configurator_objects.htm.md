---
page_id: deployment_product_configurator_objects.htm
title: Product Configurator Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_configurator_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-11-23
---

# Product Configurator Objects

This table provides the object deployment sequence and properties for Product
Configurator in Revenue Management, including object types, API names, deployment sequences, and
lookup fields.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Product Configuration Rule | ProductConfiguration​Rule | 1 | User |
| Configuration | Product Configuration Flow | ProductConfiguration​Flow | 1 | UserFlowIdentifier |
| Configuration | ExpressionSet​ConstraintObj | ExpressionSet​ConstraintObj | 1 | ExpressionSetId, ReferenceObjectId (Polymorphic) |
| Configuration | Product Configuration Flow Assignment | ProductConfig​FlowAssignment | 2 | User, ProductId, ProductClassificationId, ProductConfigurationFlow |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_configurator_objects.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
