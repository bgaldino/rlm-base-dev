---
page_id: sforce_api_objects_billingforecast.htm
title: BillingForecast
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingforecast.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BillingForecast

      Represents forecasted invoice lines generated from billing schedules before actual invoicing occurs. This object is available in API version 68.0 and later.
   

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Billing Admin permission set to
            access this object.

      

      

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
- 
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
- 
- 
- 
- 
- 
- 
- 
- 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 
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

                  

            

            
| Field | Details |
| --- | --- |
| AccountId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** Required. The ID of the account associated with the billing forecast. This field is a relationship field. **Relationship Name** Account **Refers To** Account |
| BillingAccountId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the billing account associated with the billing forecast. This field is a relationship field. **Relationship Name** BillingAccount **Refers To** BillingAccount |
| BillingArrangementId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the billing arrangement associated with the billing forecast. This field is a relationship field. **Relationship Name** BillingArrangement **Refers To** BillingArrangement |
| BillingMethod | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the type of billing used for the billing forecast. Valid values are: `Evergreen` `OrderAmount` `Usage` |
| BillingPeriodEndDate | **Type** date **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The end date of the billing period for the billing forecast. |
| BillingPeriodStartDate | **Type** date **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The start date of the billing period for the billing forecast. |
| BillingScheduleGroupId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** Required. The ID of the billing schedule group associated with the billing forecast. This field is a relationship field. **Relationship Name** BillingScheduleGroup **Refers To** BillingScheduleGroup |
| BillingScheduleId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** Required. The ID of the billing schedule associated with the billing forecast. This field is a relationship field. **Relationship Name** BillingSchedule **Refers To** BillingSchedule |
| BillingTermUnit | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Required. Specifies the unit of the billing term for the billing forecast. Valid values are: `BillingMilestonePlan` `Day` `Month` `OneTime` `Quarter` `Semi-Annual` `Week` `Year` |
| Category | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Required. Specifies the category of the billing forecast. Valid values are: `AmendQuantity` `Amendment` `Cancellation` `Original` `Renewal` |
| ChargeAmount | **Type** currency **Properties** Create, Filter, Sort, Update **Description** Required. The charge amount for the billing forecast. |
| InvoiceBatchRunId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the invoice batch run associated with the billing forecast. This field is a relationship field. **Relationship Name** InvoiceBatchRun **Refers To** InvoiceBatchRun |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferencedDate isn’t null, the user accessed this record or list view indirectly. |
| LegalEntityAccountingPeriodId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the legal entity accounting period associated with the billing forecast. This field is a relationship field. **Relationship Name** LegalEntityAccountingPeriod **Refers To** LegalEntyAccountingPeriod |
| LegalEntityId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the legal entity associated with the billing forecast. This field is a relationship field. **Relationship Name** LegalEntity **Refers To** LegalEntity |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Required. An auto-generated number assigned to the billing forecast. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Required. The ID of the owner of this record. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| PaymentTermId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the payment term associated with the billing forecast. This field is a relationship field. **Relationship Name** PaymentTerm **Refers To** PaymentTerm |
| Quantity | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The quantity of the product or service for the billing forecast. |
| ReferenceEntityId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the reference entity associated with the billing forecast. This field is a polymorphic relationship field. **Relationship Name** ReferenceEntity **Refers To** Order, Quote |
| ReferenceEntityItemId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the reference entity line item associated with the billing forecast. This field is a polymorphic relationship field. **Relationship Name** ReferenceEntityItem **Refers To** DebitMemoLine, OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, QuoteLineItem |
| UnitPrice | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The unit price of the product or service for the billing forecast. |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[BillingForecastShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
