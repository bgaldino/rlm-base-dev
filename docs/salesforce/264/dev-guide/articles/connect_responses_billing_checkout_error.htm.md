---
page_id: connect_responses_billing_checkout_error.htm
title: Billing Checkout Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_checkout_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_responses_billing_checkout_output.htm
fetched_at: 2026-09-29
---

# Billing Checkout Error

Output representation of an error that occurred during a checkout transaction.

    

## JSON Example

      
      

```
{
  "errorCode": "PaymentAmountMustMatchInvoiceTotal",
  "message": "The payment amount must match the invoice total for a full payment."
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Error code for the checkout failure. | Small, 68.0 | 68.0 |
| `message` | String | Message that states the reason for the error, if any. | Small, 68.0 | 68.0 |
