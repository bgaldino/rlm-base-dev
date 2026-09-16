---
page_id: connect_responses_context_definition_interface_metadata.htm
title: Context Definition Interface Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_metadata.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Interface Metadata

Output representation of the metadata associated with the context definition
    interface.

        
          

**JSON example**

          
: 
            

```
{
  "contextDefinitionInterfaceMetadata": {
    "createdBy": "Automated Process",
    "createdDate": "2024-05-15T00:00:00.000Z",
    "description": "Test Interface",
    "developerName": "TestBaseInterface",
    "interfaceName": "TestBaseInterface",
    "lastModifiedBy": "Automated Process",
    "parentInterfaces": [
      "TestBaseInterface1"
    ],
    "version": "62.1"
  }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `createdBy` | String | User, system, or object that created the context definition interface. | Small, 62.0 | 62.0 |
| `createdDate` | String | Date when the context definition interface was created. | Small, 62.0 | 62.0 |
| `description` | String | Description of the context definition interface. | Small, 62.0 | 62.0 |
| `developerName` | String | Developer name of the context definition interface. | Small, 62.0 | 62.0 |
| `interfaceName` | String | Title of the context definition interface. | Small, 62.0 | 62.0 |
| `lastModifiedBy` | String | User, system, or object that last updated the context definition interface. | Small, 62.0 | 62.0 |
| `parentInterfaces` | String[] | List of parent context definition interfaces that this interface is inherited from. | Small, 62.0 | 62.0 |
| `version` | String | Version number of the context definition interface. | Small, 62.0 | 62.0 |
