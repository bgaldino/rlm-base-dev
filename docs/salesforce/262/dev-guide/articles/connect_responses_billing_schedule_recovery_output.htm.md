---
page_id: connect_responses_billing_schedule_recovery_output.htm
title: Billing Schedule Recovery
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_schedule_recovery_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Billing Schedule Recovery

Output representation of the details of the recovered billing schedules.

JSON example
:   ```
        "billingSchedules": [
            {
              "billingScheduleId": "44bDU00000000XX",
              "billingScheduleStatus": "ReadyForInvoicing"
            }
        ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Schedule​Id` | String | ID of the billing schedule. | Big, 62.0 | 62.0 |
| `billing​Schedule​Status` | String | Flag that indicates the billing schedule status. | Big, 62.0 | 62.0 |
