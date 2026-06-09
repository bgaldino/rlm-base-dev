---
page_id: connect_responses_credit_memo_line_applied_response.htm
title: Credit Memo Line Applied Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_line_applied_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Credit Memo Line Applied Response

Output representation of the list of applied credit memo line results.

JSON example
:   ```
      "appliedCreditResponses": [
       {
        "creditMemoLineInvoiceLineId": "4sGSG0000002pMb2AI",
        "errors": null,
        "invoiceLineId": "5TVSG0000003CuH4AU",
        "success": true
       }
      ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemo​LineInvoice​LineId` | String | ID of the credit memo line invoice line ID. | Big, 62.0 | 62.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `invoice​LineId` | String | ID of the invoice line record that the credit is applied to. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the credit memo line is successfully applied (`true`) or not (`false`). | Big, 62.0 | 62.0 |
