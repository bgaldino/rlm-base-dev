---
page_id: connect_responses_fields_output.htm
title: Fields Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Fields Response

Output representation of the details of the optional fields on the usage-based selling-related objects.

## JSON Example

```
  "fields": {
    "MyCustomDate__c": {
      "displayValue": "2024-09-24",
      "value": "2024-09-24T17:46:30.662Z"
    },
    "MyCustomNumber__c": {
      "displayValue": "20.0",
      "value": 20
    }
  }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Value` | String | Display value of a field. | Big, 63.0 | 63.0 |
| `value` | Object | Value of a field in its original data form. | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
