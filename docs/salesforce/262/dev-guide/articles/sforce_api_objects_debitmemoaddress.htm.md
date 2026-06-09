---
page_id: sforce_api_objects_debitmemoaddress.htm
title: DebitMemoAddress
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_debitmemoaddress.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# DebitMemoAddress

Represents the buyer's address information, which is used to
determine the tax amount for a buyer when a debit memo is issued. This object is
available in API version 65.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms
to align with our company value of Equality. We maintained certain terms to avoid any
effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and one of these permission sets to access this
object.

- Billing Admin permission set
- Billing Operations User permission set
- Payments Admin permission set
- Payments Operation User permission set
- Credit Memo Operations User permission set

## Fields

| Field | Details |
| --- | --- |
| Address | Type  address  Properties  Filter  Description  The billing or shipping address of the debit memo. |
| DebitMemoAddressNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The auto-generated reference number for the debit memo address. |
| DebitMemoId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the debit memo associated with the address.  This field is a relationship field.  Relationship Name  DebitMemo  Relationship Type  Master-detail  Refers To  DebitMemo (the master object) |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a debit memo address record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a debit memo address record. If this value is null, it’s possible that the user only accessed the debit memo address record or a related list view (LastReferencedDate), but not viewed the debit memo address record itself. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[DebitMemoAddressHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
