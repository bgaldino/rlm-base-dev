---
page_id: connect_responses_notification_expiration_respons.htm
title: E-signature Notification Expiration
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_notification_expiration_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# E-signature Notification Expiration

E-signature notification expiration settings.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `expireAfter` | Integer | Integer specifying the number of days that a sent envelope remains active before it expires. | Small, 56.0 | 56.0 |
| `expireEnabled` | Boolean | Indicates whether the envelope is no longer available for signing after the specified number of days after it was sent. | Small, 56.0 | 56.0 |
| `expireWarn` | Integer | Integer that specifying the number of days before the envelope expires that an expiration warning email is sent to the recipient; if set to 0 (zero), no warning email is sent. | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_notification_expiration_respons.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
