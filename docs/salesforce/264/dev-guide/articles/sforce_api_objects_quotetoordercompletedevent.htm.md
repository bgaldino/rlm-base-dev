---
page_id: sforce_api_objects_quotetoordercompletedevent.htm
title: QuoteToOrderCompletedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotetoordercompletedevent.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_platform_event.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# QuoteToOrderCompletedEvent

Notifies subscribers when the `/actions/standard/createOrderFromQuote` REST request is complete. If the
			request is successful, use this event to learn about the Order record. If the request
			isn’t successful, use this event to learn about the errors associated with the
			request. This object is available in API version 56.0 and later. 

		

## Supported Calls

			
			

`describeSObjects()`

		

		

## Supported Subscribers

			
			

					
					
					
						
							

							

						

					

					
						
							

							

						

						
							

							

						

						
							

							

						

						
							

							

						

						
							

							

						

					

				
| Subscriber | Supported? |
| --- | --- |
| Apex Triggers |  |
| Flows |  |
| Processes |  |
| Pub/Sub API |  |
| Streaming API (CometD) |  |

		

		

## Subscription Channel

			
			

`/event/QuoteToOrderCompletedEvent`

		

		

## Event Delivery Allocation Enforced

			
			

No

		

		

## Special Access Rules

			
			

This object is available with Revenue Cloud.

		

		

				
				
				
					
						

						

					

				

				
					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

					
						

						

: 

: 

: 

					

				

			
| Field | Details |
| --- | --- |
| CorrelationIdentifier | **Type** string **Properties** Nillable **Description** Reserved for future use. |
| EventUuid | **Type** string **Properties** Nillable **Description** A universally unique identifier (UUID) that identifies a platform event message. |
| HasErrors | **Type** boolean **Properties** Defaulted on create **Description** Contains `true` if errors occurred during the process; otherwise `false`. The default value is `false`. |
| OrderId | **Type** string **Properties** Nillable **Description** The ID of the order created from the quote. If the process failed, this field is null. |
| OrderNumber | **Type** string **Properties** Nillable **Description** The user-friendly, unique number assigned to the order created from the quote. |
| QuoteToOrderErrorDetailEvents | **Type** [QuoteToOrderErrDtlEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.platform_events.meta/platform_events/sforce_api_objects_quotetoordererrdtlevent.htm)[] **Properties** Nillable **Description** Contains a list of error messages and error codes if the request failed. |
| ReplayId | **Type** string **Properties** Nillable **Description** Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | **Type** string **Properties** Nillable **Description** The unique ID returned in the `actions/standard/createOrderFromQuote` response. Use this ID to identify the event for a specific request. |
