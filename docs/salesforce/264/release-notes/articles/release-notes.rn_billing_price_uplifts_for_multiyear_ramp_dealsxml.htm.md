---
article_id: release-notes.rn_billing_price_uplifts_for_multiyear_ramp_dealsxml.htm
title: Automate Compound Price Uplifts for Multiyear Ramp Deals
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_price_uplifts_for_multiyear_ramp_dealsxml.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing_schedules_arrangements.htm
fetched_at: 2026-09-30
---

# Automate Compound Price Uplifts for Multiyear Ramp Deals

Compound uplift builds each ramp segment's price on the net price of the segment before it, not the original list price. Multiyear deals no longer need manual, error-prone uplift calculations outside Salesforce, and deal approvers get an accurate number right away. The same compounding logic carries through amendments and renewals, and billing schedules reflect the compounded price automatically once you activate the order.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced license.

How: To turn on compound uplift for new ramp schedules, from Setup, enter Revenue Settings in the Quick Find box, select Revenue Settings, and turn on Advanced Transaction Detail Line Pricing. Then set Ramp Uplift Type to Compound Uplift. The existing default, Standard Uplift, stays in place until you change it, and sales reps can't override this setting unless you grant edit access at the ramp schedule or segment level. Billing schedules pick up the calculated price automatically when you activate the order, so no separate billing configuration is required.

SEE ALSO
Apply Compound Price Uplifts to Multiyear Ramp Deals to Adjust Pricing Over Time
Reduce Pricing Errors and Improve Deal Transparency on Ramp Deals
