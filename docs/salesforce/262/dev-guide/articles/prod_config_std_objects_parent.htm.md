---
page_id: prod_config_std_objects_parent.htm
title: Product Configurator Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/prod_config_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_overview.htm
fetched_at: 2026-06-09
---

# Product Configurator Standard Objects

The Product Configurator data model provides objects and fields to manage the product
configurator flow.

- **[ExpressionSetConstraintObj](./sforce_api_objects_expressionsetconstraintobj.htm.md)**  
  Represents the association between a Product object and the constraint model tags defined in a given constraint model. This object is available in API version 63.0 and later.
- **[ProductConfigurationFlow](./sforce_api_objects_productconfigurationflow.htm.md)**  
  Specifies the many-to-many relationship between Product Classification, Product, and Flow Definition objects. The flow definition is used to configure standalone and bundled products of a specific product classification along with the product attributes, quantities, and product selling models. This object is available in API version 60.0 and later.
- **[ProductConfigurationRule](./sforce_api_objects_productconfigurationrule.htm.md)**  
  Represents the validation, inclusion, and exclusion rules for products in the context of the selling process. The selling process can be quoting, configuration, or ordering. This object is available in API version 61.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
