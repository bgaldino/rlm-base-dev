---
page_id: sforce_api_objects_placeordercompletedevent.htm
title: PlaceOrderCompletedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_placeordercompletedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_platform_event.htm
fetched_at: 2026-06-09
---

# PlaceOrderCompletedEvent

Notifies subscribers of an order being created or updated by invoking
the Place Order API or the Place Sales Transaction API. This object is available in
API version 63.0 and later.

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

`/event/PlaceOrderCompletedEvent`

## Event Delivery Allocation Enforced

Yes

## Fields

| Field | Details |
| --- | --- |
| AppUsageTypes | Type  string  Properties  Nillable  Description  Tag that represents the application that's using the order and determines how an order is processed. For example, the AppUsageTypes field value for Revenue Cloud orders is `RevenueLifecycleManagement`. |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| HasErrors | Type  boolean  Properties  Defaulted on create  Description  Indicates whether errors occurred when creating or updating the order (`true`) or not (`false`).  The default value is `false`. |
| OrderId | Type  reference  Properties  Nillable  Description  ID of the order record.  This field is a relationship field.  Relationship Name  Order  Refers To  Order |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  ID of the request that triggered the event. |
