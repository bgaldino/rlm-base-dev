---
page_id: sforce_api_objects_documentclauseset.htm
title: DocumentClauseSet
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentclauseset.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentClauseSet

Represents a grouping for clauses, which can hold multiple variations of the same clause such as main clause and alternate pre-approved clauses based on language.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

DocumentClauseSet is available for users with the ClauseManagement user permission set licenses. Salesforce Org must have a ClauseManagement platform license to access this object.

    

  

    

## Fields

    
      

### Category

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the category of the clause set.

        

Possible values are `0zMRO000000003P`—Test

      

      

### CategoryReferenceId

        
        

**Type:** reference

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** This field is used for validating category values.

        

This field is a relationship field.

        

**Relationship Name:** CategoryReference

        

**Relationship Type:** Lookup

        

**Refers To:** ClauseCatgConfiguration

      

      

### DefaultLanguage

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the default language of the clause set.

        

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

        

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the clause set.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

        

**Description:** Specifies the status of the clause set.

        

Possible values are `Active`, `Archived`, or `Draft`

        

The default value is `Draft`.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentClauseSetChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentClauseSetFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentClauseSetHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentClauseSetOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentClauseSetShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
