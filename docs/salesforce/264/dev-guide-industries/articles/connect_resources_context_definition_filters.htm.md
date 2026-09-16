---
page_id: connect_resources_context_definition_filters.htm
title: Context Definition Filters (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_filters.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Filters (GET, POST)

Create or get context filters associated with a specific context definition. Context
    filters are criteria or conditions that refine or limit data operations based on specific
    parameters.

    
      
        
          

**Resource**

          
: 

```
/connect/context-definitions/${contextDefinitionId}/context-filters
```

The
              `contextDefinitionId` property value is the unique
            identifier for the context definition whose filters you want to retrieve.

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/context-definitions/SimpleDef/context-filters
```

          

        
        
          

**Available version**

          
: 65.0

        
        
          

**HTTP methods**

          
: GET, POST

        
        
          

**Response body for GET**

          
: [Context Definition Filter List](./connect_responses_context_definition_filter_list.htm.md)

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "filters": [
    {
      "filterApiName": "FilterAccount",
      "filterName":"FilterAccount",
      "filtersPerNode": "{\"Account\":{\"filterCondition\":{\"attribute\":\"City\",\"operator\":\"EQUALS\",\"operands\":[{\"value\":\"Bengaluru\",\"type\":\"STRING\"}],\"composite\":false},\"orderByConditions\":[{\"orderByAttribute\":\"Name\",\"ascending\":false,\"nullsFirst\":false}],\"limit\":5}}",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE"
    }
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filters` | [Context Definition Filter Input](./connect_requests_context_definition_filter_input.htm.md)[] | List of context definition filter inputs. | Required | 65.0 |

          

        
        
          

**Response body for POST**

          
: [Context Definition Filter List](./connect_responses_context_definition_filter_list.htm.md)
