---
page_id: billing_sforce_api_objects_expressionset.htm
title: Billing Fields on ExpressionSet
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_expressionset.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on ExpressionSet

Standard fields extend the ExpressionSet object for use in Billing.
These fields represent information about an expression set that performs a series of
calculations by using lookups and user-defined variables and constants to calculate
taxes. This object is available in API version 66.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| UsageType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The Revenue Standard Tax Calculation value that’s using the expression set to calculate taxes. |
