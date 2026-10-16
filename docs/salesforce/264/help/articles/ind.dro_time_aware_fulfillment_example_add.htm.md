---
article_id: ind.dro_time_aware_fulfillment_example_add.htm
title: "Example: Add Action with Time-Awareness Turned On"
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_example_add.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# Example: Add Action with Time-Awareness Turned On

Let's see how Dynamic Revenue Orchestrator (DRO) uses time-awareness to decompose a multi-year ramp deal into fulfillment order line items (FOLIs) and Fulfillment Asset State Period (FASP) records that align with each year's effective dates.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Consider a commercial product, Agentforce for Sales, that decomposes into SC-Business or SC-Enterprise based on the Business attribute, and Tenant and License Provisioning. This example uses the Business attribute, so only SC-Business is created.

EXAMPLE

The customer purchases Agentforce for Sales in a 3-year ramp deal that starts January 1, 2026, with license quantities increasing each year.

Year 1: 100 licenses
Year 2: 200 licenses
Year 3: 300 licenses

Without time-awareness, decomposition produces a single configuration with no effective start or end dates. Later amendments overwrite past or future data and leave the asset in an inaccurate state.

With time-awareness enabled, DRO generates FOLIs mapped to each effective date range.

DRO generates these FOLIs for each technical product:

SC-Business: Three FOLIs for 100, 200, and 300 licenses, one per year.
License Provisioning: Three FOLIs that match the ramping quantities across the timeline.
Tenant: Three FOLIs that maintain a quantity of 1 across all three years. Because Tenant has account scope, its quantity stays at 1 regardless of the license ramp.

Each FOLI produces an Add action because no prior Fulfillment Asset or FASP records existed for these technical products on this account.

Because the FOLIs are sliced by time, DRO creates FASP 1, FASP 2, and FASP 3 for each FA. This structure prevents data overwrites and makes sure that the asset configuration that is active at any point in time drives orchestration.
