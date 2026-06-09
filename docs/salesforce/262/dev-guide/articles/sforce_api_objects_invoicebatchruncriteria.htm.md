---
page_id: sforce_api_objects_invoicebatchruncriteria.htm
title: InvoiceBatchRunCriteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoicebatchruncriteria.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# InvoiceBatchRunCriteria

Represents a batch processing job and its required criteria in
Billing. During an invoice batch run, all billing schedules that meet the specified
criteria are processed, resulting in the generation of invoices. This object is
available in API version 62.0 and later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Comments | Type  textarea  Properties  Filter, Nillable, Sort  Description  Additional notes or comments for the invoice batch run criteria. |
| CriteriaExpression | Type  textarea  Properties  Filter, Nillable, Sort  Description  The formula that specifies criteria for filtering the billing schedules. For example, you can filter billing schedules by the currency code. |
| CriteriaMatchType | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Required. The type of matching criteria required for the batch.  Valid value is `MatchAll`.  The default value is `MatchAll`. |
| ExpectedInvoiceStatus | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of invoice a batch run generates.  Valid values are:  - `Draft` - `Posted` |
| InvoiceBatchRunCriteriaNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the invoice batch run criteria. |
| InvoiceDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date displayed on the invoice. This date is also used for tax calculations. |
| InvoiceDateOffset | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The offset that's applied to the target date to calculate the invoice date. |
| IsInvoiceDateFromRunDate | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether the invoice date is derived from the run date (`true`) or not (`false`).  The default value is `false`. Available in API version 63.0 and later. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the user who created the invoice batch run criteria.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| TargetDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The target date for the invoice run. Billing schedules having the next billing date before this date are picked up for invoicing. |
| TargetDateOffset | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The offset that's applied to the next run date to calculate the target date. |
