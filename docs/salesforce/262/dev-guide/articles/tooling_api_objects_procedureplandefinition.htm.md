---
page_id: tooling_api_objects_procedureplandefinition.htm
title: ProcedurePlanDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_procedureplandefinition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedurePlanDefinition

Represents the setup of a unified procedure from a list of multiple
procedures that can be sequenced in any order based on business needs. Each procedure plan
definition contains sections and subsections where procedures can be configured by using a
lookup table or rule-based criteria. This object is available in API version 62.0 and
later.

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
| Description | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the procedure plan definition. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the procedure plan definition record.  This name must begin with a letter and use only alphanumeric characters and underscores. It can't include spaces, end with an underscore, or have two consecutive underscores. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the procedure plan definition.  Valid values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The master label of the procedure plan definition. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation.  The namespace prefix can have one of the following values.  - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There’s an exception if an object is   in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This   field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an   installed managed package. There’s no namespace prefix for   all other objects. |
| PrimaryObject | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort  Description  The object associated to the procedure plan definition. The fields in the object are used as variables in the procedure plan criterion. |
| ProcessType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Identify the business processes that need a procedure plan for each SObject and definition.  Possible values are:  - `Billing` - `DRO` - `DeepClone`—Deep   Clone - `Default` - `ProductDiscovery`—Product Discovery - `RLM`  The default value is `Default`. |
