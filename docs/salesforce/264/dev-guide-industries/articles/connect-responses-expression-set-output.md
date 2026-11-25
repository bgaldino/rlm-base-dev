---
page_id: connect-responses-expression-set-output
title: Expression Set Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-responses
legacy_page_id: connect_responses_expression_set_output.htm
fetched_at: 2026-11-25
---

# Expression Set Output

Output representation of the expression set create, update and delete request.

- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `api​Name` | String | Unique name of the expression set. | Small, 58.0 | 58.0 |
| `context​Definitions` | [Context ​Definition Output](./connect-responses-context-definition-output.md) | List of context definitions in an expression set. | Small, 58.0 | 58.0 |
| `description` | String | Description of the expression set. | Small, 58.0 | 58.0 |
| `error` | [Expression Set​ Error](./connect-responses-expression-set-error.md) | Details of the error message in the case of failure of the expression set create request. | Small, 58.0 | 58.0 |
| `id` | String | ID of the expression set. | Small, 58.0 | 58.0 |
| `name` | String | Name of the expression set. | Small, 58.0 | 58.0 |
| `status` | String | Response status of the expression set. Valid values are: `Failed``Success` | Small, 58.0 | 58.0 |
| `usage​Type` | String | Usage type of the expression set. Valid value is `Bre`. The default value is `Bre`. When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Small, 58.0 | 58.0 |
| `versions` | [Expression Set​ Version Output](./connect-responses-expression-set-version-output.md) | List of the expression set versions. | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-expression-set-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
