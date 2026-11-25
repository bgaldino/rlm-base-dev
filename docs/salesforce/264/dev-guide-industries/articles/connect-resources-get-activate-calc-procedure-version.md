---
page_id: connect-resources-get-activate-calc-procedure-version
title: Calculation Procedure Version Definition (Activate, Get)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-get-activate-calc-procedure-version.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-resources
legacy_page_id: connect_resources_get_activate_calc_procedure_version.htm
fetched_at: 2026-11-25
---

# Calculation Procedure Version Definition (Activate, Get)

Retrieve the definition of an expression set (also known as calculation procedure) version record. Activate an expression set version record.

## Resource

```
/connect/omnistudio/evaluation-services/version-definitions/${id}
```

## Example

```
/services/data/v53.0/connect/omnistudio/evaluation-services/
version-definitions/0lIxx000000001dEAA
```

## Available Version

53.0

## Requires Chatter

No

## HTTP Methods

GET, PATCH

## Response Body for GET

[Calculation Procedure Version Definition Output](./connect-responses-calculation-procedure-version-definition-output.md)

## Response Body for PATCH

[Calculation Procedure Activation Output](./connect-responses-calculation-procedure-activation-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-get-activate-calc-procedure-version.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
