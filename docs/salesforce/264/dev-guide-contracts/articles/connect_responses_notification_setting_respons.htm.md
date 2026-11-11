---
page_id: connect_responses_notification_setting_respons.htm
title: E-signature Notification Settings
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_notification_setting_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# E-signature Notification Settings

E-signature notification settings.

    

## Properties

      
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `expirations` | [Notification ​Expiration Setting](./connect_responses_notification_expiration_respons.htm.md) | Expirations settings for notification setting. | Small, 56.0 | 56.0 |
| `reminders` | [Notification ​Reminder Setting](./connect_responses_notification_reminder_respons.htm.md) | Reminder settings for notification setting. | Small, 56.0 | 56.0 |
| `useAccountDefaults` | Boolean | Indicates whether the Account defaults for notifications should be used by the envelope [ true | false ]. | Small, 56.0 | 56.0 |

    

    

## JSON Example

      
      

```

{  
   
    "useAccountDefaults": true,
    "reminders": {
        "reminderEnabled": true,
        "reminderDelay": 4,
        "reminderFrequency": 5
    },
    "expirations": {
        "expireEnabled": true,
        "expireAfter": 4,
        "expireWarn": 5
    }
    
}
```
