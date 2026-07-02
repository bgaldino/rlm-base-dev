---
page_id: deployment_product_catalog_management_metadata.htm
title: Product Catalog Management Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_catalog_management_metadata.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Metadata

This table provides the metadata deployment reference for Product Catalog Management in
Revenue Cloud, including setup paths and configuration details.

| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Omnistudio Settings | Setup > Apps > Packaging > Installed Packages | Prerequisite: Omnistudio Managed package must be installed. |
| Flag | Managed Package Runtime | Setup > Feature Settings > Omni interaction > Omnistudio Settings | Disable |
| Flag | Define Custom Lightning Web Components in Standard Runtime | Setup > Feature Settings > Omni interaction > Omnistudio Settings | Enable |
| Setup | Discovery Framework | Setup > Discovery Framework | Prerequisite: Enable guided product selection through this path. Setup> Product Discovery > Product Discovery Settings- > Guided Product Selection |
| Flag | Discovery Framework | Setup > Discovery Framework > General Settings | Enable |
| Flag | Import & Export | Setup > Discovery Framework > General Settings | Enable |
| Flag | Sample Templates | Setup > Discovery Framework > General Settings | Enable. Also, refer to these steps.  - In the **Sample Templates** section, click the Discovery   Framework Sample Template page link. The Discovery Framework Sample Templates page   appears. - Click **Deploy** if not already deployed. |
| Setup | Procedure Plan Definition | Procedure Plan Setup > Procedure Plan Definitions |  |
| Setup | Product Discovery Settings | Setup> Product Discovery > Product Discovery Settings |  |
| Field | Select Context Definition | Setup> Product Discovery > Product Discovery Settings |  |
| Field + Flag | Select Pricing Procedure | Setup> Product Discovery > Product Discovery Settings |  |
| Field + Flag | Select Qualification Procedure | Setup> Product Discovery > Product Discovery Settings |  |
| Field | Select a Custom Flow for Browsing and Adding Products in Revenue Cloud | Setup> Product Discovery > Product Discovery Settings |  |
| Field | Select Default Catalog | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Product Field Search | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Use Indexed Data for Product Listing and Search | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Dynamic Product Facets | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Semantic Search | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Guided Product Selection | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Generate Product Descriptions with Einstein AI | Setup> Product Discovery > Product Discovery Settings |  |
| Flag | Product Catalog Management Cache | Setup> Product Discovery > Product Discovery Settings |  |
| Permission Sets | Product Catalog Management Customer Community User | Setup > Users > Permission Sets |  |
| Permission Sets | Product Catalog Management Partner Community User | Setup > Users > Permission Sets |  |
| Permission Sets | Product Catalog Management Cache | Setup > Users > Permission Sets |  |
| Permission Sets | Product Discovery Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Product Discovery User | Setup > Users > Permission Sets |  |
| Permission Sets | ProductImport API | Setup > Users > Permission Sets |  |
| Permission Sets | DecimalQuantityDesigntime | Setup > Users > Permission Sets |  |
| Permission Sets | DecimalQuantityRuntime | Setup > Users > Permission Sets |  |
| Permission Sets | Advanced CSV Data Import | Setup > Users > Permission Sets | Data Processing Engine (DPE) is included. Data Cloud is licensed and deployed separately. |
| Permission Sets | Basic CSV Data Import | Setup > Users > Permission Sets |  |
| Permission Sets | Context Service Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Context Service Runtime | Setup > Users > Permission Sets |  |
| Permission Sets | Fulfillment Designer | Setup > Users > Permission Sets |  |
| Permission Sets | Omnistudio Admin | Setup > Users > Permission Sets |  |
| Permission Sets | Omnistudio User | Setup > Users > Permission Sets |  |
| Flow | Discover Products | Setup > Flow | Supports Flow version, activation, and deactivation |
| Omniscript | ProductGuidedSelectionIntegration | All Apps > Omnistudio | Supports Omniscript version, activation, and deactivation |
| Decision Table Definition | ProductQualificationDT | Setup > Decision Table |  |
| Decision Table Definition | ProductDisqualificationQualificationDT | Setup > Decision Table |  |
| Decision Table Definition | ProductCategoryQualificationDT | Setup > Decision Table |  |
| Decision Table Definition | ProductCategory​Disqualification​Qualification​DT | Setup > Decision Table |  |
