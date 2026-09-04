---
article_id: ind.product_catalog_partial_search.htm
title: Partial Search
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_partial_search.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_index_and_search_of_product_catalog.htm
fetched_at: 2026-09-04
---

# Partial Search

Partial search helps you find products by entering an incomplete product code or product SKU. It matches the term that you enter to any part of the product code or product SKU, ignoring special characters such as hyphens, underscores, spaces, periods, and slashes.

REQUIRED EDITIONS
View supported products and editions.

Partial search works on Product Code and Product SKU fields, if they're marked as searchable. To make the fields searchable, see Configure Searchable Fields & Attributes.

Searches don't require SKU or sku prefixes to return Product SKU results. For example, searching for "12345" returns "SKU-12345".
Searches don't need special characters such as hyphens, underscores, periods, and slashes. For example, searching for "1234567" returns "SKU-1234567".
Search terms must include at least 3 characters for optimal results.
EXAMPLE

If a product Titanium Pro 2026 has the product SKU LP-X1C-2025 and the product code TPX1C:

SEARCH TERM	MATCHES	DESCRIPTION
X1C	Product SKU	Matches the middle of the SKU
2025	Product SKU	Matches the end of the SKU
LP	Product SKU	Matches the beginning of the SKU
TPX or X1C	Product Code	Matches the product code
Configure Partial Search
Find products more efficiently by searching with partial product codes or product SKUs.
