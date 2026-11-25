---
page_id: connect-responses-invoice-recovery-output
title: Invoice Recovery
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-invoice-recovery-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_invoice_recovery_output.htm
fetched_at: 2026-11-25
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
| `billing​Schedules` | [Billing Schedule Recovery](./connect-responses-billing-schedule-recovery-output.md)[] | Billing schedules associated with this invoice. | Big, 62.0 | 62.0 |
| `invoice​Errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors encountered during the invoice recovery. | Big, 62.0 | 62.0 |
| `invoice​Id` | String | ID of the recovered invoice. | Big, 62.0 | 62.0 |
| `invoice​Status` | String | Flag that indicates the invoice status. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the overall transaction was successful or not (`true`) or not (`false`). | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-invoice-recovery-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
