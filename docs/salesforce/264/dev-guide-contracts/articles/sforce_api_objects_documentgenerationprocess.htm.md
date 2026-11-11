---
page_id: sforce_api_objects_documentgenerationprocess.htm
title: DocumentGenerationProcess
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentgenerationprocess.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentGenerationProcess

Supports server-side document generation requests and responses. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### AdditionalMetadata

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Stores metadata for dynamic images used during document generation. Available in API version 66.0 and later.

      

      

### ContextTokenProcessingType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The context token processing path used for the document generation request. This field is only available with the Revenue Events Starter Pack, Revenue Cloud Advanced, and Revenue Cloud Billing license. Valid values are:

        
          
- 
`Regular`—Uses standard token processing.

          
- 
`Large`—Specify this value for requests that process high volumes of token data across multiple records or line items.

        

        

The default value is `Regular`. Available in API version 67.0 and later.

      

      

### DataRaptorInput

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Any additional input required for document generation, such as object ID, JSON, or a string.

      

      

### DocGenAdditionalInput

        
        

**Type:** textarea

        

**Description:** For internal use only.

      

      

### DocGenAdditionalInputType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** For internal use only.

      

      

### DocGen​ApiVersion​Type

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Specifies the API version to use for document generation. Possible values include `Basic` and `Advanced`. The default value is `Basic`.

        

Available in API version 62.0

      

      

### Document​TemplateId

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** ID of the document template for operations like cloning or creating a new version.

        

Available in API version 62.0.

      

      

### EstimatedDocumentSize

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** For internal use only.

      

      

### DocumentInputType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The input type of the document.

        

Possible values are:

        
          
- 
`DocumentTemplate`—Document Template

          
- `None`

        

        

The default value is `None`.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Autonumber, Defaulted on create, Filter, idLookup, Sort

        

**Description:** Represents an automatically generated system name. Example: Request-001.

      

      

### HasDocGenFontSource

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the document template font (true) or a rich text editor font (false) is used for rendering values during document generation.

        

The default value is `false`.

      

      

### IsLocalizationEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether document generation applies the user’s locale to context token data ( `true`) or not ( `false`). If set to `true`, the document generation process uses the translated text and localized date, time, and currency formats. This option applies only when the template uses context token mapping. The default value is `false`. Available in API version 67.0 and later.

      

      

### IsSharedExternally

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the document is shared with external users ( `true`) or not ( `false`).

        

The default value is `false`. Available in API version 66.0 and later.

      

      

### LastReferencedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed a record related to this record.

      

      

### LastViewedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed.

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** ID of the user that owns this record.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Refers To:** Group, User

      

      

### PdfDocIdentifiersList

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The PDF document IDs of the contract documents to be converted into a single .pdf file. You can combine upto ten PDFs into a single file. Make sure the content version ID for each PDF file is 18 characters long. Available in API version 63.0 and later.

      

      

### ReferenceObject

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** Refers to the object to which generated document is attached.

      

      

### RequestText

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Requests parameters that are passed in the payload.

      

      

### ResponseText

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Requests parameters that are passed in the payload.

      

      

### ShouldUseLargeFileSizeProc

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether document generation is routed through the Large File Size (LFS) infrastructure ( `true`) instead of using the default standard file size–based routing ( `false`). The default value is `false`. This field is available in API version 67.0 and later with the Revenue Events Starter Pack, Revenue Cloud Advanced, and Revenue Cloud Billing license.

      

      

### IsTocUpdateRequired

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the table of contents of the generated document is to be updated ( `true`) or not ( `false`). Supported only for documents up to 25 MB. The default value is `false`. Available in API version 67.0 and later.

      

      

### SourceObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Specifies the object from which the document generation request is created. For example, Contract Document Version.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** SourceObject

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Contains the status of the request.

        

Possible values are `Failure`, `Success`, or `InProgress`

        

The default value is `InProgress`.

      

      

### TokenData

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Contains JSON data with information that users enter in the new, generated document.

      

      

### TokenData​Content​Document

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort

        

**Description:** The Token Data Content Document associated with the Document Generation Process. Contains information that users enter in the new generated document.

      

      

### Type

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Type of service requested for the document for generating and converting to PDF.

        

Possible values are `Generate`, `Convert`, `GenerateAndConvert`, or `MergePDF`

        

The default value is `Generate`.
