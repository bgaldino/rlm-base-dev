---
page_id: connect_requests_billing_checkout_billing_contact_input.htm
title: Billing Contact Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_billing_contact_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_input.htm
fetched_at: 2026-09-29
---

# Billing Contact Input

Input representation of billing contact details used when billingProfileId isn't provided. Creates the contact if it doesn't exist.

    

## JSON Example

      
      

```
{
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane.doe@example.com",
  "phone": "4155550100"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `email` | String | Email address of the billing contact. | Optional | 68.0 |
| `first​Name` | String | First name of the billing contact. | Optional | 68.0 |
| `last​Name` | String | Last name of the billing contact. | Optional | 68.0 |
| `phone` | String | Phone number of the billing contact. | Optional | 68.0 |
