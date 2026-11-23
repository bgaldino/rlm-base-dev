---
page_id: connect_responses_warning_message_output.htm
title: Warning Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_warning_message_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Warning Message

Output representation of the details of records that triggered this specific warning.

## JSON Example

This example shows a warning message with details.

```
{
  "warningMessages": [
    {
      "warningMessage": "PUR and RCE date ranges could be optimized for better performance",
      "warningDetails": [
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
| `warningMessage` | String | Human-readable warning message that describes the validation concern. | Big, 66.0 | 66.0 |
| `warningDetails` | [Error Warning Details](./connect_responses_error_warning_details_output.htm.md "Output representation of the individual warning or error message with associated record details.")[] | Details of records that triggered this specific warning. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_warning_message_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
