---
page_id: sforce_api_objects_quotetoordercompletedevent.htm
title: QuoteToOrderCompletedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotetoordercompletedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_platform_event.htm
fetched_at: 2026-06-09
---

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
| Apex Triggers | Yes |
| Flows | Yes |
| Processes | Yes |
| Pub/Sub API | Yes |
| Streaming API (CometD) | Yes |

## Subscription Channel

`/event/QuoteToOrderCompletedEvent`

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available with Revenue Cloud.

| Field | Details |
| --- | --- |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| HasErrors | Type  boolean  Properties  Defaulted on create  Description  Contains `true` if errors occurred during the process; otherwise `false`. The default value is `false`. |
| OrderId | Type  string  Properties  Nillable  Description  The ID of the order created from the quote. If the process failed, this field is null. |
| OrderNumber | Type  string  Properties  Nillable  Description  The user-friendly, unique number assigned to the order created from the quote. |
| QuoteToOrderErrorDetailEvents | Type  [QuoteToOrderErrDtlEvent](https://developer.salesforce.com/docs/atlas.en-us.262.0.platform_events.meta/platform_events/sforce_api_objects_quotetoordererrdtlevent.htm "HTML (New Window)")[]  Properties  Nillable  Description  Contains a list of error messages and error codes if the request failed. |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  The unique ID returned in the `actions/standard/createOrderFromQuote` response. Use this ID to identify the event for a specific request. |
