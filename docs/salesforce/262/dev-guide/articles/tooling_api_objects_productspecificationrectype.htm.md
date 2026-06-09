---
page_id: tooling_api_objects_productspecificationrectype.htm
title: ProductSpecificationRecType
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_productspecificationrectype.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# ProductSpecificationRecType

Represents the association of a product specification type with record types
defined on the Product object. The product specification record type also determines if the
product specification is sold commercially or not. This object is available in API
version 60.0 and later.

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

## Special Access Rules

Ensure Product Catalog Management is enabled to
access this object.

## Fields

| Field | Details |
| --- | --- |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Label is **Record Type Name**. |
| IsCommercial | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the product is sold commercially (`true`) or not (`false`). The default value is `true`. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Language of the product specification record type instance.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese (Simplified) - `zh_TW`—Chinese (Traditional) |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Label assigned to the ProductSpecificationRecType object. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |
| ProductSpecificationType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required.  Product specification type that's associated with the record type. This field is unique within your organization.  The picklist values that are available to you depend on your industry solution and permission sets. |
| RecordType | Type  sObject  Properties  Nillable  Description  Custom record type of Product2 object. |
| RecordTypeId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. ID of the product record type associated with the product specification type. This field is unique within your organization.  This field is a relationship field.  Relationship Name  RecordType  Relationship Type  Lookup  Refers To  RecordType |
