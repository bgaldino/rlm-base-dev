---
page_id: connect-responses-update-favorite-output
title: Configuration Update
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-update-favorite-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_update_favorite_output.htm
fetched_at: 2026-11-25
---

# Configuration Update

Output representation of the details of the updated configuration.

## JSON Example

This example shows a sample when the update operation is successful.

```
{
  "errors": [],
  "success": true
}
```

This example shows a sample when the update operation has errors.

```
{
  "errors": [
    {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "INVALID_REFERENCEOBJECTID"
    }
  ],
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](./connect-responses-configuration-list-error-response.md) | List of errors that contains a message and an error code. | Small, 63.0 | 63.0 |
| `success` | Boolean | Indicates whether the update operation is successful (`true`) or not (`false`) | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-update-favorite-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
