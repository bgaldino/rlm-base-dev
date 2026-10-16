---
page_id: connect_requests_billing_checkout_customer_details_input.htm
title: Billing Checkout Customer Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_customer_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_input.htm
fetched_at: 2026-09-29
---

# Billing Checkout Customer Details Input

Input representation of customer details used to create a customer when accountId isn't provided.

    

## JSON Example

      
      

```
{
  "companyName": "Acme Corporation",
  "currencyIsoCode": "USD",
  "email": "billing@acme.example.com",
  "website": "https://www.acme.example.com"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `company​Name` | String | Name of the customer's company. | Optional | 68.0 |
| `currency​Iso​Code` | String | ISO currency code for the customer. | Optional | 68.0 |
| `email` | String | Email address of the customer. | Optional | 68.0 |
| `website` | String | Website of the customer. | Optional | 68.0 |
