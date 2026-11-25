---
page_id: connect-responses-record-details-output
title: Record Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-record-details-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_record_details_output.htm
fetched_at: 2026-11-25
---

# Record Details

Output representation of the record details including ID and name.

## JSON Example

This example shows the record details with ID and name.

```
{
  "records": [
    {
      "id": "a0bxx0000004CqZAAU",
      "name": "PUR-001"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | Unique identifier of the object. | Big, 66.0 | 66.0 |
| `name` | String | Display name of the object. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-record-details-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
