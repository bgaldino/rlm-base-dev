---
page_id: sforce_api_objects_refundlinecreditmemo.htm
title: RefundLineCreditMemo
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_refundlinecreditmemo.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# RefundLineCreditMemo

      Represents a junction between a refund and a credit memo. This object is available in API version 68.0 and later.
   

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

      
      

         `create()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `update()`, 
         `upsert()`
      

      

      

## Special Access Rules

         
         

To access this object, you need the Billing permission set licenses and the Billing Admin permission set.

      

      

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
- 
- 
- 

                  

            

            
| Field | Details |
| --- | --- |
| AccountId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** The account associated with the credit memo to which the refund is applied. This field is a relationship field. **Relationship Name** Account **Refers To** Account |
| Amount | **Type** currency **Properties** Create, Filter, Sort **Description** Required. The refund amount that’s been applied to or unapplied from the credit memo. |
| AppliedDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort **Description** The date and time when the refund was applied to the credit memo. |
| Comments | **Type** textarea **Properties** Create, Filter, Nillable, Sort, Update **Description** Additional details about the credit memo refund. |
| CreditMemoBalance | **Type** currency **Properties** Filter, Nillable, Sort **Description** The balance of the credit memo after the refund was applied or unapplied. |
| CreditMemoId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Required. The credit memo to which the refund has been applied or unapplied. This field is a relationship field. **Relationship Name** CreditMemo **Relationship Type** Master-detail **Refers To** CreditMemo (the master object) |
| CreditMemoRefundNumber | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Required. An auto-generated string assigned to the refund line credit memo record. |
| EffectiveDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort **Description** The date and time when the refund’s application or unapplication takes effect. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferencedDate isn’t null, the user accessed this record or list view indirectly. |
| LegalEntityAccountingPeriodId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity accounting period record that’s related to the credit memo refund. This field is a relationship field. **Relationship Name** LegalEntityAccountingPeriod **Refers To** LegalEntyAccountingPeriod |
| LegalEntityId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The legal entity related to the credit memo refund. This field is a relationship field. **Relationship Name** LegalEntity **Refers To** LegalEntity |
| RefundBalance | **Type** currency **Properties** Filter, Nillable, Sort **Description** The balance of the refund after the refund was applied or unapplied. |
| RefundId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Required. The refund associated with the credit memo. This field is a relationship field. **Relationship Name** Refund **Refers To** Refund |
| RelatedCreditMemoRefundId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** The applied credit memo refund that’s being unapplied. This field is a relationship field. **Relationship Name** RelatedCreditMemoRefund **Refers To** CreditMemoRefund |
| Type | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort **Description** Required. Specifies whether the refund has been applied to or unapplied from the credit memo. Valid values are: `Applied` `Unapplied` |
| UnappliedDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort **Description** The date and time when the refund was unapplied from the credit memo. |
| UnappliedStatus | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort **Description** Required. Specifies whether the refund has been unapplied from the credit memo. Valid values are: `NA` `No` `Yes` |
