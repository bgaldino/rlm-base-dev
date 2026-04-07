# Salesforce Product Discovery APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Discovery (CPQ) APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Product Discovery APIs (`/connect/cpq/`) are the context-aware counterpart to the PCM APIs. All operations use POST, allowing a buyer context (account, pricing model, entitlements) to be passed in the request body. This makes them the preferred choice for storefront and quoting flows where catalog content must reflect what a specific customer can see and buy.

---

## CATALOG APIs

### 1. List Catalogs (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/catalogs`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/catalogs`
- **Description:** Retrieve a list of catalogs visible to the current buyer context. Unlike the PCM equivalent, this returns only catalogs the buyer is entitled to see based on account and pricing configuration.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `pageSize` (Integer, Optional): Number of catalog records to return (default: 100)

---

### 2. Get Catalog (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/catalogs/{catalogId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/catalogs/{{defaultCatalogId}}`
- **Description:** Retrieve details of a specific catalog in the buyer context. Use when you need catalog metadata alongside entitlement and pricing context.
- **Available Version:** 57.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog. Use `{{defaultCatalogId}}`.
- **Request Body Fields:**
  - Buyer context fields (Optional): Account ID, pricing context, etc.

---

## CATEGORY APIs

### 3. List Categories (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/categories`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/categories`
- **Description:** List product categories available to the buyer. Filters out categories containing no entitled products for the given buyer context.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `pageSize` (Integer, Optional): Number of category records to return (default: 100)

---

### 4. Get Category (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/categories/{categoryId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/categories/{{defaultCategoryId}}`
- **Description:** Retrieve the details of a specific category in the buyer context, including any category-level attributes or pricing rules.
- **Available Version:** 57.0
- **Path Parameters:**
  - `categoryId` (String, Required): Salesforce ID of the category. Use `{{defaultCategoryId}}`.
- **Request Body Fields:**
  - Buyer context fields (Optional)

---

## PRODUCT APIs

### 5. List Products (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/products`
- **Description:** Retrieve a filtered, paginated list of products for a buyer session. Applies entitlements and optionally applies pricing context. Primary endpoint for populating product grids in quoting or eCommerce flows.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `pageSize` (Integer, Optional): Number of products to return per page (default: 100)
  - `offset` (Integer, Optional): Pagination offset for subsequent pages
  - `filters` (Array, Optional): Filter criteria objects to narrow the result set (e.g., by category, attribute, or price range)

---

### 6. Get Product (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/{productId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/products/{{defaultTermDefinedAnnualProductId}}`
- **Description:** Retrieve the full details of a single product in a buyer context. Returns pricing, attribute, and entitlement data specific to the account.
- **Available Version:** 57.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product
- **Request Body Fields:**
  - Buyer context fields (Optional): Account, pricing context

---

### 7. Global Search (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/search`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/products/search`
- **Description:** Perform a full-text search across the product catalog within the buyer context. Leverages the PCM product index for fast keyword-based discovery. Requires the product index to be deployed (see [PCM Index APIs](pcm-business-apis-reference.md)).
- **Available Version:** 61.0
- **Request Body Fields:**
  - `query` (String, Required): Search string to match against product names, descriptions, and indexed fields
  - `pageSize` (Integer, Optional): Number of results to return (default: 100)
  - `filters` (Array, Optional): Additional filter criteria to narrow search results

---

### 8. Bulk Product Details (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/bulk`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/products/bulk`
- **Description:** Retrieve context-aware details for multiple products in a single request. Equivalent to calling Get Product for each product individually, but in one round trip. Use when loading a pre-selected set of products for a quote line.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `productIds` (Array of String, Required): List of Salesforce product record IDs to retrieve

---

## GUIDED SELLING & QUALIFICATION APIs

### 9. Guided Selection (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/products/guided-selection`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/products/guided-selection`
- **Description:** Execute a guided selling flow to recommend products based on account characteristics and buyer-provided criteria. Guided selling rules must be configured in Revenue Cloud Setup. Returns a filtered, ranked product list based on the criteria.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `accountId` (String, Required): Salesforce ID of the buyer account. Use `{{defaultAccountId}}`.
  - `criteria` (Object, Required): Key-value pairs representing the buyer's answers to guided selling questions (e.g., `{"industry": "Technology"}`)

---

### 10. Qualification (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/qualification`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/qualification`
- **Description:** Evaluate whether an account qualifies for specific products or promotions based on configured qualification rules. Returns a qualification result indicating eligible and ineligible products with reasons. Used in guided selling and promotional logic.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `accountId` (String, Required): Salesforce ID of the account to evaluate. Use `{{defaultAccountId}}`.
  - `qualificationCriteria` (Object, Required): Criteria object specifying the qualification type and parameters
    - `type` (String): Qualification type — e.g., `"ACCOUNT_BASED"`, `"PRODUCT_BASED"`

---

## Key Differences: PCM vs. Product Discovery

| Aspect | PCM (`/connect/pcm/`) | Product Discovery (`/connect/cpq/`) |
|--------|----------------------|-------------------------------------|
| HTTP Method | GET and POST | POST only |
| Buyer Context | No | Yes — filters by entitlements |
| Pricing Applied | No | Yes — context-aware pricing |
| Best For | Admin catalog management | Quoting, storefront, eCommerce flows |
| Search | Via index APIs | Via `/products/search` |
| Guided Selling | Not available | Supported via `/guided-selection` |

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{defaultAccountId}}` | Default account record ID | Setup Runner |
| `{{defaultCatalogId}}` | Default catalog record ID | Setup Runner |
| `{{defaultCategoryId}}` | Default category record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |

---

## Related Domains

- **[Product Catalog Management APIs](pcm-business-apis-reference.md)** — Direct catalog management (admin operations, index management, UoM).
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Configure complex bundles and options after product discovery.
- **[Pricing APIs](pricing-business-apis-v66.md)** — Price calculation once products are selected.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using discovered products.
- **[Context Service APIs](context-service-apis-reference.md)** — Define and manage the context definitions that power buyer-aware operations.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
