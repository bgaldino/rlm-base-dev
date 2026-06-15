---
article_id: ind.product_catalog_example_provide_a_localized_french_buying_experience.htm
title: "Example: Provide a Localized French Buying Experience"
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_example_provide_a_localized_french_buying_experience.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Example: Provide a Localized French Buying Experience

This example shows how data translation changes the runtime experience for French users. See how translated values appear in catalogs, categories, products, and search results. Deliver localized catalogs without duplicate configurations. Buyers benefit from intuitive search and browsing in their preferred language, reducing confusion and improving adoption.

Export translations

From Setup, export Product2, Product Category, and related PCM entities. The XLIFF file includes base English values, such as:


    <trans-unit id="catalog_hardware">
    <source>Hardware Catalog</source>
    <target></target>
    </trans-unit>
    <trans-unit id="category_laptops">
    <source>Laptops</source>
    <target></target>
    </trans-unit>
    <trans-unit id="product_laptop_pro">
    <source>Laptop Pro</source>
    <target></target>
    </trans-unit>
    <trans-unit id="desc_laptop_pro">
    <source>Powerful laptop for professionals</source>
    <target></target>
    </trans-unit>
    <trans-unit id="attr_color_black">
    <source>Black</source>
    <target></target>
    </trans-unit>
   
Add translations

Edit the XLIFF file and add French values in the <target> fields:


    <trans-unit id="catalog_hardware">
    <source>Hardware Catalog</source>
    <target>Catalogue de matériel</target>
    </trans-unit>
    <trans-unit id="category_laptops">
    <source>Laptops</source>
    <target>Ordinateurs portables</target>
    </trans-unit>
    <trans-unit id="product_laptop_pro">
    <source>Laptop Pro</source>
    <target>Ordinateur portable Pro</target>
    </trans-unit>
    <trans-unit id="desc_laptop_pro">
    <source>Powerful laptop for professionals</source>
    <target>Ordinateur puissant pour les professionnels</target>
    </trans-unit>
    <trans-unit id="attr_color_black">
    <source>Black</source>
    <target>Noir</target>
    </trans-unit>
   

Reimport the file and rebuild the index.

Display the localized catalog

Configure English and French as supported languages, with English as the default language.

If a user’s org is set to a supported language, values display in that language. If a user’s org is set to an unsupported language (for example, German), values display in the default language (English).

OBJECT	FIELD	ENGLISH (DEFAULT)	FRENCH	GERMAN
Catalog	Name	Hardware Catalog	Catalogue de matériel	Hardware Catalog
Category	Name	Laptops	Ordinateurs portables	Laptops
Product2	Name	Laptop Pro	Ordinateur portable Pro	Laptop Pro
Product2	Description	Powerful laptop for professionals	Ordinateur puissant pour les professionnels	Powerful laptop for professionals
Attribute (Picklist)	Color	Black	Noir	Black
NOTE If a user’s org language isn’t one of the configured supported languages, Product Discovery displays values in the default language.
Buyer’s experience in French

When a French user browses the catalog:

The catalog shows Catalogue de matériel.
The category shows Ordinateurs portables.
The product shows Ordinateur portable Pro.
Searching for portable returns the translated product.
Filters show Noir instead of Black.
Business impact

Admins can deliver localized catalogs without duplicate configurations. Buyers benefit from intuitive search and browsing in their preferred language, reducing confusion and improving adoption.
