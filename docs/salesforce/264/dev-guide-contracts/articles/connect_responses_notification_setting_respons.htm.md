---
page_id: connect_responses_notification_setting_respons.htm
title: E-signature Notification Settings
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_notification_setting_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# E-signature Notification Settings

E-signature notification settings.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `expirations` | [Notification ​Expiration Setting](./connect_responses_notification_expiration_respons.htm.md "E-signature notification expiration settings.") | Expirations settings for notification setting. | Small, 56.0 | 56.0 |
| `reminders` | [Notification ​Reminder Setting](./connect_responses_notification_reminder_respons.htm.md "E-signature notification reminder settings.") | Reminder settings for notification setting. | Small, 56.0 | 56.0 |
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_notification_setting_respons.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
