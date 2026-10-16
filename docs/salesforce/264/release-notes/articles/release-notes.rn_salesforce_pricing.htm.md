---
article_id: release-notes.rn_salesforce_pricing.htm
title: Salesforce Pricing
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Salesforce Pricing

Apply compounding uplifts to ramp deal segments, scale your pricing logic with pricing recipes and procedures for each cloud, and reusable list variables. Set weekly as a proration frequency, and get standard decimal notation in pricing API responses.

Reduce Pricing Errors and Improve Deal Transparency on Ramp Deals
Calculate each segment's price uplift from the previous segment's uplift percentage instead of the original list price. Previously, uplifts on a ramp deal were always calculated from the product's original list price, so a 3-year deal with a $100 list price and a 10% annual uplift increased by $10 every year. Many multi-year agreements instead call for uplifts that compound: each year's increase applies to the prior year's already-uplifted price, not the original list price. Without compounding, sales teams calculated these prices manually outside the system, creating a risk of errors and reducing deal transparency for approvers.
Keep Calculated Values in Context with Local List Variables
Define local list variables directly within a pricing procedure to store and reuse calculated values across elements. Previously, storing a calculated value required creating a context tag or constant within the Pricing Procedure Builder ahead of time. Now, create, edit, and map list variables as you build your procedure, and reference them in the Price Waterfall.
Tailor Pricing Rules for Multiple Industry Clouds
Segment pricing recipes and pricing procedures by industry clouds using the Subtype field. Each cloud now gets its own default recipe and decision tables, instead of sharing one recipe that forced teams to coordinate unrelated pricing rules. Element lookups in a procedure now show only the decision tables from that subtype's default recipe, so pricing teams manage their metadata independently.
Prorate with High-Velocity and Short-Term Sales Models
Set Weekly as the proration frequency for a product to align subscription pricing with short-term service contracts and high-velocity consumption models. Previously, the system supported only annual, semiannual, quarterly, or monthly cycles. When you set a product's proration frequency to weekly, the pricing engine calculates the subtotal by multiplying the unit price by the number of 7-day cycles in the term, including partial weeks.
Avoid Integration Parsing Errors from Pricing API Decimal Values
The Pricing Connect API returns numeric values in standard decimal notation instead of scientific notation. For example, the API returns 10000000 instead of 1E+7.
New and Changed Connect REST APIs in Salesforce Pricing
Clone a pricing recipe along with its pricing recipe table mapping records, and optionally assign a different pricing usage subtype to the cloned pricing recipe. Streamline pricing recipe setup by retrieving valid pricing element types for a specific pricing usage subtype in a single API request, which reduces invalid configurations by returning only the elements supported by the selected context. Improve design-time governance and support multi-cloud operations by restricting context definitions and pricing procedures to vertical-specific options.
