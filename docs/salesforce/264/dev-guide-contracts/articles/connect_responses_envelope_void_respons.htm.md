---
page_id: connect_responses_envelope_void_respons.htm
title: Envelope Void
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_envelope_void_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Envelope Void

Void envelope related details.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `failedEnvelopeList` | [​Envelope Status[]](./connect_responses_envelope_status_respons.htm.md "Output representation of the envelope status record.") | List of envelopes that failed to void and their details. | Small, 56.0 | 56.0 |
| `sourceObjectId` | String | ID of the parent object. | Small, 56.0 | 56.0 |
| `successful​EnvelopeIds` | String[] | ID of envelopes successfully voided. | Small, 56.0 | 56.0 |
| `totalEnvelopes​ToBeVoided` | Integer | Total number of envelopes to be voided. | Small, 56.0 | 56.0 |
| `totalEnvelopes​Voided` | Integer | Actual count of envelopes voided. | Small, 56.0 | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_envelope_void_respons.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
