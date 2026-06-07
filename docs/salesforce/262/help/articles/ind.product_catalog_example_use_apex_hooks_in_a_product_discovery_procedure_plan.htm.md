---
article_id: ind.product_catalog_example_use_apex_hooks_in_a_product_discovery_procedure_plan.htm
title: "Example: Use Apex Hooks to Extend Pricing Logic"
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_example_use_apex_hooks_in_a_product_discovery_procedure_plan.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Example: Use Apex Hooks to Extend Pricing Logic

See how Apex hooks interact with Pricing sections when configured as pre- or post-hooks in a Product Discovery procedure plan.

Example Setup

This setup shows how external and internal prices interact. The procedure plan includes:

An Apex section that returns an external price (for example, $1234)
A Pricing section that applies internal pricing logic (for example, PSM = One Time → $199, PSM = Null → $149)

The placement of the Apex section determines whether its price takes effect or is overridden.

Pre-Hook Example: Internal Pricing as the Final Authority

Use this configuration when you want to fetch external prices but still rely on internal pricing as the final authority.

Procedure Plan

Section 1 – Apex (PricingApex)
Section 2 – Pricing (PricingProcedure)

How it works

The Apex hook fetches an external price of $1234 for the null PSM.
The Pricing procedure then calculates $149 and overwrites the null PSM price.

Returned Prices

PSM = One Time → $199
PSM = Null → $149
Post-Hook Example: Override Internal Pricing with External Logic

Use this configuration when you want external prices to override the results of internal pricing logic.

Procedure Plan

Section 1 – Pricing (PricingProcedure)
Section 2 – Apex (PricingApex)

How it works

The Pricing procedure calculates $199 and $149.
The Apex hook then updates the null PSM price to $1234.

Returned Prices

PSM = One Time → $199
PSM = Null → $1234
