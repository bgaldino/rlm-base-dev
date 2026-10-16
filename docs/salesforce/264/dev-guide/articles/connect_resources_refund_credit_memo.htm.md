---
page_id: connect_resources_refund_credit_memo.htm
title: Refund Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_refund_credit_memo.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-09-29
---

# Refund Credit Memo (POST)

Initiate a refund against a credit memo.

    
      

Initiates a refund for a credit memo. Locks the credit memo, calls the Commerce Refund API, and applies the refund inline (sync) or defers the apply until the payment gateway event is received (async).

    

    

## Resource

      
      

```
/revenue/billing/refunds/unreferenced-refunds/actions/process
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/revenue/billing/refunds/unreferenced-refunds/actions/process
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "appliedToId": "0PMxx0000000001AAA",
  "refundAmount": 100,
  "currencyIsoCode": "USD",
  "refundReason": "Customer requested refund",
  "paymentMethodId": "08pxx0000000001AAA",
  "refundNotes": "Refund processed per case 00298475."
}
```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applied​To​Id` | String | ID of the credit memo that the refund is applied to. | Required | 68.0 |
| `currency​Iso​Code` | String | ISO currency code. Required when multi-currency is enabled. Must match the credit memo's currency. | Required if multi-currency is enabled | 68.0 |
| `payment​Method​Id` | String | ID of the payment method to issue the refund. Must reference a valid, active payment method. | Required | 68.0 |
| `refund​Amount` | Double | Amount to be refunded. Must be greater than 0 and not exceed the remaining balance on the credit memo. | Required | 68.0 |
| `refund​Notes` | String | Optional notes that are stored in the comments of the refund entity. | Optional | 68.0 |
| `refund​Reason` | String | Reason for the refund. | Required | 68.0 |

    

    

## Response Body for POST

      
      

[Refund Credit Memo](./connect_responses_refund_credit_memo_output.htm.md)
