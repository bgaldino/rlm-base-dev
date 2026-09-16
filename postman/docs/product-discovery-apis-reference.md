# Salesforce Product Discovery APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Discovery (CPQ) APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Product Discovery APIs (`/connect/cpq/`) are the context-aware counterpart to the PCM APIs. All operations use POST, allowing a buyer context (account, pricing model, entitlements) to be passed in the request body. This makes them the preferred choice for storefront and quoting flows where catalog content must reflect what a specific customer can see and buy. The 264 snapshot also includes a Product Recommendations endpoint (available from API v67.0 / Release 262) under a separate `/revenue/product-discovery/` base path (see below).

---

## CATALOG APIs

### 1. List Catalogs (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/catalogs`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/catalogs`
- **Description:** Retrieve a paginated list of catalogs visible to the current buyer context. Unlike the PCM equivalent, this returns only catalogs the buyer is entitled to see based on account and pricing configuration. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique identifier value attached to the request and messages; accepts references to a particular transaction or event chain.
  - `limit` (Integer, Optional): Number of items to include in the response.
  - `offset` (Integer, Optional): Offset size from which to get the catalog count.
  - `orderBy` (String[], Optional): Sort order for the catalogs (e.g., `"name:asc"`, `"id:desc"`).
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.

---

### 2. Get Catalog (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/catalogs/{catalogId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/catalogs/{{defaultCatalogId}}`
- **Description:** Retrieve details of a specific catalog in the buyer context. Use when you need catalog metadata alongside entitlement and pricing context. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog. Use `{{defaultCatalogId}}`.
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique identifier for the request/event chain.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.

---

## CATEGORY APIs

### 3. List Categories (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/categories`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/categories`
- **Description:** List product categories and subcategories of a specified catalog, filtered to the buyer context. Filters out categories containing no entitled products for the given buyer context. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `catalogId` (String, Required): ID of the catalog.
  - `correlationId` (String, Optional): Unique identifier for the request/event chain.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.
  - `additionalContextData` (Array, Optional): Additional nodes added to the custom or default context definition. Max 10 nodes.
  - `contextDefinition` (String, Optional): API name of the custom context definition sent for context creation. Defaults to the default context definition.
  - `contextMapping` (String, Optional): Default context mapping of the context definition.
  - `customFields` (String[], Optional): Additional custom fields to include in the response.
  - `depth` (Integer, Optional — 61.0+): Levels of subcategories to retrieve beneath the parent category. Only applies when `parentCategoryId` is provided.
  - `enableQualification` (Boolean, Optional): Whether to enable qualification rules for the products. Default `true`.
  - `filter` (Object, Optional — 62.0+): Filters records; supported property is `isQualified` with operators `eq`, `in`, `contains` (`contains` not applicable when the **Use Indexed Data For Product Listing and Search** toggle is enabled).
  - `parentCategoryId` (String, Optional — 61.0+): ID of the parent category whose subcategories to retrieve. If omitted, only root-level categories are returned.
  - `qualificationProcedure` (String, Optional): API name of the custom qualification procedure. Defaults to the default qualification procedure.
  - `usePromotions` (Boolean, Optional — 66.0+): Fetch eligible promotions from Global Promotion Management (GPM) for the category and its products. Defaults to `true` if Promotion is enabled in the org, else `false`.

---

### 4. Get Category (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/categories/{categoryId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/categories/{{defaultCategoryId}}`
- **Description:** Retrieve the details of a specific category in the buyer context, including any category-level attributes or pricing rules. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Path Parameters:**
  - `categoryId` (String, Required): Salesforce ID of the category. Use `{{defaultCategoryId}}`.
- **Request Body Fields:**
  - `additionalContextData` (Object, Optional): Additional context nodes. Max 10 nodes.
  - `catalogId` (String, Optional): ID of the catalog. If specified, returns the list of offers from the catalog with pricing details related to the catalog.
  - `contextDefinition` (String, Optional): Custom context definition API name.
  - `contextMapping` (String, Optional): Default context mapping of the context definition.
  - `customFields` (String[], Optional): Category fields to retrieve in the response.
  - `correlationId` (String, Optional): Unique identifier for the request/event chain.
  - `enableQualification` (Boolean, Optional): Whether to enable qualification rules for the categories. Default `true`. The **Qualification Procedure** Setup toggle overrides this property.
  - `filter` (Object, Optional): Filters records; supported property is `name`. Supported operators: `eq`, `in`, `contains`, and (63.0+, Number/Date/Datetime only) `gt`, `lt`, `gte`, `lte`. Multiple criteria combine with `and`.
  - `qualificationProcedure` (String, Optional): Custom qualification procedure API name.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.
  - `usePromotions` (Boolean, Optional — 66.0+): Fetch eligible GPM promotions for the category and its products.

---

## PRODUCT APIs

### 5. List Products (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/products`
- **Description:** Retrieve a filtered, paginated list of products for a buyer session, for a specified catalog, category, or subcategory. Applies entitlements and optionally applies pricing context. Primary endpoint for populating product grids in quoting or eCommerce flows. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `priceBookId` (String, Required): ID of the price book to get prices from. If omitted, prices from the standard price book are fetched.
  - `additionalContextData` (Array, Optional): Additional context nodes. Max 10 nodes.
  - `additionalFields` (Map<String, Object>, Optional — 61.0+): Additional standard/custom Product2 fields to include in the response.
  - `catalogId` (String, Optional): ID of the catalog.
  - `categoryId` (String, Optional): ID of the category. If omitted, returns the list of offers from the catalog.
  - `contextDefinition` (String, Optional), `contextMapping` (String, Optional): Context definition/mapping overrides.
  - `correlationId` (String, Optional): Unique identifier of the request.
  - `currencyCode` (String, Optional): Required if multiple currencies are enabled for the org.
  - `cursor` (String, Optional): Unique ID representing the position of each product in the dataset.
  - `enablePricing` (Boolean, Optional): Default `true`. The **Pricing Procedure** Setup toggle overrides this property.
  - `enableQualification` (Boolean, Optional): Default `true`. The **Qualification Procedure** Setup toggle overrides this property.
  - `executeConfigurationRules` (Boolean, Optional — 67.0+): Whether to execute configuration rules.
  - `filter` (Object, Optional): Supported property `name`; operators `eq`, `in`, `contains` (`contains` not applicable when indexed search is enabled).
  - `includeCatalogDetails` (Boolean, Optional — 61.0+): Include catalog details in the response.
  - `limit` (Integer, Optional): Default `10`.
  - `offset` (Integer, Optional): Reserved for internal use.
  - `orderBy` (String[], Optional): Ascending (`asc`, default) or descending (`desc`). With indexed search enabled, sorting supports `name` only.
  - `pricingProcedure` (String, Optional), `qualificationProcedure` (String, Optional): Custom procedure overrides.
  - `productClassificationId` (String, Optional).
  - `relatedObjectFilters` (Array, Optional): Filter on related objects; supported object `ProductSpecificationRecType`, property `IsCommercial`, operator `eq`.
  - `transactionContextId` (String, Optional — 67.0+), `transactionId` (String, Optional — 67.0+).
  - `usePromotions` (Boolean, Optional — 66.0+): Fetch applicable GPM promotions per product.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.

---

### 6. Get Product (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/{productId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/products/{{defaultTermDefinedAnnualProductId}}`
- **Description:** Retrieve the full details of a single product — attributes, hierarchy, cardinality — in a buyer context. Returns pricing, attribute, and entitlement data specific to the account. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product.
- **Request Body Fields:**
  - `priceBookId` (String, Required): ID of the price book to fetch prices from.
  - `additionalContextData` (Array, Optional): Additional context nodes. Max 10 nodes.
  - `additionalFields` (Map<String, Object>, Optional — 61.0+): Additional Product2 / ProductAttributeDefinition fields. From 66.0, also supports requesting proration policy details (`ArePartialPeriodsAllowed`, `ProrationPolicyType`) per product selling model option via `ProductSellingModelOption.additionalFields.ProrationPolicy`.
  - `catalogId` (String, Optional), `contextDefinition` (String, Optional), `contextMapping` (String, Optional).
  - `correlationId` (String, Optional).
  - `currencyCode` (String, Optional): Required if multiple currencies are enabled for the org.
  - `enablePricing` (Boolean, Optional), `enableQualification` (Boolean, Optional): Default `true` each; Setup toggles can override.
  - `pricingProcedure` (String, Optional), `qualificationProcedure` (String, Optional).
  - `productSellingModelId` (String, Optional): ID of the product selling model.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.

---

### 7. Global Search (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/search`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/products/search`
- **Description:** Retrieve a list of products based on a search query or search term, within the buyer context. Leverages the PCM product index for fast keyword-based discovery when index data is enabled (see [PCM Index APIs](pcm-business-apis-reference.md)). This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `query` (Map<String, Object>, Required unless `searchTerm` is used): Structured query to search products (e.g., `{"textQuery": {"searchPhrase": "laptop"}}`).
  - `searchTerm` (String, Optional — 62.0+): Alternative to `query` — matches product names containing the term.
  - `catalogId` (String, Optional), `categoryId` (String, Optional): If `categoryId` is omitted, returns matching query offers from the catalog.
  - `contextDefinition` (String, Optional), `contextMapping` (String, Optional).
  - `correlationId` (String, Optional), `currencyCode` (String, Optional), `cursor` (String, Optional).
  - `additionalContextData` (Array, Optional): Max 10 nodes.
  - `additionalFields` (Map<String, Object>, Optional — 61.0+): Additional Product2 fields.
  - `enablePricing` (Boolean, Optional), `enableQualification` (Boolean, Optional): Default `true` each.
  - `executeConfigurationRules` (Boolean, Optional — 67.0+).
  - `filter` (Object, Optional): Supported property `name`; operators `eq`, `in`, `contains`, and (63.0+) `gt`, `lt`, `gte`, `lte`.
  - `includeCatalogDetails` (Boolean, Optional — 61.0+).
  - `limit` (Integer, Optional): Default `10`. `offset` (Integer, Optional): Reserved for internal use.
  - `orderBy` (String[], Optional).
  - `priceBookId` (String, Optional): If omitted, prices from the standard price book are fetched.
  - `pricingProcedure` (String, Optional), `productClassificationId` (String, Optional), `qualificationProcedure` (String, Optional).
  - `relatedObjectFilter` (Array, Optional): Supported object `ProductSpecificationRecType`, property `IsCommercial`, operator `eq`.
  - `transactionContextId` (String, Optional — 66.0+), `transactionId` (String, Optional — 66.0+).
  - `usePromotions` (Boolean, Optional — 66.0+).
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.

---

### 8. Bulk Product Details (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/bulk`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/products/bulk`
- **Description:** Retrieve context-aware details for multiple products in a single request. Equivalent to calling Get Product for each product individually, but in one round trip. Use when loading a pre-selected set of products for a quote line. This is a composite API for Product Discovery.
- **Available Version:** 61.0
- **Request Body Fields:**
  - `productData` (Array, Required): List of `{productId, productSellingModelId}` pairs.
  - `correlationId` (String, Optional), `priceBookId` (String, Optional): ID of the price book to fetch prices from.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.
  - `additionalContextData` (Array, Optional): Max 10 nodes.
  - `additionalFields` (Map<String, Object>, Optional): Additional Product2 fields; from 66.0 also supports proration policy details per product selling model option.
  - `contextDefinition` (String, Optional), `contextMapping` (String, Optional), `currencyCode` (String, Optional).
  - `enablePricing` (Boolean, Optional), `enableQualification` (Boolean, Optional): Default `true` each.
  - `pricingProcedure` (String, Optional), `qualificationProcedure` (String, Optional).

---

## GUIDED SELLING & QUALIFICATION APIs

### 9. Guided Selection (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/guided-selection`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/products/guided-selection`
- **Description:** Retrieve a list of products based on the response identifier or search terms of a guided selling flow. Guided selection captures user requirements to recommend suitable products. Guided selling rules must be configured in Revenue Cloud Setup.
- **Available Version:** 62.0
- **Request Body Fields:**
  - `catalogId` (String, Required), `priceBookId` (String, Required).
  - `guidedSelectionResponseId` (String, Required if `searchTerms` isn't specified): Response identifier of the guided selection.
  - `searchTerms` (Array, Required if `guidedSelectionResponseId` isn't specified): List of `{term, tags}`. If both properties are specified, `searchTerms` takes precedence.
  - `correlationId` (String, Optional), `limit` (Integer, Optional, default 10), `cursor` (String, Optional).
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.
  - `categoryId` (String, Optional), `contextDefinition` (String, Optional), `contextMapping` (String, Optional), `currencyCode` (String, Optional).
  - `enableQualification` (Boolean, Optional), `enablePricing` (Boolean, Optional): Default `true` each.
  - `executeConfigurationRules` (Boolean, Optional — 67.0+).
  - `filter` (Object, Optional): Supported property `name`; operators `eq`, `in`, `contains`.
  - `includeCatalogDetails` (Boolean, Optional), `orderBy` (String[], Optional), `productClassificationId` (String, Optional).
  - `pricingProcedure` (String, Optional), `qualificationProcedure` (String, Optional).
  - `transactionContextId` (String, Optional — 67.0+), `transactionId` (String, Optional — 67.0+).
  - `usePromotions` (Boolean, Optional — 66.0+).
  - `additionalContextData` (Array, Optional): Max 10 nodes.
  - `additionalFields` (Map<String, Object>, Optional): Additional Product2 fields.

---

### 10. Qualification (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/qualification`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/qualification`
- **Description:** Run the qualification procedure on a list of product IDs, evaluating whether the account qualifies for those products based on configured qualification rules. Returns eligible and ineligible products with reasons. Used in guided selling and promotional logic. This is a composite API for Product Discovery.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `productIds` (String[], Required): List of product IDs for the qualification check.
  - `userContext` (Object, Optional): User context details — account ID, contact ID, etc.
  - `additionalContextData` (Array, Optional): Max 10 nodes.
  - `catalogId` (String, Optional), `categoryId` (String, Optional).
  - `contextDefinition` (String, Optional), `contextMapping` (String, Optional).
  - `correlationId` (String, Optional).
  - `qualificationProcedure` (String, Optional): Custom qualification procedure API name. Defaults to the default qualification procedure.

---

## PRODUCT RECOMMENDATION APIs

### 11. Product Recommendations (POST) — v67.0 (Release 262)
- **HTTP Method:** POST
- **URI Path:** `/revenue/product-discovery/products/recommendations`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/product-discovery/products/recommendations`
- **Description:** Get a list of recommended products for the current quote or order, based on applicable constraint rules, along with recommendation reasons and compatibility indicators. Note this endpoint uses a different base path (`/revenue/product-discovery/`) than the rest of the Product Discovery composite APIs (`/connect/cpq/`).
- **Available Version:** 67.0
- **Request Body Fields:**
  - `catalogId` (String, Optional): Catalog to fetch recommended products from.
  - `priceBookId` (String, Optional): If omitted, prices from the standard price book are fetched.
  - `transactionId` (String, Optional): ID of the quote or order.
  - `currencyCode` (String, Optional): Required if multiple currencies are enabled; otherwise fetched from the account.
  - `cursor` (String, Optional).
  - `enablePricing` (Boolean, Optional, default `true`): Cannot be overridden to `true` in orgs where Salesforce Pricing is disabled.
  - `enableQualification` (Boolean, Optional, default `true`): Cannot be overridden to `true` in orgs where Qualification Procedure is disabled.
  - `filter` (Object, Optional): A single Filter Input object with a `criteria` array (`Filter Criteria Input[]`); each criterion has `property`, `operator` (`eq`, `in`, `contains`), and `value`. (The source properties table annotates the type as `Filter Input[]`, but every captured JSON example — including Filter Input's own — serializes `filter` as one object with the array at `criteria`.)
  - `limit` (Integer, Optional, default `10`).
  - `pricingProcedure` (String, Optional), `qualificationProcedure` (String, Optional).
  - `transactionContextId` (String, Optional).
  - `usePromotions` (Boolean, Optional, default `false`).
  - `userContext` (Object, Optional), `additionalContextData` (Array, Optional, max 10 nodes), `additionalFields` (Map<String, Object>, Optional).
  - `contextDefinition` (String, Optional), `contextMapping` (String, Optional).

---

## Key Differences: PCM vs. Product Discovery

| Aspect | PCM (`/connect/pcm/`) | Product Discovery (`/connect/cpq/`, `/revenue/product-discovery/`) |
|--------|----------------------|-------------------------------------|
| HTTP Method | GET and POST | POST only |
| Buyer Context | No | Yes — filters by entitlements |
| Pricing Applied | No | Yes — context-aware pricing |
| Best For | Admin catalog management | Quoting, storefront, eCommerce flows |
| Search | Via index APIs | Via `/products/search` |
| Guided Selling | Not available | Supported via `/guided-selection` |
| Recommendations | Not available | Supported via `/revenue/product-discovery/products/recommendations` (67.0+) |

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `68.0`) | Manual setup |
| `{{defaultAccountId}}` | Default account record ID | Setup Runner |
| `{{defaultCatalogId}}` | Default catalog record ID | Setup Runner |
| `{{defaultCategoryId}}` | Default category record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |

---

## Related Domains

- **[Product Catalog Management APIs](pcm-business-apis-reference.md)** — Direct catalog management (admin operations, index management, UoM).
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Configure complex bundles and options after product discovery.
- **[Pricing APIs](pricing-business-apis-v68.md)** — Price calculation once products are selected.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using discovered products.
- **[Context Service APIs](context-service-apis-reference.md)** — Define and manage the context definitions that power buyer-aware operations.

---

*Reference for: Agentforce Revenue Management APIs v68.0 (Winter '27) | Salesforce Revenue Cloud Developer Guide v264*
