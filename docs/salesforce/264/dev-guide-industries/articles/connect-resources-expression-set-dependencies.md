---
page_id: connect-resources-expression-set-dependencies
title: Expression Set Version Dependencies (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-expression-set-dependencies.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-resources
legacy_page_id: connect_resources_expression_set_dependencies.htm
fetched_at: 2026-11-25
---

# Expression Set Version Dependencies (GET)

Retrieve expression set version dependencies.

## Resource

```
/connect/business-rules/expression-set/version/${expressionSetVersionId}/dependencies
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v58.0/connect/business-rules/expression-set/version/9QARN000000016v4AA/dependencies
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

58.0

## Requires Chatter

No

## HTTP Methods

GET

## Response Body for GET

[Expression Set Version Dependency](./connect-responses-expression-set-version-dependency-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-expression-set-dependencies.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
