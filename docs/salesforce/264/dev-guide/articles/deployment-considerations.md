---
page_id: deployment-considerations
title: Deployment Considerations
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-considerations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-overview
legacy_page_id: deployment_considerations.htm
fetched_at: 2026-11-25
---

# Deployment Considerations

In any deployment scenario, you must understand all dependencies and prerequisites related to your planned changes.

Here’s a list of things to consider and plan for.

Key considerations include:

- What’s the sequence followed for object deployment? What dependencies exist on related objects?

- Do your objects have Draft, Active, or Inactive states?

- Does activation occur through an API or by simply setting a boolean field (active flag)?

- Are there special fields to consider, such as text fields with embedded IDs, JSON, or fields populated via triggers?

- Are there fields or objects that represent unique or sequential data that must be preserved in the target org?

- How would you handle system settings between the orgs? For example, making sure that a feature toggle is turned off in the target org so that automation doesn’t start executing when you insert data from your source org.

- What’s the impact of versioning on your deployment? For example, schema, app, or API versions.

**Note:**

For detailed information about these deployment considerations, see [Additional Deployment Information](./deployment-appendix-c.md).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-considerations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
