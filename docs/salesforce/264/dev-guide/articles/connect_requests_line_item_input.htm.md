---
page_id: connect_requests_line_item_input.htm
title: Line Item Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_line_item_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Line Item Input

Input representation of the details of the line item for tax calculation.

**JSON example**

: 

```
{
  "lineItems": [
    {
      "quantity": 1,
      "amount": 100,
      "taxCode": "TX0001",
      "productCode": "Y0001",
      "productSKU": "PRES-RX-12896745",
      "description": "New Product",
      "effectiveDate": "2022-03-09T10:30:41.000Z",
      "lineNumber": "5TVxx0000004C92GAE",
      "addresses": {
        "shipFrom": {
          "street": "123 Alaskan Way",
          "city": "Seattle",
          "state": "WA",
          "country": "US",
          "postalCode": "98101",
          "latitude": 45.12,
          "longitude": 45.12
        },
        "shipTo": {
          "street": "123 Auburn Blvd",
          "city": "Sacramento",
          "state": "CA",
          "country": "US",
          "postalCode": "95841",
          "latitude": 45.12,
          "longitude": 45.12
        },
        "soldTo": {
          "street": "123 Auburn Blvd",
          "city": "Sacramento",
          "state": "CA",
          "country": "US",
          "postalCode": "95841",
          "latitude": 45.12,
          "longitude": 45.12
        },
        "billTo": {
          "street": "123 Auburn Blvd",
          "city": "Sacramento",
          "state": "CA",
          "country": "US",
          "postalCode": "95841",
          "latitude": 45.12,
          "longitude": 45.12
        }
      }
    }
  ]
}
```

**Properties**

: 

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Addresses Input](./connect_requests_addresses_input.htm.md) | Address types that specify different locations associated with the transaction of the line item. | Optional | 62.0 |
| `amount` | Double | Total amount for the line item. | Required | 62.0 |
| `description` | String | Description of the line item. | Optional | 62.0 |
| `effectiveDate` | String | Date that tax rules are applicable from. This property value overrides the global effective date. | Optional | 62.0 |
| `legalEntity` | String | Legal entity that's related to the tax treatment. | Optional | 63.0 |
| `lineNumber` | String | Unique identifier for the line item. | Required | 62.0 |
| `productCode` | String | Product code of the line item according to the tax treatment rules of the tax engine. | Optional | 62.0 |
| `productId` | String | ID of the product. | Optional | 63.0 |
| `productSKU` | String | Unique identifier of a product that can be used to identify products that are exempted from tax. | Optional | 64.0 |
| `quantity` | Double | Quantity of the line item. | Required | 62.0 |
| `taxCode` | String | Tax code of the line item according to the tax treatment rules of the tax engine. | Optional | 62.0 |
| `unitPrice` | Double | Unit price of the product. | Optional | 63.0 |
