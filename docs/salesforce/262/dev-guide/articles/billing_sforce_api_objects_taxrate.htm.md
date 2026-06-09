---
page_id: billing_sforce_api_objects_taxrate.htm
title: Billing Fields on TaxRate
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_taxrate.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on TaxRate

Standard fields extend the TaxRate object for use in Billing. These fields
represent information about the tax rate for a transaction that's determined by the
applicable tax code and country. This object is available in API version 66.0 and
later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Billing Admin permission set or Tax Admin permission set access to this
object.

## Fields

| Field | Details |
| --- | --- |
| ApplicationBasis | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether the tax rate is applied on the net or gross amount.  Valid values are:  - `Gross` - `Net`  The default value is `Gross`. |
| City | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The city to which the tax rate applies. |
| Country | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The country name that’s derived from the GeoCountry field value.  This field is a calculated field. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The currency ISO code that’s applicable to the tax rate. |
| EndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date until when the tax rate is valid. |
| FlatTaxAmount | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The flat tax amount that’s applied to the transaction. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a tax rate record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a tax rate record. If this value is null, it’s possible that the user only accessed the debit memo line tax record or a related list view (LastReferencedDate), but not viewed the debit memo line tax record itself. |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The legal entity to which the tax rate applies.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the invoice line. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the user who owns a TaxRate record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The code of the product for which the tax rate applies. |
| RateUsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether the tax rate is created for Commerce or Revenue Cloud.  Valid values are:  - `Commerce` - `RevCloud`  The default value is `Commerce`. |
| StartDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date from when the tax rate is valid. |
| State | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The state name that’s derived from the GeoState field value.  This field is a calculated field. |
| ZipCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The postal or ZIP code to which the tax rate applies. |
