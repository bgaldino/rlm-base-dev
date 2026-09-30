---
article_id: release-notes.rn_product_catalog_management.htm
title: Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_catalog_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Product Catalog Management

Set attribute display orders across levels to guide reps through configurations, and easily convert simple products into bundles without creating records. Replace the generic cog icon with a clear text button, and hide the Add button to prevent incorrect selections. Automate cache invalidation to maintain accurate product details, and cache list prices for instant updates. Quickly locate items by typing any part of a Product Name, Product Code, or Product SKU by using prefix and partial search.

Simplify Product Configuration with Custom Attribute and Category Ordering
Help your sales reps navigate complex configurations by arranging attribute categories and attributes in a logical sequence. Previously, you couldn’t control the display order of attribute categories, and attributes appeared alphabetically by name. You can now set or change the display order at the Product Classification, Product Subclassification, or Product level. Products inherit the ordering from their classification, and sales reps see the sequence in the Configurator UI.
Guide Sales Reps Through Product Setup with Dynamic UI Controls
Give your sales reps a clear starting point for configuring products by replacing the generic cog wheel icon with a custom text button. A text button provides clear, immediate direction that is easier to spot than the standard icon. You can also hide the Add button for static or configurable products or both, which prevents sales reps from adding products incorrectly. With UI and performance enhancements, product discovery is more intuitive, and you can track the progress of adding or deleting a product.
Discover Products Faster by Using Price Book Filters
When browsing large catalogs with minimal price book overlap, you could encounter situations where no products or only a few products appeared. With price book filtering, you can now see complete product lists when browsing catalogs. This early filtering retrieves only products associated with the selected price book, so sales reps see relevant results without wading through the full catalog.
Find Products with Prefix Matching and Partial Search
Index and Search now support prefix matching for Product Name or Product Code, or Product SKU fields when marked as searchable. For more flexibility, partial search helps sales reps find products by typing any portion of Product Code or Product SKU, including the beginning, middle, or end, without needing exact formatting or delimiters.
See Instant Updates in Product Discovery While Building Quotes
Add or remove products with instant feedback as you build a quote in Product Discovery. Product Discovery uses optimistic UI patterns when Transaction Preview, Configuration Rules, Product Recommendations, and Auto Save settings is turned on. Badges highlight products added to prevent duplicate selections. Quote totals and transaction previews refresh in the background without blocking your page. Previously, sales reps waited for loading indicators to complete after every product selection, which slowed down multi-product quoting.
Get Accurate Product Details with Automated Product Cache Management
Automatically invalidate stale cache data and retrieve up-to-date product information whenever product details change. Product Catalog Management Cache recursively identifies all impacted products and clears their cached data. Subsequent requests retrieve updated details instantly without manual cache refreshes or administrative intervention.
Get Faster Product Pricing with List Price Caching
Retrieve product details and pricing faster when building quotes. Product Catalog Management now stores list prices from price book entries alongside product details in the cache. Pricing is read directly from the cache instead of resolved through a pricing procedure, providing sales reps with immediate pricing updates.
Changed Connect REST APIs in Product Catalog Management
Present a product's attribute categories in a consistent, predetermined order. The single and bulk Product Detail APIs now return the display sequence of each attribute category in the response.
runtime_industries_cpq Namespace
Work with product variations and units of measure during product discovery and selection. The runtime_industries_cpq namespace includes new classes and properties that represent a product's variation attributes, variation class, child variations, and units of measure.
