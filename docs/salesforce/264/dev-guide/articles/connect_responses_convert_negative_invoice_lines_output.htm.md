---
page_id: connect_responses_convert_negative_invoice_lines_output.htm
title: Convert Negative Invoice Lines
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_convert_negative_invoice_lines_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Convert
    Negative Invoice Lines

Output representation of the details of the created memo along with the status of the
    request.

        
          

**JSON example**

          
: 
            

```
  {
  "id": "50gxx000000g0WwAAI",
  "success": true,
  "errors": []
  }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.252.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `id` | String | ID of the credit memo that’s created after the conversion of the negative invoice lines. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
