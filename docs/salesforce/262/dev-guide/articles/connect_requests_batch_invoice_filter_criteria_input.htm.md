---
page_id: connect_requests_batch_invoice_filter_criteria_input.htm
title: Batch Invoice Filter Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_batch_invoice_filter_criteria_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Batch Invoice Filter Criteria Input

Input representation of the filter criteria for an invoice batch run.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `field​Name` | String | Name of the field that this filter is applicable for. Valid values are:  - `Currency_Iso_code`—If   multiple currencies are enabled for the org, then   this value is required. - `InvoiceRunMatchingValue` - `BillingAccount` - `LegalEntity` - `BillingTermUnit` | Required | 62.0 |
    | `object​Name` | Object | Name of the object that the filter is applicable for. Valid values are:   - `BillingSchedule` - `BillingScheduleGroup` | Required | 62.0 |
    | `operation` | String | Operation to be performed for comparison. Valid values are:  - `Equals` - `InList`—This value supports   only the `InvoiceRunMatchingValue` and `BillingTermUnit`   fields with API version 62.0 and later. In   addition, this value supports the `CurrencyIsoCode` field   with API version 63.0 and later. - `NotEquals` | Required | 62.0 |
    | `value` | String | Value for the filter criteria. | Required | 62.0 |
