---
article_id: ind.product_catalog_management_essentials.htm
title: Product Catalog Management Essentials
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_management_essentials.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Product Catalog Management Essentials

Browse through this collection of terms, key objects, and key concepts. This collection is designed to give Salesforce admins, sales reps, and developers a clear and consistent understanding of Product Catalog Management (PCM) concepts and helps them navigate the PCM landscape.

Attributes
Attributes are the characteristics or properties that define products and product classifications. They are also referred to as Dynamic Attributes.
Attribute Categories
You can group attributes into logical groups called attribute categories. Attribute categories help users easily find and use the right attributes when they create product classifications. You can assign attributes to product classifications individually or through an attribute category.
Attribute Fields
Attribute Fields are special fields that affect how attributes behave at run time. You can update these field values when you edit product classification attributes or configure product attributes.
Attribute Inheritance
This process helps a product automatically obtains a set of dynamic attributes from its associated Product Classification. These attributes are available to the product even if you haven’t explicitly defined them.
Auto Save
Auto Save ensures that when a product is added from the catalog, it is automatically saved to the transaction line without requiring a manual save action. This ensures the transaction preview stays perfectly in sync and helps sales reps to continue browsing and adding products seamlessly.
Bundled Products
Bundled products are a group of products that are sold together as one unit. You can create static or dynamic bundled products. For static products, you can’t add or remove child products, alter product quantities, or configure product attributes at run time. For configurable products, you can add or remove child products, alter product quantities, and configure product attributes at run time.
Catalog
A catalog is a collection of the products that you sell, organized into categories for easier discoverability. You must create a catalog before you create catalog categories and assign products to the categories.
Category
Organize and group products in your catalog by creating catalog categories and catalog subcategories. Assign products to more than one catalog category and subcategory. The Categories tab shows a hierarchical view of categories that you can expand or collapse to show or hide the catalog subcategories.
Decision Tables
Advanced lookup tables can provide multiple matching outcomes for the same set of inputs. Decision tables can read rules from Salesforce objects and support various operators for each field within the object.
Dynamic Bundle
A bundle with complex hierarchy that's configurable at run time. A Dynamic bundle is a complex product hierarchy that starts with a root product and includes child products, product component groups, or product classes as children. The parent-child relationship can be multilevel.
Faceted Search
Facets offer an effective way to filter your search results, allowing you to quickly find the products you need by narrowing results based on selected criteria. For example, when searching for a phone, you can filter by attributes such as color, screen size, storage capacity, memory. Auto-faceting also displays relevant filters based on the selected category or search keyword.
Global Search
A search that helps users find desired products on the Product List page of Product Discovery.
Group Cardinality
Group cardinality defines the minimum and maximum number of child products that users can add in the run time across the group’s immediate child products.
Guided Product Selection
A feature that uses dynamic questions to identify requirements and show matching products. Users can click the Guide Me button on the Product List page to show personalized list of products. Available only in Salesforce Lightning Service Console.
Local Cardinality and Group Cardinality
A product bundle consists of multiple products sold as a single package. You can define cardinality for each product within the bundle, which ensures that the correct quantities are added to the cart.
Local Cardinality
Use local cardinality to determine whether a product component or products based on a product classification component are required, included in the bundle by default, and whether their quantities can be changed. When quantities can be changed, use local cardinality to set the default, minimum, and maximum quantities allowed in the product bundle. You can adjust quantities only if the price of the bundle doesn’t include the price of the product component or the product classification component.
Nested Bundle
The ability within Product catalog management for users to define a *Bundle* component that contains another existing *Bundle*, enabling modularity and reuse.
Nested Product Component Groups
It's a nesting of groups for better organisation of related products in a bundle.
Picklists
Attributes of the data type picklist can have multiple values. Picklists represent all possible values for such attributes. Users choose one of these values when they purchase a product. You must define picklists before you create attributes for the picklist data type.
Products
Products are all the items and services that you sell to customers. Products can also be nonsellable. There are two types of products: simple products and bundled products. Simple products don’t have an associated product hierarchy, while bundled products generally have one. Bundled products are a group of products that are sold together as one unit.
Product Category Qualification Rules
Product categories are a group of products that are categorized in a certain way for sale. Product category qualification rules evaluate the availability and eligibility of product categories during browsing.
Product Classifications
A product classification is a template that you can use to quickly define and create products. Product classifications hold a collection of dynamic attributes. You can reuse product classifications to create multiple products that are similar yet different. You can also organize your product catalog by building classification hierarchies with up to three levels of subclassification. Each subclassification inherits attributes from its parent, with the flexibility to include additional attributes as needed. This approach helps you create and manage related product classes more efficiently.
Product Component Attributes Override
You can override the attributes of product components in the context of the product bundle. This mechanism is called overriding the bundle component attributes. This mechanism doesn’t change the attributes on the product that’s used as a component. The changes remain localized to the bundle that you’re overriding the attributes in.
Product Detail Cache
Caching solution adds a caching layer to quickly retrieve product details. Product Details API uses the Product Catalog Management cache to access the frequently used product details without reloading them from the source every time.
Product Details Page (PDP)
This page shows detailed product information, such as product attributes, bundle hierarchy, and pricing, when a sales rep selects a product.
Product Discovery
Product Discovery offers a simple, structured browsing experience for sales reps and customers to efficiently identify the most suitable products. Product Catalog Management ensures a seamless product discovery experience for sales reps when browsing products on the Product List and Product Details pages.
Product Recommendations
Product recommendations are contextual, rule-based suggestions that surface directly in the user interface based on the current transaction. These recommendations are driven by predefined configuration rules and honor all existing qualification rules. Product recommendations help sales reps to identify and add compatible products directly from a recommendations list.
Product Relationships
A product can be related to another product. The relationship can be parent-child. For example, bundled products consist of components such as groups, products, and product classifications. These components are related to each other through product relationships.
Product Specification
Define product specification types unique to your industry. These types are linked to product specification record types, which are associated with the Product object. The record type determines whether a product is sold commercially.
Product Qualification Rules
Products are the items and services that you sell. Qualification rules evaluate the products’ availability and eligibility when users browse the products. By default, only qualified products are visible to users. You can view disqualified products as well, but you can’t purchase them.
Product Selling Model
Product selling models define how you sell products. The models can be one-time, term-defined, or evergreen. For example, a phone is sold one time or in a term of 12 months. However, the cellular data plan is billed monthly in an evergreen model until the user cancels the plan. Product selling model is an optional feature.
Product Variants
Product variants are a group of related products that share a common core design but differ in specific attributes, such as size or color. This structure simplifies catalog management and streamlines the browsing experience. Instead of scrolling through multiple individual product records, sales reps can view a single parent product and select the required configuration or options the customer needs.
Qualification Procedure Elements
Qualification Procedure Elements are the building blocks of expression sets. Product Catalog Management supports two elements.
EvaluateQualification: Evaluates rules of type qualification by looking up the decision tables based on objects that store qualification rules.
EvaluateDisqualification: Evaluates rules of type disqualification by looking up the decision tables based on objects that store disqualification rules.
Qualification Rules
Use qualification rules to define ‌customer eligibility and availability for products, or product categories. Eligibility and availability criteria include location, account attributes, and other related information.
A product or product category is qualified only if you’ve defined a qualification rule and the product or the product category meets the qualification.
Qualification Rule Object
The source object that contains the rules. The columns of the object act as criteria, and each row in the object represents a rule. You can look up these objects faster by creating a decision table for each object.
Simple Products
Products that don't have any parent-child relationship with other products. Their product type is None.
Static Bundle
A complex product hierarchy that starts with a root product and includes child products. The parent-child relationship can be multilevel. This type of bundle can't be configured at run time.
Transaction Preview
Transaction preview is an embedded panel that displays the current transaction in real time alongside the product catalog. It updates automatically as users add or remove products.
Visibility Rule
A visibility rule determines whether a product is displayed or hidden in the product list during product discovery. When constraint rules or disqualification rules apply to a specific product based on the current transaction, the visibility rule automatically hides the affected product from the default view.
