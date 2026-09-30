---
page_id: connect_requests_billing_checkout_payment_details_input.htm
title: Billing Checkout Payment Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_payment_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_input.htm
fetched_at: 2026-09-29
---

# Billing Checkout Payment Details Input

Input representation of payment details used during checkout, referencing a saved payment method.

    

## JSON Example

      
      

```
{
  "idempotencyKey": "a1B2c3D4-e5F6-7890-gH1i-2j3K4l5M6n7O",
  "paymentGatewayId": "0cGxx0000004C99",
  "savedPaymentMethodId": "0cAxx0000004C98"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `idempotency​Key` | String | Unique key used to retry the checkout payment safely without creating a duplicate charge. | Optional | 68.0 |
| `payment​Gateway​Id` | String | Unique ID of the preconfigured payment gateway. | Optional | 68.0 |
| `saved​Payment​Method​Details` | [Saved Payment Method Details Input](./connect_requests_billing_checkout_saved_payment_method_details_input.htm.md) | Details required to create a saved payment method during checkout. | Optional | 68.0 |
| `saved​Payment​Method​Id` | String | Unique ID of the saved payment method to use during checkout. | Optional | 68.0 |

    

  

- 
**[Saved Payment Method Details Input](./connect_requests_billing_checkout_saved_payment_method_details_input.htm.md)**  

Input representation of the details required to create a saved payment method during checkout.
