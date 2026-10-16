---
page_id: sforce_api_objects_bindingobjusagersrcplcy.htm
title: BindingObjUsageRsrcPlcy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_bindingobjusagersrcplcy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BindingObjUsageRsrcPlcy

Represents the policies that are used for the usage resource that's
         associated with an asset or a binding object. This object is available in API version
      65.0 and later.

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`
         

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| BindingObjectId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The object that's bounded with the quote line policy or order policy. This field is a polymorphic relationship field. **Relationship Name** BindingObject **Refers To** Account, Asset, BindingObjectCustomExt, Contract |
| DrawdownOrder | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the order that's used to debit consumption of entitlements related to the usage resource from the usage entitlement bucket. Valid values are: `ExpiringFirst` `GrantedFirst` `GrantedLast` |
| EffectiveEndDate | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** The date and time until when the policy remains effective. |
| EffectiveStartDate | **Type** dateTime **Properties** Create, Filter, Sort, Update **Description** The date and time when the policy becomes effective. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date when this record was last referenced. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed a record related to this record. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The auto-generated identifier for the quote line item usage resource policy record. For example, BOURP-000004. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** The ID of the owner of the binding object usage resource policy. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| RatingFrequencyPolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The rating frequency policy associated with the usage resource. This field is a relationship field. **Relationship Name** RatingFrequencyPolicy **Refers To** RatingFrequencyPolicy |
| UsageAggregationPolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The usage aggregation policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageAggregationPolicy **Refers To** UsageResourceBillingPolicy |
| UsageCommitmentPolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The usage commitment policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageCommitmentPolicy **Refers To** UsageCommitmentPolicy |
| UsageOveragePolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The usage overage policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageOveragePolicy **Refers To** UsageOveragePolicy |
| UsageResourceId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The usage resource associated with the usage product. This field is a relationship field. **Relationship Name** UsageResource **Refers To** UsageResource |

      

      

## Binding Object Usage Resource Policy Behavior During Asset
            Operations

When you create or update an order and an asset is created or modified, Usage Management creates
            a Binding Object Usage Resource Policy (BOURP) record per Usage Resource based on the
            Product Usage Resource Policy (PURP) from the asset that's processed first. After the
            BOURP record is created, the policy references remain unchanged regardless of subsequent
            operations.

The Effective Start Date and
            Effective End Date fields extend to accommodate new or renewed assets associated with
            the same Binding Object and Usage Resource. However, the policy fields can't be updated
            after initial BOURP creation.

Here's how each operation affects BOURP creation,
            date ranges, and policy updates.

               
               
               
               
               
               
               
                  
                     

                     

                     

                     

                     

                     

                  

               

               
                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                     

                  

               

            
| Operation | BOURP Create | Start Date Update | End Date Update | Policy Update | Delete/Expire |
| --- | --- | --- | --- | --- | --- |
| New Sale (first asset for Binding Object) | Yes | — | — | — | — |
| New Sale (subsequent asset, same Binding Object, and Usage Resource) | No | Extends to an earlier date, if applicable | Extends to a later date, if applicable | No | — |
| Renew (existing BOURP) | No | No | Extends to a later date, if applicable | No | — |
| Renew (new Usage Resource on asset) | Yes | — | — | — | — |
| Amend (new Usage Resource on asset) | Yes | — | — | — | — |
| Amend (existing Usage Resource) | No | No | No | No | — |
| Cancel | No | No | No | No | No |

#### Important

 Policy fields on a BOURP record are never updated after the initial record
            is created. If an asset operation introduces a different Product Usage Resource Policy
            for the same Binding Object and Usage Resource combination, the BOURP retains the policy
            from the first asset that was processed. The system doesn’t split BOURP records or
            create multiple BOURPs per Usage Resource and Binding Object combination. 

#### Note

 If you must change the policy for a Usage Resource, you must manually update the existing
            BOURP record or implement custom automation to handle policy changes during specific
            operations.
