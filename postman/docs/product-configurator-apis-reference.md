# Salesforce Product Configurator APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Product Configurator APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Product Configurator APIs enable interactive configuration of complex products — bundles, option groups, and rule-driven selections — within a quoting or eCommerce flow. Configuration state is maintained as a server-side "instance" across multiple API calls, allowing incremental changes before the final configuration is committed to a transaction.

---

## CONFIGURATION ACTION APIs

### 1. Configure (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/configure`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/configure`
- **Description:** Initialize a new configuration session for a product. Returns a configuration instance with the product's option groups, rules, and constraints applied. This is the entry point for interactive configuration flows — the returned instance ID is used in subsequent node and instance management calls.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `productId` (String, Required): Salesforce ID of the product to configure
  - `selectedOptions` (Array, Optional): Initial option selections to pre-populate the configuration
    - `optionId` (String): ID of the option
    - `value` (String): Selected value for the option

---

## SAVED CONFIGURATION APIs

Saved configurations allow reusable configuration templates that can be loaded into new quotes or orders without repeating the interactive configuration process.

### 2. List Saved Configurations (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/cpq/configurator/saved-configuration`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration`
- **Description:** Retrieve all saved product configurations available in the org. Returns configuration names, IDs, associated products, and creation metadata.
- **Available Version:** 59.0

---

### 3. Create Saved Configuration (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/saved-configuration`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration`
- **Description:** Save a product configuration for future reuse. Saved configurations can be loaded directly into quotes or orders, eliminating the need to repeat option selection for common configurations.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `name` (String, Required): Human-readable name for the saved configuration
  - `productId` (String, Required): Salesforce ID of the product being configured
  - `configurationData` (Object, Required): The complete configuration state to save
    - `selectedOptions` (Array): Option selections included in the saved state

---

### 4. Update Saved Configuration (PUT)
- **HTTP Method:** PUT
- **URI Path:** `/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Description:** Replace the full contents of an existing saved configuration. Use when the configuration needs to reflect updated product options or corrected selections.
- **Available Version:** 59.0
- **Path Parameters:**
  - `configurationId` (String, Required): ID of the saved configuration to update
- **Request Body Fields:**
  - `name` (String, Optional): Updated display name for the saved configuration
  - `configurationData` (Object, Required): Complete replacement configuration data
    - `selectedOptions` (Array): Full replacement option selections

---

### 5. Delete Saved Configuration (DELETE)
- **HTTP Method:** DELETE
- **URI Path:** `/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration/{configurationId}`
- **Description:** Permanently delete a saved product configuration. This action cannot be undone.
- **Available Version:** 59.0
- **Path Parameters:**
  - `configurationId` (String, Required): ID of the saved configuration to delete

---

## INSTANCE MANAGEMENT APIs

Configuration instances represent the in-progress state of an active configuration session. Instances are created by the Configure action and can be retrieved, loaded, saved, and replaced.

### 6. Get Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/get-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/get-instance`
- **Description:** Retrieve the current state of an active configuration instance. Returns all nodes, selected options, and applied rules for the given instance.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the configuration instance to retrieve

---

### 7. Load Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/load-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/load-instance`
- **Description:** Load a previously saved configuration into a new active instance. Use to hydrate a configuration session from a saved template, then apply further changes before committing to a transaction.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `configurationId` (String, Required): ID of the saved configuration to load

---

### 8. Save Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/save-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/save-instance`
- **Description:** Persist the current state of a configuration instance as a saved configuration for future reuse.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the active configuration instance to save
  - `configurationData` (Object, Optional): Additional or overriding configuration data to include in the saved record

---

### 9. Set Instance (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/set-instance`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/set-instance`
- **Description:** Fully replace the configuration data for an existing active instance. Unlike node-level updates, this replaces the entire instance state in one call. Use when applying a complete configuration from an external source.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the configuration instance to replace
  - `configurationData` (Object, Required): Complete replacement configuration state
    - `selectedOptions` (Array): Full replacement option selections

---

## NODE OPERATION APIs

Nodes represent individual components within a configuration — products, bundles, and option groups. Node operations allow granular, incremental changes to the configuration tree.

### 10. Add Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/add-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/add-nodes`
- **Description:** Add one or more product or option nodes to an existing configuration instance. Use during interactive configuration when a user selects additional bundle components or optional add-ons.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the active configuration instance
  - `nodesToAdd` (Array, Required): List of nodes to add, each containing:
    - `parentNodeId` (String): ID of the parent node (use `"root"` for top-level additions)
    - `productId` (String): Salesforce ID of the product to add as a node

---

### 11. Delete Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/delete-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/delete-nodes`
- **Description:** Remove one or more nodes from an active configuration instance. Use when a user deselects bundle components or optional add-ons. Configuration rules are re-evaluated after node removal.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the active configuration instance
  - `nodeIdsToDelete` (Array of String, Required): IDs of the nodes to remove from the configuration

---

### 12. Update Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/update-nodes`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/update-nodes`
- **Description:** Update the properties of one or more nodes in an active configuration instance — for example, changing quantity or attribute values. Configuration rules are re-evaluated after each update.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the active configuration instance
  - `nodesToUpdate` (Array, Required): List of node updates, each containing:
    - `nodeId` (String): ID of the node to update
    - `properties` (Object): Key-value pairs of properties to change (e.g., `{"quantity": 2}`)

---

### 13. Set Product Quantity (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/cpq/configurator/actions/set-product-quantity`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/set-product-quantity`
- **Description:** Set the quantity for a specific product within a configuration instance. A convenience shortcut for the common pattern of updating a node's quantity property. Quantity rules and UoM rounding are applied automatically.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `instanceId` (String, Required): ID of the active configuration instance
  - `productId` (String, Required): Salesforce ID of the product whose quantity to update
  - `quantity` (Integer, Required): New quantity value to set

---

## Typical Configuration Workflow

```
1. Configure          → Initialize instance with product, get instanceId
2. Add Nodes          → User selects optional components (instanceId)
3. Update Nodes       → User adjusts quantities (instanceId)
4. Delete Nodes       → User removes unwanted components (instanceId)
5. Get Instance       → Review final configuration state (instanceId)
6. Save Instance      → Optionally save for reuse (instanceId → configurationId)
7. Commit to Quote    → Pass configured product + instance data to Transaction Management
```

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Discover and select products before configuring.
- **[Product Catalog Management APIs](pcm-business-apis-reference.md)** — Manage product catalog, options, and attributes.
- **[Pricing APIs](pricing-business-apis-v66.md)** — Price the configured product after configuration is complete.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Place quotes and orders using configured products.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
