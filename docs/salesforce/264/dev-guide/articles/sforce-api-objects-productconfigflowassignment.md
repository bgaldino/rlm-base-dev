---
page_id: sforce-api-objects-productconfigflowassignment
title: ProductConfigFlowAssignment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productconfigflowassignment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: prod-config-std-objects-parent
legacy_page_id: sforce_api_objects_productconfigflowassignment.htm
fetched_at: 2026-11-25
---

# ProductConfigFlowAssignment

A junction object that represents the many-to-many relationship between Product Configuration Flow, Product, and Product Classification. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssignmentType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Specifies whether the Product Configuration Flow is assigned to the primary product or classification, or to dynamic components added within a bundle.

Valid values are `DynamicAdditionFlow` or `PrimaryConfiguratorFlow`.

The default value is `PrimaryConfiguratorFlow`. Available in API version 65.0 and later.

### ProductClassificationId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The product classification associated with the Product Configuration Flow.

This field is a relationship field.

- **Relationship Name**: ProductClassification

- **Relationship Type**: Lookup

- **Refers To**: ProductClassification

### ProductConfigurationFlowId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The Product Configuration Flow associated with the Product Classification or Product.

This field is a relationship field.

- **Relationship Name**: ProductConfigurationFlow

- **Relationship Type**: Lookup

- **Refers To**: ProductConfigurationFlow

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The product associated with the Product Configuration Flow.

This field is a relationship field.

- **Relationship Name**: Product

- **Relationship Type**: Lookup

- **Refers To**: Product2

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productconfigflowassignment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
