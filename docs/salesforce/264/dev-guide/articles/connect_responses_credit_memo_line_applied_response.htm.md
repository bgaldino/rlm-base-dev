---
page_id: connect_responses_credit_memo_line_applied_response.htm
title: Credit Memo Line Applied Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_line_applied_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Credit Memo Line Applied Response

Output representation of the list of applied credit memo line results.

        
          

**JSON example**

          
: 
            

```
  "appliedCreditResponses": [
   {
    "creditMemoLineInvoiceLineId": "4sGSG0000002pMb2AI",
    "errors": null,
    "invoiceLineId": "5TVSG0000003CuH4AU",
    "success": true
   }
  ]
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemo​LineInvoice​LineId` | String | ID of the credit memo line invoice line ID. | Big, 62.0 | 62.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `invoice​LineId` | String | ID of the invoice line record that the credit is applied to. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the credit memo line is successfully applied (`true`) or not (`false`). | Big, 62.0 | 62.0 |
