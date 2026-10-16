---
page_id: billing_sforce_api_objects_refund_line_payment.htm
title: Billing Fields on RefundLinePayment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_refund_line_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Fields on RefundLinePayment

Standard fields extend the Refund Line Payment object for use in
         Billing to represent information about accounting periods for legal entities. This
      object is available in API version 64.0 and later.

      

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

                  

               

            
| Field | Details |
| --- | --- |
| LegalEntityAccountingPeriodId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity accounting period related to the refund. This field is a relationship field. **Relationship Name** LegalEntityAccountingPeriod **Refers To** LegalEntityAccountingPeriod |
| LegalEntityId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity related to the refund. This field is a relationship field. **Relationship Name** LegalEntity **Refers To** LegalEntity |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[RefundLinePaymentHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
