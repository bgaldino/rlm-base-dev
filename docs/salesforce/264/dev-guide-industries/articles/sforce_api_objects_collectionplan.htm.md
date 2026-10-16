---
page_id: sforce_api_objects_collectionplan.htm
title: CollectionPlan
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_collectionplan.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Collections and Recovery
parent_page: collections_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CollectionPlan

      Represents details about the outstanding amounts linked to financial
         accounts, billing accounts, contacts, accounts, or cases associated with individuals or an
         organization. This object is available in API version 63.0 and later.

      

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

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

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
- 
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| AccountId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The account associated with the collection plan record. This field is a relationship field. **Relationship Name** Account **Refers To** Account |
| AutoDebitRequestCount | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The count of the auto debit requests initiated for a collection plan. |
| ClosedDate | **Type** date **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The date when the collection plan was closed. |
| CollectionAgencyAccountId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The account of the recovery agency, which may be a third-party agency, responsible for managing the collection activities associated with this collection plan. Available in API version 65.0 and later. This field is a relationship field. **Relationship Name** CollectionAgencyAccount **Refers To** Account |
| CollectionPlanReasonId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of collection plan reason associated with the collection plan. This field is a relationship field. **Relationship Name** CollectionPlanReason **Refers To** CollectionPlanReason |
| CollectionPlanSegment | **Type** picklist **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Specifies a predefined group associated with the collection plan record. The group is derived based on various criteria, such as collection amount and days past due. |
| ContactId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The contact associated with the collection plan record. This field is a relationship field. **Relationship Name** Contact **Refers To** Contact |
| CurrentDueAmount | **Type** currency **Properties** Create, Filter, Sort, Update **Description** The current outstanding amount for the collection plan. |
| DaysPastDue | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The number of days that a payment is past its scheduled or expected due date. |
| DueDate | **Type** date **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The date by which the organization or individuals are expected to make a payment towards the outstanding amount. |
| FirstCallDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** The timestamp when the first phone call is made to notify an individual or organization about the repayment of funds. |
| FirstEmailDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** The timestamp when the first email is sent to notify an individual or organization about the repayment of funds. |
| FirstSmsDateTime | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** The timestamp when the first message is sent to notify an individual or organization about the due amount. |
| FinancialAccountId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The financial account associated with the collection plan record. This field is a relationship field. **Relationship Name** FinancialAccount **Refers To** FinancialAccount |
| InitialDueAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The initial due amount of the collection plan. |
| InteractionOutcome | **Type** picklist **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Specifies the result of the collections specialist's interaction with a customer, such as promised to pay, escalated to recovery, legal case created, no commitment, or bankruptcy. Available in API version 64.0 and later. |
| IsClosed | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates if the collection plan is active (`true`) or not (`false`). The default value is `false`. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferencedDate is not null, the user accessed this record or list view indirectly. |
| LegalRepresentativeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The contact details of the borrower's legal representative or attorney. Available in API version 64.0 and later. This field is a relationship field. **Relationship Name** LegalRepresentative **Refers To** Contact |
| MaximumPromisetoPayCount | **Type** int **Properties** Create, Defaulted on create, Filter, Group, Nillable, Sort, Update **Description** The maximum number of promises to pay allowed for a collection plan. Available in API version 64.0 and later. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The name of the collection plan record. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** The ID of the owner of the collection plan record. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| PromiseToPayCount | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The number of commitments made by an individual or an organization to repay the amount they owe within a specified timeframe. |
| RiskScore | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The numerical score that is computed based on the Einstein model. This score is used to assess an individual's repayment capacity. |
| SourceSystemRecordIdentifier | **Type** string **Properties** Create, Filter, Group, idLookup, Nillable, Sort, Update **Description** The unique identifier of the collection plan in an external system. |
| Status | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the status of the collection plan, such as new, in progress, promise to pay registered, promise to pay broken, and closed. Possible values are: `Close` `InProgress` `New` |
| TotalFeesAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The sum of any fee amount associated with the collection plan. It includes any applicable surcharges, processing fees, penalties, and any other additional charges incurred. |
| TotalInterestAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The cumulative sum of all interest charges accrued over a specified time period. |
| TotalPaymentsReceived | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** Total amount of payments received that are associated with a collection plan. Available in API version 63.0 and later. |
| TotalTaxAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The total tax amount of the collection plan. |
| UsageType | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Name of the cloud or the function that uses the Collections feature. Possible values are: `Automotive` `Billing` `Financial Services Cloud` |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[CollectionPlanChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)**

               
: Change events are available for the object.

            
            
            
               

**[CollectionPlanHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)**

               
: History is available for tracked fields of the object.

            
            
               

**[CollectionPlanOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)**

               
: Sharing rules are available for the object.

            
            
               

**[CollectionPlanShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)**

               
: Sharing is available for the object.
