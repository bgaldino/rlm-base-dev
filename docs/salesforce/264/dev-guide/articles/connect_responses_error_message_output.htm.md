---
page_id: connect_responses_error_message_output.htm
title: Error Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_message_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
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
| `errorDetails` | [Error Warning Details](./connect_responses_error_warning_details_output.htm.md "Output representation of the individual warning or error message with associated record details.")[] | Details of records that failed with this specific error. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_message_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
