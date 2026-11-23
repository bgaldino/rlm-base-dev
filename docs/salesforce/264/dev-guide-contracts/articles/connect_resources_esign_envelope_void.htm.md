---
page_id: connect_resources_esign_envelope_void.htm
title: E-signature Envelope Void
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_envelope_void.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_docgen_resources.htm
fetched_at: 2026-11-23
---

# E-signature Envelope Void

Expire or void envelopes associated with an object.

## Resource

```
/connect/e-sign/signature-requests/$SOURCE_OBJECT_ID/envelopes/void
```

## Available Version

56.0

## HTTP Methods

PATCH

## Example

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/e-sign/signature-requests/{sourceObjectId}/envelopes/void
```

## JSON Example

```
{
    "voidedReason": "",//required
    "senderEmail": ""
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `senderEmail` | String | Refers to the email of the user who initiated the voiding. | Optional | 56.0 |
| `voidedReason` | String | Reason for which the envelope is being voided. | Required | 56.0 |

## Response Body for PATCH

[Envelope Void Response](./connect_responses_envelope_void_respons.htm.md "Void envelope related details.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_esign_envelope_void.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
