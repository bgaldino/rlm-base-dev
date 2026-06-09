---
page_id: connect_responses_on_demand_doc_gen_output.htm
title: On-Demand Document Generation Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_on_demand_doc_gen_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# On-Demand Document Generation Response

Output representation of the details of the generated document along with error
response.

JSON example
:   ```
    {
      "requestIdentifier": "aad8ee2d-d94d-4760-8759-a2c5d63ce6db",
      "isSuccess": true,
      "details": {
        "documentEntityId": "1BBSM00000003KT4AY",
        "documentGenerationProcessId": "0nnSM00000009jFYAQ",
        "documentTitle": "DOC-000000197",
        "existingDocumentId": "069SM000002PYQLYA4",
        "recordId": "3ttSM0000000o58YAA",
        "documentTemplateId": "0694x000000XyzABC"
      },
      "errors": []
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `details` | [Document Details](./connect_responses_document_details_output.htm.md "Output representation of the details of the generated document.")[] | Details of the generated document. | Big, 66.0 | 66.0 |
| `errors` | [Error Response](./connect_responses_error_response.htm.md "Output representation of the error details encountered during the API request.")[] | Error details of any issues encountered during the enqueue operation. | Big, 66.0 | 66.0 |
| `isSuccess` | Boolean | Status of the enqueuing PDF generation task. | Big, 66.0 | 66.0 |
| `requestIdentifier` | String | Unique request identifier that's used to poll the asynchronous request. | Big, 66.0 | 66.0 |
