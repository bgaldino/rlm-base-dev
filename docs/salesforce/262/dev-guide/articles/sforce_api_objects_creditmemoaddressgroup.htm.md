---
page_id: sforce_api_objects_creditmemoaddressgroup.htm
title: CreditMemoAddressGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemoaddressgroup.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CreditMemoAddressGroup

Represents the storage of the buyer's address information, which is
used to determine the tax credit amount for a buyer when a credit memo is issued. This
object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`

## Special Access Rules

You need the Credit Memo Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Address | Type  address  Properties  Filter, Nillable  Description  The buyer's address. |
| CreditMemoAddressGroupNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the credit memo address group. |
| CreditMemoId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the credit memo associated with the address group.  This field is a relationship field.  Relationship Name  CreditMemo  Relationship Type  Master-detail  Refers To  CreditMemo (the master object) |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a credit memo address group record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a credit memo address group record. If this value is null, it’s possible that the user only accessed the credit memo address group record or a related list view (LastReferencedDate), but not viewed the credit memo address group record itself. |
