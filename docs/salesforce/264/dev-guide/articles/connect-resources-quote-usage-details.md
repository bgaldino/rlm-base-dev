---
page_id: connect-resources-quote-usage-details
title: Quote Line Item Usage Details (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-quote-usage-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-resources
legacy_page_id: connect_resources_quote_usage_details.htm
fetched_at: 2026-11-25
---

# Quote Line Item Usage Details (GET)

Get details of a usage-based product associated with a quote line item.

Here are the details that this API returns.

- Grants and resources for the product, if rates aren’t configured.

- Grants, resources, and any configured rates for the product. The rates are returned by the [Rate Plan (GET) API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_rate_plan.htm).

- Resources that include grants, if applicable, and any negotiated rates for the product in case of a rate override request.

This API doesn’t return binding target rates. Use the [Binding Object Usage Details API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_binding_object_details.htm) to retrieve binding target rates.

## Resource

```
/commerce/quotes/line-items/{quoteLineItemId}/usage-details
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/quotes/line-items/{0QLXXXXXXXXXXXABC}/usage-details
```

## Available Version

62.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | String | Date that’s used to search for the applicable rate card entries. | Optional | 62.0 |
| `optionalFields` | String[] | Custom fields that you can use to query these objects. [QuoteLineRateCardEntry](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotelineratecardentry.htm); or [QuoteLineRateAdjustment](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotelinerateadjustment.htm). | Optional | 62.0 |

## Response Body for GET

[Usage Details](./connect-responses-usage-detail-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-quote-usage-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
