# Salesforce Product Catalog Management (PCM) APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Catalog Management (PCM) APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The PCM APIs provide direct catalog access with standard REST semantics (GET/POST/PUT/PATCH). For context-aware, buyer-session-scoped catalog operations, see the [Product Discovery APIs](product-discovery-apis-reference.md), which use POST for all operations and apply context filters, entitlements, and pricing rules.

---

## CATALOG APIs

### 1. List Catalogs (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/catalogs`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs`
- **Description:** Retrieve, search, filter, or sort catalog records. POST is used instead of GET because a request payload is sent to filter the records.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions. If unspecified, a UUID is generated.
  - `filter` (Object, Optional): Criteria to filter records. Supported operators: `eq`, `in`, `contains`. Supported properties: `name`, `catalogType`.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.
  - `offset` (Integer, Optional): Number of records to skip. Default: 0.
  - `pageSize` (Integer, Optional): Number of records per page. Valid values 1-100. Default: 100.
  - `sort` (Object, Optional): Sort order of the catalog records. Supported directions: `asc`, `desc`.

---

### 2. Get Catalog (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/catalogs/{catalogId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs/{{defaultCatalogId}}`
- **Description:** Retrieve details of a specific product catalog by its Salesforce record ID.
- **Available Version:** 60.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog record. Use `{{defaultCatalogId}}` from the Setup Runner.
- **Query Parameters:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `fields` (String[], Optional): For internal use only.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.

---

## CATEGORY APIs

### 3. List Categories (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/catalogs/{catalogId}/categories`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs/{{defaultCatalogId}}/categories`
- **Description:** Retrieve the root-level categories of a catalog based on a catalog ID, or subcategories based on a parent category. You can also search, filter, or sort the categories.
- **Available Version:** 60.0
- **Path Parameters:**
  - `catalogId` (String, Required): Salesforce ID of the catalog. Use `{{defaultCatalogId}}`.
- **Query Parameters:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `depth` (Integer, Optional): Number of levels in the category hierarchy to return. Default: 1.
  - `fields` (String[], Optional): For internal use only.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.
  - `parentCategoryId` (String, Optional): ID of the category to fetch the associated hierarchy of subcategories. If unspecified, root-level categories are returned.

---

### 4. Get Category (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/categories/{categoryId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/categories/{{defaultCategoryId}}`
- **Description:** Retrieve details of a specific product category by its Salesforce record ID.
- **Available Version:** 60.0
- **Path Parameters:**
  - `categoryId` (String, Required): Salesforce ID of the category record. Use `{{defaultCategoryId}}` from the Setup Runner.
- **Query Parameters:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `fields` (String[], Optional): For internal use only.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.

---

## PRODUCT APIs

### 5. List Products (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products`
- **Description:** Retrieve products. You can also search, filter, or sort the products.
- **Available Version:** 60.0
- **Query Parameters:**
  - `productClassificationId` (String, Optional): ID of the product classification template. Specify either the product classification ID, list of category IDs, or list of catalog IDs to retrieve products.
- **Request Body Fields:**
  - `additionalFields` (Map<String, Additional Fields Input>, Optional, Available Version 61.0): Map of object (supported: `Product2`) to the list of standard/custom fields to include in the response.
  - `catalogIds` (String[], Optional): List of catalog IDs to scope the returned products.
  - `categoryIds` (String[], Optional): List of category IDs to scope the returned products.
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `filter` (Criteria Input, Optional): Criteria to filter records. Supported properties: `name`, `description`, `isActive` (or `name` only when indexed search is enabled). Supported operators: `eq`, `in`, `contains`, and (from 63.0) `gt`, `lt`, `gte`, `lte` for Number/Date/Datetime fields.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.
  - `offset` (Integer, Optional): Number of records to skip. Default: 0.
  - `pageSize` (Integer, Optional): Number of records per page. Valid values 1-200. Default: 100.
  - `relatedObjectFilters` (Related Object Filter[], Optional): Criteria for related objects. Supported object: `ProductSpecificationRecType`; supported property: `IsCommercial`; supported operator: `eq`.
  - `searchTerm` (String, Optional, Available Version 62.0): String used to match products by name.
  - `sort` (Sort, Optional): Sort order for the products.

---

### 6. Get Product (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/products/{productId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}`
- **Description:** Retrieve the full details of a single product record or bundle by its Salesforce record ID.
- **Available Version:** 60.0
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product. Use `{{defaultTermDefinedAnnualProductId}}` or another product variable from the Setup Runner.
- **Query Parameters:**
  - `catalogSystems` (String[], Optional, Available Version 66.0): Name of the catalog system — `epc` (Enterprise Product Catalog) or `pcm` (Product Catalog Management, default). Only one value is honored even though the parameter accepts a list.
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `fields` (String[], Optional): For internal use only.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.

---

### 7. Bulk Product Details (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/bulk`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products/bulk`
- **Description:** Retrieve full product details for multiple products in a single request. More efficient than individual Get Product calls when loading several products at once.
- **Available Version:** 61.0
- **Request Body Fields:**
  - `additionalFields` (Map<String, Additional Fields Input>, Optional): Map of object to additional standard/custom fields to include. Supported objects: `Product2`, `ProductAttributeDefinition` (fields must also exist on `ProductClassificationAttr`); if Dynamic Revenue Orchestrator is enabled, also supports `AttributeDefinition` with `OptOutAssetization`, `OptOutDecompositionAction`, `OptOutSupplementalAction`.
  - `catalogSystems` (String[], Optional, Available Version 66.0): Name of the catalog system — `epc` or `pcm` (default). Only one value is honored even though the parameter accepts a list.
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `language` (String, Optional, Available Version 64.0): Custom language for translated field data.
  - `productIds` (String[], Required): List of Salesforce product record IDs. Blank, invalid, or not-found IDs are skipped; the request proceeds with the valid ones.
  - `uptoLevel` (Integer, Optional): Hierarchy level of child components to return for a bundle. Maximum supported value is 1. If unspecified, the full bundle hierarchy is returned.

---

### 8. Product Related Records (POST)
- **Retained from the prior extraction; not present in the 264 snapshot** — the Revenue Cloud Developer Guide's 264 PCM resource index lists no article for this route. Item 9 (`Product Related Records List`, `/connect/pcm/relatedRecords/{entityName}`) is the 264-grounded equivalent. Verify this route against a live 264 org before relying on it.
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/{productId}/related-records`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}/related-records`
- **Description:** Retrieve related records for a product, such as variants and bundles. Use `relationshipTypes` to specify which relationship types to include.
- **Available Version:** 59.0 (unverified — not confirmed against the 264 snapshot; carried over from a prior extraction)
- **Path Parameters:**
  - `productId` (String, Required): Salesforce ID of the product
- **Request Body Fields:**
  - `relationshipTypes` (Array of String, Required): Relationship types to retrieve. Supported values: `"VARIANTS"`, `"BUNDLES"`

---

### 9. Product Related Records List (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/relatedRecords/{entityName}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/relatedRecords/product2`
- **Description:** Retrieve related `ProductRampSegment` or `ProductUsageGrant` records for the `Product2` object. The supported entity/object is `Product2`.
- **Available Version:** 62.0
- **Path Parameters:**
  - `entityName` (String, Required): Related entity name. Supported value: `product2`.
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `recordIds` (String[], Required): List of record IDs to return related-object records for. Maximum 20 record IDs.
  - `relatedObjectNodes` (Related Object Node Input[], Required): List of nodes for the related objects (maximum 2). Each node specifies `relatedObjectAPIName` (Required; `ProductRampSegment` or `ProductUsageGrant`), `pageSize` (Optional, default 100), `offSet` (Optional, default 0), and `filter` (Optional; for `ProductUsageGrant`, supported properties `StartDate`, `EndDate`, `Status` with operators `eq`, `gte`, `lte`).

---

### 10. Product Variants (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/products/variants`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/products/variants`
- **Description:** Retrieve the variation product(s) associated with one or more parent variant products. A parent variant product is a non-purchasable product that groups related variations; this API returns the mapping between parent variant product IDs and their associated variation product IDs.
- **Available Version:** 67.0
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique ID to track and associate related events or transactions.
  - `parentVariantsIds` (String[], Required): List of parent variant product IDs whose variations to retrieve. Blank/invalid/not-found IDs are skipped and returned in `inValidProductIds`; valid IDs that aren't parent variant products are returned in `nonVariantParentIds`.

---

### 11. Product Classification Details (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/product-catalog-management/product-classifications/details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/product-catalog-management/product-classifications/details`
- **Description:** Retrieve metadata, attributes, and attribute categories associated with product classifications across supported catalog systems. New in Spring '26 (v66.0).
- **Available Version:** 66.0
- **Request Body Fields:**
  - `catalogSystems` (String[], Optional): Name of the catalog system. Valid value: `epc` (Enterprise Product Catalog).
  - `productClassificationIds` (String[], Required): List of product classification IDs to retrieve details for. In the `epc` catalog system, these are `Product2` record IDs.

---

### 12. Product Classification List (POST)
- **HTTP Method:** POST
- **URI Path:** `/revenue/product-catalog-management/product-classifications/list`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/product-catalog-management/product-classifications/list`
- **Description:** Retrieve a paginated list of product classification records from the PCM or Enterprise Product Catalog (EPC) catalog system. Supports search, filter, and sort.
- **Available Version:** 67.0
- **Request Body Fields:**
  - `catalogSystem` (String, Optional): Name of the catalog system — `pcm` (default) or `epc`.
  - `filter` (Criteria Input, Optional): Criteria to filter records. Supported property: `name`. Supported operators: `eq`, `in`, `contains`.
  - `offset` (Integer, Optional): Number of records to skip. Default: 0.
  - `pageSize` (Integer, Optional): Valid values are 5, 10, 25, 50, and 100. Default: 100.
  - `searchTerm` (String, Optional): String to match against the product classification name.
  - `sort` (Order Input, Optional): Sort order. Defaults to name ascending.

---

### 13. Deep Clone (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/deep-clone`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/deep-clone`
- **Description:** Copy related records of an object along with the main product record. Useful for creating product variants or templates.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `mainObjectApiName` (String, Required): API name of the object. Supported object: `Product2`.
  - `mainRecordFieldValues` (Map<String, String>, Optional): Mapping of field API name to value, set on the created record. Only the `Name` field can be passed through this map.
  - `mainRecordId` (String, Required): ID of the record to clone.

---

## INDEX APIs

### 14. Index Configuration Collection (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/configurations`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/configurations`
- **Description:** Retrieve the current product index configurations. The product index drives search performance in Product Discovery APIs.
- **Available Version:** 62.0
- **Query Parameters:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `fieldTypes` (String[], Optional): Filters returned index configurations by type. Supported values: `STANDARD`, `CUSTOM`, `ProductDynamicAttribute`, `ProductAttributeDefinitionStandard`, `ProductAttributeDefinitionCustom`.
  - `includeMetadata` (Boolean, Optional): Whether to include metadata in the response.

---

### 15. Update Index Configuration (PUT)
- **HTTP Method:** PUT
- **URI Path:** `/connect/pcm/index/configurations`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/configurations`
- **Description:** Replace the full set of product index configurations. Use to define which fields are included in the search index.
- **Available Version:** 62.0
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `indexConfigurations` (Array, Required): Array of index configuration objects, each with:
    - `attributeDefinitionId` (String): Required if `attributeFieldId` isn't specified.
    - `attributeFieldId` (String): Required if `attributeDefinitionId` isn't specified.
    - `name` (String, Required): Name of the index-configured field.
    - `type` (String, Required): Type of the index-configured field (e.g., `Standard`, `Custom`, `ProductDynamicAttribute`).
    - `isSearchable` (Boolean, Optional): Whether the field is searchable.
    - `isFacetable` (Boolean, Optional, Available Version 63.0): Whether the field is facetable.
    - `facetDisplayRank` (Integer, Optional, Available Version 63.0): Sort order for displaying facets at run time.

---

### 16. Index Setting (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/setting`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/setting`
- **Description:** Retrieve global index settings, including supported languages, default language, and product grouping behavior.
- **Available Version:** 63.0

---

### 17. Update Index Setting (PATCH)
- **HTTP Method:** PATCH
- **URI Path:** `/connect/pcm/index/setting`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/setting`
- **Description:** Update global product index settings.
- **Available Version:** 63.0
- **Query Parameters:**
  - `settingId` (String, Required): ID of the setting to update. Passed as a request parameter — the resource path `/connect/pcm/index/setting` has no path placeholder.
- **Request Body Fields:**
  - `setting` (Object, Required): Object containing the setting details:
    - `defaultLanguage` (String, Required): Default language for the API.
    - `supportedLanguages` (String[], Required): List of supported language locales for indexing.
    - `productsGrouping` (String, Optional): Product grouping behavior (e.g., `GROUPING_VARIATION`) — shown in the dev-guide example but not itemized in the formal Setting Input schema; treat as unconfirmed shape.

---

## SNAPSHOT APIs

### 18. Snapshot Collection (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/snapshots`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/snapshots`
- **Description:** List all available product index snapshots. Snapshots represent point-in-time captures of the index that can be deployed to production.
- **Available Version:** 62.0
- **Query Parameters:**
  - `numberOfIndexLogs` (Integer, Optional, Available Version 63.0): Number of index logs to include in the response. Valid values 0-100. Default: 25.

---

### 19. Deploy Snapshot (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/index/deploy`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/deploy`
- **Description:** Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms.
- **Available Version:** 62.0
- **Request Body Fields:**
  - `buildType` (String, Required): `FULL` for a full index build, or `INCREMENTAL` (Available Version 63.0) for an incremental build.
  - `snapshot` (Object, Required): Run-time Catalog Snapshot details:
    - `activationType` (String, Required): Valid value: `IMMEDIATE` (snapshot activates immediately after a successful build).
    - `id` (String, Required): ID of the snapshot.
    - `activationDate` (String, Optional): Activation date of the snapshot.

---

### 20. Snapshot Index Error (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/index/error`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/error`
- **Description:** Retrieve the count and details of errors that occurred during the indexing process.
- **Available Version:** 63.0
- **Query Parameters:**
  - `indexId` (String, Required): ID of the index.
  - `snapshotIndexId` (String, Required): ID of the snapshot index.

---

## UNIT OF MEASURE APIs

### 21. Unit of Measure Info (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/pcm/unit-of-measure/info`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/unit-of-measure/info`
- **Description:** Retrieve metadata about units of measure (UoM) configured in the org. UoMs define how product quantities are measured and rounded.
- **Available Version:** 63.0
- **Query Parameters:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `ids` (String, Optional): IDs of the unit of measure records to retrieve. If unspecified, returns info for all configured UoMs.

---

### 22. Unit of Measure Rounded Data (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/pcm/unit-of-measure/rounded-data`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/unit-of-measure/rounded-data`
- **Description:** Round off and scale decimal data for a specific set of fields, based on the unit of measure and its configured precision. Use to ensure quantities conform to UoM rounding rules before placing orders.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `correlationId` (String, Optional): Unique token to track and associate related events or transactions.
  - `dataRowInputs` (Array, Required): List of row inputs, each with:
    - `key` (String, Required): Key identifying a unique data row.
    - `fieldDataInputs` (Array, Required): List of field-level rounding inputs, each with:
      - `fieldApiName` (String, Required): Unique API name of the field.
      - `originalValue` (String, Required): Original value of the field.
      - `unitOfMeasureId` (String, Required): ID of the unit of measure record associated with the field.

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `68.0`) | Manual setup |
| `{{defaultCatalogId}}` | Default catalog record ID | Setup Runner |
| `{{defaultCategoryId}}` | Default category record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Context-aware, buyer-session-scoped catalog access. Uses PCM data but applies entitlements, pricing, and guided selling rules.
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Bundle and option configuration for complex products.
- **[Pricing APIs](pricing-business-apis-v68.md)** — Price calculation and waterfall analysis.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using products discovered via PCM.

---

*Reference for: Agentforce Revenue Management APIs v68.0 (Winter '27) | Salesforce Revenue Cloud Developer Guide v264*
