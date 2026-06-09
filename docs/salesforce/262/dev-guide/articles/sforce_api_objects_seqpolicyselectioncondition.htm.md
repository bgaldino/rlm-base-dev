---
page_id: sforce_api_objects_seqpolicyselectioncondition.htm
title: SeqPolicySelectionCondition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_seqpolicyselectioncondition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# SeqPolicySelectionCondition

Represents the condition used to determine which sequence policy is
applied to a record. This object is available in API version 65.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| ConditionNumber | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  Required. A unique number that’s assigned to a condition in a sequence policy. |
| FilterField | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The field used in the filter condition. |
| FilterFieldType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The data type of the filter field.  Valid values are:  - `Boolean` - `Currency` - `Date` - `DateTime` - `MultiPicklist` - `Number` - `Percent` - `Picklist` - `Reference` - `Text` |
| FilterValue | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The value in the filter condition. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a sequence policy selection condition record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a sequence policy selection condition record. If this value is null, it’s possible that the user only accessed the sequence policy selection condition record or a related list view (LastReferencedDate), but not viewed the sequence policy selection condition record itself. |
| Operator | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The relational operator used to compare the filter field with the filter value.  Valid values are:  - `Equals` - `Not Equals` |
| SequencePolicyId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The parent sequence policy associated with the sequence policy selection condition. Deleting a sequencing policy automatically removes all its associated criteria.  This field is a relationship field.  Relationship Name  SequencePolicy  Relationship Type  Master-detail  Refers To  SequencePolicy (the master object) |
| SequencePolicySelectionConditionName | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the sequence policy selection condition. |

## Usage

You can create, update, or delete sequence policy selection condition records by using
sObject API from API version 67.0 and later.

Create a sequence policy selection condition record by making a POST request to this
resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SeqPolicySelectionCondition
```

This example shows a sample request.

```
{
  "SequencePolicyId": "1VdSG00000001fF0AQ",
  "FilterField": "Status",
  "FilterValue": "Draft",
  "Operator": "Equals",
  "ConditionNumber": 1
}
{
  "SequencePolicyId": "1VdSG00000001fF0AQ",
  "FilterField": "Description",
  "FilterValue": "Testing",
  "Operator": "Equals",
  "ConditionNumber": 2
}
```

Update a sequence policy selection condition record record by making a PATCH request to
this resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SeqPolicySelectionCondition/id
```

This example shows a sample request.

```
{
 "FilterValue": "654"
}
```

Delete a sequence policy selection condition record by making a DELETE request to this
resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SeqPolicySelectionCondition/id
```
