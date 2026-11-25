---
page_id: deployment-contracts-additional-info
title: Salesforce Contracts Additional Information
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-additional-info.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-c
legacy_page_id: deployment_contracts_additional_info.htm
fetched_at: 2026-11-25
---

# Salesforce Contracts Additional Information

Get to know additional deployment information for Salesforce Contracts in Revenue Cloud, including active or inactive states, and migration considerations.

Document clauses can be in different states, such as Draft, In Approval, Active, and Archived. Keep these considerations in mind regarding the clause statuses.

- 

A clause is created in Draft status.

- 

During the import process, the clause must be in Draft status. You can update the status after you complete the import process.

- 

An archived clause can’t be updated.

- 

An active clause can’t be updated, but it can change to Draft status only if it’s not used.

- 

An active clause must be moved to Draft status before you update it to Active status.

- 

**[Clause Migration Considerations](./deployment-contracts-clause-migration.md)**

Clause migration is a prerequisite for Microsoft 365 template migration. Review these considerations to understand how clause structure, versions, and relationships must exist in the target org before migrating document templates.

- 

**[Clause Validations and Migration Constraints](./deployment-contracts-clause-validation-migration-constraints.md)**

Validation rules, data model constraints, and known migration behaviors that affect clause records during migration. Review this reference to understand sequencing, status handling, and dependency requirements that can impact migration success.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-contracts-additional-info.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
