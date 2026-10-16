---
page_id: connect_responses_addresses_output.htm
title: Addresses
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_addresses_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Addresses

Output representation of the details of the addresses that are used for calculating
    tax.

    

        
          

**JSON example**

          
: 
            

```
{
  "addresses": {
    "shipFrom": {
      "locationCode": "67890"
    },
    "shipTo": {
      "locationCode": "12345"
    },
    "soldTo": {
      "locationCode": "12345"
    }
  }
}

```

          

        
      

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `shipFrom` | [Address](./connect_responses_address_output.htm.md) | Address that the item is shipped from. | Big, 62.0 | 62.0 |
| `shipTo` | [Address](./connect_responses_address_output.htm.md) | Address that the item is shipped to. | Big, 62.0 | 62.0 |
| `soldTo` | [Address](./connect_responses_address_output.htm.md) | Address that the item is sold to. | Big, 62.0 | 62.0 |
