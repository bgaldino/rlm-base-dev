---
page_id: sforce_api_objects_pricingrecipe.htm
title: PricingRecipe
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingrecipe.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# PricingRecipe

Represents one out of various data models or sets of entities of a particular
cloud that'll be consumed by the pricing data store during design and run time. This
object is available in API version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Special Access Rules

## Fields

| Field | Details |
| --- | --- |
| DefaultPricingProcedureId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The expression set definition or Salesforce flow definition associated with this pricing recipe settings.  This field is a relationship field.  Relationship Name  DefaultPricingProcedure  Relationship Type  Lookup  Refers To  ExpressionSetDefinition |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The developer name of the pricing recipe. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the pricing recipe is active (true) or not (false).  The default value is `false`. |
| IsInternal | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates if the price recipe record is created internally by the Salesforce platform (true) or not (false).  The default value is `false`. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The languages in which pricing recipe is supported.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese (Simplified) - `zh_TW`—Chinese (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  A user-friendly name for pricing recipe, which is defined when the pricing recipe is created. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation.  The namespace prefix can have one of the following values.  - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There’s an exception if an object is   in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This   field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an   installed managed package. There’s no namespace prefix for   all other objects. |
