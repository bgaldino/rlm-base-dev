---
page_id: sforce_api_objects_taxpolicy.htm
title: TaxPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_taxpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# TaxPolicy

Represents information about a group of tax treatments, where each
treatment represents parameters to determine how a particular product is taxed for a
transaction line item. Tax policies are related to products, which pass the policy on to
the resulting order items and in turn the billing schedules. This object is available
in API version 62.0 and later.

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

You need the Tax Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| DefaultTaxTreatmentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the default tax treatment record. When you order a product, the order product, and in turn the billing schedule receives this tax treatment.  This field is a relationship field.  Relationship Name  DefaultTaxTreatment  Refers To  TaxTreatment |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the tax policy. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed an invoice batch draft to posted run record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a tax policy record. If this value is null, it’s possible that the user only accessed the tax policy record or a related list view (LastReferencedDate), but not viewed the tax policy record itself. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the tax policy. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the tax policy. To calculate tax for order products, products must have an active tax policy. Tax policies are created with a `Draft` status before being assigned to a product or order product. After activating a tax policy, you can't edit certain policy fields.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| TreatmentSelection | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Specifies the selection of tax treatments to billing schedules that are related to the tax policy.  Valid values are:  - Default —Billing schedules receive the tax treatment   defined in the tax policy's   DefaultTreatmentId field. - `LegalEntity`—Billing schedules receive the   tax treatment based on matching legal entities between itself   and the tax treatment. - `Manual`—Billing   schedules don't receive tax treatments based on the tax   policy. You must specify the treatment. |
