---
page_id: connect_requests_credit_invoice_line_tax_input.htm
title: Credit Invoice Line Tax Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_invoice_line_tax_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Credit Invoice Line Tax Input

Input representation of the details of the tax lines to be created manually for the
    invoice line.

    
      
        
          

**JSON example**

          
: 
            

```
      "taxes": [
        {
          "taxAmount": 15,
          "taxName": "abc",
          "taxCode": "taxCode",
          "taxRate": 7
        }
      ]
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `taxAmount` | Double | Amount of tax to be applied related to this invoice line. | Required | 62.0 |
| `taxCode` | String | Tax code to be applied related to this invoice line to create the tax line. | Optional | 62.0 |
| `taxName` | String | Name of tax to be applied related to this invoice line. | Optional | 62.0 |
| `taxRate` | Double | Tax rate used to create the tax line. | Optional | 62.0 |
