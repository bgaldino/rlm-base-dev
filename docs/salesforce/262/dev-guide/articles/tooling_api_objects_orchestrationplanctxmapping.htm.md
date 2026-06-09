---
page_id: tooling_api_objects_orchestrationplanctxmapping.htm
title: OrchestrationPlanCtxMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_orchestrationplanctxmapping.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_tooling_api_parent.htm
fetched_at: 2026-06-09
---

# OrchestrationPlanCtxMapping

Represents an orchestration plan context mapping entry in the org.
This entry is used to connect the business data in an object to the orchestration logic
within Dynamic Revenue Orchestrator (DRO) by using the orchestration type. This object
is available in API version 66.0.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

## Fields

| Field | Details |
| --- | --- |
| ContextDefinition | Type  reference  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Name of the context definition to be used for the object. |
| ContextItemNode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Required. Name of the node that represents an item in the context definition. |
| ContextMapping | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. Name of the context definition mapping to apply. This mapping must be related to the specified context definition. |
| ContextRootNode | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. Name of the node that represents the root in the context definition. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. With this field, a developer can change the object’s name in a managed package and the changes are reflected in a subscriber’s organization. Label is **Record Type Name**. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language of the OrchestrationPlanCtxMapping tooling API object.  Valid values are: |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Label for the orchestration plan context mapping. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix associated with this object. Each Developer Edition organization that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. The namespace prefix can have one of the following values:   - In Developer Edition organizations, the namespace prefix is   set to the namespace prefix of the organization for all   objects that support it. There is an exception if an object   is in an installed managed package. In that case, the object   has the namespace prefix of the installed managed package.   This field’s value is the namespace prefix of the Developer   Edition organization of the package developer. - In organizations that are not Developer Edition   organizations, NamespacePrefix is only   set for objects that are part of an installed managed   package. There is no namespace prefix for all other   objects. |
| ObjectName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  API name of the object for orchestration. |
| OrchestrationType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Name of the type of the orchestration plan.  Valid value is `Generic`. |
