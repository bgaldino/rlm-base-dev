---
page_id: connect_requests_simulation_version_info_input.htm
title: Simulation Version Info Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_version_info_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-11-23
---

# Simulation Version Info Input

Input information of the version details to run
simulation.

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurationVersionId` | String | The ID of the expression set version record. | Required | 53.0 |
| `effectiveDate` | String | The expression set version that's active on this date is simulated. When multiple versions are active on the effective date, the version with higher priority is executed. | Optional | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_simulation_version_info_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
