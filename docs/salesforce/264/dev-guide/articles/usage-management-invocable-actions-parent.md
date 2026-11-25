---
page_id: usage-management-invocable-actions-parent
title: Usage Management Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-invocable-actions-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-overview
legacy_page_id: usage_management_invocable_actions_parent.htm
fetched_at: 2026-11-25
---

# Usage Management Standard Invocable Actions

Learn more about the standard invocable actions available with Usage Management.

- 

**[Invoke Summary Creation Action](./actions-obj-invoke-summary-creation.md)**

Invoke the service that creates various summaries, such as usage, ratable, and liable summaries where the usage amount is zero. The service also checks and updates the billing period of the usage entitlement account if the billing period is expired.

- 

**[Process Consumption Overages Action](./actions-obj-process-consumption-overages.md)**

Process consumption overages for the usage summary records with `SummaryComplete` status. This action uses the entitlement service to process the overages.

- 

**[Refresh Usage Entitlement Bucket Action](./actions-obj-refresh-usage-entitlement-bucket.md)**

Refresh entitlements by evaluating the usage entitlement bucket records and creating a new usage entitlement entry.

- 

**[Retrigger Entitlement Creation Process Action](./actions-obj-retrigger-entitlement-creation-process.md)**

Retrigger entitlement creation process for failed or unprocessed assets.

**See Also**

- 

[*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.api_action.meta/api_action/actions_intro_overview.htm)

- 

[*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_actions_invocable_standard.htm)

- 

[*Salesforce Help*: Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/usage-management-invocable-actions-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
