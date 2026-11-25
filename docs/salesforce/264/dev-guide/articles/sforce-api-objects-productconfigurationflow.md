---
page_id: sforce-api-objects-productconfigurationflow
title: ProductConfigurationFlow
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productconfigurationflow.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: prod-config-std-objects-parent
legacy_page_id: sforce_api_objects_productconfigurationflow.htm
fetched_at: 2026-11-25
---

# ProductConfigurationFlow

Specifies the many-to-many relationship between Product Classification, Product, and Flow Definition objects. The flow definition is used to configure standalone and bundled products of a specific product classification along with the product attributes, quantities, and product selling models. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### FlowIdentifier

- **Type**: String

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Stores the flow API name.

### IsDefault

- **Type**: Boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates the default configurator flow.

The default value is `false`.

### IsRequestDetailEditable

- **Type**: Boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether request attributes and products can be edited (`true`) or not (`false`). When enabled, users can modify the attributes and products in associated cases, incidents, or service requests after the request is created.

The default value is `false`.

### Status

- **Type**: Picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Indicates the status of the product configuration flow. Possible values include Draft, Active, and Inactive

Possible values are `Active`, `Draft`, or `Inactive`

The default value is `Draft`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productconfigurationflow.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
