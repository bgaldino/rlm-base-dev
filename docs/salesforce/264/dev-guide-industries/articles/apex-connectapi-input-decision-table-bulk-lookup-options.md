---
page_id: apex-connectapi-input-decision-table-bulk-lookup-options
title: ConnectApi.DecisionTableBulkLookupOptions
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-input-decision-table-bulk-lookup-options.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apex-input-classes
fetched_at: 2026-11-25
---

# ConnectApi.DecisionTableBulkLookupOptions

Input representation of the lookup options for a versioned CSV decision table. The API ignores these options for any other decision table type.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | [String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string) | Effective date in ISO 8601 format, such as `2022-12-03T10:15:30Z`. The API uses this date to resolve the version number when `versionNumber` isn’t provided. | Optional | 67.0 |
| `versionNumber` | [Integer](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_integer.htm) | Version number for the lookup. When `effectiveDate` and `versionNumber` are both provided, the API uses `versionNumber`. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-input-decision-table-bulk-lookup-options.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
