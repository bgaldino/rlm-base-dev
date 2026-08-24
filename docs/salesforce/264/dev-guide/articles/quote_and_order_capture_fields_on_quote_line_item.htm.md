---
page_id: quote_and_order_capture_fields_on_quote_line_item.htm
title: Transaction Management Fields on Quote Line Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_quote_line_item.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Fields on Quote Line Item

      Standard and custom fields extend the standard Quote Line Item object for use
         in Transaction Management to represent information about line items in a quote. This object
         is available in API version 60.0 and later. 

      

## Special Access Rules

         
         

These fields require the Revenue Cloud Advanced license. See [Quote Line Item](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_quotelineitem.htm) for fields on the Salesforce
            platform object.

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 
: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 

: 

                  

                  
                     

                     

: 

: 

: 
: 
: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
: 
- 

                  

               

            
| Field | Details |
| --- | --- |
| ApplUnitPriceUpliftPct | **Type** percent **Properties** Create, Filter, Nillable, Sort, Update **Description** The unit price uplift percent that’s applied to the quote line item, used for ramp pricing. This field is available in API version 68.0 and later. |
| DiscountAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** Specifies the fixed amount discount to apply to the quote line item. |
| EffectiveGrantDate | **Type** date **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The date on which the resources associated with the quote line item are granted. |
| EndDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The end date and time of the quote line item, which is calculated by using the values in the EndDate, EndTime, and StartEndTimeZone fields. If the EndTime field doesn’t have a value, 23:59:59 is used for the calculation. If the StartEndTimeZone field doesn’t have a value, GMT is used for the calculation. Available in API version 65.0 and later. |
| EndQuantity | **Type** double **Properties** Filter, Nillable, Sort **Description** The quantity available on the quote line item end date. The field is read-only. It’s calculated by adding the Start Quantity and the existing Quantity fields. |
| EndTime | **Type** time **Properties** Create, Filter, Nillable, Sort, Update **Description** The end time of the quote line item. Available in API version 65.0 and later. |
| Margin | **Type** percent **Properties** Create, Filter, Nillable, Sort, Update **Description** The optional margin percentage, specified by the sales representative at the line item level. Available in API version 65.0 and later. |
| MarginAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The optional margin amount specified by the sales representative at the line item level. Available in API version 65.0 and later. |
| PartnerDiscountPercent | **Type** percent **Properties** Create, Filter, Nillable, Sort, Update **Description** The discount percentage given to the partner for the quote line. |
| PartnerUnitPrice | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The unit price after discount given to the partner for the quote line. |
| PriceWaterfallIdentifier | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The price waterfall identifier generated by Salesforce Pricing that's associated with the pricing of the detail record. |
| RampUpliftType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The pricing uplift calculation type for ramp segments. Valid values are: `Compound` `Standard` This field is available in API version 68.0 and later. |
| StartDateTime | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The start date and time of the quote line item, which is calculated by using the values in the StartDate, StartTime, and StartEndTimeZone fields. If the StartTime field doesn’t have a value, 00:00:00 is used for the calculation. If the StartEndTimeZone field doesn’t have a value, GMT is used for the calculation. Available in API version 65.0 and later. |
| StartEndTimeZone | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The time zone for the quote line item's start and end dates, times, and datetimes. Available in API version 65.0 and later. |
| StartTime | **Type** time **Properties** Create, Filter, Nillable, Sort, Update **Description** The start time of the quote line item. Available in API version 65.0 and later. |
| StartQuantity | **Type** double **Properties** Create, Filter, Nillable, Sort **Description** The quantity available on the quote line item start date. |
| TotalAdjustment | **Type** percent **Properties** Filter, Nillable, Sort **Description** The total discount percentage applied at the line item level. This percentage is calculated by using the formula: (Total Line Amount - Net Total Price) / Total Line Amount. Available in API version 65.0 and later. |
| TotalCost | **Type** currency **Properties** Filter, Nillable, Sort **Description** The total cost of all products sold in the order is calculated by multiplying the quantity by the unit cost. Available in API version 65.0 and later. |
| TotalMargin | **Type** percent **Properties** Filter, Nillable, Sort **Description** The effective margin percentage at the line item level. This percentage is calculated by using the formula: (Net Total Price - Total Cost) / Net Total Price. Available in API version 65.0 and later. |
| TotalMarginAmount | **Type** currency **Properties** Filter, Nillable, Sort **Description** The effective margin amount at the line item level. This amount is calculated by subtracting total cost from net total price. Available in API version 65.0 and later. |
| UnitCost | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The unit cost of a product sold as part of the order. Available in API version 65.0 and later. |
| ValidationResult | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies whether the quote line item is configured and priced. A quote can be activated only after all its quote line items are configured and priced. Valid value is: `Warning`—Indicates that the quote line item isn’t configured and priced. Available in API version 60.0 and later. |
