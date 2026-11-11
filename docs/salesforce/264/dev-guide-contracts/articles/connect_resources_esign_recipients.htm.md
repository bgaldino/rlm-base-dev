---
page_id: connect_resources_esign_recipients.htm
title: E-signature Recipients
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_recipients.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-10-13
---

# E-signature Recipients

Get list of e-signature recipients.

    

## Resource

      
      

```
/connect/e-sign/recipients
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

GET

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/recipients?sourceObjectId=<sourceObjectId>&recipientSelector=<recipientCustomClassName>
```

    

    

## Request Parameters for GET

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `recipientSelector` | String | Create a list of recipients that receive the DocuSign envelope for signing or viewing for a custom object. | Optional | 56.0 |
| `sourceObjectId` | String | Object Id of the document. | Optional | 56.0 |

    

    

## Response Body for GET

      
      

[Recipient List Response](./connect_responses_recipient_list_respons.htm.md)
