---
page_id: connect_requests_envelope_send_documents_reques.htm
title: Envelope Documents Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_documents_reques.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Envelope Documents Input

Input to get document details for e-signature.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentId` | String | Sequence number of the document in the e-signature envelope. For example, 1, 2, 3, and so on. | Required | 56.0 |
| `fileExtension` | String | File extension type. | Required | 56.0 |
| `name` | String | Name of document. | Required | 56.0 |
| `sourceId` | String | Object ID of the document. | Required | 56.0 |
| `sourceType` | String | Object type of the document object. | Required | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_documents_reques.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
