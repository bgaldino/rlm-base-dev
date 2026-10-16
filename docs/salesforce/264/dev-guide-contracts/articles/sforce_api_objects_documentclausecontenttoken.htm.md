---
page_id: sforce_api_objects_documentclausecontenttoken.htm
title: DocumentClauseContentToken
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentclausecontenttoken.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentClauseContentToken

Represents a token used in document clause content.
      Supported token types include merge tokens, which are resolved at run time, and
      placeholder tokens, which are provided at run time. This object is available in API
      version 68.0 and later.

      

## Supported Calls

      
      

         `create()`,
         `delete()`,
         `describeSObjects()`,
         `getDeleted()`,
         `getUpdated()`,
         `query()`,
         `retrieve()`,
         `search()`,
         `undelete()`,
         `update()`,
         `upsert()`
      

      

      

      

## Fields

      
         

### CreatedById

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Filter, Group, Sort

                 
- 
**Description**: The user who created this record.

             

         

         

### CreatedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Sort

                 
- 
**Description**: The date and time when this record was created.

             

         

         

### CurrencyIsoCode

             
             
                 
- 
**Type**: picklist

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

                 
- 
**Description**: Available only if the multicurrency feature is enabled. Contains
                                 the ISO code for any currency allowed by the organization.

                 
- 
**Default value**: `USD`

                 
- 
**Possible values**:
                                    
  - 
`INR`—Indian Rupee

                                    
  - 
`JPY`—Japanese Yen

                                    
  - 
`USD`—U.S. Dollar

                                 

             

         

         

### DefaultValue

             
             
                 
- 
**Type**: string

                 
- 
**Properties**: Create, Filter, Group, Nillable, Sort, Update

                 
- 
**Description**: The default value of the placeholder token which gets added when
                                 the parent clause is associated with a record.

             

         

         

### DocumentClauseId

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Create, Filter, Group, Sort

                 
- 
**Description**: The parent document clause associated with the token. The token
                                 is deleted when the parent clause is deleted.

This field is a relationship field.

                 
- 
**Relationship Name**: DocumentClause

                 
- 
**Relationship Type**: Master-detail

                 
- 
**Refers To**: DocumentClause (the master object)

             

         

         

### LastModifiedById

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Filter, Group, Sort

                 
- 
**Description**: The user who most recently modified this record.

             

         

         

### LastModifiedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Sort

                 
- 
**Description**: The date and time when this record was most recently
                                 modified.

             

         

         

### Name

             
             
                 
- 
**Type**: string

                 
- 
**Properties**: Create, Filter, Group, idLookup, Sort, Update

                 
- 
**Description**: The token name used in the clause content.

             

         

         

### TokenType

             
             
                 
- 
**Type**: picklist

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

                 
- 
**Description**: The type of the token used in the clause content.

                 
- 
**Default value**: `Merge`

                 
- 
**Possible values**:
                                    
  - `Merge`

                                    
  - `Placeholder`

                                 

             

         

         

### ValueType

             
             
                 
- 
**Type**: picklist

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

                 
- 
**Description**: Specifies the data type of the placeholder token value.

                 
- 
**Default value**: `String`

                 
- 
**Possible values**:
                                    
  - `Currency`

                                    
  - `Date`

                                    
  - `Percentage`

                                    
  - `String`

                                 

             

         

      

   

      

## Associated Objects

      
            
                

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[DocumentClauseContentTokenChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)**

               
: Change events are available for the object.

            
            
               

**[DocumentClauseContentTokenFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)**

               
: Feed tracking is available for the object.

            
            
               

**[DocumentClauseContentTokenHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)**

               
: History is available for tracked fields of the object.

            
            
               

**[DocumentClauseContentTokenShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)**

               
: Sharing is available for the object.
