---
page_id: sforce_api_objects_contractextractionresult.htm
title: ContractExtractionResult
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contractextractionresult.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContractExtractionResult

Represents contract-specific data extracted by the Contracts AI from an uploaded PDF that's ready for review. For example, account name, owner, start date, contract name, contract record type, contract term, and clauses. Before contract record creation, users can access, review, and modify the temporarily stored information. This object is available in API version 60.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContentDocumentId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The content document associated with the contract.

        

This field is a relationship field.

        

**Relationship Name:** ContentDocument

        

**Refers To:** ContentDocument

      

      

### DocumentAIJobIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The unique identifier of the Document AI job that generated the extraction result. Available in API version 67.0 and later.

      

      

### ExtractedClauseContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The clauses that are reviewed during the extraction review process.

      

      

### ExtractedClauseContentDocId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The document containing clauses that exceeds 131K characters and are reviewed during the extraction review process.

        

This field is a relationship field.

        

**Relationship Name:** ExtractedClauseContentDoc

        

**Refers To:** ContentDocument

      

      

### ExtractedClauseCount

        
        

**Type:** int

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The number of clauses extracted during the extraction review process.

      

      

### ExtractedContractDetails

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The contract fields that are extracted and reviewed during the extraction review process.

      

      

### ExtractedContractFieldCount

        
        

**Type:** int

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The number of contract fields extracted during the extraction review process.

      

      

### ExtractionMode

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The mode of document extraction.

        

Valid values are `BulkExtraction`—The document was a part of a bulk extraction or `SingleExtraction`—The document was extracted as a single document. The default value is `SingleExtraction`. Available in API version 67.0 and later.

      

      

### LastReferencedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed a record related to this record.

      

      

### LastViewedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the contract extraction review.

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** ID of the user that owns this record.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Refers To:** Group, User

      

      

### SourceDocumentIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The unique identifier of the source document in the connected external repository. Available in API version 67.0 and later.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the contract extraction review status.

        

Possible values are `ExtractionFailed`—Extraction Failed, `ExtractionInProgress`—Extraction In Progress, `ReviewCompleted`—Review Completed, `ReviewInProgress`—Review In Progress, or `ReviewNotStarted`—Review Not Started

      

      

### SubBatchJobSequence

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The sequence number of the sub-batch within a batch extraction job. Available in API version 67.0 and later.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContractExtractionResultChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContractExtractionResultFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContractExtractionResultHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContractExtractionResultOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContractExtractionResultShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
