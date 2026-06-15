---
article_id: ind.product_catalog_product_classifications.htm
title: Create Product Templates Using Product Classifications
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_classifications.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Product Templates Using Product Classifications

Product classifications are templates that organize your product catalog and streamline product creation. Define attributes once, and let subclassifications automatically inherit them, while still allowing you to manually override attributes as needed. Product classifications help you maintain data consistency and reduce repetitive manual tasks, allowing you to quickly define and launch products with shared characteristics.

REQUIRED EDITIONS
View supported products and editions.

Product classifications are attribute templates that you can reuse to quickly define and create products that share similar attributes. These classifications are required to assign attributes to products. Configure and override the inherited attributes for each product if necessary. You can also define and manage attribute properties, such as whether an attribute is required, optional, visible, or hidden.

Product subclassifications helps you organize your product catalog into a hierarchy of up to three levels, where a parent can have up to five child nodes at a given level. Subclassifications automatically inherit all attributes from their parent classification, while still allowing you to manually override attributes as needed. This functionality streamlines the creation and maintenance of related product classes, ensuring data consistency and reducing redundant assignments.

EXAMPLE

Autz, an automobile company that sells cars and uses product classifications to manage its catalog. Instead of creating each car model from scratch, Autz establishes a parent classification called Cars that includes common attributes like Engine and Wheels.

To handle specific vehicle types, Autz then creates subclassifications under the Cars parent, such as Sedan and SUV.

The Sedan subclassification automatically inherits the Engine and Wheels attributes from its parent. Autz can also add a unique attribute like Music System to it. When a new product, like Sedan-X, is associated with this subclassification, it receives all the attributes: Engine, Wheels, and Music System.

Similarly, the SUV subclassification also inherits the Engine and Wheels attributes from the parent. Autz can add a unique attribute like 4 Wheel Drive to it. When a new product, like SUV-Y, is associated with this subclassification, it receives all the attributes: Engine, Wheels, and 4 Wheel Drive.

This tiered system streamlines the product creation process. It ensures that common attributes are automatically applied, saving time and ensuring consistency across all car models.

Create a Product Classification
A product classification is a template that you use to create products with similar characteristics. Product classifications are the primary tool for assigning attributes to products.
Create a Product Subclassification
Create and manage product classification hierarchies up to three levels deep to enhance the product catalog’s structure. Subclassifications automatically inherit attributes from their parent, simplifying attribute management and reducing redundant work.
/apex/HTViewHelpDoc?id=ind.Chunk1756966362.htm#product_catalog_assign_attributes_to_a_product_classification

Include or Exclude Picklist Values in a Product Classification Attribute
For product classification attributes of the data type picklist, all the picklist values are included by default. To exclude specific picklist values and ensure they’re unavailable to products at run time, use Include or Exclude Picklist Values. Use the same functionality to include picklist values when your requirements change.
Explore Product Classification with an Example
Streamline the creation of a car product template by engineering a product classification hierarchy. Create a parent classification to automatically share attributes with child subclassifications, and curate valid options for specific models to reduce data entry errors.
