---
page_id: sforce_api_objects_billingtreatment.htm
title: BillingTreatment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingtreatment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingTreatment

Represents information about the billing of an order item. This
object is available in API version 62.0 and later.

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

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillingPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The billing policy that's related to the billing treatment.  This field is a relationship field.  Relationship Name  BillingPolicy  Refers To  BillingPolicy |
| CanChangeBillingFrequency | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the billing frequency can be changed for the billing treatment (`true`) or not (`false`).  The default value is `false`. |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the billing treatment. |
| ExcludeFromBilling | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Specifies whether any order items assigned to the treatment are excluded from billing.  Valid values are:  - `No` - `Yes` |
| IsMilestoneBilling | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether the billing treatment is for milestone billing (`true`) or not (`false`).  The default value is `false`. This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a billing treatment indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a billing treatment. If this value is null, it’s possible that the user only accessed the billing treatment or a related list view (LastReferencedDate), but not viewed the billing treatment itself. |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity that's used to assign the treatment to order items when the parent billing policy's BillingTreatmentSelection field value is `LegalEntity`.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the billing treatment. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the billing treatment.  Valid values are:  - `Active` - `Draft` - `Inactive`  Draft or inactive billing treatments can't be assigned to order items. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[BillingTreatmentHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
