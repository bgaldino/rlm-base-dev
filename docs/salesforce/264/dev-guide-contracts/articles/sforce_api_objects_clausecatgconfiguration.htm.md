---
page_id: sforce_api_objects_clausecatgconfiguration.htm
title: ClauseCatgConfiguration
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_clausecatgconfiguration.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ClauseCatgConfiguration

Represents the configuration about the clause category that can be used in a response document by the user.

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `query()`, 
         `retrieve()`, 
         `update()`, 
         `upsert()`
      

      

      

## Special Access Rules

         
         

Salesforce Org must have ClauseManagement platform license enabled. Users must have the
            ClauseManagementAddOn license to access this object.

      

   

      

## Fields

      
         

### Description

            
            

**Type:** string

            

**Properties:** Create, Filter, Group, Nillable, Sort, Update

            

**Description:** The description about the clause category configuration.

         

         

### MasterLabel

            
            

**Type:** string

            

**Properties:** Create, Filter, Group, Sort, Update

            

**Description:** The name of the clause library category used in the
               configuration.

         

         

### UsageType

            
            

**Type:** picklist

            

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

            

**Description:** Specifies the usage of the clause category.

            

Possible values are `ContractClauseCategory`—Contract Clause Category or `DisclosureCategory`—Disclosure Category.

         

      

   

      

## Associated Objects

      
         
            

This object has the following associated objects. If the API version isn’t specified,
               they’re available in the same API versions as this object. Otherwise, they’re available
               in the specified API version and later.

            

**[ClauseCatgConfigurationChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

            

**[ClauseCatgConfigurationFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

            

**[ClauseCatgConfigurationHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

            

**[ClauseCatgConfigurationOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

            

**[ClauseCatgConfigurationShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
