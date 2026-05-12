---
article_id: ind.product_catalog_product_catalog_management_personas.htm
title: Product Catalog Management Personas for Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_catalog_management_personas.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Product Catalog Management Personas for Agentforce Revenue Management

Explore the different types of users who work with Product Catalog Management and the permission sets they need.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
Create Users and Profiles

To begin, create users for Product Catalog Management. Then assign users the appropriate permission sets. To help you plan, refer to the Product Catalog Management personas table.

When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

PERSONA	DESCRIPTION	REQUIRED PERMISSION SETS
Salesforce Admin	Administers Product Catalog Management, integrates Product Catalog Management features, and assigns permission set groups to admins who handle specific areas; for example, a catalog admin. Only Salesforce admins can set up Specification Types.	Product Catalog Management Designer
Catalog Admin	Creates and manages attributes, attribute categories, product classifications, product classification attributes, product catalogs, and product categories.	Product Catalog Management Designer
Product Designer	Creates and manages products, product groups, product attributes, product components, product relationships, and Qualification Rules. The Product Designer also assigns products to product categories.	Product Catalog Management Designer
Product Discovery Admin	Manages features and settings. The Product Discovery Admin also customizes product browsing experience in Lightning App Builder and Experience Builder.	Product Catalog Management Designer
Sales Agent	Browses catalogs and products, and can optionally create quotes, and place orders.	Product Catalog Management Viewer
Partner Community User	Sells Product Catalog Management products to their customers via the partner community portal.	Product Catalog Management Partner Community User
Customer Community User	Purchases Product Catalog Management products from the customer community portal.	Product Catalog Management Customer Community User

Assign permission sets to your users based on their persona.

SEE ALSO
Manage Permission Set Assignments
View and Manage Users
Create or Clone Profiles
