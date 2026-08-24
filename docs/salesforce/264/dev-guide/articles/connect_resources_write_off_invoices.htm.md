---
page_id: connect_resources_write_off_invoices.htm
title: Posted Invoice List Write-Off (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_write_off_invoices.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Posted Invoice List Write-Off (POST)

Create credit memos with the total charge amount on the invoice as the
      write-off amount and close the invoice.

    
      

You can write off invoices to maintain accurate financial records and to prioritize
        invoices with a higher probability of payment, which is essential for compliance with
        accounting standards.

    

    

## Special Access Rules

      
      

To use this API, you need the Billing Operations User or Credit Memo Operations User
        permission set.

    

    
      
        
          

**Resource**

          
: 
            

```
/commerce/invoicing/invoices/actions/write-off
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/actions/write-off
```

          

        
        
          

**Available version**

          
: 64.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "invoices": [
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Bad Debt",
      "description": "Bad Debt"
    },
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Concession",
      "description": "Concession"
    }
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoices` | [Posted Invoice Write-Off Input](./connect_requests_write_off_posted_invoice_input.htm.md)[] | Details of the invoices that you want to write off. | Required | 64.0 |

          

        
        
          

**Response body for POST**

          
: [Posted Invoice List
              Write-Off](./connect_responses_write_off_posted_invoice_list_output.htm.md)
