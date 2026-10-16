---
page_id: sforce_api_objects_contextusecasemapping.htm
title: ContextUseCaseMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contextusecasemapping.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContextUseCaseMapping

Represents the setup configuration details such as the context definition and mapping definitions used to invoke context service APIs. This object is available in API version 61.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### AdditionalUseCaseInput

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Stores any additional input for the extraction template that’s required by any UseCase Type. As of now we only need it to store the LLM Model associated with template(Extract Contract Details UseCase). Available in API version 67.0 and later.additional data for the extraction template, such as the selected `llmModel`, and descriptions for `clauseName` and `clauseText`.

      

      

### ContextDefinitionName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The name of the context definition that stores the hydration and persistence mapping details.

      

      

### DeveloperName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The developer name of the record.

      

      

### Language

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The language associated with this record.

        

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

        

**Description:** The user interface label for context use case mapping.

      

      

### NamespacePrefix

        
        

**Type:** string

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `NAMESPACE_PREFIX__COMPONENT_NAME` notation. The namespace prefix can have one of the following values.

        
          
- In Developer Edition orgs, NamespacePrefix is set to the namespace prefix of the org for all objects that support it, unless an object is in an installed managed package. In that case, the object has the namespace prefix of the installed managed package. This field’s value is the namespace prefix of the Developer Edition org of the package developer.

          
- In orgs that are not Developer Edition orgs, NamespacePrefix is set only for objects that are part of an installed managed package. All other objects have no namespace prefix.

        

      

      

### MappingName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The name of the mapping that's associated with the MappingType.

      

      

### MappingType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the mapping type used for context use case mapping.

        

Possible values are `Hydration` or `Persistence`

        

The default value is `Hydration`.

      

      

### ReferenceObjectName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The standard or custom source object from which the context mapping is fetched.

      

      

### TargetObjectCustomFieldName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the custom field in the target object that's used to link the target object with the reference object.

      

      

### TargetObjectName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the standard or custom object to which context mapping from the reference object is pushed.

      

      

### UseCaseType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the usage for which the context definition and mapping are defined.

        

Possible values are `ContractCreationOrUpdation`—Create Contract or Update Contract or `ContractExtraction`—Extract Contract Details

        

The default value is `ContractCreationOrUpdation`.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContextUseCaseMappingChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContextUseCaseMappingFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContextUseCaseMappingHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContextUseCaseMappingOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContextUseCaseMappingShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
