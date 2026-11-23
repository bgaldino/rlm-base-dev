---
page_id: connect_requests_envelope_send_recipients_reques.htm
title: Envelope Recipients Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_recipients_reques.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Envelope Recipients Input

Input to get different recipients list.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `carbonCopies` | [Envelope Send ​Recipient​ Detail Request[]](./connect_requests_envelope_send_recipient_detail_reques.htm.md "Input to get recipient details.") | Carbon copy user details. | Optional | 56.0 |
| `certifiedDeliveries` | [Envelope Send ​Recipient​ Detail Request[]](./connect_requests_envelope_send_recipient_detail_reques.htm.md "Input to get recipient details.") | Certificate deliveries details. | Optional | 56.0 |
| `inPersonSigners` | [Envelope Send ​Recipient​ Detail Request[]](./connect_requests_envelope_send_recipient_detail_reques.htm.md "Input to get recipient details.") | In person signer details. | Optional | 56.0 |
| `signers` | [Envelope Send ​Recipient​ Detail Request[]](./connect_requests_envelope_send_recipient_detail_reques.htm.md "Input to get recipient details.") | Array of signer details. | Required | 56.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_send_recipients_reques.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
