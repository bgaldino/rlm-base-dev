---
page_id: connect-responses-expression-set-version-output
title: Expression Set Version Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-version-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-responses
legacy_page_id: connect_responses_expression_set_version_output.htm
fetched_at: 2026-11-25
---

# Expression Set Version Output

Output representation of an expression set version.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `api​Name` | String | API name of the expression set version. | Small, 58.0 | 58.0 |
| `description` | String | Description of the expression set version. | Small, 58.0 | 58.0 |
| `enabled` | Boolean | Indicates whether the expression set version is active (`true`) or inactive (`false`). | Small, 58.0 | 58.0 |
| `end​Date` | String | Effective end date of the expression set version. | Small, 58.0 | 58.0 |
| `id` | String | ID of the expression set version. | Small, 58.0 | 58.0 |
| `name` | String | Name of the expression set version. | Small, 58.0 | 58.0 |
| `rank` | Integer | Rank of the expression set version. | Small, 58.0 | 58.0 |
| `show​Expl​Externally` | Boolean | Indicates whether the decision explanation is exposed to community users (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `start​Date` | String | Effective start date of the expression set version. | Small, 58.0 | 58.0 |
| `steps` | [Expression Set Version Step](./connect-responses-expression-set-version-step-output.md) | List of steps in an expression set. | Small, 58.0 | 58.0 |
| `variables` | [Expression Set Version Variable](./connect-responses-expression-set-version-variable-output.md) | List of variables in an expression set. | Small, 58.0 | 58.0 |
| `version​Number` | Integer | Version number of the expression set version. | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-version-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
