---
page_id: connect_resources_document_recipient.htm
title: Document Recipient (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_recipient.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_customer_community_user.htm
fetched_at: 2026-10-13
---

# Document Recipient (GET)

Fetch recipient status for contract document
      versions to monitor e-signature progress and identify decline reasons.

    

## Resource

      
      

```
/connect/clm/cc/documentRecipient
```

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/cc/documentRecipient?contractDocumentVersion=11nxx000001hOozAAE
```

    

    

## Available Version

      
      

61.0

    

    

## HTTP Methods

      
      

GET

    

    

## Request Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contract​Document​VersionId` | String | Record ID of the contract document version. | Required | 61.0 |

    

    

## Response Body for GET

      
      

[Document Recipient Status](./connect_responses_document_recipient_status_c_c.htm.md)
