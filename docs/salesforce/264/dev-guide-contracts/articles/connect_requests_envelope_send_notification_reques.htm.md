---
page_id: connect_requests_envelope_send_notification_reques.htm
title: Envelope Notification Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_notification_reques.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Envelope Notification Input

Input to get notification information for
    e-signature.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `expirations` | [Envelope Send Notification​Expirations Request](./connect_requests_envelope_send_notification_expirations_reques.htm.md) | Expiration settings. | Optional | 56.0 |
| `reminders` | [Envelope Send Notification ​Reminders Request](./connect_requests_envelope_send_notification_reminders_reques.htm.md) | Reminder settings. | Optional | 56.0 |
| `useAccountDefaults` | Boolean | Indicates whether or not the account defaults for notifications must be used by the envelope [ true | false ]. | Optional | 56.0 |
