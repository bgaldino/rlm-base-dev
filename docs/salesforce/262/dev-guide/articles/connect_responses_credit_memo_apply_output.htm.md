---
page_id: connect_responses_credit_memo_apply_output.htm
title: Credit Memo Apply
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_apply_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Credit Memo Apply

Output representation of the list of applied credit memo results.

JSON example
:   ```
      "applyCreditResults" : [ {
        "appliedToId" : "3ttxx000000003FAAQ",
        "errors" : null,
        "id" : "4sFxx00000002ppEAA",
        "success" : true
      }, {
        "appliedToId" : "3ttxx0000000001AAA",
        "errors" : null,
        "id" : "4sFxx00000002pqEAA",
        "success" : true
      } ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `appliedToId` | String | ID of the invoice record that the credit is applied to. | Big, 62.0 | 62.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `id` | String | ID of the credit memo invoice application. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the credit memo is successfully applied (`true`) or not (`false`). | Big, 62.0 | 62.0 |
