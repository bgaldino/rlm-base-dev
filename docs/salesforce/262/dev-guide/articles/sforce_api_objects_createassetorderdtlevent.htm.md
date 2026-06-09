---
page_id: sforce_api_objects_createassetorderdtlevent.htm
title: CreateAssetOrderDtlEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_createassetorderdtlevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: sforce_api_objects_createassetorderevent.htm
fetched_at: 2026-06-09
---

# CreateAssetOrderDtlEvent

Contains information about an attempt to create or update an asset as a
result of `/actions/standard/createOrUpdateAssetFromOrder`. If the request was
successful, the event shows information about the asset. If the request failed, the
event shows error information. This object is included in an `CreateAssetOrderEvent` message. You can't subscribe to
`CreateAssetOrderDtlEvent` directly. This object is
available in API version 55.0 and later.

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

`/event/CreateAssetOrderDtlEvent`

## Special Access Rules

This object is available if Revenue Cloud is installed in your org. Users must have Read
access on this event to receive or view event notifications.

## Fields

| Field | Details |
| --- | --- |
| AssetId | Type  reference  Properties  Nillable  Description  The ID of the asset that was created or updated.  This field is a relationship field.  Relationship Name  Asset  Relationship Type  Lookup  Refers To  Asset |
| ErrorCode | Type  string  Properties  Nillable  Description  Reference code for the type of error that occurred. |
| ErrorMessage | Type  string  Properties  Nillable  Description  Information about the error that occurred after the request was made. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| IsSuccess | Type  boolean  Properties  Defaulted on create  Description  Indicates whether the request to create the asset for the order item was successful (true) or not (false).  The default value is `false`. Available in API version 61.0 and later. |
| OrderItemId | Type  reference  Properties    Description  The ID of the order item used in the request. Available in API version 61.0 and later.  This field is a relationship field.  Relationship Name  OrderItem  Relationship Type  Lookup  Refers To  OrderItem |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
