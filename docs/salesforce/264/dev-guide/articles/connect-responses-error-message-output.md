---
page_id: connect-responses-error-message-output
title: Error Message
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-error-message-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_error_message_output.htm
fetched_at: 2026-11-25
---

# Error Message

Output representation of the details of records that failed with this specific error.

## JSON Example

This example shows an error message with details.

```
{
  "errorMessages": [
    {
      "errorMessage": "PUR and RCE effective date ranges must have overlap for proper rating functionality",
      "errorDetails": [
        {
          "relatedObjectAPIName": "ProductUsageRule",
          "records": [
            {
              "id": "a0bxx0000004CqZAAU",
              "name": "PUR-001"
            }
          ]
        }
      ]
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Human-readable error message that describes the validation failure. | Big, 66.0 | 66.0 |
| `errorDetails` | [Error Warning Details](./connect-responses-error-warning-details-output.md)[] | Details of records that failed with this specific error. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-error-message-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
