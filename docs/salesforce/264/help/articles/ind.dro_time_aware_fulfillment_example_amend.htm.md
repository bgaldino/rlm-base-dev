---
article_id: ind.dro_time_aware_fulfillment_example_amend.htm
title: "Example: Mid-Year Amendment with Split Fulfillment Asset State Periods"
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_example_amend.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# Example: Mid-Year Amendment with Split Fulfillment Asset State Periods

Let's see how Dynamic Revenue Orchestrator (DRO) uses time-awareness to split existing Fulfillment Asset State Period (FASP) records when a new contract starts mid-year, and how it derives No Change, Amend, and Renew actions for the overlapping timeline.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

This example builds on the 3-year Agentforce for Sales ramp deal described in Example: Add Action with Time-Awareness Turned On. The account now adds Agentforce for Service in a second 3-year ramp deal that starts on June 1, 2026. Agentforce for Service decomposes into the same two shared technical products as Agentforce for Sales: Tenant and License Provisioning.

EXAMPLE

The Agentforce for Service ramp specifies these quantities:

Year 1: 50 licenses
Year 2: 150 licenses
Year 3: 250 licenses

Because the Agentforce for Service deal starts mid-Year 1 of the existing Agentforce for Sales contract, time-aware decomposition splits the Year 1 FASP timeline for the shared technical products into two segments: January 1 to May 31, and June 1 to December 31. The split generates six fulfillment order line items (FOLIs) for Tenant and six FOLIs for License Provisioning across the 3-year overlap.

Time-awareness derives these actions from the overlap:

No Change
The Tenant technical product has account scope, so its quantity stays at 1 across all periods. Tenant doen't require new FASP values for the existing periods.
Amend
The License Provisioning technical product uses an aggregate quantity rule. Starting June 1, Agentforce for Service contributes 50 more License Provisioning, which aggregate with the existing Agentforce for Sales License Provisioning for the second half of Year 1. The Amend action updates the existing License Provisioning FASPs to reflect the new aggregated quantity.
Renew
The Renew action applies in two situations: to insert a new FASP between two existing FASPs when DRO splits the timeline, and to add a new FASP for the final term of the Agentforce for Service deal that extends into 2029.

DRO marks the baseline License Provisioning and Tenant FASPs as superseded and replaces them with the newly generated FASPs that reflect the split time periods and the derived actions.

NOTE This example doesn't demonstrate the Cancel action. Cancel applies when a FASP that existed before technical assetization no longer exists afterward, such as when a customer terminates a specific term of a subscription.
