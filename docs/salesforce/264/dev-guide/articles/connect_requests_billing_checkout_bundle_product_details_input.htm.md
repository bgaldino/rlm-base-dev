---
page_id: connect_requests_billing_checkout_bundle_product_details_input.htm
title: Bundle Product Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_bundle_product_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_line_item_input.htm
fetched_at: 2026-09-29
---

# Bundle Product Details Input

Input representation of a bundle line item's child product. Recursive to support nested bundles.

    

## JSON Example

      
      

```
{
  "productId": "01txx0000004C92",
  "productName": "Add-On Support",
  "associatedTransactionPricing": "IncludedInBundlePrice",
  "quantity": 1,
  "unitPrice": 50.00,
  "netUnitPrice": 50.00,
  "lineTotal": 50.00,
  "sellingModelType": "TermDefined",
  "periodBoundary": "DayOfPeriod",
  "billingDayOfMonth": 1,
  "billingTermUnit": "Month",
  "billingTerm": 12,
  "taxTreatmentId": "0cXxx0000004C93",
  "billingTreatmentId": "0cYxx0000004C94",
  "bundleProductDetails": []
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `associated​Transaction​Pricing` | String | When your transaction is part of a bundle, this value describes how the child transaction is priced in relation to the primary transaction. The default value is `IncludedInBundlePrice`. Valid values are `IncludedInBundlePrice` or `NotIncludedInBundlePrice`. | Optional | 68.0 |
| `billing​Day​Of​Month` | Integer | The day of the month a recurring billing process is scheduled to occur for the transaction. Required when `periodBoundary` is `DayOfPeriod`. | Optional | 68.0 |
| `billing​Term` | Integer | Number of billing term units. Must be `1` for `OneTime` selling models. | Optional | 68.0 |
| `billing​Term​Unit` | String | Unit of measurement for the billing term. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `OneTime`, `Day`, `Week`, `Month`, `Quarter`, `SemiAnnual`, `Year`, or `BillingMilestonePlan`. | Optional | 68.0 |
| `billing​Treatment​Id` | String | ID of the billing treatment used to create the billing schedule for the transaction. If you don't specify a `billingTreatmentId`, the org-default `billingTreatmentId` is considered. | Optional | 68.0 |
| `bundle​Product​Details` | [Bundle Product Details Input](#)[] | Nested array of child products for bundle-of-bundles scenarios, including pricing. | Optional | 68.0 |
| `line​Total` | Double | Net unit price multiplied by quantity. | Required | 68.0 |
| `net​Unit​Price` | Double | Net unit price after discount calculation. | Optional | 68.0 |
| `period​Boundary` | String | Period boundary for the billing schedule. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `AlignToCalendar`, `Anniversary`, `DayOfPeriod`, or `LastDayOfPeriod`. | Optional | 68.0 |
| `product​Id` | String | Product ID of the child component. | Required | 68.0 |
| `product​Name` | String | Product name of the child component. | Optional | 68.0 |
| `quantity` | Integer | Quantity of the child component. | Required | 68.0 |
| `selling​Model​Type` | String | Selling model of the child component. Defaults to `OneTime`. A `TermDefined` or `Evergreen` value requires `billingTermUnit`. Valid values are `OneTime`, `TermDefined`, or `Evergreen`. | Optional | 68.0 |
| `tax​Treatment​Id` | String | ID of the tax treatment used to calculate tax for the transaction. If you don't specify a `taxTreatmentId`, the org-default `taxTreatmentId` is considered. | Optional | 68.0 |
| `unit​Price` | Double | Price per unit before any discounts are applied. | Required | 68.0 |
