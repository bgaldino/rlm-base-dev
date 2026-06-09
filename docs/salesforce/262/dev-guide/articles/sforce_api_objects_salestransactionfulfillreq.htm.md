---
page_id: sforce_api_objects_salestransactionfulfillreq.htm
title: SalesTransactionFulfillReq
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_salestransactionfulfillreq.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# SalesTransactionFulfillReq

Represents the statuses of all the sub-orders that belong to the selected
commercial or technical product. This object is available in API version 62.0 and
later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Fields

| Field | Details |
| --- | --- |
| AssetizationStatus | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Specifies the status of the assetization.  Valid values are:  - `Completed` - `Failed` - `InProgress` - `NotStarted` - `Rejected` - `NotApplicable`-   Available in API version 64.0 and later. |
| DecompositionStatus | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Specifies the status of the decomposition.  Valid values are:  - `Completed` - `Failed` - `InProgress` - `NotStarted` - `Rejected` - `NotApplicable`-   Available in API version 64.0 and later. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the sales transaction fulfillment request. |
| OrchestrationGroupKey | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The identifier of the group of sales transactions that require synchronization before processing. This field is available in API version 63.0 and later. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort  Description  The ID of the user who created the request record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PlanCompositionStatus | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  For internal use only.  Valid values are:  - `Completed` - `Failed` - `InProgress` - `NotStarted` - `Rejected` - `NotApplicable` -   Available in API version 64.0 and later. |
| PlanExecutionStatus | Type  picklist  Properties  Filter, Group, Nillable, Sort  Description  Specifies the status of the plan execution.  Valid values are:  - `InProgress` - `Frozen` - `Freezing` |
| PlanId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The identifier of the plan.  This field is a relationship field.  Relationship Name  Plan  Refers To  FulfillmentPlan |
| PreviousRequestId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The identifier of the previous fulfillment request.  This field is a relationship field.  Relationship Name  PreviousRequest  Refers To  SalesTransactionFulfillReq |
| ReferenceObjectIdentifier | Type  reference  Properties  Filter, Group, idLookup, Nillable, Sort  Description  The ID of the sales transaction record. This field is available in API version 64.0 and later. |
| SalesTransactionType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Specifies the type of sales transaction that's processed by the fulfillment request.  Valid values are:  - `StandardOrder` - `GenericAdapter`—Available in API version 64.0   and later. |
| Status | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Specifies the overall status of the fulfillment.  Valid values are:  - `Created` - `Freezing` - `Frozen` - `Fulfilled` - `Fulfilling` - `Rejected` - `Superseded` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[SalesTransactionFulfillReqShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
