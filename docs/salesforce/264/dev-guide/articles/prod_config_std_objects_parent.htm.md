---
page_id: prod_config_std_objects_parent.htm
title: Product Configurator Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/prod_config_std_objects_parent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_overview.htm
fetched_at: 2026-11-23
---

# Product Configurator Standard Objects

The Product Configurator data model provides objects and fields to manage the product
configurator flow.

These objects are documented in the [Salesforce Object Reference](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_list.htm).

- [ExpressionSetConstraintObj](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_expressionsetconstraintobj.htm "HTML (New Window)")

- **[ProductConfigurationFlow](./sforce_api_objects_productconfigurationflow.htm.md)**  
  Specifies the many-to-many relationship between Product Classification, Product, and Flow Definition objects. The flow definition is used to configure standalone and bundled products of a specific product classification along with the product attributes, quantities, and product selling models. This object is available in API version 60.0 and later.
- **[ProductConfigFlowAssignment](./sforce_api_objects_productconfigflowassignment.htm.md)**  
  A junction object that represents the many-to-many relationship between Product Configuration Flow, Product, and Product Classification. This object is available in API version 60.0 and later.
- **[ProductConfigurationRule](./sforce_api_objects_productconfigurationrule.htm.md)**  
  Represents the validation, inclusion, and exclusion rules for products in the context of the selling process. The selling process can be quoting, configuration, or ordering. This object is available in API version 61.0 and later.

#### See Also

- [*Object Reference for the platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.264.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/prod_config_std_objects_parent.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
