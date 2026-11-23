---
article_id: ind.product_catalog_turn_on_price_book_filtering.htm
title: Turn On Price Book Filtering
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_turn_on_price_book_filtering.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_set_up_product_catalog_management.htm
fetched_at: 2026-11-23
---

# Turn On Price Book Filtering

Price book filtering addresses incomplete product results in large catalogs when the price book and catalog overlap are minimal. Price book filtering retrieves only the products that are associated with the selected price book, so you see relevant results without going through the entire catalog.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To turn on price book filtering:	Product Catalog Management Designer

This issue occurs in these two scenarios when you:

Browse catalogs with a quote that has a selected price book.
Configure bundles by using product classifications.

When browsing catalogs, you can encounter situations where no products or only a few products appear, even though products with matching price book entries exist in your catalog. A similar issue occurs during bundle configuration when valid products are available for a product classification.

Price book filtering uses your transaction's price book earlier in the process during product listing, search, and guided selection.

If you use the index and search capability, rebuild the search index when you associate price books with products or remove price books from products. To learn when to run a full or partial index rebuild, see Manage Your Product Index.

Before you begin:

If you're using indexed data, rebuild the index before turning on Price Book Filtering. See Build the Product Index.

From Setup, in the Quick Find box, enter Product Discovery, and then select Product Discovery Settings.
Turn on Price Book Filtering.
SEE ALSO
Manage Your Product Index

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_turn_on_price_book_filtering.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
