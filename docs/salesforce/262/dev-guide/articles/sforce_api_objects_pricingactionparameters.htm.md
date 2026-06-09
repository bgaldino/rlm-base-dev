---
page_id: sforce_api_objects_pricingactionparameters.htm
title: PricingActionParameters
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingactionparameters.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# PricingActionParameters

Represents a pricing action associated to a context definition and a pricing
procedure. This object is available in API version 60.0 and later.

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
| ContextDefinition | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The context definition record associated with the pricing action. |
| ContextMapping | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The context mapping record that's associated with the pricing action. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the pricing action parameter record.  This name must begin with a letter and use only alphanumeric characters and underscores. It can't include spaces, end with an underscore, or have two consecutive underscores. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the pricing action comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time till when the pricing action is in effect. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the pricing action parameter.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese (Simplified) - `zh_TW`—Chinese (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The master label of the pricing action parameter. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation.  The namespace prefix can have one of the following values.  - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There’s an exception if an object is   in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This   field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an   installed managed package. There’s no namespace prefix for   all other objects. |
| ObjectName | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the object associated to the pricing action.  Possible values are:  - `Case` - `Contract` - `Opportunity` - `Order` - `Quote` - `SalesAgreement` - `WorkOrder` |
| PricingProcedure | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The pricing procedure record associated with this pricing action. |
