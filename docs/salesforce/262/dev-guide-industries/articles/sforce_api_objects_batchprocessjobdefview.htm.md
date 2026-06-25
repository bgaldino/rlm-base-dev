---
page_id: sforce_api_objects_batchprocessjobdefview.htm
title: BatchProcessJobDefView
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchprocessjobdefview.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_standard_object.htm
fetched_at: 2026-06-25
---

# BatchProcessJobDefView

Represents the details of a Batch Job definition. The definition can also be
file-based definitions that are available in your Salesforce org. This object is
available in API version 51.0 and later.

## Supported Calls

`describeSObjects()`,
`query()`

## Fields

| Field | Details |
| --- | --- |
| DurableId | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier for the field. Always retrieve this value before using it, as the value isn’t guaranteed to stay the same from one release to the next. Simplify queries by using this field instead of making multiple queries. |
| IsActive | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the definition is active. |
| Label | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The label of the Batch Job definition. |
| Name | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the Batch Job definition. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the namespacePrefix\_\_componentName notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is set to the   namespace prefix of the organization for all objects that support it.   There is an exception if an object is in an installed managed package. In   that case, the object has the namespace prefix of the installed managed   package. This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition organizations,   NamespacePrefix is only set for objects that are part of an installed   managed package. There is no namespace prefix for all other objects. |
| ProcessDefinition | Type  textarea  Properties  Nillable  Description  The name of the process group for the batch process job definition. |
| ProcessGroup | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The team or group for which the definition processes records. |
| SourceObjectName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The API name of the object whose records are processed. |
| Type | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The type of process for which the Batch Management job processes records.  Possible values are:  - `Flow` - `LoyaltyProgramProcess`   This field is available in API version 55.0 and later. |
| TypeInstance | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The API name of the process that's processed by the Batch Job definition. |
