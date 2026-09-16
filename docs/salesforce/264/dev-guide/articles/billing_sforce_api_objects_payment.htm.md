---
page_id: billing_sforce_api_objects_payment.htm
title: Billing Fields on Payment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Fields on Payment

      Standard fields extend the Payment object for use in Billing to represent
         information about corporate currency, transaction amounts in corporate currency, and
         accounting periods for legal entities. This object is available in API version 64.0
      and later.

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`
         

      

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
            Payment Operations User permission set to access this object.

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| CorporateCurrencyCnvAmount | **Type** double **Properties** Filter, Nillable, Sort, Update **Description** The payment amount in corporate currency. |
| CorporateCurrencyCvsnDate | **Type** date **Properties** Filter, Group, Nillable, Sort, Update **Description** The date on which the payment amount is converted into corporate currency. |
| CorporateCurrencyCvsnRate | **Type** double **Properties** Filter, Nillable, Sort, Update **Description** The exchange rate that's used to convert the payment amount into corporate currency. |
| CorporateCurrencyIsoCode | **Type** string **Properties** Filter, Group, Nillable, Sort, Update **Description** The currency ISO code of the corporate currency. |
| FunctionalCurrencyCnvAmount | **Type** double **Properties** Filter, Nillable, Sort, Update **Description** The amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | **Type** date **Properties** Filter, Group, Nillable, Sort, Update **Description** The date on which the amount value is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | **Type** double **Properties** Filter, Nillable, Sort, Update **Description** The exchange rate that's used to convert the amount value into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | **Type** string **Properties** Filter, Group, Nillable, Sort, Update **Description** The ISO code of the functional currency. Available in API version 66.0 and later. |
| LegalEntityAccountingPeriodId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity accounting period related to the payment. This field is a relationship field. **Relationship Name** LegalEntityAccountingPeriod **Refers To** LegalEntityAccountingPeriod |
| LegalEntityId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity related to the payment. This field is a relationship field. **Relationship Name** LegalEntity **Refers To** LegalEntity |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[PaymentFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
         

      

   

#### See Also

- [*Object Reference for the platform*: Payment](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_payment.htm)
