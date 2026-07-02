---
article_id: ind.rm_element_list_group_list_operation.htm
title: List Group and List Operation
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_list_group_list_operation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# List Group and List Operation

A list group element filters items in a list based on the filter conditions and then performs further operations on the filtered lists. A list operation is always the first step in the list group and defines how items in the list are filtered.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

When you create a list group, your first element, List Operation, defines how items in the list are filtered. The rating elements added later within the list group depend on the conditions applied.

EXAMPLE Create a List Group element and filter the base rate based on the consumption over the base limit. For consumption over 100 units, give a 10% discount. Here’s how to configure your list group element and rating procedure.
Ensure that you already created your rating procedure and configured rating settings.
Add the List Group rating element to the procedure.
In the list group, configure the list operation to filter consumption over 100 units.
Add a calculation step and calculate the updated base rate after applying the 10% discount.

In this image, we see that the list operation applied has the condition that the overage quantity must be greater than 100 units. When this condition is met, the rating procedure moves to the Formula-Based Rating element to calculate the net unit rate for the usage resource.

If a customer consumes fewer than 100 units of the usage resource, it doesn’t meet the condition, and the rating procedure skips this step altogether. When a customer consumes more than 100 units of usage resource, the procedure applies a discount of 10% to the net unit rate.

Simulate and verify the data that’s queried. When you activate the rating procedure, the Waterfall view shows every step of the rating calculation and the discounts applied.
