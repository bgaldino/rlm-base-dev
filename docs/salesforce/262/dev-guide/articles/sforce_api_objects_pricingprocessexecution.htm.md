---
page_id: sforce_api_objects_pricingprocessexecution.htm
title: PricingProcessExecution
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingprocessexecution.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PricingProcessExecution

Represents a record generated during the execution of a discovery or pricing
procedure. Multiple procedures may be performed within a single API call, with each
recorded in a Pricing API Execution record. This object is available in API version
63.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.  Possible values are:  - `BHD`—Bahraini   Dinar - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is `USD`. |
| ExecutionKey | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The unique execution ID generated each time a pricing API runs. |
| ExecutionType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of execution defined internally within the pricing API.  Possible values are:  - `Api_Execution`—Api Execution - `Discovery` - `Discovery_Line`—Discovery Line - `Pricing` - `Pricing_Line`—Pricing Line  The default value is `Pricing`. |
| ExecutionTypeKey | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique execution type ID generated internally for procedure executions, such as pricing or discovery procedures. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Message | Type  textarea  Properties  Create, Nillable, Update  Description  The message generated upon running a pricing process. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The Salesforce ID of the sales representative who owns the pricing procedure resolution.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Status | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the status of the execution type.  Possible values are:  - `Failure` - `Partial_Success`—Partial Success - `Success`  The default value is `Success`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PricingProcessExecutionFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[PricingProcessExecutionHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[PricingProcessExecutionShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
