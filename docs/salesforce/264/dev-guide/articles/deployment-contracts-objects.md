---
page_id: deployment-contracts-objects
title: Salesforce Contracts Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-objects.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-a
legacy_page_id: deployment_contracts_objects.htm
fetched_at: 2026-11-25
---

# Salesforce Contracts Objects

This table provides the deployment sequence, object types, API names, and lookup fields for Salesforce Contracts in Revenue Management.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | Clause Category Configuration | ClauseCatgConfiguration | 1 | None |
| Configuration | Document Clause Set | DocumentClauseSet | 2 | ClauseCatgConfiguration |
| Configuration | Document Clause | DocumentClause | 3 | DocumentClauseSet, ContentDocument |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-objects.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
