---
page_id: connect_requests_payment_run_batch_filter_criteria_input.htm
title: Payment Run Batch Filter Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_run_batch_filter_criteria_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Payment Run Batch Filter Criteria Input

Input representation of the filter criteria for an invoice batch run. This representation
covers the criteria and sequence for filtering payment run details. It specifies the field and
object names, comparison operations, and values to be used for filtering.

JSON example
:   ```
      "filterCriteria": [
        {
          "objectName": "PaymentScheduleItem",
          "fieldName": "PaymentRunMatchingValue",
          "operation": "Equals",
          "value": "1",
          "criteriaSequence": 1
        },
        {
          "objectName": "PaymentScheduleItem",
          "fieldName": "PaymentRunMatchingValue",
          "operation": "Equals",
          "value": "2",
          "criteriaSequence": 2
        },
        {
          "objectName": "PaymentScheduleItem",
          "fieldName": "PaymentRunMatchingValue",
          "operation": "Equals",
          "value": "3",
          "criteriaSequence": 3
        }
      ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `criteriaSequence` | Integer | Sequence that's used to filter the payment run details. | Required | 64.0 |
    | `fieldName` | String | Name of the field that this filter is applicable for. Valid value is `PaymentRunMatchingValue`. | Required | 64.0 |
    | `objectName` | Object | Name of the object that the filter is applicable for. Valid value is `PaymentScheduleItem`. | Required | 64.0 |
    | `operation` | String | Operation that's used for comparison. Valid values are:   - `Equals` - `InList` - `NotEquals` | Required | 64.0 |
    | `value` | String | Value that's used for the filter criteria. | Required | 64.0 |
