---
page_id: sforce_api_objects_billingarrangement.htm
title: BillingArrangement
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingarrangement.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingArrangement

Represents the arrangement for invoicing a transaction’s billing amount to
one or more accounts. The arrangement specifies whether the total amount must be invoiced
to the owning account or a different billing account, or whether the invoices must be split
among multiple billing accounts. This object is available in API version 66.0 and
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
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the billing arrangement record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the billing arrangement record was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. A user-defined name for the billing arrangement. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the billing arrangement record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RemainderBillingPercentage | Type  double  Properties  Filter, Sort  Description  Required. The percentage of the billing amount that isn’t assigned to any of the billing accounts. |
| ShouldBillRemainderToAccount | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether to bill the remainder billing percentage to the owning account (`true`) or not (`false`). |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Specifies the status of the billing arrangement.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| VersionNumber | Type  int  Properties  Filter, Group, Nillable, Sort  Description  A numerical value indicating the current version of the billing arrangement record. The version number increases when new billing arrangement line records are added or existing billing arrangement line records are updated. |
