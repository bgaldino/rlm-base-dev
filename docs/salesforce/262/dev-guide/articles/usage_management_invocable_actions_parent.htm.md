---
page_id: usage_management_invocable_actions_parent.htm
title: Usage Management Standard Invocable Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/usage_management_invocable_actions_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_overview.htm
fetched_at: 2026-06-09
---

# Usage Management Standard Invocable Actions

Learn more about the standard invocable actions available with Usage
Management.

- **[Invoke Summary Creation Action](./actions_obj_invoke_summary_creation.htm.md)**  
  Invoke the service that creates various summaries, such as usage, ratable, and liable summaries where the usage amount is zero. The service also checks and updates the billing period of the usage entitlement account if the billing period is expired.
- **[Process Consumption Overages Action](./actions_obj_process_consumption_overages.htm.md)**  
  Process consumption overages for the usage summary records with `SummaryComplete` status. This action uses the entitlement service to process the overages.
- **[Refresh Usage Entitlement Bucket Action](./actions_obj_refresh_usage_entitlement_bucket.htm.md)**  
  Refresh entitlements by evaluating the usage entitlement bucket records and creating a new usage entitlement entry.
- **[Retrigger Entitlement Creation Process Action](./actions_obj_retrigger_entitlement_creation_process.htm.md)**  
  Retrigger entitlement creation process for failed or unprocessed assets.

#### See Also

- [*Actions Developer Guide*: Overview](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_action.meta/api_action/actions_intro_overview.htm "Actions Developer Guide: Overview - HTML (New Window)")
- [*REST API Developer Guide*: Invocable Actions Standard](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/resources_actions_invocable_standard.htm "REST API Developer Guide: Invocable Actions Standard - HTML (New Window)")
- [*Salesforce Help*: Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management.htm&language=en_US "Salesforce Help: Usage Management - HTML (New Window)")
