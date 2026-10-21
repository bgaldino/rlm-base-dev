---
page_id: sforce_api_objects_salescontractline.htm
title: SalesContractLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_salescontractline.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# SalesContractLine

Stores a contract's product information, including price, quantity, and components covered. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContractId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** Parent contract identifier.

        

This is a relationship field.

        

**Relationship Name:** Contract

        

**Relationship Type:** Lookup

        

**Refers To:** Contract

      

      

### Description

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Description of the contract line item.

      

      

### EffectiveEndDateTime

        
        

**Type:** dateTime

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** End date and time for the line item.

      

      

### EffectiveStartDateTime

        
        

**Type:** dateTime

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** Start date and time for the line item.

      

      

### LineItemNumber

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Indicates the line item number.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Name of the contract line item.

      

      

### OpportunityProductId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the associated OpportunityLineItem.

        

This is a relationship field.

        

**Relationship Name:** OpportunityProduct

        

**Relationship Type:** Lookup

        

**Refers To:** OpportunityLineItem

      

      

### OrderProductId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the associated OrderItem.

        

This is a relationship field.

        

**Relationship Name:** OrderProduct

        

**Relationship Type:** Lookup

        

**Refers To:** OrderItem

      

      

### OriginalLineItemId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the original line item that this line item references (for example if this line item is due to a contract amendment).

        

This is a relationship field.

        

**Relationship Name:** OriginalLineItem

        

**Relationship Type:** Lookup

        

**Refers To:** SalesContractLine

      

      

### Product2Id

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Product ID associated with the line item.

        

This is a relationship field.

        

**Relationship Name:** Product2

        

**Relationship Type:** Lookup

        

**Refers To:** Product2

      

      

### ProductCode

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Product code associated with the line item.

      

      

### Quantity

        
        

**Type:** double

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** Product quantity associated with the line item.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Status of the contract line item.

        

Possible values are `Active` or `Inactive`

      

      

### TotalPrice

        
        

**Type:** currency

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** Total price of the line item.

      

      

### UnitPrice

        
        

**Type:** currency

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** Unit price of the line item.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[SalesContractLineChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[SalesContractLineFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[SalesContractLineHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[SalesContractLineOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[SalesContractLineShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
