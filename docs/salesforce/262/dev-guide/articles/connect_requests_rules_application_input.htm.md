---
page_id: connect_requests_rules_application_input.htm
title: Rules Application Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_rules_application_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Rules Application Input

Input representation for applying payments and credits to invoices based on rules.

JSON example
:   ```
    {
      "accountId": "001xx000003DGbQAAW",
      "targetDate": "2024-01-15"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `accountId` | String | ID of the account to perform the settlement of payments and credits against invoices in adherence with the applied rules. | Required | 66.0 |
    | `targetDate` | String | The date used to select invoices and invoice lines with a posted date equal to or later than the target date to apply payments and credits. | Optional | 66.0 |
