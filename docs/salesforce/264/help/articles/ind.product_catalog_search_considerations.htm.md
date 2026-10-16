---
article_id: ind.product_catalog_search_considerations.htm
title: Search Considerations When Using Indexed Data
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_search_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_index_and_search_of_product_catalog.htm
fetched_at: 2026-09-04
---

# Search Considerations When Using Indexed Data

When users search for a product by using a search term, Product Catalog Management checks for an exact match to the search term. If it can't find an exact match, PCM uses typo correction to help users find the product they're looking for.

REQUIRED EDITIONS
View supported products and editions.

Here are some search considerations to keep in mind.

Search terms support prefix matching, which is enabled by default and works alongside partial search. It helps locate products when your search term matches the beginning of a product name, product code, or product SKU. For example, typing “Think” finds “ThinkPro X1 Carbon” and typing “LP-X1” finds SKU “LP-X1C-2025”.

Prefix matching applies to search terms with at least 3 characters. It works on the Product Name, Product SKU, and Product Code fields, if they're marked as searchable. To make the fields searchable, see Configure Searchable Fields & Attributes.

Typo tolerance in search terms is supported, provided the search terms have three or more characters. Typo tolerance handles user input errors, such as misspellings and typographical errors, and it provides relevant search results. Typo tolerance can autocorrect a search term when the closest match is within 2 character corrections. For example, the search term “Coff” is autocorrected to “Coffee”. However, the search term “Cof” can't be autocorrected to Coffee because it takes more than 2 character corrections to reach Coffee.
You can enter a maximum of 1024 characters or 32 words in the search field as a search term per search.
EXAMPLE Acme sells a wide range of computers. Here are the different products they offer and their attributes. Only some of its fields and attributes are marked as searchable and indexed.
PRODUCT NAME (INDEXED FIELD)	STORAGE	RAM (INDEXED ATTRIBUTE)	DISPLAY SIZE (INDEXED ATTRIBUTE)	COLOR (INDEXED ATTRIBUTE)	GRAPHICS CARD
Laptop 1	256GB	16GB	15Inch	Red	16GB
Laptop 2	256GB	32GB	21Inch	Blue	16GB
Laptop 3	512GB	64GB	15Inch	Black	32GB
Laptop 4	512GB	64GB	21Inch	Silver	32GB
Desktop 1	256GB	16GB	15Inch	Red	16GB
Desktop 2	256GB	32GB	21Inch	Blue	16GB
Desktop 3	512GB	64GB	15Inch	Black	32GB
Desktop 4	512GB	64GB	21Inch	Silver	32GB
Supercomputer	1TB	256GB	24Inch	Gray	128GB

Here are some sample search terms and responses based on the indexed data.

SEARCH TERMS	RESPONSES	REASON
15Inch Laptop	
Laptop 1
Laptop 3
Desktop 1
Desktop 3
	The size field is indexed and all these products have at least 1 matching term (15Inch).
Desktop	
Desktop 1
Desktop 2
Desktop 3
Desktop 4
	The product name is indexed.
Gray Supercomputer	Supercomputer	Only one product matches the search terms.
Supercomptute	Supercomputer	The search term has more than 3 characters and there's a typo with less than 2 incorrect characters.
16GB	
Laptop 1
Desktop 1
	

The RAM attribute is indexed and these two products have a matching value.

Although 16GB also matches the graphics card for Laptop 2 and Desktop 2, they're not returned in the search because the Graphics Card attribute isn't indexed.


Lap	
Laptop 1
Laptop 2
Laptop 3
Laptop 4
	Prefix matching is enabled by default and matches the beginning of the product name, so this three-character term returns all products whose name starts with "Lap".
512GB	No results	The storage field isn't marked as searchable and isn't indexed.
