---
page_id: connect_responses_sequence_gap_reconciliation_error_output.htm
title: Sequence Gap Reconciliation Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_gap_reconciliation_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequence Gap Reconciliation Error

Output representation of the errors encountered during the processing of the API
    request.

      
        
          

**JSON example**

          
: This example shows a sample error
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
