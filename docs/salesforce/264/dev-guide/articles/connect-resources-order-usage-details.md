---
page_id: connect-resources-order-usage-details
title: Order Item Usage Details (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-order-usage-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-resources
legacy_page_id: connect_resources_order_usage_details.htm
fetched_at: 2026-11-25
---

# Order Item Usage Details (GET)

Get details of a usage-based product associated with an order item.

Here are the details that this API returns.

- Grants and resources for the product, if rates aren’t configured.

- Grants, resources, and any configured rates for the product. The rates are returned by the [Rate Plan (GET) API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_rate_plan.htm).

- Resources that include grants, if applicable, and any negotiated rates for the product in case of a rate override request.

This API doesn’t return binding target rates. Use the [Binding Object Usage Details API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_binding_object_details.htm) to retrieve binding target rates.

## Resource

```
/commerce/sales-orders/line-items/{orderItemId}/usage-details
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/sales-orders/line-items/{802SG000003vZ15YAE}/usage-details
```

```
https://{yourInstance}.salesforce.com/services/data​/v68.0/commerce/sales-orders/line-items/{802SG000003vZ15YAE}/usage-details?optionalFields=OrderItemRateCardEntry.MyCustomDate__c,OrderItemRateCardEntry.MyCustomNumber__c,OrderItemRateAdjustment.myCustomString__c
```

## Available Version

63.0

## HTTP Methods

GET

## Path Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `orderItemId` | String | ID of the order item. | Required | 63.0 |

## Query Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | String | Date that’s used to search for the applicable rate card entries. | Optional | 63.0 |
| `optionalFields` | String[] | Custom fields that you can use to query these objects. [OrderItemRateCardEntry](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_orderitemratecardentry.htm); or [OrderItemRateAdjustment](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_orderitemrateadjustment.htm). | Optional | 63.0 |

## Response Body for GET

[Usage Details](./connect-responses-usage-detail-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-order-usage-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
