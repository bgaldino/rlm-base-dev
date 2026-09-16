---
article_id: ind.product_catalog_configure_prodoct_catalog_management_cache.htm
title: Configure the Product Catalog Management Cache
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_prodoct_catalog_management_cache.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_set_up_product_catalog_management.htm
fetched_at: 2026-09-04
---

# Configure the Product Catalog Management Cache

Store frequently requested product details in a dedicated cache for faster retrieval. You can then access product details without reloading them from the source every time. When product details change, the system detects the updates and regenerates the cache. If a user requests information for a product that isn’t in the cache, the system fetches the information from the database and saves it to the cache for future requests.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To configure the product catalog management cache:	Product Catalog Management Designer with the Product Catalog Management permission set

Before you begin:

You have disabled Data Translation, see Set Up Data Translation in Product Catalog Management
From Setup, in the Quick Find box, enter Product Discovery, and then select Product Discovery Settings.
Enable product catalog management cache.

When product details change, the system automatically detects the updates and recursively identifies all impacted products. It then invalidates their cache, ensuring subsequent requests retrieve the latest information and regenerate the cache automatically.

IMPORTANT If your changes impact a small number of products, rely on the automated cache to detect and regenerate those records. If you import or update products in bulk, or if your changes impact a large number of products, use Refresh Existing Products or Cache All Products instead. These options let you manage cached product details manually so you see your changes immediately. The time to automatically regenerate the cache increases as the number of impacted products grows.
Manage Product Details in the Cache

Store frequently requested product details in a dedicated caching layer to ensure faster retrieval. Manage the cached product details by either refreshing, updating, or clearing the cache.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To manage product details in the cache:	Product Catalog Management Designer
From Setup, in the Quick Find box, enter Flows, and then select Flows.
Create a flow, and add Runtime_industries_epc_ProductCatalogCacheRefresh batch job as an action element.

For example, Create a Schedule-Triggered Flow. Add an Action element and edit the element to add Runtime_industries_epc_ProductCatalogCacheRefresh batch job.

To manage the product details, click the action element to view the cache management options. Select Clear Cache to empty the cache, Refresh Existing Products to refresh current records, or Cache All Products to sync all products from the database, including new ones. Use these options to resolve data discrepancies or see the latest product changes.

Save and activate the flow.

To check the flow status, from Setup, in the Quick Find box, find and select Monitor Workflow Services. For more information, see Monitor Your Batch Jobs

When a user requests information for a specific product, the system first checks the cache. If the details are found there, they are retrieved instantly. If not, the system fetches the information from the database and saves it to the cache, ensuring the data loads much faster for future requests.
