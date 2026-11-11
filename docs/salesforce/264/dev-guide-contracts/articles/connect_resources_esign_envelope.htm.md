---
page_id: connect_resources_esign_envelope.htm
title: E-signature Envelope
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_envelope.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-10-13
---

# E-signature Envelope

Send document envelope to vendor for e-signature.

    

## Resource

      
      

```
/connect/e-sign/signature-requests/$SOURCE_OBJECT_ID/envelope/send
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

POST

    

    

## Example

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/signature-requests/{sourceObjectId}/envelope/send
```

    

    

## JSON Example

      
      

```
{
    "emailSettings" :  { // API: required, UI: required
        "emailSubject": "",// API: required,
        "emailBody": ""
    },
    "vendor": "Docusign",// API: required,
    "recipients": {// API: required,
        "signers": [{// API: required,
                "name": "",// API: required,
                "email": "",// API: required,
                "routingOrder": "",// API: required,
                "recipientId": "",// API: required,
                "signerRole": "",// API: required,
                "recipientType": "",// API: required,
                "recipientLocale": "",
                "phone": "",
                "emailNotification": {
                    "emailSubject": "",
                    "emailBody": "",
                    "supportedLanguage": ""
                }
            }
        ],
        "inPersonSigners": [{
                "name": "",
                "email": "",
                "routingOrder": "",
                "recipientId": "",
                "signerRole": "",
                "emailNotification": {
                    "emailSubject": "",
                    "emailBody": "",
                    "supportedLanguage": ""
                }
            }
        ],
        "certifiedDeliveries": [{
                "name": "",
                "email": "",
                "routingOrder": "",
                "recipientId": "",
                "signerRole": "",
                "emailNotification": {
                    "emailSubject": "",
                    "emailBody": "",
                    "supportedLanguage": ""
                }
            }
        ],
        "carbonCopies": [{
                "name": "",
                "email": "",
                "routingOrder": "",
                "recipientId": "",
                "signerRole": "",
                "emailNotification": {
                    "emailSubject": "",
                    "emailBody": "",
                    "supportedLanguage": ""
                }
            }
        ]
    },
    "documents": [{ // API: required
            "name": "",// API: required,
            "sourceId": "",// API: required,
            "fileExtension": "",// API: required,
            "sourceType": "",// API: required,
            "documentId": ""// API: required,
        }
    ],
    "notificationSettings": {
        "useAccountDefaults": "", 
        "reminders": {
            "reminderEnabled": "",
            "reminderDelay": "",
            "reminderFrequency": ""
        },
        "expirations": {
            "expireEnabled": "",
            "expireAfter": "",
            "expireWarn": ""
        }
    }
}
```

    

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documents` | [Envelope Send​ Documents Request[]](./connect_requests_envelope_send_documents_reques.htm.md) | Array of documents to send. | Required | 56.0 |
| `emailSettings` | [Envelope Send ​Email Settings Request](./connect_requests_envelope_send_email_settings_reques.htm.md) | Email settings. | Required | 56.0 |
| `notificationSettings` | [Envelope Send​ Notification Request](./connect_requests_envelope_send_notification_reques.htm.md) | Notification settings. | Optional | 56.0 |
| `parentId` | String | ID of the parent object. | Optional | 56.0 |
| `recipients` | [Envelope Send ​Recipients Request](./connect_requests_envelope_send_recipients_reques.htm.md) | Map of different recipients. | Required | 56.0 |
| `vendor` | String | Vendor name. | Required | 56.0 |

    

    

## Request Parameters for POST

      
      

                      
                      
                      
                      
                      
                      
                        
                          

                          

                          

                          

                          

                        

                      

                      
                        
                          

                          

                          

                          

                          

                        

                      

                    
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `envelope` | Object | E-signature envelope containing information of the document. | Required | 56.0 |

    

    

## Response Body for POST

      
      

[Envelope Send Response](./connect_responses_envelope_send_respons.htm.md)
