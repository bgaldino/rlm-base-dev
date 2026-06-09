---
page_id: connect_requests_payment_scheduler_input.htm
title: Payment Batch Scheduler Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_payment_scheduler_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Payment Batch Scheduler Input

Input representation of the details of the request to create a payment scheduler. This
representation sets the rules and timing for a payment scheduler, including match types, dates,
frequency, and filter criteria.

JSON example
:   JSON example
    :   ```
        {
          "schedulerName": "Payment Scheduler",
          "startDate": "2022-01-01",
          "endDate": "2022-12-31",
          "preferredTime": "02:05:00.000",
          "frequencyCadence": "Monthly",
          "recursEveryMonthOnDay": "28",
          "criteriaMatchType": "MatchAny",
          "status": "Active",
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
        }
        ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `criteria​MatchType` | String | Match type for the criteria of the payment scheduler. Valid values are:   - `Match Any` - `Match None` | Required if the `frequencyCadence` property is set to `Monthly`. | 64.0 |
    | `endDate` | String | End date of the payment scheduler. | Required if the `frequencyCadence` property is set to `Monthly`. | 64.0 |
    | `frequency​Cadence` | String | Frequency cadence of the payment scheduler. Valid values are:   - `Once` - `Daily` - `Weekly` - `Monthly` | Required | 64.0 |
    | `filter​Criteria` | [Payment Run Batch Filter Criteria Input](./connect_requests_payment_run_batch_filter_criteria_input.htm.md "Input representation of the filter criteria for an invoice batch run. This representation covers the criteria and sequence for filtering payment run details. It specifies the field and object names, comparison operations, and values to be used for filtering.") | List of criteria that are used to filter the payment run details. | Required if the `frequencyCadence` property is set to `Monthly`. | 64.0 |
    | `preferredTime` | String | Preferred time for the payment scheduler run. | Required | 64.0 |
    | `recursEvery​MonthOnDay` | String | Date when the payment scheduler recurs. | Required if the `frequencyCadence` property is set to `Monthly`. | 64.0 |
    | `scheduler​Name` | String | Name of the payment scheduler. | Required | 64.0 |
    | `startDate` | String | Start date of the payment scheduler. | Required | 64.0 |
    | `status` | String | Status of the payment scheduler. Valid values are:   - `Active` - `Canceled` - `Draft` - `Inactive` | Required | 64.0 |
