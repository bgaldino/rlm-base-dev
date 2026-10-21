---
page_id: connect_resources_esign_documents_list.htm
title: E-signature Document List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_documents_list.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-10-13
---

# E-signature Document List

View a list of documents sent for e-signature.

    

## Resource

      
      

```
/connect/e-sign/documents
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

GET

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/documents?sourceObjectId=<sourceObjectId>&documentSelector=<customClassName>
```

    

    

## Request Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentSelector` | String | Specifies which class is executed. Use this when you want to define a custom class other than the default class or the one already defined for DocuSignDocumentSelector. | Optional | 56.0 |
| `sourceObjectId` | String | Record ID of the object. | Required | 56.0 |

    

    

## Response Body for GET

      
      

[Document List Response](./connect_responses_document_list_respons.htm.md)
