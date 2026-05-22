---
article_id: ind.dro_configure_fulfillment_step_jeopardy_rules.htm
title: Configure Fulfillment Step Jeopardy Rules
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_fulfillment_step_jeopardy_rules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Configure Fulfillment Step Jeopardy Rules

Configure the rules that determine when a fulfillment step is considered to be in jeopardy, and when it's considered late.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To configure fulfillment step jeopardy rules:	System Administrator profile
From Setup, in the Quick Find box, enter Fallout and SLA Settings and select it.
In the Service Level Agreement section, click Configure.
Click New.
In the Estimated Duration and Estimated Duration Unit fields, enter the time that you expect the step to take.
In the Jeopardy Threshold and Jeopardy Threshold Unit fields, enter the amount of time before the estimated duration is complete that the step is in jeopardy of running late. For example, if the estimated duration is ten minutes and you enter two minutes as the jeopardy threshold, the step is in jeopardy after running for eight minutes.
NOTE Because the jeopardy threshold counts back from the estimated duration, make sure that the jeopardy threshold is less than the estimated duration.
Optional: To specify callouts that the rule applies to, enter an integration definition in the Integration Definition field. If you leave the Integration Definition field blank, then the rule applies to all callouts.
Optional: To specify manual tasks or auto tasks that the rule applies to, enter a flow definition in the Flow Definition field. If you leave the Flow Definition field blank, then the rule applies to all manual tasks and auto tasks.
Save your work.
EXAMPLE

Let's say there's a manual task to check the credit of a customer. You set the Estimated Duration to 3 hours. Then you set the Jeopardy Threshold to 30 minutes. If the step isn’t completed within 2.5 hours after it starts, the task is considered in jeopardy.

To see the status of the fulfillment step, check the orchestration plan for the order. To learn more about monitoring your orchestration plans, see Monitor Fulfillment During Order Orchestration.
IMPORTANT If you edit an existing fulfillment step jeopardy rule, you must refresh the Fulfillment Step Jeopardy Rule Entries decision table for the changes to take effect.
SEE ALSO
Create an Integration Definition
Refresh a Decision Table
