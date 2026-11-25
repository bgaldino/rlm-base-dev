---
page_id: quote-and-order-capture-platform-event
title: Transaction Management Platform Event
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-platform-event.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-overview
legacy_page_id: quote_and_order_capture_platform_event.htm
fetched_at: 2026-11-25
---

# Transaction Management Platform Event

Use the QuoteSaveEvent event to notify subscribers after saving of a quote is processed.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in all Salesforce orgs where the admin settings for products related to the use case are enabled. The Salesforce org must have a Revenue Management or Subscription Management license. |

These events are documented in the [Platform Events Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/platform_events_intro.htm).

- 

[CreateAssetOrderEvent](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/sforce_api_objects_createassetorderevent.htm)

- 

[CreateAssetOrderDtlEvent](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/sforce_api_objects_createassetorderdtlevent.htm)

- 

[PlaceOrderCompletedEvent](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/sforce_api_objects_placeordercompletedevent.htm)

- 

[QuoteToOrderCompletedEvent](https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/sforce_api_objects_quotetoordercompletedevent.htm)

- 

**[QuoteSaveEvent](./sforce-api-objects-quotesaveevent.md)**

Notifies subscribers that the process started by the Place Quote or Place Sales Transaction API request is complete. If the process is successful, use this event to learn about the updated quote. If the request isn’t successful, use this event to learn about the errors and how to fix them. This object is available in API version 60.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/quote-and-order-capture-platform-event.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
