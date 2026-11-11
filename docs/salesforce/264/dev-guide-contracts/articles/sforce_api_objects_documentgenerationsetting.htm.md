---
page_id: sforce_api_objects_documentgenerationsetting.htm
title: DocumentGenerationSetting
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentgenerationsetting.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentGenerationSetting

Represents an org's settings for automatic document generation from templates. This object is available in API version 54.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

DocumentGenerationSetting is available if your org has the DocGen platform license and related addon and user licenses.

    

  

    

## Fields

    
      

### BatchDocGnrnPctLimitPerHour

        
        

**Type:** percent

        

**Properties:** Create, Defaulted on create, Filter, Nillable, Sort, Update

        

**Description:** The maximum percentage of hourly server-side document generation requests used for batch processing.

        

Available in version 58.0 and later.

      

      

### DeveloperName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Required. The unique name of the object in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores.

      

      

### DocumentTemplateLibraryName

        
        

**Type:** string

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the library associated with the document template.

      

      

### GenerationMechanism

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The location where the web document is generated.

        

Possible values are `ClientSide`—Client-Side or `ServerSide`—Server-Side

        

The default value is `ClientSide`.

      

      

### GuestAccessNamedCredential

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The named credential that lets guest users generate documents.

      

      

### InProgDocGenRqstTmot

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The time interval (in hours) after which InProgress DocumentGenerationProcess records (single point or batch request) are terminated and the request status is updated to Failed. Specify a valid whole number between 1 and 24. The default value is set to 6.

      

      

### IsBatchDocGnrnEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether server-side document generation requests are queued and processed within the hourly batch document generation limit.

        

The default value is `false`.

        

Available in version 58.0 and later.

      

      

### IsInProgRqstTmotEnab

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the InProgress DocGen Request Time Out (hrs) is enabled (true) or not (false).

        

The default value is `false`.

      

      

### IsServerSideDocGenEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether side server document generation is enabled `true` or not `false` for this org.

        

The default value is `false`.

      

      

### Language

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The language of the label in the user interface.

        

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

        

      

      

### MasterLabel

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The user interface label for document generation setting.

      

      

### NamespacePrefix

        
        

**Type:** string

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `NAMESPACE_PREFIX__COMPONENT_NAME` notation. The namespace prefix can have one of the following values.

        
          
- In Developer Edition orgs, NamespacePrefix is set to the namespace prefix of the org for all objects that support it, unless an object is in an installed managed package. In that case, the object has the namespace prefix of the installed managed package. This field’s value is the namespace prefix of the Developer Edition org of the package developer.

          
- In orgs that are not Developer Edition orgs, NamespacePrefix is set only for objects that are part of an installed managed package. All other objects have no namespace prefix.

        

      

      

### PreviewType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The type of viewer that’s used to view the generated web document.

        

Possible values are `PDF` or `Thumbnail`

        

The default value is `PDF`.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentGenerationSettingChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentGenerationSettingFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentGenerationSettingHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentGenerationSettingOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentGenerationSettingShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
