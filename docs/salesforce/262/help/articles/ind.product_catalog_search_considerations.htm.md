---
article_id: ind.product_catalog_search_considerations.htm
title: Search Considerations When Using Indexed Data
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_search_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Search Considerations When Using Indexed Data

When users search for a product by using a search term, Product Catalog Management checks for an exact match to the search term. If it can’t find an exact match, PCM uses typo correction to help users find the product they’re looking for.

REQUIRED EDITIONS
View supported products and editions.

Here are some search considerations to keep in mind:

Search terms don’t support partial term matching such as prefix search. For example, if users search for ‘tel’, the search doesn't return all the records that start with tel such as television, telephone, telecommunication.
Typo tolerance in search terms is supported, provided the search terms have three or more characters. Typo tolerance handles user input errors such as misspellings and typographical errors, and provides relevant search results. Typo tolerance can autocorrect a search term when the closest match is within two character corrections. For example, the search term “Coff” is autocorrected to “Coffee”. However, the search term “Cof” can’t be autocorrected to Coffee, because it takes more than two character corrections to reach Coffee.
You can enter a maximum of 1024 characters or 32 words in the search field as a search term per search.
EXAMPLE Acme sells a wide range of computers. Here are the different products they offer and their attributes. Only some of its fields and attributes are marked as searchable and are indexed.
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
Supercomptute	Supercomputer	The search term has more than 3 characters and there’s a typo with less than 2 incorrect characters.
16GB	
Laptop 1
Desktop 1
	

The RAM attribute is indexed and these two products have a matching value.

Although 16GB also matches the graphics card for Laptop 2 and Desktop 2, they’re not returned in the search because the Graphics Card attribute isn’t indexed.


Lap	No results	

Partial term matching such as prefix search isn’t supported.

However, if a user searches for ‘Lapt’, the search results contain all the laptops because only 2 characters are missing and typo tolerance is supported.


512GB	No results	The storage field isn’t marked as searchable and isn’t indexed.
