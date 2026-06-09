---
page_id: sforce_api_objects_debitmemolinetax.htm
title: DebitMemoLineTax
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_debitmemolinetax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# DebitMemoLineTax

Represents the tax information for a debit memo line. This
object is available in API version 66.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need Revenue Cloud Billing license and the Tax Admin permission set to access this
object.

## Fields

| Field | Details |
| --- | --- |
| BillingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing address specified in the parent debit memo line.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  DebitMemoAddress |
| CurrencyIsoCode | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Required. The currency ISO code of the corporate currency. |
| DebitMemoLineId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The parent debit memo line that the debit memo tax line is related to.  This field is a relationship field.  Relationship Name  DebitMemoLine  Relationship Type  Master-detail  Refers To  DebitMemoLine (the master object) |
| DebitMemoLineTaxNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number that identifies a debit memo line tax. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The description of the debit memo line tax. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The end date of the debit memo line tax that determines which billing cycle it's associated with. |
| JurisdictionTaxCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The code of the jurisdiction that's used to calculate the tax rate for the parent debit memo line. |
| JurisdictionTaxName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The user-defined name for the debit memo line tax. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a debit memo line tax record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a debit memo line tax record. If this value is null, it’s possible that the user only accessed the debit memo line tax record or a related list view (LastReferencedDate), but not viewed the debit memo line tax record itself. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The legal entity accounting period record associated with the debit memo line.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The legal entity record associated with the debit memo line.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| ShipFromAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The shipping address specified in the parent debit memo line.  This field is a relationship field.  Relationship Name  ShipFromAddress  Refers To  DebitMemoAddress |
| StartDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The start date of the debit memo line tax that determines which billing cycle it's associated with. |
| TaxAmount | Type  currency  Properties  Filter, Sort  Description  Required. The total amount of the debit memo line tax. |
| TaxRate | Type  percent  Properties  Filter, Nillable, Sort  Description  The percentage that's used to calculate tax amount based on the charge amount. |
| TaxTransactionNumber | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The transaction number in the external tax engine that calculated the tax for the parent debit memo line. |
