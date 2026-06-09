---
page_id: connect_responses_sequence_gap_reconciliation_error_output.htm
title: Sequence Gap Reconciliation Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_gap_reconciliation_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Sequence Gap Reconciliation Error

Output representation of the errors encountered during the processing of the API
request.

JSON example
:   This example shows a sample error
    response.

    ```
    {
      "jobId": "",
      "sequencePolicyIds": [
        "1vdxx0000000abc",
        "1vdxx0000000def"
      ],
      "targetObjects": [
        "Invoice"
      ],
      "status": "NotSubmitted",
      "submittedAt": "",
      "error": {
        "errorCode": "INVALID_INPUT",
        "message": "Specify a value for either sequencePolicyIds or targetObjects."
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code for the resultant error. | Big, 65.0 | 65.0 |
| `error​Message` | String | Error message for the resultant error. | Big, 65.0 | 65.0 |
