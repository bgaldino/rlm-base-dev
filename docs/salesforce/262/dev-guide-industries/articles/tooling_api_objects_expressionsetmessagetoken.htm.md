---
page_id: tooling_api_objects_expressionsetmessagetoken.htm
title: ExpressionSetMessageToken
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_expressionsetmessagetoken.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_tooling_objects_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetMessageToken

Represents a token that's used in an explainability message template.
The token can be replaced with an expression set version resource that the template is used
in. This object is available in API version 59.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The description of an expression set message token record. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name for the ExpressionSetMessageToken object.  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Label is **Record Type Name**. This field is automatically generated, but you can supply your own value if you create the record using the API. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language in which the expression set message token is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The label for the ExpressionSetMessageToken. In the UI, this field is Expression Set Message Token. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |
