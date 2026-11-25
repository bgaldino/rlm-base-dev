---
page_id: connect-requests-batch-invoice-filter-criteria-input
title: Batch Invoice Filter Criteria Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-batch-invoice-filter-criteria-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_batch_invoice_filter_criteria_input.htm
fetched_at: 2026-11-25
---

# Batch Invoice Filter Criteria Input

Input representation of the filter criteria for an invoice batch run.

## JSON Example

```
    "filterCriteria": [
        {
            "operation": "InList",
            "value": "Batch 2,Batch 3,Batch 4",
            "criteriaSequence": 1,
            "objectName": "BillingSchedule",
            "fieldName": "InvoiceRunMatchingValue"
        },
        {
            "operation": "Equals",
            "value": "001xx000003GZG5AAO",
            "criteriaSequence": 2,
            "objectName": "BillingSchedule",
            "fieldName": "BillingAccount"
        },
        {
            "operation": "Equals",
            "value": "0fwxx0000000001AAA",
            "criteriaSequence": 3,
            "objectName": "BillingScheduleGroup",
            "fieldName": "LegalEntity"
        },
        {
            "operation": "InList",
            "value": "OneTime,Recurring",
            "criteriaSequence": 4,
            "objectName": "BillingSchedule",
            "fieldName": "BillingTermUnit"
        },
        {
            "operation": "Equals",
            "value": "USD",
            "criteriaSequence": 5,
            "objectName": "BillingSchedule",
            "fieldName": "Currency_Iso_code"
        }
    ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `field​Name` | String | Name of the field that this filter is applicable for. Valid values are `Currency_Iso_code`—If multiple currencies are enabled for the org, then this value is required, `InvoiceRunMatchingValue`, `BillingAccount`, `LegalEntity`, or `BillingTermUnit`. | Required | 62.0 |
| `object​Name` | Object | Name of the object that the filter is applicable for. Valid values are `BillingSchedule` or `BillingScheduleGroup`. | Required | 62.0 |
| `operation` | String | Operation to be performed for comparison. Valid values are `Equals`; `InList`—This value supports only the `InvoiceRunMatchingValue` and `BillingTermUnit` fields with API version 62.0 and later. In addition, this value supports the `CurrencyIsoCode` field with API version 63.0 and later; or `NotEquals`. | Required | 62.0 |
| `value` | String | Value for the filter criteria. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-batch-invoice-filter-criteria-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
