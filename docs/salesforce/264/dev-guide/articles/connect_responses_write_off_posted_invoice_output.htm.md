---
page_id: connect_responses_write_off_posted_invoice_output.htm
title: Posted Invoice Write-Off
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Posted Invoice Write-Off

Output representation of the details of a posted invoice that's written off.

        
          

**JSON example**

          
: 
            

```
{
  "result": [
    {
      "requestIdentifier": null,
      "invoiceId": "3t00000000CwAGI",
      "success": false,
      "errors": {
        "errorcode": "INVALID_API_INPUT",
        "errorMessage": "Reason is missing"
      }
    },
    {
      "requestIdentifier": 37612787,
      "invoiceId": "3t00000000CwAAI",
      "success": true,
      "errors": {
        "errorcode": null,
        "errorMessage": null
      }
    }
  ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Posted Invoice Write-Off Error](./connect_responses_write_off_posted_invoice_output_error.htm.md)[] | If the request fails, this property contains a list of errors. | Small, 64.0 | 64.0 |
| `invoiceId` | String | ID of the invoice record that's written off. | Big, 64.0 | 64.0 |
| `request​Identifier` | String | If the request is successful, this property contains an asynchronous API request identifier for an invoice ID. | Big, 64.0 | 64.0 |
| `success` | Boolean | Indicates whether the invoice write-off request was successful (`true`) or not (`false`). | Big, 64.0 | 64.0 |
