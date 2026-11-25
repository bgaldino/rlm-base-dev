---
page_id: connect-responses-revenue-async-line-level
title: Revenue Async Line Level
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-revenue-async-line-level.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_revenue_async_line_level.htm
fetched_at: 2026-11-25
---

# Revenue Async Line Level

Output representation of the result of the API request for the async line level operations.

## JSON Example

```
  {
  "success": true,
  "requestIdentifier": "237e9877-e79b-12d4-a765-321741963000",
  "errors":[]
}
```

If the API request fails, the `referenceLineErrorResults` property contains a list of errors grouped by the invoice line IDs.

```
[
  {
    "referenceLineId": "5TV9A000007x2gz",
    "errors": [
      {
        "errorCode": "INVALID_INPUT",
        "message": "Invalid invoice line id"
      }
    ]
  }
]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | Details of errors, if any. | Big, 62.0 | 62.0 |
| `referenceLine​Error​Results` | [Reference Line Error](./connect-responses-reference-line-error.md)[] | List of errors grouped by the invoice line IDs if the API request fails. | Big, 62.0 | 62.0 |
| `reference​Line​Type` | String | Reference type for the reference line entity in the `referenceLineErrorResults` property. | Big, 62.0 | 62.0 |
| `request​Identifier` | String | Unique identifier of the request. | Big, 62.0 | 62.0 |
| `status​URL` | String | URL to track the status of the operation. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-revenue-async-line-level.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
