---
page_id: connect-requests-decision-matrix-options
title: Decision Matrix Options Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-options.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-requests
legacy_page_id: connect_requests_decision_matrix_options.htm
fetched_at: 2026-11-25
---

# Decision Matrix Options Input

Input representation of the options used to look up a decision matrix.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | String | The date from when a decision matrix version comes into effect. The date format is yyyy-mm-dd’T’hh:mm:ss’Z. | Optional | 55.0 |
| `useDatesOnly` | String | Specifies that only the date portion (yyyy-mm-dd) of the value of the effectiveDate field be used at the time of execution. | Optional | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-matrix-options.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
