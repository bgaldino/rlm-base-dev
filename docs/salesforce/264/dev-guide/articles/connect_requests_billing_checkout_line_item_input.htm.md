---
page_id: connect_requests_billing_checkout_line_item_input.htm
title: Billing Checkout Line Item Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_checkout_line_item_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_billing_checkout_input.htm
fetched_at: 2026-09-29
---

# Billing Checkout Line Item Input

Input representation of a single line item being purchased in the checkout transaction.

    

## JSON Example

      
      

```
{
  "productId": "01txx0000004C91",
  "productName": "Professional Services",
  "transactionId": "TXN-PROF-SERVICES-001",
  "quantity": 2,
  "unitPrice": 100.00,
  "netUnitPrice": 90.00,
  "lineTotal": 180.00,
  "startDate": "2026-09-01",
  "endDate": "2027-08-31",
  "sellingModelType": "TermDefined",
  "periodBoundary": "DayOfPeriod",
  "billingDayOfMonth": 1,
  "billingTermUnit": "Month",
  "billingTerm": 12,
  "taxTreatmentId": "0cXxx0000004C93",
  "billingTreatmentId": "0cYxx0000004C94"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Day​Of​Month` | Integer | The day of the month a recurring billing process is scheduled to occur for the transaction. Required when `periodBoundary` is `DayOfPeriod`. | Optional | 68.0 |
| `billing​Term` | Integer | Number of billing term units. Must be `1` for `OneTime` selling models. | Optional | 68.0 |
| `billing​Term​Unit` | String | Unit of measurement for the billing term. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `OneTime`, `Day`, `Week`, `Month`, `Quarter`, `SemiAnnual`, `Year`, or `BillingMilestonePlan`. | Optional | 68.0 |
| `billing​Treatment​Id` | String | ID of the billing treatment used to create the billing schedule for the transaction. If you don't specify a `billingTreatmentId`, the org-default `billingTreatmentId` is considered. | Optional | 68.0 |
| `bundle​Product​Details` | [Bundle Product Details Input](./connect_requests_billing_checkout_bundle_product_details_input.htm.md)[] | Array of child products. Its presence indicates that this line item is a bundle parent. Supports nested bundles. | Optional | 68.0 |
| `end​Date` | String | End date for the line item's billing schedule (YYYY-MM-DD). Required when `sellingModelType` is `TermDefined` or a `billingTermUnit` is provided. Defaults to the invoice date when omitted. | Optional | 68.0 |
| `line​Total` | Double | Net unit price multiplied by quantity. | Required | 68.0 |
| `net​Unit​Price` | Double | Net unit price after discount calculation. | Optional | 68.0 |
| `period​Boundary` | String | Period boundary for the billing schedule. Required when `sellingModelType` is `TermDefined` or `Evergreen`. Valid values are `AlignToCalendar`, `Anniversary`, `DayOfPeriod`, or `LastDayOfPeriod`. | Optional | 68.0 |
| `product​Id` | String | Unique product ID of the item. | Required | 68.0 |
| `product​Name` | String | Unique product name of the item. | Optional | 68.0 |
| `quantity` | Integer | Quantity of the product being purchased. | Required | 68.0 |
| `ramps` | [Billing Checkout Ramp Input](./connect_requests_billing_checkout_ramp_input.htm.md)[] | Schedule of changes in quantity or price for this line item. | Optional | 68.0 |
| `selling​Model​Type` | String | Selling model of the line item. Defaults to `OneTime`. A `TermDefined` or `Evergreen` value requires `billingTermUnit`. Valid values are `OneTime`, `TermDefined`, or `Evergreen`. | Optional | 68.0 |
| `start​Date` | String | Start date for the line item's billing schedule (YYYY-MM-DD). Defaults to the invoice date. | Optional | 68.0 |
| `tax​Treatment​Id` | String | The tax treatment ID used to calculate tax for the transaction. If you don't specify a `taxTreatmentId`, the org-default `taxTreatmentId` is considered. | Optional | 68.0 |
| `transaction​Id` | String | Client-supplied transaction identifier for this line item. Used as the transaction ID on the generated billing transaction and as the grouping key for its ramp segments and bundle components. Defaults to the product name or product ID when omitted. | Optional | 68.0 |
| `unit​Price` | Double | Price per unit before any discounts are applied. | Required | 68.0 |

    

  

- 
**[Bundle Product Details Input](./connect_requests_billing_checkout_bundle_product_details_input.htm.md)**  

Input representation of a bundle line item's child product. Recursive to support nested bundles.

- 
**[Billing Checkout Ramp Input](./connect_requests_billing_checkout_ramp_input.htm.md)**  

Input representation of a ramp period describing a change in quantity or price for a line item over time.
