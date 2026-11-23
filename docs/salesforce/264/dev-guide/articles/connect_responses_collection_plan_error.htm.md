---
page_id: connect_responses_collection_plan_error.htm
title: Collection Plan Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_collection_plan_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Collection Plan Error

Output representation of an error that occurred while creating a
collection plan.

## JSON Example

```
{
  "errorCode": "MISSING_REQUIRED_FIELD",
  "message": "Account Id is required to create a Collection Plan when UsageType is Billing.",
  "fields": [
    "accountId"
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Machine-readable code that identifies the error, such as `MISSING_REQUIRED_FIELD`. | Big, 68.0 | 68.0 |
| `fields` | String[] | Names of the fields related to the error. | Big, 68.0 | 68.0 |
| `message` | String | Human-readable description of the error. | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_collection_plan_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
