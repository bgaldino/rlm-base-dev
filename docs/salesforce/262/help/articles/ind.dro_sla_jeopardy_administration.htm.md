---
article_id: ind.dro_sla_jeopardy_administration.htm
title: SLA Jeopardy Administration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_sla_jeopardy_administration.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# SLA Jeopardy Administration

Honor your Service Level Agreements (SLAs) with alerts and other settings to handle fulfillment steps that run behind or fail to finish.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Dynamic Revenue Orchestrator (DRO) notifies you when a fulfillment step is late or in jeopardy of being late.

Jeopardy administration uses two concepts that work together: The Estimated Duration and the Jeopardy Threshold.

Estimated Duration
How long do you expect a fulfillment step to take? Enter a number, and then choose a unit, such as minutes or days. Let's say that you choose 10 minutes. If a step takes longer than ten minutes, then it's late.
Jeopardy Threshold
When do you want to be warned that a step is in jeopardy of being late? Enter a number, then choose a unit, such as minutes or days.
TIP The jeopardy threshold counts backwards from the estimated duration. So if the estimated duration is 100 minutes and the Jeopardy Threshold is 10 minutes, then the step is considered in jeopardy after 90 minutes.

To specify the callouts, manual tasks, or auto tasks that the rule applies to, enter an integration definition or a flow definition.

Integration definition
This field specifies the callouts that the rule applies to. If you leave it blank, then the rule applies to all callouts.
Flow definition
This field specifies the manual tasks or auto tasks that the rule applies to. If you leave it blank, then the rule applies to all manual tasks and auto tasks.

To create fulfillment step jeopardy rules, follow these instructions:

SEE ALSO
Turn On Features to Manage Fallout and Service Level Agreements
