---
article_id: ind.sf_contracts_throttling.htm
title: Maintain the Consistency and Resilience of Server-Side Document Generation
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_throttling.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_spring_23_release_notes.htm
fetched_at: 2026-10-13
---

# Maintain the Consistency and Resilience of Server-Side Document Generation

Use throttling to manage the incoming server-side document generation requests. Throttling also prevents degradation of the document generation service due to the high volume of requests during certain hours. You must be on Spring ‘23 Omnistudio Document Generation release.

The default limits for the maximum server-side document generation requests:

Per hour: 1000/org

Per day: 24000/org

If the server-side document generation requests exceed the hourly limit or the daily limit, the requests beyond the limit are blocked and the request details are saved in the Document Generation Processes entity.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, Professional, and Developer editions.

See Also

Metering and Throttling
