---
article_id: ind.dro_configure_fulfillment_step_retries.htm
title: Configure Fulfillment Step Retries
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_fulfillment_step_retries.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Configure Fulfillment Step Retries

Specify the number of times a failed fulfillment step tries again after failing, and how long it waits before each retry. You can even stagger the time between retries, so that, for example, it retries right away, then again in five minutes, and again in 20 minutes.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To configure fulfillment step retries:	System Administrator Profile

When steps such as callouts and auto tasks fail because a system is down, it wastes resources to immediately try again only to fail again. Fulfillment designers can schedule steps to wait before retrying. For example, they can schedule a retry every five minutes, or stagger the retries so that each retry waits longer than the one before it.

From Setup, in the Quick Find box, enter Fallout and SLA Settings, and select it.
In the Fallout section, click Configure.
Do one of these things:
To create a rule, click New.
To edit a rule that you've already created, create a list view to see the rules, then click the rule that you want to edit.
From Retry Policy, select the retry policy for the fulfillment process to follow when a step fails.
Immediate: The step immediately tries again, up to the number of times specified in the Retries Allowed field.
Monotonous: The step tries again at the intervals set in the Retry Intervals field, up to the number of times specified in the Retries Allowed field.
Staggered: The step tries again at the intervals set in the Retry Intervals field. It retries once for each interval that's specified. For example, if you set 10,15,40, then the step retries after 10 minutes, again after another 15 minutes, and then after another 40 minutes before moving to the Fatally Failed state.
In Retries Allowed, enter the number of times that the step retries before either succeeding or moving to the Fatally Failed state.
Leave this field blank for the Staggered policy.
In Retry Intervals, enter the time in minutes to wait before the step retries after failing.
Leave this field blank for the Immediate policy.
