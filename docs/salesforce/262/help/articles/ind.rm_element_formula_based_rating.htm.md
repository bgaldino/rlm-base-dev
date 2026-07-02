---
article_id: ind.rm_element_formula_based_rating.htm
title: Formula-Based Rating
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_formula_based_rating.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Formula-Based Rating

The Formula-Based Rating element performs functions and mathematical calculations to generate the rate of a usage resource.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
EXAMPLE Provide a formula to update the net unit rate of the usage products by adding a constant number (3) to it.
Add the Formula-Based Rating element to your rating procedure.
In the Input Variable section, in the Calculation Formula field, add a mathematical formula by using context tags or constant resources.
In the Output Variable field, specify the context tag that stores the calculation formula’s result.

Here, we're using the NetUnitRate context tag used to update the net unit rate of the usage resource by 3 units.
