---
article_id: ind.dro_fulfillment_viewer_page_failure.htm
title: Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_viewer_page_failure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.rev_cloud_upgrade_known_issues.htm
fetched_at: 2026-09-05
---

# Dynamic Revenue Orchestrator

If you set up Dynamic Revenue Orchestrator in Winter '27, understand these limitations and workaround, where applicable, to ensure a successful implementation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
Execution of Submit Sales Transaction action fails when Orchestration Group Key maps to a non-unique context definition field that returns more than the supported limit of 500 records. To fix this issue, update the context mapping for the Orchestration Group Key to point a unique field.
Clicking Launch Flow on a Manual Task step in a Fulfillment Plan or Fulfillment Step record results in an Flow Launch error, and halts the orchestration plan. As a workaround, run the screen flow manually. Then, mark the current step as Completed to resume the orchestration plan.
