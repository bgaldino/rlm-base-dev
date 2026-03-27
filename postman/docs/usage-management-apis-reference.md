# Salesforce Usage Management APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Usage Management APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Usage Management APIs provide visibility into metered usage across the Revenue Cloud lifecycle — from assets and orders to quotes and binding objects. Two new endpoints in Spring '26 (v66.0) add consumption traceability and usage product validation capabilities.

---

## USAGE DETAIL APIs

### 1. Asset Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/asset-management/assets/{assetId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/asset-management/assets/{{assetId}}/usage-details`
- **Description:** Retrieve usage consumption details for a specific asset. Returns metered usage records associated with the asset, including usage dimensions (e.g., GB, API calls), measurement periods, and consumption amounts. Use to surface usage data to customers or to troubleshoot unexpected billing amounts.
- **Available Version:** 59.0
- **Path Parameters:**
  - `assetId` (String, Required): Salesforce ID of the asset. Use `{{assetId}}`.

---

### 2. Order Item Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/sales-orders/line-items/{orderItemId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-orders/line-items/{orderItemId}/usage-details`
- **Description:** Retrieve usage details for a specific order line item. Returns the usage records linked to that order line, useful for verifying that consumption was correctly attributed to the right order component before billing runs.
- **Available Version:** 59.0
- **Path Parameters:**
  - `orderItemId` (String, Required): Salesforce ID of the order line item (OrderItem)

---

### 3. Quote Line Item Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/quotes/line-items/{quoteLineItemId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/quotes/line-items/{quoteLineItemId}/usage-details`
- **Description:** Retrieve usage details for a specific quote line item. Returns projected or actual usage records associated with a quote line, enabling usage-aware quote review and pricing estimates for usage-based products.
- **Available Version:** 59.0
- **Path Parameters:**
  - `quoteLineItemId` (String, Required): Salesforce ID of the quote line item (QuoteLineItem)

---

### 4. Binding Object Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/revenue/usage-management/binding-objects/{bindingObjectId}/actions/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/revenue/usage-management/binding-objects/{{bindingObjectId}}/actions/usage-details`
- **Description:** Retrieve usage details for a specific binding object. Binding objects represent the relationship between a usage resource and a subscription asset — they are the anchor point for usage attribution in complex multi-product accounts. Use this endpoint when usage must be traced at the binding level rather than the asset or order line level.
- **Available Version:** 61.0
- **Path Parameters:**
  - `bindingObjectId` (String, Required): Salesforce ID of the binding object. Use `{{bindingObjectId}}`.

---

## CONSUMPTION TRACEABILITY APIs — v66.0

### 5. Consumption Traceabilities (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/usage-management/consumption/actions/trace`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/revenue/usage-management/consumption/actions/trace`
- **Description:** Trace the full consumption lineage for a binding object over a specified date range. New in Spring '26 (v66.0). Returns a detailed audit trail showing how usage events were ingested, attributed to binding objects, and accumulated into billing-ready consumption records. Use for debugging consumption attribution issues or producing customer-facing usage statements.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `bindingObjectId` (String, Required): Salesforce ID of the binding object to trace. Use `{{bindingObjectId}}`.
  - `dateRange` (Object, Required): Date range for the trace query
    - `startDate` (String): Start date in ISO 8601 format (e.g., `"2026-01-01"`)
    - `endDate` (String): End date in ISO 8601 format (e.g., `"2026-03-26"`)

---

## USAGE PRODUCT VALIDATION APIs — v66.0

### 6. Usage Product Validation (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/usage-management/usage-products/actions/validate`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/revenue/usage-management/usage-products/actions/validate`
- **Description:** Validate that one or more products are correctly configured for usage-based billing. New in Spring '26 (v66.0). Checks that products have the required usage attributes (dimensions, metrics, binding relationships) before they are added to a quote or order. Returns validation results per product with specific error messages for misconfigured usage products.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `productIds` (Array of String, Required): Salesforce IDs of products to validate
  - `usageAttributes` (Object, Required): Expected usage configuration to validate against
    - `dimension` (String): The usage dimension (e.g., `"GB"`, `"UNIT"`, `"MINUTES"`)
    - `metric` (String): The usage metric type (e.g., `"DATA_CONSUMED"`, `"API_CALLS"`, `"ACTIVE_USERS"`)

---

## Usage Data Flow

Usage data in Revenue Cloud flows through the following stages:

```
1. Usage Events Ingested     → Raw consumption records received (via API or file upload)
2. Attribution               → Events attributed to binding objects and assets
3. Aggregation               → Consumption accumulated per billing period
4. Rating                    → Usage rated against rate cards (see Rate Management APIs)
5. Billing                   → Rated usage billed via invoice (see Billing APIs)
```

The Usage Management APIs provide visibility at steps 2–3 (attribution and aggregation). The [Rate Management APIs](rate-management-apis-reference.md) cover step 4, and the [Billing APIs](billing-business-apis-reference.md) cover step 5.

---

## Prerequisites

Usage Management APIs require the following to be configured in the org:

- Usage-based products (Platform Usage Resources / PURs) loaded via `insert_qb_rating_data`
- Rate cards loaded via `insert_qb_rates_data`
- Rating records activated via `activate_rating_records`
- `rates` and `rating` feature flags enabled in `cumulusci.yml`

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{assetId}}` | Asset record ID | Set by test scripts after order activation |
| `{{bindingObjectId}}` | Binding object record ID | Set by test scripts after order activation |

---

## Related Domains

- **[Rate Management APIs](rate-management-apis-reference.md)** — Rate plans and waterfall that price the usage captured by these APIs.
- **[Billing APIs](billing-business-apis-reference.md)** — Invoices and payments generated from rated usage.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Orders and assets that generate the usage records tracked here.
- **[Context Service APIs](context-service-apis-reference.md)** — Context definitions used to interpret usage dimensions in pricing.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
