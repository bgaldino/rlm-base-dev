---
page_id: sforce_api_objects_expressionsetconstraintobj.htm
title: ExpressionSetConstraintObj
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_expressionsetconstraintobj.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ExpressionSetConstraintObj

Represents the association between a Product object and the constraint model
tags defined in a given constraint model. This object is available in API version 63.0
and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

This object is available in orgs where Revenue Cloud is enabled.

## Fields

| Field | Details |
| --- | --- |
| ConstraintModelTag | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The product tag that is defined in the constraint model, for example, `Laptop`. |
| ConstraintModelTagType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of the product tag that is defined in the constraint model.  Possible values are:  - `Port` - `Type`  The default value is `Type`. |
| ExpressionSetId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The expression set associated with the expression set constraint object.  This field is a relationship field.  Relationship Name  ExpressionSet  Refers To  ExpressionSet |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, the user accessed this record or list view (LastReferencedDate) but didn’t view it. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the expression set constraint. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  For internal use only.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ReferenceObjectId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The object associated with the expression set constraint object.  This field is a polymorphic relationship field.  Relationship Name  ReferenceObject  Refers To  Product2, ProductClassification, ProductRelatedComponent |
