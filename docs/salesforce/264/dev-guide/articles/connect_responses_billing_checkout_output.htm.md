---
page_id: connect_responses_billing_checkout_output.htm
title: Billing Checkout
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_checkout_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-09-29
---

# Billing Checkout

Output representation of the billing checkout transaction result.

    

## JSON Example

      
      

```
{
  "checkoutStatus": "InProgressPayment",
  "paymentId": "0azXXXXXXXXXXXXXXX",
  "paymentMethodId": "0dpXXXXXXXXXXXXXXX",
  "asyncOperationTrackerId": "9btXXXXXXXXXXXXXXX",
  "statusURL": "/services/data/v64.0/sobjects/RevenueAsyncOperation/9btXXXXXXXXXXXXXXX",
  "invoicePreview": null,
  "errorsList": []
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `async​Operation​Tracker​Id` | String | ID of the AsyncOperationTracker record that tracks the async message queue processing of this checkout. | Small, 68.0 | 68.0 |
| `checkout​Status` | String | End-to-end status of the checkout process. | Small, 68.0 | 68.0 |
| `errors​List` | [Billing Checkout Error](./connect_responses_billing_checkout_error.htm.md)[] | Details of the errors generated during the checkout transaction. | Big, 68.0 | 68.0 |
| `invoice​Preview` | [Invoice Preview Result](./connect_responses_invoice_preview_output.htm.md) | Invoice Preview API response for the checkout cart. Populated only when `previewInvoice` is `true`. | Big, 68.0 | 68.0 |
| `payment​Id` | String | ID of the successful payment record. | Big, 68.0 | 68.0 |
| `payment​Method​Id` | String | ID of the newly saved payment method, if a new payment method was saved. | Big, 68.0 | 68.0 |
| `status​URL` | String | URL to poll for the status of the async checkout processing (the RevenueAsyncOperation record). | Small, 68.0 | 68.0 |

    

  

- 
**[Billing Checkout Error](./connect_responses_billing_checkout_error.htm.md)**  

Output representation of an error that occurred during a checkout transaction.
