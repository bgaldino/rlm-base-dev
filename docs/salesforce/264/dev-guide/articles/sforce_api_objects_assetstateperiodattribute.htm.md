---
page_id: sforce_api_objects_assetstateperiodattribute.htm
title: AssetStatePeriodAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetstateperiodattribute.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AssetStatePeriodAttribute

Represents a virtual object that holds the key-value pair of the
         asset attribute in a specified asset state period. This object is a child object of
         AssetStatePeriod. This object is available in API version 60.0 and later.

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

         
         

            `describeLayout()`, `describeSObjects()`, `query()`, `retrieve()`
         

      

      

## Special Access Rules

This object is available in Enterprise,
            Unlimited, and Developer Editions of Revenue Cloud with the [Access Lifecycle-Managed Assets user
            permission](https://help.salesforce.com/s/articleView?id=ind.rev_cloud_asset_migration_permission.htm&language=en_US). This object is editable only through API and not the
         UI.

      

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

                  

               

            
| Field | Details |
| --- | --- |
| AssetStatePeriodId | **Type** reference **Properties** Filter, Group, Sort **Description** The asset state period that's associated with the asset attribute. This field is a relationship field. **Relationship Name** AssetStatePeriod **Relationship Type** Master-detail **Refers To** AssetStatePeriod (the master object) |
| AttributeDefinitionId | **Type** reference **Properties** Filter, Group, Sort **Description** The attribute definition that's associated with the asset state period attribute. This field is a relationship field. **Relationship Name** AttributeDefinition **Relationship Type** Lookup **Refers To** AttributeDefinition |
| AttributeName | **Type** string **Properties** Filter, Group, idLookup, Nillable, Sort **Description** The name of the asset attribute. |
| AttributePicklistValueId | **Type** reference **Properties** Filter, Group, Nillable, Sort **Description** The value specified in the picklist type field that corresponds to the attribute in the AttributePicklistValue object. This field is a relationship field. **Relationship Name** AttributePicklistValue **Relationship Type** Lookup **Refers To** AttributePicklistValue |
| AttributeValue | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The value of the asset state period attribute. For example, a shirt can have the value of `blue`, which indicates the shirt's color, or it can have the value of `small`, which indicates the shirt's size. You can use this field to filter records only if the DataType value in the related AttributeDefinitionId record is `Text`. If the DataType value is `Picklist`, use the value in the AttributePicklistValueId field for filtering. You can’t use this field to filter records if the DataType value is `Checkbox`, `Currency`, `Date`, `Datetime`, `Multipicklist`, `Number`, or `Percent`. |

      

      

## Usage

         
         

This object doesn’t support custom fields, validation rules, or triggers. In SOQL
            queries, you can filter records by using Id and
               AttributeDefinition. You can’t use
               AttributeValue in the `WHERE`
            clause.
