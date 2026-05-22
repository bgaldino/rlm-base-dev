---
article_id: ind.product_catalog_local_cardinality_and_group_cardinality.htm
title: Define Quantity Limits for Bundled Products
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_local_cardinality_and_group_cardinality.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Define Quantity Limits for Bundled Products

For bundled products businesses can limit, or require, the quantity of items purchased. For example, an airline that offers up to two companion fares for each frequent flyer customer. In Product Catalog Management, use local and group cardinality to create these quantity limitation rules.

REQUIRED EDITIONS
View supported products and editions.
Local Cardinality

Local cardinality defines if a product component or products based on a product classification component are required, are included in the bundle by default, and whether their quantities can be changed. When the quantity can be changed, use local cardinality to define the default, minimum and maximum quantities of the product that are allowed in the product bundle.

Consider a scenario where you want to allow users to purchase up to two double beds. In this case, define the local cardinality with the minimum quantity as 1, the maximum quantity as 2, and the default quantity as 1. With this cardinality, if users enter quantity 3, they’re notified that they can add only up to two beds.

Group Cardinality

Group cardinality defines the minimum and maximum number of child components that users can add at run time. You can add a nested child group, a product classification, or multiple product components to a root group.

Consider a scenario where you have a group of 4 types of beds and you want to allow users to select a minimum of 1 bed and a maximum of 3 beds. In this case, define the group cardinality with the minimum components as 1 and the maximum components as 3.

/apex/HTViewHelpDoc?id=ind.Chunk773624560.htm#product_catalog_local_cardinality

/apex/HTViewHelpDoc?id=ind.Chunk1147392719.htm#product_catalog_group_cardinality
