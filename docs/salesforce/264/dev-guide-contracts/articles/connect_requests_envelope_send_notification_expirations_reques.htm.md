---
page_id: connect_requests_envelope_send_notification_expirations_reques.htm
title: Envelope Notification Expiration Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_notification_expirations_reques.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Envelope Notification Expiration Input

Input to get notification expiration information.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `expireAfter` | String | An integer specifying the number of days that a sent envelope remains active before it expires. | Optional | 56.0 |
| `expireEnabled` | String | Indicates whether or not the envelope is no longer available for signing after the specified number of days after it was sent. | Optional | 56.0 |
| `expireWarn` | String | Integer that specifying the number of days before the envelope expires that an expiration warning email is sent to the recipient; if set to 0 (zero), no warning email is sent. | Optional | 56.0 |
