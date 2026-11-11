---
page_id: sforce_api_objects_externaldocstorageconfig.htm
title: ExternalDocStorageConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_externaldocstorageconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ExternalDocStorageConfig

Represents a collection of fields to configure the external document storage for an object. It includes details such as location, path, and named credentials. For example, OneDrive is defined as an External Document Storage and is associated with the Salesforce Contract object.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### DocumentPath

        
        

**Type:** textarea

        

**Properties:** Create, Update

        

**Description:** Specifies the path from the root in the external storage where documents are stored.

      

      

### ExternalDocStorageIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Specifies the ID of the external document storage.

      

      

### NamedCredentialId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The Named Credential associated with the External Document Storage Configuration. A named credential can be specified as an endpoint to simplify the setup of authenticated callouts.

        

This field is a relationship field.

        

**Relationship Name:** NamedCredential

        

**Relationship Type:** Lookup

        

**Refers To:** NamedCredential

      

      

### RecordTypeId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The Record Type associated with the Reference Object.

        

This field is a relationship field.

        

**Relationship Name:** RecordType

        

**Relationship Type:** Lookup

        

**Refers To:** RecordType

      

      

### StorageDriveType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the external document storage drive. For example, Microsoft OneDrive.

        

Possible values are `MicrosoftOneDrive`—Microsoft OneDrive

        

The default value is `MicrosoftOneDrive`.

      

      

### TargetObject

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the object associated with the external document storage. For example, Document Template, Contract, All.

        

Possible values are `All`, `Contract`, or `DocumentTemplate`—Document Template

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ExternalDocStorageConfigChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ExternalDocStorageConfigFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ExternalDocStorageConfigHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ExternalDocStorageConfigOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ExternalDocStorageConfigShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
