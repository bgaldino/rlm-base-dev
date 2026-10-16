---
page_id: connect_resources_document_playbook_version.htm
title: Document Playbook Version (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_playbook_version.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_document_playbook_resources.htm
fetched_at: 2026-10-13
---

# Document Playbook Version (POST)

Create a playbook version and link it to a content
      document.

    
      

This resource validates the input, creates a `DocumentPlaybookVersion` record for the specified playbook, and creates a
          `ContentDocumentLink` record that links the new playbook
        version to the specified content document.

    

    

## Special Access Rules

      
      

Playbook must be enabled in your org, and you must have the Playbook Designer
                    permission.

    

    

## Resource

      
      

```
/connect/document-playbook/document-playbook-version
```

    

    

## Resource Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/document-playbook/document-playbook-version
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```

{
  "playbookId" : "0RDxx0000004C92GAE",
  "description" : "Initial version of the contract playbook",
  "contentDocumentId" : "069xx0000004C92GAE"
}
```

      

**Properties**

      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentDocument​Id` | String | ID of the content document. | Required | 68.0 |
| `description` | String | Description of the playbook version. | Optional | 68.0 |
| `playbookId` | String | ID of the playbook. | Required | 68.0 |

    

    

## Response Body for POST

      
      

[Playbook Version
              Details](./connect_responses_playbook_version_details.htm.md)
