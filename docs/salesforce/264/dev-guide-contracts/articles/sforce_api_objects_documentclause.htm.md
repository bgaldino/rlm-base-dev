---
page_id: sforce_api_objects_documentclause.htm
title: DocumentClause
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentclause.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentClause

Represents a clause that can be associated with multiple documents.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

DocumentClause is available for users with the ClauseManagement user permission set licenses. Salesforce Org must have a ClauseManagement platform license to access this object.

    

  

    

## Fields

    
      

### ClauseTmplVersionIdentifier

        
        

**Type:** string

        

**Properties:** Filter, Group, idLookup, Nillable, Sort

        

**Description:** The system-generated token identifier used in a document template to insert a specific clause version during document generation. This identifier always inserts the same clause version, even if a newer active version is published later. The value is auto-populated when the clause is saved and is read-only.

      

      

### Content

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Represents the HTML content of the document clause.

      

      

### Description

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Represents the summary of the document clause.

      

      

### DocumentClauseSetId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Represents the ID of Document Clause Group associated with Document Clause.

        

This field is a relationship field.

        

**Relationship Name:** DocumentClauseSet

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentClauseSet

      

      

### Format

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the format for the clause such as Rich Text.

        

Possible values are `Non_Formatted`—Non Formatted or `Rich_Text`—Rich Text

        

The default value is `Non_Formatted`.

      

      

### IsAlternateClause

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the Document Clause is main or alternate.

        

The default value is false.

      

      

### IsEligibleForTerms

        
        

**Type:** boolean

        

**Properties:** Defaulted on create, Filter, Group, Sort

        

**Description:** Indicates whether the clause can be added to the relevant Salesforce object.

      

      

### Language

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the language of the document clause.

        

Possible values are:

        
          
- 
`da`—Danish

          
- 
`de`—German

          
- 
`en_US`—English

          
- 
`es`—Spanish

          
- 
`es_MX`—Spanish (Mexico)

          
- 
`fi`—Finnish

          
- 
`fr`—French

          
- 
`it`—Italian

          
- 
`ja`—Japanese

          
- 
`ko`—Korean

          
- 
`nl_NL`—Dutch

          
- 
`no`—Norwegian

          
- 
`pt_BR`—Portuguese (Brazil)

          
- 
`ru`—Russian

          
- 
`sv`—Swedish

          
- 
`th`—Thai

          
- 
`zh_CN`—Chinese (Simplified)

          
- 
`zh_TW`—Chinese (Traditional)

        

      

      

### LastReferencedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed a record related to this record.

      

      

### LastViewedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed.

      

      

### LatestClauseTmpldentifier

        
        

**Type:** string

        

**Properties:** Filter, Group, idLookup, Nillable, Sort

        

**Description:** The system-generated token identifier used in a document template to insert the latest active version of the clause during document generation. The value is auto-populated when the clause is saved and is read-only.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Specifies the name of the document template clause.

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** ID of the user that owns this record. This field
          is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Refers To:** Group, User

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the status of the clause such as Draft, Active, Archived.

        

Possible values are:

        
          
- 
`AI_Drafted`—This value is available in API version 60.0 and later.

          
- `Active`

          
- `Archived`

          
- `Draft`

          
- `In_Approval`

          
- `Review_Requested`

        

        

The default value is `Draft`.

      

      

### Version

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The version number of the document clause.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentClauseChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentClauseFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentClauseHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentClauseOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentClauseShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
