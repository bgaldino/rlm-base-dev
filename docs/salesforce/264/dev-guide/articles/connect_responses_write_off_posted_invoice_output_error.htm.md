---
page_id: connect_responses_write_off_posted_invoice_output_error.htm
title: Posted Invoice Write-Off Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_output_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Posted Invoice Write-Off Error 

Output representation of the error response that's associated with a request to write off
    a posted invoice.

      
        
          

**JSON example**

          
: 
            

```
{
  "errors": {
    "errorcode": "INVALID_API_INPUT",
    "errorMessage": "Reason is missing"
  }
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that represents the error. | Small, 64.0 | 64.0 |
| `error​Message` | String | Message that describes the error. | Small, 64.0 | 64.0 |
