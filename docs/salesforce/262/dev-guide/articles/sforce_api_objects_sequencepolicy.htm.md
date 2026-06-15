---
page_id: sforce_api_objects_sequencepolicy.htm
title: SequencePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_sequencepolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# SequencePolicy

Represents the configuration of rules and parameters for generating
unique, sequential numbers for records. Stores settings such as numbering patterns,
prefixes, suffixes, sequence start numbers, increment values, and filter criteria to ensure
accurate and compliant numbering. This object is available in API version 65.0 and
later.

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

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| DateStampFormat | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The format of the stamp date that’s appended to the sequence number.  Valid values are:  - `MM-YYYY`—Month   Year (MM-YYYY) - `MM-dd-yyyy`—Month   Day Year (MM-DD-YYYY) - `None` - `YYYY`—Year   (YYYY) - `YYYY-YY`—Org   Fiscal Year (YYYY–YY) |
| Description | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Additional details about the sequencing policy. |
| EffectiveFromDateTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  Required. The date and time when the policy becomes effective. |
| ExpirationDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the policy expires. |
| IncrementByNumber | Type  long  Properties  Filter, Group, Sort  Description  Required. The sequence number increment value. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether the policy is active (`true`) or not (`false`).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a sequence policy record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a sequence policy record. If this value is null, it’s possible that the user only accessed the sequence policy record or a related list view (LastReferencedDate), but not viewed the sequence policy record itself. |
| MaximumSequenceNumber | Type  long  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number the sequence number can reach. The maximum width is determined by the maximum sequence number value. |
| MinimumSequenceNumberWidth | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The minimum number of digits a sequence number must have. For example, if the minimum width is set to 3, sequence numbers appear as 001, 002, and so on. If the maximum sequence number is 99999, the width would be 5 digits. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the sequence policy. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the user who owns a sequence policy record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Prefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  A string added to the start of the sequence number. |
| SelectionLogic | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The logic that determines the records to which the sequence policy applies. |
| SequenceMode | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Specifies how sequence numbers are generated.  Valid values are:  - `Basic`—Gaps are   allowed, such as when a record is canceled or rolled   back. - `Gapless`—Numbers   follow one after another with no gaps. |
| SequencePattern | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The structure of a sequence. |
| SequenceStartNumber | Type  long  Properties  Create, Filter, Group, Sort, Update  Description  Required. The starting sequence number. |
| Suffix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  A string added to the end of the sequence number. |
| TargetObject | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The object to which the policy is applied. |
| TimeZone | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The time zone applicable to the date and time related fields of the policy. When not specified, it takes the user’s time zone by default. The time zone is shown in Greenwich Mean Time (GMT). |

## Usage

You can create, update, or delete sequence policy records by
using sObject API from API version 67.0 and later.

Create a sequence policy record
by making a POST request to this
resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SequencePolicy
```

This
example shows a sample request.

```
{
  "Name": "Invoice Sequence Policy Testing",
  "Description": "Sequence policy for invoice numbering",
  "TargetObject": "Invoice",
  "SequenceMode": "Gapless",
  "SequencePattern": "IN-{Date}-{SequenceValue}",
  "DateStampFormat": "MM-dd-yyyy",
  "TimeZone": "America/Los_Angeles",
  "IsActive": false,
  "SequenceStartNumber": 1,
  "IncrementByNumber": 1,
  "MaximumSequenceNumber": 99999,
  "MinimumSequenceNumberWidth": 4,
  "EffectiveFromDateTime": "2026-03-01T00:00:00.000Z",
  "ExpirationDateTime": "2027-03-01T00:00:00.000Z"
}
```

Update a sequence policy record by making a PATCH request to this
resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SequencePolicy/id
```

This example shows a sample request.

```
{
  "Description": "Sequence policy for invoice numbering testing",
  "IsActive": true,
  "MaximumSequenceNumber": 88888
}
{
  "SelectionLogic": "1 AND 2"
}
```

Delete a sequence policy record by making a DELETE request to this resource.

```
https://yourInstance.salesforce.com/services/data/v67.0/sobjects/SequencePolicy/id
```
