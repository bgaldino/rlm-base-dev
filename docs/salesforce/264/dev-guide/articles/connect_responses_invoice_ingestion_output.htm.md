---
page_id: connect_responses_invoice_ingestion_output.htm
title: Invoice Ingestion Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_ingestion_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Invoice Ingestion Details

Output representation of the details of a generated invoice.

## JSON Example

```
{
  "invoices": [
    {
      "errors": null,
      "invoiceId": "3ttxx0000000GRNAA2",
      "requestIdentifier": "16e80fbc-e7b3-4462-9439-745647fcf0a8",
      "statusURL": "/services/data/v63.0/sobjects/AsyncOperationTracker/16Pxx0000004Gz2EAE",
      "success": true
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Invoice Ingestion Output Error](./connect_responses_invoice_ingestion_output_error.htm.md "Output representation of the details of an invoice generation error.")[] | Details of the errors if the request was unsuccessful. | Small, 63.0 | 63.0 |
| `invoice​Id` | String | ID of the Invoice record that’s created in Salesforce. | Small, 63.0 | 63.0 |
| `request​Identifier` | String | Unique request identifier that can be used to poll the async request. | Small, 63.0 | 63.0 |
| `status​URL` | String | Status URL for tracking the estimated tax callout operation. | Big, 63.0 | 63.0 |
| `success` | Boolean | Indicates whether the API request was successful (`true`) or not (`false`). | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_ingestion_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
