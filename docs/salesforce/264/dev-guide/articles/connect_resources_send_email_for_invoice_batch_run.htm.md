---
page_id: connect_resources_send_email_for_invoice_batch_run.htm
title: Send Emails for Posted Invoices (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_send_email_for_invoice_batch_run.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Send Emails for Posted Invoices (POST)

Send emails for the posted invoices of a specified invoice batch run
      ID.

    
      

Each email includes a custom message template in the email body and an attachment of the
        Invoice Document PDF. The email template is based on the user preferences defined on the
        Billing Profile, Legal Entity, or Billing Settings page.

    

    

## Special Access Rules

      
      

Enable the **Configure Email Delivery Settings** toggle from the Billing
        Settings page from Setup.

    

    
      
        
          

**Resource**

          
: 
            

```
/commerce/invoicing/invoice-batch-runs/actions/send-email
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoice-batch-runs/actions/send-email
```

          

        
        
          

**Available version**

          
: 65.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example**

          
: 
            

```
{
  "invoiceBatchRunId": "5IRLT000001SIJB4A4"
}
```

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatchRunId` | String | ID of the invoice batch run record to send emails for the posted invoices of an invoice batch run. | Required | 65.0 |

          

        
      

          

        
        
          

**Response body for POST**

          
: [Send Email
              Response](./connect_responses_send_email_for_invoice_batch_run_output.htm.md)
