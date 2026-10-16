---
page_id: connect_responses_line_item_output.htm
title: Line Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_line_item_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Line Item

Output representation of the details of the line item.

    

        
          

**JSON example**

          
: 
            

```
{
  "lineItems": [
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
      },
      "amountDetails": {
        "exemptAmount": 0,
        "taxAmount": 12.5,
        "totalAmount": 100,
        "totalAmountWithTax": 112.5
      },
      "effectiveDate": "2022-03-09T10:55:38.416Z",
      "lineNumber": "001xx000003HYEiAAO",
      "productCode": "Y0001",
      "quantity": 1,
      "taxCode": "TX0001",
      "taxes": [
        {
          "exemptAmount": 0,
          "exemptReason": "NoExemption",
          "imposition": {
            "type": "General"
          },
          "jurisdiction": {
            "country": "US",
            "id": "63000",
            "level": "CIT",
            "name": "SEATTLE",
            "region": "WA",
            "stateAssignedNo": "1726"
          },
          "rate": 12.5,
          "tax": 12.5,
          "taxId": "11000378132466",
          "taxableAmount": 100
        }
      ]
    }
  ]
}

```

          

        
      

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Addresses](./connect_responses_addresses_output.htm.md) | Different types of addresses that are used for the transaction of the line item. | Big, 62.0 | 62.0 |
| `amountDetails` | [Tax Amount Details](./connect_responses_tax_amount_details_output.htm.md) | Details of the transaction amount and the taxes applicable for the line item. | Big, 62.0 | 62.0 |
| `effectiveDate` | String | Date when the tax rules are applied on the line item. | Big, 62.0 | 62.0 |
| `lineNumber` | String | Unique identifier of the line item. | Big, 62.0 | 62.0 |
| `productCode` | String | Product code of the line item as defined by the tax engine. | Big, 62.0 | 62.0 |
| `quantity` | Double | Quantity of the line item. | Big, 62.0 | 62.0 |
| `taxCode` | String | Tax code of the line item according to the tax engine. | Big, 62.0 | 62.0 |
| `taxes` | [Tax Details](./connect_responses_tax_details_output.htm.md) [] | Tax details of the line item. | Big, 62.0 | 62.0 |
