---
page_id: connect-responses-configuration-list-error-response
title: Error Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configuration-list-error-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_configuration_list_error_response.htm
fetched_at: 2026-11-25
---

# Error Response

Output representation of the details of the error.

## JSON Example

```
{
  "errors": [
    {
      "code": "BAD_REQUEST",
      "message": "MISSING_REFERENCEOBJECTID"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the error. | Small, 63.0 | 63.0 |
| `message` | String | Description of the error. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configuration-list-error-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
