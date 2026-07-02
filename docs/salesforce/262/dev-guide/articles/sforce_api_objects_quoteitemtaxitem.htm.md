---
page_id: sforce_api_objects_quoteitemtaxitem.htm
title: QuoteItemTaxItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quoteitemtaxitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# QuoteItemTaxItem

The tax that is applied to a quote line item. This object is available
in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

This object is available if Subscription
Management is enabled in your org. This object is also available in Enterprise, Unlimited,
and Developer Editions of Revenue Cloud.

## Fields

| Field | Details |
| --- | --- |
| Amount | Type  currency  Properties  Create, Filter, Sort, Update  Description  The tax amount for the quote line item. |
| CurrencyIsoCode | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Available only for orgs with the multicurrency feature enabled. Contains the ISO code for any currency allowed by the org.  Possible values are:  - `BHD`—Bahraini   Dinar - `EUR`—Euro - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is 'USD'. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  User-defined description of the tax. For example, state sales tax or value-added tax (VAT). |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Name of the tax. |
| QuoteLineItemId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the related quote line item.  This is a relationship field.  Relationship Name  QuoteLineItem  Relationship Type  Lookup  Refers To  QuoteLineItem |
| Rate | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  If the tax is a percentage tax, then this field contains the percent value. If the tax is a fixed amount, then this field is null. |
| TaxEffectiveDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date used to calculate the tax rate. |
| Type | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Whether the tax is estimated or calculated by the tax provider.  Possible values are:  - `Actual` - `Estimated` |
