---
page_id: sforce_api_objects_productspecificationtype.htm
title: ProductSpecificationType
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productspecificationtype.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductSpecificationType

Represents the type of product specification provided by the user to make the
product terminology unique to an industry. A product specification type is associated with
a product specification record type. This object is available in API version 60.0 and
later.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  The description of the Product Specification Type. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the Product Specification Type object in the API. The name:  - must be 40 characters or fewer. - can contain only underscores and alphanumeric   characters. - must begin with a letter. - can contain only underscores and alphanumeric   characters. - can’t include spaces - can’t end with an underscore - can’t contain 2 consecutive underscores  In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The combined language and locale ISO code, which controls the language of the Product Specification Type.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese (Simplified) - `zh_TW`—Chinese (Traditional) |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Label for this Product Specification Type value. This display value is the internal label that doesn't get translated. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix_componentName` The namespace prefix can have one of the following values.   - In Developer Edition orgs,   NamespacePrefix is set to the   namespace prefix of the org for all objects that support it,   unless an object is in an installed managed package. In that   case, the object has the namespace prefix of the installed   managed package. This field’s value is the namespace prefix   of the Developer Edition org of the package developer. - In orgs that aren’t Developer Edition orgs,   NamespacePrefix is set only for   objects that are part of an installed managed package. All   other objects have no namespace prefix. |
