---
page_id: sforce_api_objects_productfulfillmentscenario.htm
title: ProductFulfillmentScenario
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productfulfillmentscenario.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductFulfillmentScenario

Represents a link between a product and the corresponding group of
fulfillment steps that's necessary to fulfill that product. This object is available
in API version 61.0 and later.

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
| Action | Type  multipicklist  Properties  Create, Filter, Nillable, Update  Description  For internal use only.  Valid values are:  - `Add` - `Amend` - `Cancel` - `NoChange` - `Renew` |
| ConditionData | Type  textarea  Properties  Create, Nillable, Update  Description  The condition for executing the product fulfillment scenario. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later. |
| FulfillmentStepDefnGroupId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The fulfillment step definition group associated with the product fulfillment scenario.  This field is a relationship field.  Relationship Name  FulfillmentStepDefnGroup  Relationship Type  Lookup  Refers To  FulfillmentStepDefinitionGroup |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  For internal use only. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  For internal use only. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the product fulfillment scenario. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  For internal use only.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ProductClassificationId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The product classification associated with the product fulfillment scenario.  This field is a relationship field.  Relationship Name  ProductClassification  Relationship Type  Lookup  Refers To  ProductClassification |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update, Nillable (Available in API version 64.0 and later)  Description  The product associated with the product fulfillment scenario.  This field is a relationship field.  Relationship Name  Product  Relationship Type  Lookup  Refers To  Product2 |
| SourceClassIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The source classification entity in the product fulfillment scenario. This field can store a Salesforce Product Class ID or an external identifier. This field is available in API version 65.0 and later. |
| SourceIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The source entity in the product fulfillment scenario. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later. |
| UsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Name of the usage type. This field is available in API version 66.0 and later.  Possible values are:  - `Fulfillment` - `Generic` - `InsuranceRuleAction`—Insurance Rule   Action - `IntegrationOrchestrator`—Integration   Orchestrator - `StageManagement`—Stage Management  The default value is `Fulfillment`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductFulfillmentScenarioShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
