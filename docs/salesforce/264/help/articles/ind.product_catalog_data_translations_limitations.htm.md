---
article_id: ind.product_catalog_data_translations_limitations.htm
title: Data Translation Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_data_translations_limitations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_data_translation.htm
fetched_at: 2026-11-23
---

# Data Translation Limits

There are limitations to where translated product details appear when you use data translation in Product Catalog Management.

REQUIRED EDITIONS
View supported products and editions.
When you use Browse Catalog from quotes and orders, the last modified date isn’t shown for any catalogs.
Asset names aren’t translated in the Managed Asset Viewer when a translated catalog is enabled.
If a Product Attribute Definition (PAD) override is present, translations aren’t supported for that attribute. Searches use only the base value.
For dynamic attributes, only picklist types support translations. Attributes of other types (such as text) use only base values.
A full reindex is required in these cases:
When partial indexing is disabled. The system automatically determines when this applies.
When translations for custom field labels are added, removed, or updated.
When translations for enum fields (dynamic, static, or multi-select) are added, removed, or updated.
In all other scenarios, partial indexing can be used.
When translations aren’t available for a language, search results fall back to the base values.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_catalog_data_translations_limitations.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
