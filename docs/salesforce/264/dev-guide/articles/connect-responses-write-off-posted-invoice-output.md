---
page_id: connect-responses-write-off-posted-invoice-output
title: Posted Invoice Write-Off
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-write-off-posted-invoice-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_write_off_posted_invoice_output.htm
fetched_at: 2026-11-25
---

# Posted Invoice Write-Off

Output representation of the details of a posted invoice that’s written off.

## JSON Example

```
{
  "result": [
    {
      "requestIdentifier": null,
      "invoiceId": "3t00000000CwAGI",
      "success": false,
      "errors": {
        "errorcode": "INVALID_API_INPUT",
        "errorMessage": "Reason is missing"
      }
    },
    {
      "requestIdentifier": 37612787,
      "invoiceId": "3t00000000CwAAI",
      "success": true,
      "errors": {
        "errorcode": null,
        "errorMessage": null
      }
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Posted Invoice Write-Off Error](./connect-responses-write-off-posted-invoice-output-error.md)[] | If the request fails, this property contains a list of errors. | Small, 64.0 | 64.0 |
| `invoiceId` | String | ID of the invoice record that’s written off. | Big, 64.0 | 64.0 |
| `request​Identifier` | String | If the request is successful, this property contains an asynchronous API request identifier for an invoice ID. | Big, 64.0 | 64.0 |
| `success` | Boolean | Indicates whether the invoice write-off request was successful (`true`) or not (`false`). | Big, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-write-off-posted-invoice-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
