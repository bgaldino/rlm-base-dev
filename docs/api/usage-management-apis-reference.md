# Salesforce Usage Management APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Usage Management APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Usage Management APIs provide visibility into metered usage across the Revenue Cloud lifecycle — from assets and orders to quotes and binding objects. Consumption traceability and usage product validation were introduced in v66.0 (Spring '26); usage product activation was introduced in v67.0 (Summer '26).

---

## USAGE DETAIL APIs

### 1. Asset Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/asset-management/assets/{assetId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/asset-management/assets/{{assetId}}/usage-details`
- **Description:** Retrieve usage consumption details for a specific asset — grants and resources for the product if rates aren't configured, or grants/resources plus any configured rates (including negotiated rates in case of a rate override) if they are. Does not return binding target rates; use Binding Object Usage Details for those.
- **Available Version:** 63.0
- **Path Parameters:**
  - `assetId` (String, Required): Salesforce ID of the asset. Use `{{assetId}}`.
- **Query Parameters:**
  - `effectiveDate` (String, Required): Date used to search for the applicable rate card entries.
  - `optionalFields` (Array of String, Optional): Custom fields to query on AssetRateCardEntry / AssetRateAdjustment.

---

### 2. Order Item Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/sales-orders/line-items/{orderItemId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/commerce/sales-orders/line-items/{orderItemId}/usage-details`
- **Description:** Retrieve usage details for a specific order line item — grants and resources for the product if rates aren't configured, or grants/resources plus any configured rates (including negotiated rates in case of a rate override) if they are. Does not return binding target rates; use Binding Object Usage Details for those.
- **Available Version:** 63.0
- **Path Parameters:**
  - `orderItemId` (String, Required): Salesforce ID of the order line item (OrderItem)
- **Query Parameters:**
  - `effectiveDate` (String, Optional): Date used to search for the applicable rate card entries.
  - `optionalFields` (Array of String, Optional): Custom fields to query on OrderItemRateCardEntry / OrderItemRateAdjustment.

---

### 3. Quote Line Item Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/quotes/line-items/{quoteLineItemId}/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/commerce/quotes/line-items/{quoteLineItemId}/usage-details`
- **Description:** Retrieve usage details for a specific quote line item — grants and resources for the product if rates aren't configured, or grants/resources plus any configured rates (including negotiated rates in case of a rate override) if they are. Does not return binding target rates; use Binding Object Usage Details for those.
- **Available Version:** 62.0
- **Path Parameters:**
  - `quoteLineItemId` (String, Required): Salesforce ID of the quote line item (QuoteLineItem)
- **Query Parameters:**
  - `effectiveDate` (String, Optional): Date used to search for the applicable rate card entries.
  - `optionalFields` (Array of String, Optional): Custom fields to query on QuoteLineRateCardEntry / QuoteLineRateAdjustment.

---

### 4. Binding Object Usage Details (GET)
- **HTTP Method:** GET
- **URI Path:** `/revenue/usage-management/binding-objects/{bindingObjectId}/actions/usage-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/usage-management/binding-objects/{{bindingObjectId}}/actions/usage-details`
- **Description:** Retrieve details of grants, resources, rates, and any configured policies for a specified binding object. Use to display binding object details during the selling journey, and after assetization on the selected binding objects. Supported binding objects: Account, Contract, BindingObjectCustomExt, or an Anchor Asset that isn't bound to a target.
- **Available Version:** 65.0
- **Path Parameters:**
  - `bindingObjectId` (String, Required): Salesforce ID of the binding object. Use `{{bindingObjectId}}`.
- **Query Parameters:**
  - `effectiveDate` (String, Required): Date filter, in `yyyy-MM-dd` format, used to retrieve the grants, rates, and applicable policies as of the specified date.

---

## CONSUMPTION TRACEABILITY APIs — v66.0

### 5. Consumption Traceabilities (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/usage-management/consumption/actions/trace`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/usage-management/consumption/actions/trace`
- **Description:** Get a comprehensive breakdown of overage charges and resource drawdown, enabling you to view information that's applicable to specific invoice lines. Introduced in v66.0 (Spring '26). Provides an automated, clear, and traceable breakdown of all charges with details of specific rates, tiers, and discounts.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `liableSummaryIds` (Array of String, Required): List of liable summary IDs to trace the consumption.

---

## USAGE PRODUCT VALIDATION APIs — v66.0

### 6. Usage Product Validation (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/usage-management/usage-products/actions/validate`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/usage-management/usage-products/actions/validate`
- **Description:** Validate cross-object relationships and business rules for usage-based products. Introduced in v66.0 (Spring '26). Returns validation results with errors and warnings.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `productIds` (Array of String, Required): List of product IDs to be validated. Maximum limit is 10 product IDs.
  - `startDate` (String, Optional): Start date of the date range in which all active records are validated.
  - `endDate` (String, Optional): End date of the date range in which all active records are validated.

---

## USAGE PRODUCT ACTIVATION APIs — v67.0

### 7. Usage Product Activation (POST) — v67.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/usage-management/usage-products/actions/activate`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/usage-management/usage-products/actions/activate`
- **Description:** Activate a usage product and its related records — usage resources, grants, policies, and rate card entries — in a single request. Introduced in v67.0 (Summer '26). Each request activates one product only (a request with more than one product returns `MAX_LIMIT_EXCEEDED`), and a maximum of 200 records (the product plus all associated child records) can activate per request. Records stay in Draft status until activation runs; if any record for the product fails to activate, the API rolls back all activations for that product. Records activate in dependency order — a child record never activates before its parent.
- **Available Version:** 67.0
- **Request Body Fields:**
  - `activationRequests` (Array of Object, Required): List of activation requests. Accepts only one entry — more than one returns `MAX_LIMIT_EXCEEDED`. Each entry contains:
    - `productId` (String, Required): ID of the Product2 record whose associated usage records are activated.
    - `usageResourceIds` (Array of String, Optional): List of usage resource IDs to activate for the given product. Activation extends to all design-time records linked to these resources (product usage grants, usage policies, units of measure, units of measure classes, rate card entries). If omitted, all usage records associated with the given product are activated.
  - `shouldValidateProductSetup` (Boolean, Optional): Whether to run product setup validation before activation. Default is `true`.

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
| `{{version}}` | API version (e.g., `68.0`) | Manual setup |
| `{{assetId}}` | Asset record ID | Set by test scripts after order activation |
| `{{bindingObjectId}}` | Binding object record ID | Set by test scripts after order activation |

---

## Related Domains

- **[Rate Management APIs](rate-management-apis-reference.md)** — Rate plans and waterfall that price the usage captured by these APIs.
- **[Billing APIs](billing-business-apis-reference.md)** — Invoices and payments generated from rated usage.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Orders and assets that generate the usage records tracked here.
- **[Context Service APIs](context-service-apis-reference.md)** — Context definitions used to interpret usage dimensions in pricing.

---

*Reference for: Agentforce Revenue Management APIs v68.0 (Winter '27) | Salesforce Revenue Cloud Developer Guide v264*
