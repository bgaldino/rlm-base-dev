---
page_id: sforce_api_objects_obligation.htm
title: Obligation
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_obligation.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# Obligation

Represents an obligation between parties to fulfill agreed conditions, such as contractual commitments. The obligation commitment assists with a strategy to achieve the desired outcome within a set timeframe and reduce risk with compliance tracking. For example, payment due dates, contract terms, renewals. This object is available in API version 59.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

This object is available if your org has ObligationManagement permission license.

    

  

    

## Fields

    
      

### AssigneeUserId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The ID of the assignee user associated with the obligation.

        

This field is a relationship field.

        

**Relationship Name:** AssigneeUser

        

**Relationship Type:** Lookup

        

**Refers To:** User

      

      

### Description

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The description of the obligation.

      

      

### EndDate

        
        

**Type:** date

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The end date of the obligation.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the obligation.

      

      

### OtherPartyAccountId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of the other party account associated with the obligation.

        

This field is a relationship field.

        

**Relationship Name:** OtherPartyAccount

        

**Relationship Type:** Lookup

        

**Refers To:** Account

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** The ID of the user that owns this record.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Relationship Type:** Lookup

        

**Refers To:** Group, User

      

      

### Party

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The party who executes or delivers the obligation. The default value is `First_Party`.

        

Possible values are `FIRST_PARTY` or `OTHER_PARTY`

      

      

### ReferenceContractId

        
        

**Type:** reference

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The contract associated with the obligation.

        

This field is a relationship field.

        

**Relationship Name:** ReferenceContract

        

**Relationship Type:** Lookup

        

**Refers To:** Contract

      

      

### ReferenceObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The object associated with the obligation. For example, `Contract`.

        

This field is a relationship field.

        

**Relationship Name:** ReferenceObject

        

**Relationship Type:** Lookup

        

**Refers To:** Contract

      

      

### StartDate

        
        

**Type:** date

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The start date of the obligation.

      

      

### State

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The start date of the obligation.

        

Possible values are `Active`, `Expired`, `InActive`—Inactive, or `OnHold`—On Hold

        

The default value is `OnHold`.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Specifies the status of the obligation.

        

Possible values are `Compliant`—Compliant, `Non Compliant`—Non Compliant, `At Risk`—At Risk, or `None`—None

        

The default value is `Compliant`.

      

      

### StatusChangeReason

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The reason to change the obligation status.

      

      

### Type

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The type of Obligation. For example, `Manufacturing Obligation`, or `Payment Obligation`.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ObligationChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ObligationFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ObligationHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ObligationOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ObligationShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
