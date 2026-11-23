---
page_id: connect_resources_esign_notification_settings.htm
title: E-signature Notification
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_notification_settings.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-11-23
---

# E-signature Notification

Get e-signature notification settings.

## Resource

```
/connect/e-sign/notification-settings
```

## Available Version

56.0

## HTTP Methods

GET

## Example

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/notification-settings?sourceObjectId=<sourceObjectId>
```

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sourceObjectId` | String | Object ID of the document. | Required | 56.0 |

## Response Body for GET

[Notification Setting Response](./connect_responses_notification_setting_respons.htm.md "E-signature notification settings.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_notification_settings.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
