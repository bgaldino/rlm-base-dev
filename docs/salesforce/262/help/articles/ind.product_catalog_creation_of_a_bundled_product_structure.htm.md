---
article_id: ind.product_catalog_creation_of_a_bundled_product_structure.htm
title: Create a Bundled Product Structure
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_creation_of_a_bundled_product_structure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create a Bundled Product Structure

After you create a bundled product (static or configurable), use the Structure tab in the bundled product to add child components such as groups, products, and product classifications.

REQUIRED EDITIONS
View supported products and editions.
Product Bundle Components

Here's a product bundle structure with home furniture as the example, along with a description of each of the bundle components.

BUNDLE COMPONENTS	THINGS TO NOTE
Product Group (1)	
A group is mandatory in a configurable product bundle.
A group is optional in a static product bundle.
The root product can have multiple root groups or multiple products as its immediate level-one child components. A root group can have either multiple child groups, or multiple products, or a single product classification component as its immediate child component. A child group can contain a single product classification or multiple products.
A group under a configurable product bundle can contain multiple product components or one product classification component.
A group under a static product bundle can contain only multiple product components.

Product Components (2)	
You can add a product component under a product or under a product group.
A static product bundle can only have these child product components:
Static simple product
Static bundle product
A configurable product bundle can have these child product components:
Static simple product
Static bundle product
Configurable simple product
Configurable bundle product

Product Classification Components (3)	
You can add product classification components only under product groups.
You can add only one product classification under a product group.

When you add a product classification component to a group, all products that are based on the product classification are automatically added to the product bundle at run time. If you have multiple products based on a product classification, you don’t need to add each product as a product component to a group. Instead, you can add the product classification component that automatically adds all the products at run time.

To create a product bundle structure, follow these instructions:

Add Components to a Static Product Bundle
Static products are non-configurable at run time. That means you can’t add or remove child products, alter product quantities, or configure product attributes at run time. You can add product and product group components to a static product bundle. Product Group components are optional.
Add Components to a Configurable Product Bundle
You can add multiple groups, multiple product components, or one product classification component under a product group in configurable bundles.
Product Relationship Management in Agentforce Revenue Management
Bundle products consist of components such as groups, products, and product classifications. These components are related to each other through product relationships.
