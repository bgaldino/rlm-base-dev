---
page_id: sforce_api_objects_billingschedulecreatedevent.htm
title: BillingScheduleCreatedEvent
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingschedulecreatedevent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_pfrm_evnt_parent.htm
fetched_at: 2026-06-09
---

# BillingScheduleCreatedEvent

Notifies subscribers when the `/commerce/invoicing/billing-schedules/actions/create` request is complete.
This object is available in API version 63.0 and later.

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

`/event/billingschedulecreatedevent`

## Event Delivery Allocation Enforced

No

## Special Access Rules

This object is available when Billing is enabled.

## Fields

| Field | Details |
| --- | --- |
| BillingScheduleCreatedEventDetail | Type  [BillSchdCreatedEventDetail](./sforce_api_objects_billschdcreatedeventdetail.htm.md "Contains details about each order item in the /commerce/invoicing/billing-schedules/actions/create request and any errors that occurred while processing the request. This object is included in an BillingScheduleCreatedEvent message. You can't subscribe to the BillSchdCreatedEventDetail platform event directly. This object is available in API version 63.0 and later.")  Properties  Nillable  Description  One `BillingScheduleCreatedEventDetail` entry is created for each order item in the `BillingScheduleCreatedEvent` request. One `BillSchdCreatedEventDetail` entry is created for each error that occurred. |
| CorrelationIdentifier | Type  string  Properties  Nillable  Description  Reserved for future use. |
| EventUuid | Type  string  Properties  Nillable  Description  A universally unique identifier (UUID) that identifies a platform event message. |
| ReplayId | Type  string  Properties  Nillable  Description  Represents an ID value that is populated by the system and refers to the position of the event in the event stream. Replay ID values aren’t guaranteed to be contiguous for consecutive events. A subscriber can store a replay ID value and use it on resubscription to retrieve missed events that are within the retention window. |
| RequestIdentifier | Type  string  Properties  Nillable  Description  ID returned in the `CreateBillingScheduleFromOrderItem` response. Use this ID to identify the `BillingScheduleCreatedEvent` for a specific request. |

- **[BillSchdCreatedEventDetail](./sforce_api_objects_billschdcreatedeventdetail.htm.md)**  
  Contains details about each order item in the `/commerce/invoicing/billing-schedules/actions/create` request and any errors that occurred while processing the request. This object is included in an `BillingScheduleCreatedEvent` message. You can't subscribe to the `BillSchdCreatedEventDetail` platform event directly. This object is available in API version 63.0 and later.
