---
article_id: ind.product_catalog_data_translation.htm
title: Translate Product Catalog Data
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_data_translation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Translate Product Catalog Data

Display product catalog data in the user’s configured language with data translation. Localize key Product Catalog Management (PCM) objects so buyers and sales teams can search, filter, and browse in their preferred language, improving accuracy and adoption.

PCM shows product and catalog data only in the org’s base language. This can make it difficult for international teams and customers who expect localized content.

Data translation solves this by letting admins add translated values for products, categories, and attributes. At runtime, users see product names, descriptions, and filters in their configured language, and they can search using local terms.

Data translation improves the global buying experience, reduces errors, and helps organizations expand into new markets with localized catalogs.

Translatable PCM Objects and Fields

OBJECT	TRANSLATABLE FIELDS
Product2	Name, Description, Help Text, and Picklist values
Product Category	Name and Description
Product Classification Attributes	Attribute name, Help text, and Picklist values
Dynamic Attributes (Picklist type only)	Display values of picklist entries

How Data Translation Works

Add translations in bulk (export, edit, and import files) or manually on each record.
Translations are included in the search index after a full reindex.
Localized values appear in product listings, filters, and search results.
Users can search with translated terms. For example, a French user can enter portable and see matching products.
IMPORTANT To use data translation, the Use Indexed Data for Product Listing and Search setting must be turned on in Index and Search Configuration. See Configure Search Options.
Set Up Data Translation in Product Catalog Management
Enable data translation and add supported languages so you can translate PCM entities into multiple languages. After you enable data translation, you can configure which languages to support and make them available in Product Catalog Management (PCM). Translations appear at runtime only after you configure Index Settings and run a full reindex.
Bulk Export and Import Translation Files
Export Product Catalog Management (PCM) translation data into STF or XLIFF files, add your localized values, and import the files back into Salesforce. Use this method to update large volumes of product, category, and attribute translations at once. After import, reindex the catalog so users see the localized values in product listings and search results.
Enter Translations Manually in the Translations Tab
Add translations directly on product, category, or attribute records using the Translations tab. Use this method for quick updates or small sets of localized values. After saving translations, reindex the catalog so users see the localized values in product listings and search results.
Use Flow Metadata to Enable Translated Product Catalogs
One method for enabling translated product catalogs is to download an updated version of the Discover Products flow and use its metadata to create a new flow.
Example: Provide a Localized French Buying Experience
This example shows how data translation changes the runtime experience for French users. See how translated values appear in catalogs, categories, products, and search results. Deliver localized catalogs without duplicate configurations. Buyers benefit from intuitive search and browsing in their preferred language, reducing confusion and improving adoption.
Data Translation Limits
There are limitations to where translated names appear when you use data translation in Product Catalog Management.
