---
page_id: product_catalog_management_business_api.htm
title: Product Catalog Management Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_business_api.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Catalog Management Business APIs

Use primitive APIs of Product Catalog Management that serve catalog definitions to
        users or applications.

        
            

This table lists the available Product Catalog Management resources.

            

                    
                    
                    
                        
                            

                            

                        

                    

                    
                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                        
                            

                            

                        

                    

                
| Resource | Description |
| --- | --- |
| [`/connect/pcm/catalogs`](./connect_resources_get_catalogs.htm.md) (POST) | Retrieve, search, filter, or sort catalog records. |
| [`/connect/pcm/catalogs/catalogId`](./connect_resources_get_catalogs_by_ID.htm.md) (GET) | Retrieve details of catalog records based on a catalog ID. |
| [`/connect/pcm/catalogs/catalogId/categories`](./connect_resources_get_categories.htm.md) (GET) | Retrieve the root-level categories of a catalog based on a catalog ID, or subcategories based on a parent category. You can also search, filter, or sort the categories. |
| [`/connect/pcm/categories/categoryId`](./connect_resources_get_category_by_ID.htm.md) (GET) | Retrieve details of individual category records based on a category ID. |
| [`/connect/pcm/products`](./connect_resources_get_products.htm.md) (POST) | Retrieve products. You can also search, filter, or sort the products. |
| [`/connect/pcm/products/productId`](./connect_resources_get_product_by_ID.htm.md) (GET) | Retrieve details of individual product records or a bundle based on a product ID. |
| [`/revenue/product-catalog-management/product-classifications/details`](./connect_resources_product_classification.htm.md) (POST) | Retrieve the details for a list of product classification records. |
| [`/revenue/product-discovery/products/recommendations`](./connect_resources_product_recommendations.htm.md) (POST) | Get a list of recommended products based on your underlying business rules. |
| [`/revenue/product-configurator/rules/actions/execute`](./connect_resources_config_rules.htm.md) (POST) | This API is used in Product Catalog Management to disable rules, get product recommendations, and get message rules. |
| [`/connect/pcm/products/bulk`](./connect_resources_product_catalog_bulk_product_details.htm.md) (POST) | Retrieve details for multiple products. |
| [`/connect/pcm/products/variants`](./connect_resources_product_variants.htm.md) (POST) | Retrieve the variation product associated with one or more parent variant products. |
| `[/connect/pcm/index/configurations](./connect_resources_index_configuration.htm.md)` (GET, PUT) | Retrieve the saved index configurations. Additionally, you can persist the index configuration. |
| [`/connect/pcm/relatedRecords/entityName`](./connect_resources_related_records.htm.md) (POST) | Retrieve related ProductRampSegment or ProductUsageGrant records for Product2 object. |
| [`/connect/pcm/index/snapshots`](./connect_resources_snapshot_get.htm.md) (GET) | Retrieve the created snapshots and snapshot indexes. |
| [`/connect/pcm/index/deploy`](./connect_resources_snapshot_deploy.htm.md) (POST) | Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms. |
| [`/connect/pcm/index/setting`](./connect_resources_get_index_settings.htm.md) (GET, PATCH) | Fetch and update settings related to indexing and search. |
| [`/connect/pcm/index/error`](./connect_resources_get_index_errors.htm.md) (GET) | Get the count and details of the errors that occurred during the indexing process. |
| [`/connect/pcm/deep-clone`](./connect_resources_deep_clone.htm.md) (POST) | Copy related records of an object along with the main product record. |
| [`/connect/pcm/unit-of-measure/info`](./connect_resources_unit_of_measure_info.htm.md) (GET) | Get details about the unit of measure for a specific set of records. |
| [`/connect/pcm/unit-of-measure/rounded-data`](./connect_resources_unit_of_measure_rounded_data.htm.md) (POST) | Round off and scale decimal data for a specific set of fields. |

        

    

- 
**[Resources](./product_catalog_management_api_resources.htm.md)**  

Learn more about the available Product Catalog Management API resources.

- 
**[Request Bodies](./product_catalog_management_api_requests.htm.md)**  

Learn more about the available Product Catalog Management API request     bodies.

- 
**[Response Bodies](./product_catalog_management_api_responses.htm.md)**  

Learn more about the available Product Catalog Management API response     bodies.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)
