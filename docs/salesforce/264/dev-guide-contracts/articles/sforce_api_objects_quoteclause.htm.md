---
page_id: sforce_api_objects_quoteclause.htm
title: QuoteClause
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_quoteclause.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# QuoteClause

Represents a clause associated with a quote. The content is
      copied from a source document clause, so updates to the quote clause remain independent
      of the source clause. This object is available in API version 68.0 and later.

      

## Supported Calls

      
      

         `create()`,
         `delete()`,
         `describeLayout()`,
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

      
         

### Content

             
             
                 
- 
**Type**: textarea

                 
- 
**Properties**: Create, Update

                 
- 
**Description**: The clause content on the quote, including any modified
                                 placeholder values.

             

         

         

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

                                 

             

         

         

### DocumentClauseId

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Create, Filter, Group, Sort, Update

                 
- 
**Description**: The document clause ID of the reference clause from the Document
                                 Clause Library.

This field is a relationship field.

                 
- 
**Relationship Name**: DocumentClause

                 
- 
**Relationship Type**: Lookup

                 
- 
**Refers To**: DocumentClause

             

         

         

### Format

             
             
                 
- 
**Type**: picklist

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

                 
- 
**Description**: Specifies whether the term's content includes rich text
                                 formatting or not.

                 
- 
**Default value**: `Non_Formatted`

                 
- 
**Possible values**:
                                    
  - 
`Non_Formatted`—Non Formatted

                                    
  - 
`Rich_Text`—Rich Text

                                 

             

         

         

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

             

         

         

### LastReferencedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Nillable, Sort

                 
- 
**Description**: The timestamp for when the current user last viewed a record
                                 related to this record.

             

         

         

### LastViewedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Nillable, Sort

                 
- 
**Description**: The timestamp for when the current user last viewed this record.
                                 If this value is null, this record might only have been
                                 referenced (LastReferencedDate) and not viewed.

             

         

         

### Name

             
             
                 
- 
**Type**: string

                 
- 
**Properties**: Create, Filter, Group, idLookup, Sort, Update

                 
- 
**Description**: The name of the quote term typically derived from the name of the
                                 source clause.

             

         

         

### OwnerId

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

                 
- 
**Description**: The ID of the user that owns this record.

This field is a polymorphic relationship field.

                 
- 
**Relationship Name**: Owner

                 
- 
**Relationship Type**: Lookup

                 
- 
**Refers To**: Group, User

             

         

         

### QuoteId

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Create, Filter, Group, Sort, Update

                 
- 
**Description**: The parent quote ID of the quote clause.

This field is a relationship field.

                 
- 
**Relationship Name**: Quote

                 
- 
**Relationship Type**: Lookup

                 
- 
**Refers To**: Quote

             

         

         

### Reason

             
             
                 
- 
**Type**: string

                 
- 
**Properties**: Create, Filter, Group, Nillable, Sort, Update

                 
- 
**Description**: Indicates the reason for which the clause was added to the
                                 quote.

             

         

      

   

      

## Associated Objects

      
            
                

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[QuoteClauseChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)**

               
: Change events are available for the object.

            
            
               

**[QuoteClauseFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)**

               
: Feed tracking is available for the object.

            
            
               

**[QuoteClauseHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)**

               
: History is available for tracked fields of the object.

            
            
               

**[QuoteClauseOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)**

               
: Sharing rules are available for the object.

            
            
               

**[QuoteClauseShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)**

               
: Sharing is available for the object.
