---
page_id: tooling_api_objects_timelineobjectdefinition.htm
title: TimelineObjectDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_timelineobjectdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Timeline
parent_page: timeline_tooling_api_object.htm
fetched_at: 2026-06-25
---

# TimelineObjectDefinition

Represents the timeline configurations. This object is available
in API version 55.0 and later.

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
| BaseObject | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The object on which a timeline is based. Information displayed in a timeline comes from objects that are related to the base object. The base object can be any Salesforce object, standard or custom. |
| Definition | Type  textarea  Properties  Create, Update  Description  The timeline definition stored in JSON format. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the timeline. |
| FullName | Type  string  Properties  Create, Group, Nillable  Description |
| IsActive | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the timeline is active.  The default value is `false`. |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The language of the timeline object definition.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish   (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description    Possible values are:  - `beta`—Managed-Beta - `deleted`—Managed-Proposed-Deleted - `deprecated`—Managed-Proposed-Deprecated - `deprecatedEditable`—SecondGen-Installed-Deprecated - `installed`—Managed-Installed - `installedEditable`—SecondGen-Installed-Editable - `released`—Managed-Released - `unmanaged`—Unmanaged |
| MasterLabel | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| Metadata | Type  TimelineObjectDefinition  Properties  Create, Nillable, Update  Description  The timeline object definition's metadata. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |

## Associated Objects

This
object has the following associated objects. If the API version isn’t
specified, they’re available in the same API versions as this object. Otherwise, they’re
available in the specified API version and later.

[TimelineObjectDefinitionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm "HTML (New Window)") (API version 60.0)
:   Change events are available for the object.
