---
page_id: connect_responses_batch_invoice_doc_gen_output.htm
title: Batch Invoice Document Generation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_invoice_doc_gen_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Batch Invoice Document Generation

Output representation of the request to generate or regenerate the PDF documents for
      the invoices that are in the `Draft` or `Posted` status.

        
          

**JSON example**

          
: 
            

```
{
  "errors": [
    {
      "errorCode": "API_DISABLED_FOR_ORG",
      "errorMessage": "Document Generation is not enabled for this org!"
    },
    {
      "errorCode": "INVALID_API_INPUT",
      "errorMessage": "Invalid Invoice Batch Run Id"
    }
  ],
  "requestIdentifier": "5IRDU000000009i4AA",
  "success": false
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Batch Invoice Document Generation Error []](./connect_responses_batch_invoice_doc_gen_error.htm.md) | Details of the error if the operation fails. | Big, 63.0 | 63.0 |
| `requestIdentifier` | String | Unique ID that’s associated with the specific error, and is used for tracking and referencing the request. | Big, 63.0 | 63.0 |
| `success` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Big, 63.0 | 63.0 |
