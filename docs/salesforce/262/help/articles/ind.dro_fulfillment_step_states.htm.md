---
article_id: ind.dro_fulfillment_step_states.htm
title: Fulfillment Step States
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_step_states.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Fulfillment Step States

As steps progress through the fulfillment process, you can check the fulfillment plan to see the state that the steps are in.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Table of Fulfillment Step States

STATE	MEANING
Pending	This fulfillment step is waiting for prerequisites to finish before moving to the next state.
Ready	This fulfillment step is ready to run, but hasn't started running yet. For example, it might be a manual task that no one has started working on yet.
In Progress	This fulfillment step is running.
Completed	This fulfillment step is completed.
Failed	This fulfillment step has failed and will be retried, based on the retry policy and fallout rules. Note: This state and Fatally Failed appear in the same color.
Fatally Failed	This fulfillment step has failed and the allowed number of retries, as defined in the fallout rule, have failed as well. The step won't be executed. Note: This state and Failed appear in the same color.
Skipped	This fulfillment step didn't run as planned. The conditions for the step's Execute On rule weren't met, so the step never executed.
Amended	A completed fulfillment step enters this state when a supplemental order amends the original order.
Canceled	A completed fulfillment step enters this state when a supplemental order cancels the original order.
Discarded	An incomplete fulfillment step enters this state when a supplemental order cancels the original order.
Scheduled	A future-dated fulfillment step that is waiting to run at a designated time.
