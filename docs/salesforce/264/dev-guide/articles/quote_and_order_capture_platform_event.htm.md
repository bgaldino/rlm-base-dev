---
page_id: quote_and_order_capture_platform_event.htm
title: Transaction Management Platform Event
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_platform_event.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_overview.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Platform Event

Use the QuoteSaveEvent event to notify subscribers after saving of a quote is
  processed.

          
            

          

          
            

          

        

| Available in: Lightning Experience |
| --- |
| Available in all Salesforce orgs where the admin settings for products related to the use case are enabled. The Salesforce org must have a Revenue Management or Subscription Management license. |

  

- 
**[CreateAssetOrderEvent](./sforce_api_objects_createassetorderevent.htm.md)**  

Notifies subscribers that the process started by the `/actions/standard/createOrUpdateAssetFromOrder` or  `/actions/standard/createOrUpdateAssetFromOrderItem` 			request is complete. If the process is successful, use this event to learn about the new 			assets. If the request isn't successful, use this event to learn about the errors and 			how to fix them. This object is available in API version 55.0 and 		later.

- 
**[PlaceOrderCompletedEvent](./sforce_api_objects_placeordercompletedevent.htm.md)**  

Notifies subscribers of an order being created or updated by invoking 			the Place Order API or the Place Sales Transaction API. This object is available in 		API version 63.0 and later.

- 
**[QuoteSaveEvent](./sforce_api_objects_quotesaveevent.htm.md)**  

Notifies subscribers that the process started by the Place Quote or 			Place Sales Transaction API request is complete. If the process is successful, use this 			event to learn about the updated quote. If the request isn't successful, use this event 			to learn about the errors and how to fix them. This object is available in API 		version 60.0 and later.

- 
**[QuoteToOrderCompletedEvent](./sforce_api_objects_quotetoordercompletedevent.htm.md)**  

Notifies subscribers when the `/actions/standard/createOrderFromQuote` REST request is complete. If the 			request is successful, use this event to learn about the Order record. If the request 			isn’t successful, use this event to learn about the errors associated with the 			request. This object is available in API version 56.0 and later.
