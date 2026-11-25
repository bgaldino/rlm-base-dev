---
page_id: connect-responses-object-with-reference-response
title: Object Reference
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-object-with-reference-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_object_with_reference_response.htm
fetched_at: 2026-11-25
---

# Object Reference

Output representation of an sObject with a reference ID along with any potential error.

## Sample Response

```
{
  "referenceid": "refQuote",
  "record": {
    "attributes": {
      "type": "Quote",
      "method": "POST"
    },
    "quantity": "2"
  },
  "error": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Reference Id format is irrelevant."
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `referenceId` | String | ID that identifies the specific Salesforce object that’s returned in the API response. | Small, 59.0 | 59.0 |
| `record` | Map<String, Object> | The sObject record data represented as a map of attribute names to their values. | Small, 59.0 | 59.0 |
| `error` | [https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm)[] | Detailed information about any error associated with the sObject in the response. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-object-with-reference-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
