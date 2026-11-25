---
page_id: connect-resources-calculation-procedure
title: Calculation Procedure
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-calculation-procedure.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-resources
legacy_page_id: connect_resources_calculation_procedure.htm
fetched_at: 2026-11-25
---

# Calculation Procedure

Retrieve the details for a given expression set (also known as calculation procedure) record.

**Note:**

This API has been deprecated as of API version 55.0. In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

## Resource

```
/connect/omnistudio/evaluation-services/${id}
```

## Example

```
/services/data/v53.0/connect/omnistudio/evaluation-services/0k0x000000000BQAAY
```

## Available Version

53.0

## Requires Chatter

No

## HTTP Methods

GET

## Response Body for GET

[Calculation Procedure Detail Output](./connect-responses-calculation-procedure-detail-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-calculation-procedure.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
