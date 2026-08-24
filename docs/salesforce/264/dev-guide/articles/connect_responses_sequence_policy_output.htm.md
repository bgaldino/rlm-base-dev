---
page_id: connect_responses_sequence_policy_output.htm
title: Sequence Policy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_policy_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Sequence Policy

Output representation that shows the status of the assigned sequence pattern
    values.

        
          

**JSON example**

          
: This example shows a sample successful
            response.

```
{
  "error": null,
  "isSuccess": true,
  "sequencePolicyId": "1Vdxx0000000GRNAA2"
}
```

          
: This example shows a sample error
            response.

```
{
  "error": {
    "errorCode": "INVALID_INPUT",
    "message": "Specify a valid selectionLogic."
  },
  "isSuccess": false,
  "sequencePolicyId": null
}
```

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Sequence Error](./connect_responses_sequence_error_output.htm.md)[] | Details of any error that encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the sequence policy is generated (`true`) or not (`false`). | Big, 65.0 | 65.0 |
| `sequencePolicyId` | String | ID of the sequence policy. | Big, 65.0 | 65.0 |
