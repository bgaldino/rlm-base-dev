---
page_id: connect_responses_billing_schedule_recovery_list_output.htm
title: Billing Schedule Recovery List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_schedule_recovery_list_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Billing Schedule Recovery List

Output representation of the recovered details of the billing schedules and associated
invoice.

JSON example
:   ```
    {
      "recoveryResults": [
        {
          "billingSchedules": [
            {
              "billingScheduleId": "44bDU00000000XX",
              "billingScheduleStatus": "ReadyForInvoicing"
            }
          ],
          "invoiceErrors": [],
          "invoiceId": null,
          "success": true
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recovery​Results` | [Invoice Recovery](./connect_responses_invoice_recovery_output.htm.md "Output representation of the details of the recovered invoice and billing schedules.")[] | Details of the recovered invoice and billing schedules. | Big, 62.0 | 62.0 |
