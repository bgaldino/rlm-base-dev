---
page_id: sforce_api_associated_objects_history.htm
title: StandardObjectNameHistory
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_associated_objects_history.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Associated Objects
parent_page: sforce_api_associated_objects_list.htm
fetched_at: 2026-06-09
---

# StandardObjectNameHistory

StandardObjectNameHistory is the model for all
history objects associated with standard objects. These objects represent the history of
changes to the values in the fields of a standard object.

The object name is variable and uses StandardObjectNameHistory
syntax. For example, AccountHistory represents the history of changes to the values
of an account record’s fields. We list the available associated history objects at
the end of this topic. For specific version information, see the documentation for
the standard object.

## Supported Calls

`describeSObjects()`, `getDeleted()`, `getUpdated()`,
`query()`, `retrieve()`

You can also enable `delete()` in API version 42.0
and later. See [Enable delete of Field
History and Field History Archive](https://help.salesforce.com/articleView?id=000321814&type=1&mode=1&language=en_US "HTML (New Window)").

## Special Access Rules

For specific special access rules, if any, see
the documentation for the standard object. For example, for AccountHistory, see the
special access rules for Account.

## Fields

| Field Name | Details |
| --- | --- |
| StandardObjectNameId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the standard object. |
| DataType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Data type of the field that was changed. |
| Field | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Name of the field that was changed. |
| NewValue | Type  anyType  Properties  Nillable, Sort  Description  New value of the field that was changed. |
| OldValue | Type  anyType  Properties  Nillable, Sort  Description  Old value of the field that was changed. |
