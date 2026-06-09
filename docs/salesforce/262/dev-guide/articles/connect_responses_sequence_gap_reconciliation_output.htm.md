---
page_id: connect_responses_sequence_gap_reconciliation_output.htm
title: Sequence Gap Reconciliation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_gap_reconciliation_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Sequence Gap Reconciliation

Output representation of the details of the sequence gap reconciliation.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "jobId": "0B1xx0000006P12",
      "sequencePolicyIds": [
        "1vdxx0000000uyr",
        "1vdxx0000000lrf"
      ],
      "targetObjects": [
        "Invoice"
      ],
      "status": "Submitted",
      "submittedAt": "2025-06-05T09:12:28Z",
      "error": {}
    }
    ```
:   This example shows a sample error response for an invalid
    input.

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
        "message": "Missing required field in the request."
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Sequence Gap Reconciliation Error](./connect_responses_sequence_gap_reconciliation_error_output.htm.md "Output representation of the errors encountered during the processing of the API request.")[] | List of errors encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `jobId` | String | Unique identifier assigned to the sequence gap reconciliation asynchronous process. | Big, 65.0 | 65.0 |
| `sequence​PolicyIds` | String[] | List of IDs of the sequence policies. | Big, 65.0 | 65.0 |
| `status` | String | Status of the sequence gap reconciliation API request. Valid values are:   - `Submitted` - `NotSubmitted` | Big, 65.0 | 65.0 |
| `submitted​At` | String | Date and time when the reconciliation request was submitted to the async job. | Big, 65.0 | 65.0 |
| `target​Objects` | String[] | List of objects to which the policies are applied. | Big, 65.0 | 65.0 |
