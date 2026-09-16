# Salesforce Product Configurator APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Configurator APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Product Configurator APIs enable interactive configuration of complex products — bundles, option groups, and rule-driven selections — within a quoting or eCommerce flow. Configuration state is maintained server-side as a **context** (`contextId`), tied to a transaction (`transactionId`/`transactionLineId`), across multiple API calls — allowing incremental changes (add/update/delete nodes, quantity changes) before the final configuration is committed. The 264 snapshot also includes a Config Rules endpoint (available from API v67.0 / Release 262) under a separate `/revenue/product-configurator/` base path (see below).

---

## CONFIGURATION ACTION APIs

### 1. Configure (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/configure`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/configure`
- **Description:** Retrieve and update a product's configuration from a configurator. Executes configuration rules and notifies users of any violations for changes to a product bundle, attributes, or product quantity within a bundle. Also gets pricing details for the configured bundle. This is the entry point for interactive configuration flows, and is also used for incremental node changes (add/update/delete) in a single round trip.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `transactionId` (String, Required): ID of the sales transaction (quote or order) being configured.
  - `transactionLineId` (String, Optional): ID of the specific transaction line item to configure.
  - `correlationId` (String, Optional): Unique identifier attached to the request for tracing.
  - `configuratorOptions` (Object, Optional): Options passed to the configurator — a single object (not an array). Sub-fields: `pricingProcedure` (String) — API name of the pricing procedure to use during calls to Salesforce Pricing Management; all other sub-fields are Boolean — `addDefaultConfiguration`, `executeConfigurationRules`, `executePricing`, `explainabilityEnabled` (66.0+), `qualifyAllProductsInTransaction`, `returnProductCatalogData`, `validateAmendRenewCancel`, `validateProductCatalog`.
  - `contextResponseType` (String, Optional — 65.0+): Controls response payload size for large transactions. Values: `Delta`, `Full`, `None`, `Product`. Required when the transaction has more than 1,000 and fewer than 15,000 line items.
  - `qualificationContext` (Object, Optional): User context used for qualification rules — `accountId`, `contactId`, `contextId`.
  - `transactionContextId` (String, Optional): Context ID of an existing transaction session.
  - `addedNodes` (Array, Optional): Nodes to add — each with `path` (String[]) and `addedObject` (Object). See [Configurator Added Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_added_node_input.htm.md).
  - `updatedNodes` (Array, Optional): Nodes to update — each with `path` (String[]) and `updatedAttributes` (Object). See [Configurator Updated Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_updated_node_input.htm.md).
  - `deletedNodes` (Array, Optional): Nodes to delete — each with `path` (String[]). See [Configurator Deleted Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_deleted_node_input.htm.md).

---

## SAVED CONFIGURATION APIs

Saved configurations allow reusable configuration templates — tied to a `referenceRecordId` (e.g., a quote or opportunity) — that can be loaded into new transactions without repeating the interactive configuration process.

### 2. List Saved Configurations (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/cpq/configurator/saved-configuration`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/saved-configuration?referenceRecordId={{defaultQuoteId}}`
- **Description:** Get a list of the saved configurations for a record.
- **Available Version:** 63.0
- **Request Parameters:**
  - `referenceRecordId` (String, Required): ID of the record whose saved configurations to retrieve.

---

### 3. Create Saved Configuration (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/saved-configuration`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/saved-configuration`
- **Description:** Save a record's configuration for future reuse. Saved configurations can be loaded directly into quotes or orders, eliminating the need to repeat option selection for common configurations.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `referenceRecordId` (String, Required): ID of the record (e.g., quote) the configuration is saved against.
  - `data` (String, Optional): JSON representation of the sales transaction to save.
  - `name` (String, Optional): Human-readable name for the saved configuration.
  - `description` (String, Optional): Description of the saved configuration.

---

### 4. Update Saved Configuration (PUT)
- **HTTP Method:** PUT
- **URI Path:** `/connect/cpq/configurator/saved-configuration/{id}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Description:** Update a record's saved configuration by using the configuration ID.
- **Available Version:** 63.0
- **Path Parameters:**
  - `id` (String, Required): ID of the saved configuration to update.
- **Request Body Fields:**
  - `data` (String, Required): Updated JSON representation of the sales transaction.
  - `description` (String, Required): Updated description of the saved configuration.
  - `name` (String, Required): Updated display name of the saved configuration.

---

### 5. Delete Saved Configuration (DELETE)
- **HTTP Method:** DELETE
- **URI Path:** `/connect/cpq/configurator/saved-configuration/{id}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Description:** Delete a record's saved configuration by using the configuration ID. This action cannot be undone.
- **Available Version:** 63.0
- **Path Parameters:**
  - `id` (String, Required): ID of the saved configuration to delete.

---

## INSTANCE MANAGEMENT APIs

Configuration instances represent the JSON state of an active configuration session, addressed by a `contextId`. Instances are created via Configure/Load Instance and can be fetched, loaded, saved, and replaced.

### 6. Get Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/get-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/get-instance`
- **Description:** Fetch the JSON representation of a product configuration. Use the response to display the configuration on the Salesforce UI, or to save the configuration instance to an external system.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Transaction context ID of the configuration instance to fetch.

---

### 7. Load Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/load-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/load-instance`
- **Description:** Create a session for the product configuration instance using the transaction ID. Returns a session/context ID that includes the results of actions such as configuration rules, qualification rules, and pricing management.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `transactionId` (String, Required): ID of the quote or order to load into a configuration session.
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `contextMappingId` (String, Optional): Context mapping to apply to the loaded instance.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

### 8. Save Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/save-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/save-instance`
- **Description:** Save a configuration instance after a successful product configuration, persisting the in-memory session state back to the transaction.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Context ID of the configuration instance to save.

---

### 9. Set Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/set-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/set-instance`
- **Description:** Set a product configuration instance. Used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `transaction` (String, Required): JSON representation of the transaction to set as the configuration instance.
  - `contextMappingId` (String, Required): Context mapping to apply to the instance.
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

## NODE OPERATION APIs

Nodes represent individual components within a configuration — products, bundles, and option groups — addressed by `path` (an array of node identifiers) within the context identified by `contextId`.

### 10. Add Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/add-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/add-nodes`
- **Description:** Add a node to the context through the runtime system, without using the Salesforce UI. Use during interactive configuration when a user selects additional bundle components or optional add-ons.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Context ID of the active configuration instance.
  - `addedNodes` (Array, Required): Nodes to add — each with `path` (String[]: location within the configuration tree) and `addedObject` (Object: the node payload to add). See [Configurator Added Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_added_node_input.htm.md).
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

### 11. Delete Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/delete-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/delete-nodes`
- **Description:** Delete nodes from a product configuration. Configuration rules are re-evaluated after node removal.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Context ID of the active configuration instance.
  - `deletedNodes` (Array, Required): Nodes to delete — each with `path` (String[]: location of the node to remove). See [Configurator Deleted Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_deleted_node_input.htm.md).
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

### 12. Update Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/update-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/update-nodes`
- **Description:** Update nodes in a product configuration — for example, changing attribute values. Configuration rules are re-evaluated after each update.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Context ID of the active configuration instance.
  - `updatedNodes` (Array, Required): Nodes to update — each with `path` (String[]: location of the node to update) and `updatedAttributes` (Object: key-value pairs of attributes to change). See [Configurator Updated Node Input](../../docs/salesforce/264/dev-guide/articles/connect_requests_configurator_updated_node_input.htm.md).
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

### 13. Set Product Quantity (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/set-product-quantity`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/set-product-quantity`
- **Description:** Set the quantity of a product through the runtime system. A convenience shortcut for the common pattern of updating a node's quantity. Quantity rules and UoM rounding are applied automatically.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextId` (String, Required): Context ID of the active configuration instance.
  - `quantity` (Integer, Required): New quantity value to set.
  - `transactionLinePath` (String[], Required): Path to the transaction line item whose quantity to set.
  - `configuratorOptions` (Object, Optional): See item 1 (Configure)'s `configuratorOptions` sub-fields above.
  - `qualificationContext` (Object, Optional): `accountId`, `contactId`, `contextId` used for qualification rules.

---

## CONFIGURATION RULE APIs

### 14. Config Rules (POST) — v67.0 (Release 262)
- **HTTP Method:** POST
- **URI Path:** `/revenue/product-configurator/rules/actions/execute`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/product-configurator/rules/actions/execute`
- **Description:** Run configuration rules for a specific quote or order, based on a context ID or transaction ID. Note this endpoint uses a different base path (`/revenue/product-configurator/`) than the rest of the Product Configurator APIs (`/connect/cpq/configurator/`).
- **Available Version:** 67.0
- **Request Body Fields:**
  - `transactionContextId` (String, Required if `transactionId` isn't specified): Context ID of the transaction whose configuration rules to run.
  - `transactionId` (String, Required if `transactionContextId` isn't specified): ID of the quote or order whose configuration rules to run.
  - `ruleOptions` (Object, Optional): Options for rule execution — supports `isUpdateContextRequired` (Boolean).

---

## Typical Configuration Workflow

```
1. Configure / Load Instance → Initialize a session for a transaction, get contextId
2. Add Nodes                 → User selects optional components (contextId)
3. Update Nodes               → User adjusts attributes/quantities (contextId)
4. Delete Nodes                → User removes unwanted components (contextId)
5. Get Instance                → Review final configuration state (contextId)
6. Config Rules                → Re-run rules on demand (transactionContextId/transactionId)
7. Save Instance                → Persist the session state back to the transaction (contextId)
8. Commit to Quote               → Configured product + configuration data flow to Transaction Management
```

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `68.0`) | Manual setup |
| `{{defaultQuoteId}}` | Default quote record ID | Setup Runner |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Discover and select products before configuring.
- **[Product Catalog Management APIs](pcm-business-apis-reference.md)** — Manage product catalog, options, and attributes.
- **[Pricing APIs](pricing-business-apis-v68.md)** — Price the configured product after configuration is complete.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using configured products.

---

*Reference for: Agentforce Revenue Management APIs v68.0 (Winter '27) | Salesforce Revenue Cloud Developer Guide v264*
