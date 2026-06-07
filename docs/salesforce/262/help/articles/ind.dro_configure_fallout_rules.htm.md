---
article_id: ind.dro_configure_fallout_rules.htm
title: Configure Fallout Rules
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_fallout_rules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Configure Fallout Rules

Configure rules for how Dynamic Revenue Orchestrator (DRO) handles callouts and auto tasks that fail. Specify how often they're retried, at what intervals, and which queue they go to if they fatally fail.

REQUIRED EDITIONS

.

Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To configure Fallout:	System Administrator Profile

To configure fallout rules:

From Setup, in the Quick Find box, enter Fallout and SLA Settings, and select it.
In the Fallout section, turn on the fallout settings, then click Configure.
Click New.
If necessary, enter the integration definition that the callout uses to integrate with the external system.
If you leave the Integration Definition field blank, then the rule applies to all callouts or auto tasks that don't use more specific rules.
For auto tasks, add a flow definition name.
To set up retries, enter the retry policy, the retry intervals, and the retries allowed.
See: Configure Fulfillment Step Retries.
Enter the queue where fatally failed steps are assigned.
The queue must have fulfillment steps as supported objects. From that queue, you can bulk retry or bulk complete the steps.
If necessary, enter the error expected from the external system.
If you leave the Error Code field blank, then the rule applies to all callouts or auto tasks that don't use more specific rules.
IMPORTANT If you're changing the rules after previously saving them, you must refresh the Fulfillment Fallout Rules decision table to implement the new rules.
SEE ALSO
Create an Integration Definition
Refresh a Decision Table
