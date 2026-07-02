---
page_id: billing_sforce_api_objects_refund.htm
title: Billing Fields on Refund
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_refund.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on Refund

Standard fields extend the Refund object for use in Billing to
represent information about corporate currency, transaction amounts in corporate currency,
and accounting periods for legal entities. This object is available in API version
64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| CorporateCurrencyCnvAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The refund amount in corporate currency. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the refund amount is converted into corporate currency. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the refund amount into corporate currency. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The currency ISO code of the corporate currency. |
| FunctionalCurrencyCnvAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the amount value is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the amount value into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period related to the refund.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntityAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity related to the refund.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |

#### See Also

- [*Object Reference for the Salesforce Platform*: Refund](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_refund.htm "Object Reference for the Salesforce Platform: Refund - HTML (New Window)")
