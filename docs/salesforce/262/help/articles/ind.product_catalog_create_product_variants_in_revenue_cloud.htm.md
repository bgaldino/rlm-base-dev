---
article_id: ind.product_catalog_create_product_variants_in_revenue_cloud.htm
title: Create Product Variants in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_product_variants_in_revenue_cloud.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Product Variants in Agentforce Revenue Management

Use product variants to group related products that share a common identity but differ by specific characteristics. Instead of creating separate, disconnected entries in your catalog for every minor difference, variants help you organize these options logically under a single umbrella record.

REQUIRED EDITIONS
View supported products and editions.
Why Use Product Variants?

Managing a complex product catalog is overwhelming. Product variants offer several key benefits.

Streamlined catalog management: Avoid cluttering your catalog with hundreds of standalone entries. You can manage shared details in one place, such as the product descriptions or core features.

Accurate tracking and quoting: Every distinct variation maintains its own unique stock keeping unit (SKU) to ensure precise tracking for inventory, pricing, quoting, and revenue recognition.

Simplifed buyer experience: Users can configure a product by selecting the required options from a single interface, rather than searching through a massive catalog for a specific product.
Primary Components

A product variant structure consists of four primary components.

Variation Parent: The overarching record that groups the variations together. Variation parent is a structural template that holds shared information. A variation parent can’t be purchased. It only serves to organize its children.

Attributes: The defining characteristics that distinguish the variations from one another. Common attributes include size, color, storage capacity, or material.

Variation Attribute Set: A logical grouping of individual attributes (up to 5) that you apply to a variation parent. Rather than assigning individual attributes one by one, bundling them into a set ensures efficiency and structural consistency across your catalog.

Variation Product: The actual, purchasable record. It’s a child of the variation parent and represents one specific, unique combination of attribute values. Every variation product requires its own distinct SKU.

EXAMPLE : Selling a phone.

To understand how these constituents work together, consider a catalog offering a new smartphone.

Variation Parent: Phone (non-purchasable umbrella record)

Attributes: Individual traits such as memory (128 GB, 256 GB) and color (red, green)

Variation Attribute Set: Phone specifications (a grouping that contains the memory and color attributes, applied directly to the phone variation parent)

Variation Products: Based on the parent and the applied attribute set, the system houses the specific, purchasable child records. Each has its own SKU.

Phone - Red - 128 GB

Phone - Red - 256 GB

Phone - Green - 128 GB

Phone - Green - 256 GB

Turn On Product Variants
Enable product variation to create and manage variant products in Product Catalog Management and make them available for product discovery.
Create a Variation Attribute Set in Product Catalog Management
Group product attributes, such as size or color, into an attribute set to apply them to products efficiently. Because a product can have multiple attributes, applying a set to one or more products rather than assigning individual attributes provides consistency across products.
Create a Variation Parent
Group related product variants and simplify your catalog management. The parent variant stores shared attributes across a product’s different variants to eliminate redundant data entry for admins. Sales reps go to this parent variant in product discovery before selecting the exact specifications a customer needs.
Create a Variation Product
Define specific, sellable configurations of a parent product. Each variation product represents a unique set of attribute values and has its own product code.
