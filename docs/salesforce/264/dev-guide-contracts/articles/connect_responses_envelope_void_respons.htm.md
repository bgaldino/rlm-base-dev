---
page_id: connect_responses_envelope_void_respons.htm
title: Envelope Void
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_envelope_void_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Envelope Void

Void envelope related details.

              

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `failedEnvelopeList` | [​Envelope Status[]](./connect_responses_envelope_status_respons.htm.md) | List of envelopes that failed to void and their details. | Small, 56.0 | 56.0 |
| `sourceObjectId` | String | ID of the parent object. | Small, 56.0 | 56.0 |
| `successful​EnvelopeIds` | String[] | ID of envelopes successfully voided. | Small, 56.0 | 56.0 |
| `totalEnvelopes​ToBeVoided` | Integer | Total number of envelopes to be voided. | Small, 56.0 | 56.0 |
| `totalEnvelopes​Voided` | Integer | Actual count of envelopes voided. | Small, 56.0 | 56.0 |
