---
page_id: connect_responses_invoice_recovery_output.htm
title: Invoice Recovery
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_recovery_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Invoice Recovery

Output representation of the details of the recovered invoice and billing schedules.

## JSON Example

```
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
| `billing​Schedules` | [Billing Schedule Recovery](./connect_responses_billing_schedule_recovery_output.htm.md "Output representation of the details of the recovered billing schedules.")[] | Billing schedules associated with this invoice. | Big, 62.0 | 62.0 |
| `invoice​Errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors encountered during the invoice recovery. | Big, 62.0 | 62.0 |
| `invoice​Id` | String | ID of the recovered invoice. | Big, 62.0 | 62.0 |
| `invoice​Status` | String | Flag that indicates the invoice status. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the overall transaction was successful or not (`true`) or not (`false`). | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_recovery_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
