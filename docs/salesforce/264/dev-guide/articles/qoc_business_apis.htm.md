---
page_id: qoc_business_apis.htm
title: Transaction Management Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/qoc_business_apis.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Business APIs

Use the Transaction Management Business APIs to fetch instant pricing data on a quote
    or an order, to create a quote, or to create an order.

    

This table lists the available Transaction Management resources.

    

        
        
        
          
            

            

          

        

        
          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

          
            

            

          

        

      
| Resource | Description |
| --- | --- |
| [`/connect/revenue-management/assets/actions/amend`](./connect_resources_assets_amend.htm.md) (POST) | Initiate and execute the amendment of a quote or an order. |
| [`/connect/revenue-management/assets/actions/cancel`](./connect_resources_assets_cancel.htm.md) (POST) | Initiate and execute the cancellation of an asset. |
| [`/connect/revenue-management/assets/actions/renew`](./connect_resources_assets_renew.htm.md) (POST) | Initiate and execute the renewal of an asset. |
| [`/industries/cpq/quotes/actions/get-instant-price`](./connect_resources_cpq_instant_pricing.htm.md) (POST) | Fetch instant pricing data on the quote or order line data grid and associated summary component. This API offers capabilities to either create a context or update the existing one based on the provided context ID. |
| [`/commerce/sales-orders/actions/place`](./connect_resources_place_order.htm.md) (POST) | Place orders with integrated pricing, configuration, and validation, and manage them throughout their entire lifecycle. Additionally, update an order or insert order items. |
| [`/commerce/quotes/actions/place`](./connect_resources_place_quote.htm.md) (POST) | Create a quote to discover and price products and services. Additionally, insert, update, or delete a quote line item. |
| [`/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-create`](./connect_resources_create_ramp_deal.htm.md) (POST) | Create a ramp deal for a customer on a product. Sales reps can use ramp deals to provide yearly deals to a customer, resulting in long-term revenue and customer relationship. A customer can create, update, or view multiple segments of periods for their subscription term with different attributes for each segment. |
| [`/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-update`](./connect_resources_update_ramp_deal.htm.md) (POST) | Modify a ramp deal in scenarios where a segment has updates such as quantity, discount, or date change. |
| [`/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-view`](./connect_resources_view_ramp_deal.htm.md) (GET) | View a ramp deal related to a quote line item or an order item. |
| [`/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-delete`](./connect_resources_delete_ramp_deal.htm.md) (POST) | Delete a ramp deal to convert a ramped product to include a single quote line item or order item. |
| [`/connect/rev/sales-transaction/actions/place`](./connect_resources_place_sales_transaction.htm.md) (POST) | Create a sales transaction, such as an order or a quote, with integrated pricing and configuration. Also, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax. |
| [`/connect/rev/sales-transaction/actions/clone`](./connect_resources_clone_sales_transaction.htm.md) (POST) | Create a clone of a sales transaction, such as a quote or an order. You can also clone a quote line item or an order item record with its related records and configurations. |
| [`/connect/rev/sales-transaction/actions/place-supplemental-transaction`](./connect_resources_place_supplemental_transaction.htm.md) (POST) | Create a supplemental order or change orders after they are submitted for processing, such as during the fulfillment process. |
| [`/connect/revenue/transaction-management/sales-transactions/actions/read`](./connect_resources_read_sales_transaction.htm.md) (POST) | Retrieve sales transaction data efficiently from an initialized or a hydrated context. |
| [`/global-promotions-management/promotions`](./connect_resources_create_promotions.htm.md) (GET, POST, PUT) | Get rewards based on a product selling model template. |
| [`/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions`](./connect_resources_get_eligible_promotions.htm.md) (POST) | Get eligible promotions for line items within a quote or an order. |
| [`/revenue/transaction-management/assets/actions/swap`](./connect_resources_initiate_swap.htm.md) (POST) | Exchange one product for another of equivalent or different value. The change is tracked as a swap request with linked asset actions and a net-zero order total where applicable. The API creates an amendment quote and order with order actions and quote action subtypes. |
| [`/revenue/transaction-management/assets/actions/upgrade`](./connect_resources_initiate_upgrade.htm.md) (POST) | Move a lower-tier product to a higher-tier product. The change is tracked as an upgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with order actions and quote action subtypes. |
| [`/revenue/transaction-management/assets/actions/downgrade`](./connect_resources_initiate_downgrade.htm.md) (POST) | Move to a lower-tier or lower-value product. The change is tracked as a downgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with downgrade-specific order actions and quote action subtypes. |

  

- 
**[Resources](./qoc_business_apis_rest_references.htm.md)**  

Learn more about the available Quote and Order Capture resources.

- 
**[Request Bodies](./qoc_api_requests.htm.md)**  

Learn more about the available API request bodies.

- 
**[Response Bodies](./qoc_api_responses.htm.md)**  

Learn more about the available response bodies.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)
