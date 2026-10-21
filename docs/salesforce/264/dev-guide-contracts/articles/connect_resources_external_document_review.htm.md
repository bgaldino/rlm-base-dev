---
page_id: connect_resources_external_document_review.htm
title: External Document Review (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_external_document_review.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_external_document_resources.htm
fetched_at: 2026-10-13
---

# External Document Review (GET)

Retrieve external document for review using latest contract document
    version.

    

## Resource

      
      

```
/connect/clm/cc/external-document
```

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/cc/external-document?contractDocumentVersion=11nxx000001hOozAAE
```

    

    

## Available Version

      
      

61.0

    

    

## HTTP Methods

      
      

GET

    

    

## Request Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contract​Document​VersionId` | String | Record ID for the contract document version. | Required | 61.0 |

    

    

## Response Body for GET

      
      

[External Document Review CC](./connect_responses_external_document_review_c_c.htm.md)
