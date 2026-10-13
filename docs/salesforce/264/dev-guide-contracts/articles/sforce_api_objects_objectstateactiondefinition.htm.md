---
page_id: sforce_api_objects_objectstateactiondefinition.htm
title: ObjectStateActionDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_objectstateactiondefinition.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ObjectStateActionDefinition

Represents the link between the object state definition and object state transition based on a defined action.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ActionType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the action type for the object state action definition, whether it's Apex or Reference Object.

        

Possible values are `Apex` or `ReferenceObject`—Reference Object

      

      

### DisplayLabel

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The display name of the object state action definition.

      

      

### InvocableClassName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the Apex invocable class.

      

      

### InvocableMethodName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the Apex invocable class method.

      

      

### IsSystem

        
        

**Type:** boolean

        

**Properties:** Defaulted on create, Filter, Group, Sort

        

**Description:** Indicates whether the action is provided by the Salesforce (True) application or is a custom action (False). The field is uneditable.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort

        

**Description:** The API name of the object state action definition.

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** The name of the user who creates the object state action definition.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Relationship Type:** Lookup

        

**Refers To:** Group, User

      

      

### ReferenceObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The Reference Object associated with the Object State Action Definition.

        

This field is a relationship field.

        

**Relationship Name:** ReferenceObject

        

**Relationship Type:** Lookup

        

**Refers To:** OmniProcess

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ObjectStateActionDefinitionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ObjectStateActionDefinitionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ObjectStateActionDefinitionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ObjectStateActionDefinitionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ObjectStateActionDefinitionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
