---
page_id: connect-resources-bre-expression-set-id-delete-get
title: Expression Set (DELETE, GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-expression-set-id-delete-get.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-resources
legacy_page_id: connect_resources_bre_expression_set_id_delete_get.htm
fetched_at: 2026-11-25
---

# Expression Set (DELETE, GET)

Read or delete expression set for a specified expression set ID.

## Resource

```
/connect/business-rules/expression-set/${expressionSetId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/business-rules/expression-set/$11Oxx0000006PcLEAU
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

58.0

## Requires Chatter

No

## HTTP Methods

DELETE, GET

## Response Body for GET

[Expression Set Output](./connect-responses-expression-set-output.md)

## Response Body for DELETE

None.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-expression-set-id-delete-get.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
