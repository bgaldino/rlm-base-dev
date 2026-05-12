---
article_id: ind.dro_fulfillment_viewer_page_failure.htm
title: Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_viewer_page_failure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Dynamic Revenue Orchestrator

If you set up Dynamic Revenue Orchestrator in Summer ’26, understand these limitations and workaround, where applicable, to ensure a successful implementation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management
A user with Fulfillment Manager/Operator permission set could encounter a data access exception while trying to access Decomposition Viewer. As a workaround, set Field Level Security for the OverriddenInheritedAttribute field in ProductClassificationAttr object. Then, refresh the Decomposition Viewer tab in the order page.
Execution of Submit Sales Transaction action fails when Orchestration Group Key maps to a non-unique context definition field that returns more than the supported limit of 100 records. To fix this issue, update the context mapping for the Orchestration Group Key to point a unique field.
Order decomposition fails if a mandatory technical product attribute lacks both a default value and an enrichment rule. To resolve this, either uncheck the Is Requiredsetting or define a default value in the attribute definition and the product classification attribute. Alternatively, configure an enrichment rule in the decomposition rule definition and ensure that the attribute value is provided in the order line item.
