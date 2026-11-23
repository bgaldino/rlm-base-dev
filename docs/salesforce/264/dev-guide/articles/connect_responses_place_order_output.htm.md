---
page_id: connect_responses_place_order_output.htm
title: Place Order Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_order_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-11-23
---

# Place Order Response

Output representation of the request to create or update an order.

## JSON Example

```
{
  "requestId": "16PRM0000004DBq",
  "orderId": "801S70000001VKgIAM",
  "success": true,
  "errors": [],
  "statusURL": "/services/data/vXX.X/sobjects/AsyncOperationTracker/16PRM0000004DBq"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Place Order​Error​Response](./connect_responses_place_order_error_response.htm.md "Output representation of the error response for the place order request.")[] | List of errors encountered during the synchronous processing. | Small, 60.0 | 60.0 |
| `orderId` | String | ID of the order created after a successful request. | Small, 60.0 | 60.0 |
| `requestId` | String | Request ID of the process to query asynchronous status of the place order API. | Small, 60.0 | 60.0 |
| `status​URL` | String | Asynchronous status URL of the request, if available. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_order_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
