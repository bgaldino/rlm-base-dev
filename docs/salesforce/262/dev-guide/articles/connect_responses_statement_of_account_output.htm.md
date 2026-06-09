---
page_id: connect_responses_statement_of_account_output.htm
title: Statement of Account
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_statement_of_account_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Statement of Account

Output representation of the details of the generated account statement with async
tracking details.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "requestIdentifier": "a0Bxx000000001ZEAQ",
      "statusURL": "/services/data/v60.0/commerce/billing/document-generation-process/a0Bxx000000001ZEAQ/status",
      "success": true,
      "accountId": "001xx000003DGb2AAG",
      "templateId": "0TRxx000000001XGAQ",
      "errors": null
    }
    ```
:   This example shows a sample error
    response.

    ```
    {
      "success": false,
      "errors": [
        {
          "code": "ACCOUNT_NOT_FOUND",
          "message": "Account with ID 001XX000004DKy5YAG not found",
          "field": "accountId"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | Primary account ID the statement is generated for. | Big, 66.0 | 66.0 |
| `errors` | [Error Response](./connect_responses_error_response.htm.md "Output representation of the error details encountered during the API request.")[] | List of errors encountered during the processing of the API request. | Big, 66.0 | 66.0 |
| `requestIdentifier` | String | Unique identifier for the request. | Big, 66.0 | 66.0 |
| `statusURL` | String | Status URL to track the operation. | Big, 66.0 | 66.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `templateId` | String | Document template ID that's used to generate the PDF. | Big, 66.0 | 66.0 |
