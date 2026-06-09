---
page_id: sforce_api_objects_bindingobjectcustomext.htm
title: BindingObjectCustomExt
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_bindingobjectcustomext.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BindingObjectCustomExt

Represents the external or custom target object that's bound to the
entitlements granted with the sellable product. This object is available in API
version 64.0 and later.

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

## Special Access Rules

- This object is available in Revenue Cloud when Rate Management is enabled.
- Users with any Rate Management permission set (Admin, Manager, Designtime,
  Runtime) can view records. Only Admins can create, edit, and delete records.

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the binding custom object record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the product usage grant.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
