---
article_id: ind.product_catalog_sort_categories_in_a_catalog.htm
title: Sort Categories in a Catalog
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_sort_categories_in_a_catalog.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Sort Categories in a Catalog

Make the browsing experience consistent and predictable for your buyers by defining category display order in Product Catalog Management (PCM) at design time. The same order appears in Product Discovery (PD) at runtime.

REQUIRED EDITIONS
View supported products and editions.

Unsorted categories can confuse users and slow product discovery. Adding sort order values ensures a consistent browsing experience and lets catalog admins prioritize categories without custom workarounds.

Categories sort in the sequence: null → negative → zero → positive.
If all categories have a null sort order, they’re listed by creation time in descending order (newest first).
If two or more categories share the same sort order value, they’re listed by creation timestamp in descending order (newest first).
Editing a category doesn’t change its position unless you change its sort order.

Suppose your hardware catalog contains these categories:

Desktop (Sort Order = null, created on Jan 1)
Tablet (Sort Order = –1, created on Feb 1)
Laptop (Sort Order = 0, created on Mar 1)
Monitor (Sort Order = 1, created on Apr 1)
Printer (Sort Order = null, created on May 1)

When users browse the catalog, the categories appear in this order:

Printer (null, newest created among nulls)
Desktop (null, older null)
Tablet (–1, negative)
Laptop (0)
Monitor (1, positive)
Set the Display Order of Catalog Categories
Define the display order of catalog categories by assigning numeric sort order values. Use null, negative, zero, or positive numbers to control which categories appear first, in the middle, or last.
