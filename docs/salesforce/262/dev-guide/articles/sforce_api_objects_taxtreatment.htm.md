---
page_id: sforce_api_objects_taxtreatment.htm
title: TaxTreatment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_taxtreatment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# TaxTreatment

Represents information about tax calculation by external
engines. Each product requires a tax policy to determine whether to apply tax. Each tax
policy requires at least one tax treatment. The tax treatments determine how taxable
products are taxed. This object is available in API version 62.0 and
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
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

You need the Tax Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the tax treatment. |
| IsTaxable | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether to calculate tax for the order items covered by the tax treatment (`true`) or not (`false`). When this value is `true`, the CalculateTax API is called for the order item during the order item's creation.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a tax treatment record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a tax treatment record. If this value is null, it’s possible that the user only accessed the tax treatment record or a related list view (LastReferencedDate), but not viewed the tax treatment record itself. |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity record that's related to the tax treatment.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the tax treatment. |
| ProductCode | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The code of the product that the tax treatment applies to. |
| ProductId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the product that the tax treatment applies to.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| ShouldUseTaxTreatmentItems | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether the tax codes and product codes of the related tax treatment items must be used when requesting tax calculations (`true`) or not (`false`).  The default value is `false`. The tax code and product code of the tax treatment are ignored by default. Available in API version 66.0 and later. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the tax treatment record.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| TaxCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The reference code that's used when an external tax engine calculates tax. |
| TaxEngineId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the tax engine record that's related to the tax treatment. When tax is calculated for an order item, the tax engine that's related to order item’s tax treatment is used. If the tax treatment’s IsTaxable field value is `True`, the treatment requires a tax engine.  This field is a relationship field.  Relationship Name  TaxEngine  Refers To  TaxEngine |
| TaxPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the tax treatment’s parent tax policy.  This field is a relationship field.  Relationship Name  TaxPolicy  Refers To  TaxPolicy |
