---
page_id: connect_responses_write_off_posted_invoice_list_output.htm
title: Posted Invoice List Write-Off
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_list_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Posted Invoice List Write-Off 

Output representation of the list of invoices that are written off.

        
          

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
        "errorMessage": "Reason is missing."
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
| `result` | [Posted Invoice Write-Off](./connect_responses_write_off_posted_invoice_output.htm.md)[] | Details of the invoices for which the write-off process is initiated. | Big, 64.0 | 64.0 |
