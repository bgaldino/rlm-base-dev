---
page_id: sforce_api_objects_documenttemplateconfig.htm
title: DocumentTemplateConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documenttemplateconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentTemplateConfig

Represents the shadow object that supports migration of document templates between environments. The Developer field in the shadow object references the UniqueName field in the document template object and is used to retrieve the document template details. For internal use only. This object is available in API version 58.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### DeveloperName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Required. The unique name of the object in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores.

      

      

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

        

      

      

### NamespacePrefix

        
        

**Type:** string

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `NAMESPACE_PREFIX__COMPONENT_NAME` notation. The namespace prefix can have one of the following values.

        
          
- In Developer Edition orgs, NamespacePrefix is set to the namespace prefix of the org for all objects that support it, unless an object is in an installed managed package. In that case, the object has the namespace prefix of the installed managed package. This field’s value is the namespace prefix of the Developer Edition org of the package developer.

          
- In orgs that are not Developer Edition orgs, NamespacePrefix is set only for objects that are part of an installed managed package. All other objects have no namespace prefix.

        

      

      

### MasterLabel

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Required The user interface label for the document template config.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentTemplateConfigChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentTemplateConfigFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentTemplateConfigHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentTemplateConfigOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentTemplateConfigShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
