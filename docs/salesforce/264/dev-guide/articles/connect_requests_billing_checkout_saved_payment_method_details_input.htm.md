---
page_id: connect_requests_billing_checkout_saved_payment_method_details_input.htm
title: Saved Payment Method Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_saved_payment_method_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_payment_details_input.htm
fetched_at: 2026-09-29
---

# Saved Payment Method Details Input

Input representation of the details required to create a saved payment method during checkout.

    

## JSON Example

      
      

```
{
  "gatewayToken": "tok_1NxyzAbcDef",
  "type": "Card",
  "name": "Corporate Visa",
  "gatewayReference": "pm_1NxyzAbcDef",
  "merchantAccount": "0MAxx0000004C9A"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `gateway​Reference` | String | Reference ID of the payment method at the gateway. | Optional | 68.0 |
| `gateway​Token` | String | Token that represents the saved payment method at the gateway. | Required | 68.0 |
| `merchant​Account` | String | ID of the merchant account associated with the payment method. | Optional | 68.0 |
| `name` | String | Name of the saved payment method. | Optional | 68.0 |
| `type` | String | Type of the saved payment method. Valid values are `Card`, `Us_bank_account`, `Sepa_debit`, `Ideal`, `Bancontact`, `Bacs_debit`, `Au_becs_debit`, or `Amazon_pay`. | Required | 68.0 |
