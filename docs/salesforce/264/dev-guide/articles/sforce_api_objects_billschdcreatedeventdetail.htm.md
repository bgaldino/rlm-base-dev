---
page_id: sforce_api_objects_billschdcreatedeventdetail.htm
title: BillSchdCreatedEventDetail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billschdcreatedeventdetail.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: sforce_api_objects_billingschedulecreatedevent.htm
fetched_at: 2026-11-23
---

# BillSchdCreatedEventDetail

Contains details about each order item in the `/commerce/invoicing/billing-schedules/actions/create` request and any errors that occurred while processing the request. This object is included in an `BillingScheduleCreatedEvent` message. You can't subscribe to the `BillSchdCreatedEventDetail` platform event directly. This object is available in API version 63.0 and later.

## Supported Calls

`describeSObjects()`

## Special Access Rules

This object is available when Billing is enabled in your org.

## Fields

### BillingScheduleId

- **Type**: reference
- **Properties**: Nillable
- **Description**: If the request was successful, this field contains the ID of the billing schedule for the order item.

This field is a relationship field.

- **Relationship Name**: BillingSchedule
- **Refers To**: BillingSchedule

### ErrorCode

- **Type**: string
- **Properties**: Nillable
- **Description**: If the request wasn’t successful, this field contains the error code.

### ErrorMessage

- **Type**: string
- **Properties**: Nillable
- **Description**: If the request wasn’t successful, this field contains the error message.

### EventUuid

- **Type**: string
- **Properties**: Nillable
- **Description**: A universally unique identifier (UUID) that identifies a platform event message.

### IsSuccess

- **Type**: boolean
- **Properties**: Defaulted on create
- **Description**: Indicates whether the request to create a billing schedule for the order item is successful (`true`) or not (`false`).

The default value is `false`.

### OrderItemId

- **Type**: reference
- **Properties**:
- **Description**: The ID of the order item used in the  `/actions/standardCreateBillingScheduleFromOrderItem` REST request.

This field is a relationship field.

- **Relationship Name**: OrderItem
- **Refers To**: OrderItem

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billschdcreatedeventdetail.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
