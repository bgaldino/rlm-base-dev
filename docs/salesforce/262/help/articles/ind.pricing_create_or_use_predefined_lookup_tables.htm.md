---
article_id: ind.pricing_create_or_use_predefined_lookup_tables.htm
title: Decision Tables
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_or_use_predefined_lookup_tables.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Decision Tables

Decision tables are essential as they match your input values with the input rows in a decision table, returning the matching row’s output pricing element that uses it in a pricing procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

Decision tables provide a structured, efficient, and maintainable way to manage complex pricing logic without needing to hardcode numerous conditional statements. You can centralize and organize these rules into a clear, tabular format using decision tables. The tabular format makes it easy to see all the conditions applied and their corresponding outcomes at a glance. This transparency helps in understanding why a particular price was derived and makes it easier to audit pricing decisions.

NOTE We recommend that you use the Advanced decision table type instead of the Standard type.

When working with decision tables, you'll map various variables.

Input Rule Variables: These refer to the input from the selected decision table.
Output Rule Variables: These refer to the output from the selected decision table.
Input Variables: These refer to the input provided by the pricing element.
Output Variables: These refer to the output generated from the pricing element.
Additional Variables: These are custom output variables reflecting a pricing change. Their values can only be added using the Advanced mode (JSON) during simulation and are visible in the waterfall view.
NOTE To enable multicurrency with active pricing procedures linked to predefined Salesforce Pricing decision tables, first deactivate the pricing procedure, then enable multicurrency, and finally reactivate the procedure. Similarly, to add the Currency field to a predefined decision table in a multicurrency org, you must deactivate the decision table, add the field, and then activate it.
