---
page_id: sforce_api_objects_procedureoutputresolution.htm
title: ProcedureOutputResolution
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_procedureoutputresolution.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedureOutputResolution

Represents the pricing resolution for an pricing element determined using
strategy name and formula. This object is available in API version 63.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| BusinessVertical | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The business vertical associated with the procedure output resolution record.  Possible values are:  - `RLM` |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The name of the procedure output resolution. |
| Formula | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The formula function used to determine the minimum or maximum price of a product. The supported operations are MIN and MAX. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the procedure output resolution is active (true) or not (false). Only active procedure output resolutions can be applied to a procedure.  The default value is `false`. |
| IsInternal | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates if the procedure output resolution record is created internally by the Salesforce platform (true) or not (false).  The default value is `false`. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The languages in which pricing recipe is supported.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  A user-friendly name for procedure output resolution, which is defined when the procedure output resolution record is created. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation.  The namespace prefix can have one of the following values.  - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There’s an exception if an object is   in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This   field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an   installed managed package. There’s no namespace prefix for   all other objects. |
| PricingElement | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the pricing element on which the procedure output resolution is defined.  Possible values are:  - `ListPrice`—List   Price - `MinimumPrice`—Price Tracking - `PriceAdjustmentMatrix`—Price Adjustment   Matrix |
