# Salesforce Product Catalog Management (PCM) APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Catalog Management (PCM) APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The PCM APIs provide direct catalog access with standard REST semantics (GET/POST/PUT/PATCH). For context-aware, buyer-session-scoped catalog operations, see the [Product Discovery APIs](product-discovery-apis-reference.md), which use POST for all operations and apply context filters, entitlements, and pricing rules.

---

## CATALOG APIs

### 1. List Catalogs (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/catalogs`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/catalogs`
- **Description:** Retrieve a paginated list of all product catalogs in the org.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `pageSize` (Integer, Optional): Number of records to return per page (default: 100)
  - `offset` (Integer, Optional): Pagination offset
  - `q` (String, Optional): Search query string to filter catalogs by name

---

### 2. Get Catalog (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/catalogs/{catalogId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/catalogs/{{defaultCatalogId}}`
- **Description:** Retrieve details of a specific product catalog by its Salesforce record ID.
- **Available Version:** 57.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog record. Use `{{defaultCatalogId}}` from the Setup Runner.

---

## CATEGORY APIs

### 3. List Categories (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/catalogs/{catalogId}/categories`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/catalogs/{{defaultCatalogId}}/categories`
- **Description:** List all categories belonging to a specific catalog.
- **Available Version:** 57.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog. Use `{{defaultCatalogId}}`.

---

### 4. Get Category (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/categories/{categoryId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/categories/{{defaultCategoryId}}`
- **Description:** Retrieve details of a specific product category by its Salesforce record ID.
- **Available Version:** 57.0
- **Path Parameters:**
  - `categoryId` (String, Required): Salesforce ID of the category record. Use `{{defaultCategoryId}}` from the Setup Runner.

---

## PRODUCT APIs

### 5. List Products (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products`
- **Description:** Retrieve a paginated, filterable list of products from the catalog. Supports sorting and filter criteria.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `pageSize` (Integer, Optional): Number of records to return (default: 100)
  - `offset` (Integer, Optional): Pagination offset
  - `filters` (Array, Optional): Array of filter objects to narrow results
  - `sortBy` (String, Optional): Field to sort results by (e.g., `"Name"`)
  - `sortOrder` (String, Optional): Sort direction — `"ASC"` or `"DESC"`

---

### 6. Get Product (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/products/{productId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}`
- **Description:** Retrieve the full details of a single product by its Salesforce record ID.
- **Available Version:** 57.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product. Use `{{defaultTermDefinedAnnualProductId}}` or another product variable from the Setup Runner.

---

### 7. Bulk Product Details (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/bulk`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products/bulk`
- **Description:** Retrieve full product details for multiple products in a single request. More efficient than individual Get Product calls when loading several products at once.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `productIds` (Array of String, Required): List of Salesforce product record IDs

---

### 8. Product Related Records (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/{productId}/related-records`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}/related-records`
- **Description:** Retrieve related records for a product, such as variants and bundles. Use `relationshipTypes` to specify which relationship types to include.
- **Available Version:** 59.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product
- **Request Body Fields:**
  - `relationshipTypes` (Array of String, Required): Relationship types to retrieve. Supported values: `"VARIANTS"`, `"BUNDLES"`

---

### 9. Product Classification Details (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/classification`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products/classification`
- **Description:** Retrieve classification details — including the product hierarchy and attribute assignments — for one or more products. New in Spring '26 (v66.0).
- **Available Version:** 66.0
- **Request Body Fields:**
  - `productIds` (Array of String, Required): List of Salesforce product record IDs
  - `includeHierarchy` (Boolean, Optional): When `true`, returns the full classification hierarchy for each product (default: `true`)

---

### 10. Deep Clone Product (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/{productId}/actions/deep-clone`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}/actions/deep-clone`
- **Description:** Create a full deep copy of a product, including its attributes and relationships. Useful for creating product variants or templates.
- **Available Version:** 59.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product to clone
- **Request Body Fields:**
  - `cloneName` (String, Required): Name for the cloned product
  - `cloneAttributes` (Boolean, Optional): Include product attributes in the clone (default: `true`)
  - `cloneRelationships` (Boolean, Optional): Include product relationships (bundles, variants) in the clone (default: `true`)

---

## INDEX APIs

### 11. Index Configuration Collection (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/configurations`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/configurations`
- **Description:** Retrieve the current product index configurations. The product index drives search performance in Product Discovery APIs.
- **Available Version:** 61.0

---

### 12. Update Index Configuration (PUT)
- **HTTP Method:** PUT
- **URI Path:** `/connect/pcm/index/configurations`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/configurations`
- **Description:** Replace the full set of product index configurations. Use to define which fields are included in the search index.
- **Available Version:** 61.0
- **Request Body Fields:**
  - `indexConfigurations` (Array, Required): Array of index configuration objects, each with:
    - `id` (String): Configuration ID
    - `name` (String): Configuration name
    - `fields` (Array of String): Fields to include in the index (e.g., `["Name", "Description", "SKU"]`)

---

### 13. Index Setting (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/setting`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/setting`
- **Description:** Retrieve global index settings including whether indexing is enabled and the auto-index frequency.
- **Available Version:** 61.0

---

### 14. Update Index Setting (PATCH)
- **HTTP Method:** PATCH
- **URI Path:** `/connect/pcm/index/setting`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/setting`
- **Description:** Update global product index settings. Use to enable/disable automatic indexing or change the indexing frequency.
- **Available Version:** 61.0
- **Request Body Fields:**
  - `indexingEnabled` (Boolean, Optional): Enable or disable product indexing
  - `autoIndexFrequency` (String, Optional): Frequency for automatic re-indexing — `"DAILY"`, `"WEEKLY"`, or `"MANUAL"`
  - `batchSize` (Integer, Optional): Number of products to process per indexing batch

---

## SNAPSHOT APIs

### 15. Snapshot Collection (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/snapshots`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/snapshots`
- **Description:** List all available product index snapshots. Snapshots represent point-in-time captures of the index that can be deployed to production.
- **Available Version:** 61.0

---

### 16. Deploy Snapshot (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/index/snapshots/{snapshotId}/actions/deploy`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/snapshots/{snapshotId}/actions/deploy`
- **Description:** Deploy a specific index snapshot. Snapshots must be deployed before product search reflects catalog changes.
- **Available Version:** 61.0
- **Path Parameters:**
  - `snapshotId` (String, Required): ID of the snapshot to deploy
- **Request Body Fields:**
  - `options` (Object, Optional): Deployment options
    - `deploymentStrategy` (String): Strategy to use — `"INCREMENTAL"` (only changed records) or `"FULL"` (rebuild entire index)

---

### 17. Snapshot Index Error (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/snapshots/{snapshotId}/errors`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/index/snapshots/{snapshotId}/errors`
- **Description:** Retrieve any errors that occurred during a snapshot deployment. Use to diagnose failed or partially-failed deploys.
- **Available Version:** 61.0
- **Path Parameters:**
  - `snapshotId` (String, Required): ID of the snapshot to check for errors

---

## UNIT OF MEASURE APIs

### 18. Unit of Measure Info (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/unit-of-measure`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/unit-of-measure`
- **Description:** Retrieve metadata about all units of measure (UoM) configured in the org. UoMs define how product quantities are measured and rounded.
- **Available Version:** 59.0

---

### 19. Unit of Measure Rounded Data (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/unit-of-measure/actions/round`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/pcm/unit-of-measure/actions/round`
- **Description:** Calculate the rounded quantity for a given value based on a specified unit of measure and precision. Use to ensure quantities conform to UoM rounding rules before placing orders.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `quantity` (Decimal, Required): The raw quantity value to round
  - `unitOfMeasure` (String, Required): The UoM code to apply (e.g., `"LITRE"`, `"EACH"`, `"GB"`)
  - `decimalPlaces` (Integer, Required): Number of decimal places to round to

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{defaultCatalogId}}` | Default catalog record ID | Setup Runner |
| `{{defaultCategoryId}}` | Default category record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Context-aware, buyer-session-scoped catalog access. Uses PCM data but applies entitlements, pricing, and guided selling rules.
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Bundle and option configuration for complex products.
- **[Pricing APIs](pricing-business-apis-v66.md)** — Price calculation and waterfall analysis.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using products discovered via PCM.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
