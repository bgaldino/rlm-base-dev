---
page_id: tooling_api_objects_customfulfillmentscopecnfg.htm
title: CustomFulfillmentScopeCnfg
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_customfulfillmentscopecnfg.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# CustomFulfillmentScopeCnfg

Represents a user-defined scope to define and customize scope-specific
validation and orchestration for flexible fulfillment. This object is available in API
version 64.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| AssetContextTag | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Context tag that's used to derive custom scope value from assets. This field is available in API version 65.0 and later. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. Name of the custom fulfillment scope. |
| DoesParticipatingAssetImpact | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether the technical assets related to sales transactions impact the fulfillment line item actions (`true`) or not (`false`). If set to `true`, Dynamic Revenue Orchestrator reuses the existing technical assets with the same custom value.  The default value is `false`. |
| FallbackScope | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Scope that's used when custom scope can't be determined.  Valid value is:  - `LineItem`  If an empty value is returned, then ID of the line item is used.  The default value is `LineItem`. |
| IsAssetized | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the fulfillment line items grouped by the custom scope are assetized `true` or not (`false`). If set to `false`, then the scope can't be associated with assetizable products.  The default value is `false`. |
| ItemContextTag | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. Context tag that's used to derive custom scope from item context nodes. The supported value is of string type only. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the CustomFulfillmentScopeCnfg tooling API object. |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Label of the custom fulfillment scope. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |
