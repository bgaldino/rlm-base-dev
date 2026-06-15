---
page_id: deployment_product_configurator_metadata.htm
title: Product Configurator Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_configurator_metadata.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-06-09
---

# Product Configurator Metadata

This table provides the metadata deployment reference for Product Configurator in
Revenue Cloud, including setup paths and configuration details.

| Type | Label | Setup Path | Comments |
| --- | --- | --- | --- |
| Setup | Context Service | Context Service > Context Service Settings | Enable (prerequisite to Product Configurator). |
| Setup | Configure Products at Runtime | Setup > Feature Settings > Revenue Cloud > Revenue Settings |  |
| Setup | Set Up Configuration Rules with Business Rules Engine | Setup > Feature Settings > Revenue Cloud > Revenue Settings | Standard Configurator Prerequisite: Create a Rule Library Version ([Set Up Configurator With Business Rules Engine](https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_configuration_rules.htm&language=en_US "HTML (New Window)")) |
| Setup | Set Up Configuration Rules and Constraints with Constraints Engine | Setup > Feature Settings > Revenue Cloud > Revenue Settings |  |
| Setup | Transaction processing for quotes and orders | Setup > Feature Settings > Revenue Cloud > Revenue Settings | If both Business Rules Engine and Constraint Builder are enabled in the org, ConstraintBuilder is used. Exception is Transaction Processing Type on Quotes and Orders override. |
| Setup | Set Up Asset Context for Product Configurator | Setup > Feature Settings > Revenue Cloud > Revenue Settings |  |
| Custom Field | ConstraintEngine​Node​Status (Text Area (Long), length 5000) | Setup > Object Manager > Quote Line Item | Prerequisite for Constraint Builder. |
| Custom Field | ConstraintEngine​Node​Status (Text Area (Long), length 5000) | Setup > Object Manager > Order Product | Prerequisite for Constraint Builder. |
| Custom Field | ConstraintEngine​Node​Status (Text Area (Long), length 5000) | Setup > Object Manager > Asset Action Source | Prerequisite for Constraint Builder. |
| Context Mapping | ConstraintEngine​Node​Status | Setup > Feature Settings > Context Definitions > [Context] | Map the three custom fields, which are mentioned in the previous rows, with the ConstraintEngineNodeStatus tag. |
| Permission Set | Product Configurator | Setup > Users > Permission Sets |  |
| Permission Set | Product Configuration Rules Designer | Setup > Users > Permission Sets | Prerequisite for Business Rules Engine Configurator. |
| Permission Set | Product Configuration Constraints Designer | Setup > Users > Permission Sets | Prerequisite for Constraint Builder. |
| Flow | Default Product Configurator Flow | Setup > Flow | Supports Flow version, and activation or deactivation. Other Flows can be created. |
