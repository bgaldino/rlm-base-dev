---
page_id: sforce_api_objects_productconfigurationflow.htm
title: ProductConfigurationFlow
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productconfigurationflow.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductConfigurationFlow

Specifies the many-to-many relationship between Product Classification,
Product, and Flow Definition objects. The flow definition is used to configure standalone
and bundled products of a specific product classification along with the product
attributes, quantities, and product selling models. This object is available in API
version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| FlowIdentifier | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Stores the flow API name. |
| IsDefault | Type  Boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates the default configurator flow.  The default value is `false`. |
| Status | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Indicates the status of the product configuration flow. Possible values include Draft, Active, and Inactive  Possible values are:  - `Active` - `Draft` - `Inactive`  The default value is `Draft`. |
