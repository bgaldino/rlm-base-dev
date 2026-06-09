---
page_id: connect_requests_create_ramp_deal_input.htm
title: Create Ramp Deal Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_create_ramp_deal_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Create Ramp Deal Input

Input representation of the request to create a ramp deal.

JSON example
:   ```
    {
      "transactionId": "0Q0xx0000004C92CAE",
      "transactionLineId": "0QLxx0000004C9VGAU",
      "subscriptionTerm": 14,
      "subscriptionTermUnit": "MONTHS",
      "trialTerm": 45,
      "trialTermUnit": "DAYS",
      "segmentType": "YEARLY",
      "executionSettings": {
           "executePricing": true,
           "executeConfigRules": false
       }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `execution​Settings` | [Execution Settings Input](./connect_requests_execution_settings_input.htm.md "Input representation of the execution settings for a ramp deal.")[] | Settings to run the pricing or configuration rules. | Optional | 62.0 |
    | `segment​Type` | String | Type of segment that the user wants to create. Valid values are:  - `FREE_TRIAL` - `CUSTOM` - `YEARLY` | Required | 62.0 |
    | `subscription​Term` | Integer | Subscription length of the term-defined product. | Required | 62.0 |
    | `subscription​TermUnit` | String | Unit of time for the subscription length. Valid value is:   - `MONTHS` | Required | 62.0 |
    | `transaction​Id` | String | ID of the sales transaction that’s configured, such as quote or order. | Required | 62.0 |
    | `transaction​LineId` | String | Quote line item ID or order item ID that the price ramp is created for. | Required | 62.0 |
    | `trialTerm` | Integer | Length of the trial period, if any. | Optional | 62.0 |
    | `trialTerm​Unit` | String | Unit of time for the trial period. Valid value is:   - `DAYS` | Optional. Required if `trialTerm` property is specified. | 62.0 |
