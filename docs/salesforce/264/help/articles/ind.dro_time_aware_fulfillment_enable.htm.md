---
article_id: ind.dro_time_aware_fulfillment_enable.htm
title: Turn On Time-Awareness
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_enable.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_advanced_setup.htm
fetched_at: 2026-09-05
---

# Turn On Time-Awareness

Dynamic Revenue Orchestrator (DRO) supports both time-agnostic and time-aware data. During decomposition and assetization, time-awareness evaluates timelines to identify changes in fulfillment asset quantities and attributes over time.

REQUIRED EDITIONS
Available in: Both Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To define how a product decomposes:	

Fulfillment Designer

OR

DRO Admin User

Before you enable time-awareness, run the migration scripts that move your existing time-agnostic data to the time-aware model. See Migrate Fulfillment Assets from Time-Agnostic to Time-Aware.
Update your orchestration plans that were designed for time-agnostic data so they can handle the fulfillment order line item outputs that time-aware decomposition generates.
NOTE
Staged assetization of ramp segments is supported only for time-aware fulfillment assets. For more information, see Staged Assetize Step.
Once you turn on time-awareness, you can't turn it off.

Time-awareness is turned off by default. To turn it on, complete these steps.

From Setup, in the Quick Find box, enter and then select Dynamic Revenue Orchestrator Settings.
Turn on Time-Awareness.
SEE ALSO
Order Fulfillment With Time-Awareness
