---
page_id: sforce_api_objects_objectstatetransitionaction.htm
title: ObjectStateTransitionAction
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_objectstatetransitionaction.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ObjectStateTransitionAction

Represents a junction between object state transition and object state action definition. State transition determines the valid transition of an object from one state to another and the state action determines which action triggers which state transition.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### DisplaySequence

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Determines the display order of the object state action for the associated state transition. Supports a whole number that's greater than 0 to define the order.

      

      

### IsActive

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the object state action definition for the specified object state transition is active (True) or not (False).

        

The default value is `false`.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the object state action transition.

      

      

### ObjectStateActionDefinitionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The object state action definition associated with the record.

        

This field is a relationship field.

        

**Relationship Name:** ObjectStateActionDefinition

        

**Relationship Type:** Lookup

        

**Refers To:** ObjectStateActionDefinition

      

      

### ObjectStateDefinitionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The object state definition associated with the record.

        

This field is a relationship field.

        

**Relationship Name:** ObjectStateDefinition

        

**Relationship Type:** Lookup

        

**Refers To:** ObjectStateDefinition

      

      

### ObjectStateTransitionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The object state definition transition with the record.

        

This field is a relationship field.

        

**Relationship Name:** ObjectStateTransition

        

**Relationship Type:** Lookup

        

**Refers To:** ObjectStateTransition

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        
        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Relationship Type:** Lookup

        

**Refers To:** Group, User

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ObjectStateTransitionActionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ObjectStateTransitionActionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ObjectStateTransitionActionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ObjectStateTransitionActionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ObjectStateTransitionActionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
