# Revenue Lifecycle Management v260 Business APIs Reference

**API Version:** 66.0
**Salesforce Release:** Spring 2026 (API v66.0)
**Extraction Date:** 2026-03-26

---

## Rate Management Business APIs

**Pages:** 627-635

Use the Rate Management Business APIs to get rate plan and persisted rating waterfall details.

### 1. Rate Plan (GET)

**Endpoint:** `GET /services/data/v66.0/connect/core-rating/rate-plan`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/core-rating/rate-plan
?contextId=858a3ad3e5a0e5c319652a6ab92f6fdb2b4fa8be72b390506d014596c6da62c9
&procedureApiName=SampleProcedure
```

**API Version:** 62.0

**Description:**
Get a rate plan for a specified set of context input. Use this API to retrieve rate cards, rate card entries, and related adjustments based on the filter criteria for the context input.

**Special Access Rules:**
- Org must have the Rate Management: Run Time User permission set
- Org must have a default usage rating discovery procedure defined in Revenue Settings

**Considerations:**
- API request supports one pricebook and one sellable product
- Product ID is required to invoke this API
- Invoke this API even if a hydrated context is available

**Request Parameters:**

| Parameter | Type | Description | Required | API Version |
|-----------|------|-------------|----------|-------------|
| `contextId` | String | ID of the context to specify as input to the procedure | Yes | 62.0 |
| `procedureApiName` | String | API name of the procedure to be executed | Yes | 62.0 |

**Response Body Type:** Rate Plan Response

**Notable Response Fields:**
- `success` (Boolean): Indicates if request is successful
- `executionId` (String): ID of the procedure execution record
- `error` (Rating Error Response[]): Error response if any

---

### 2. Rating Waterfall (GET)

**Endpoint:** `GET /services/data/v66.0/connect/core-pricing/waterfall/{lineItemId}/{executionId}`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/core-pricing/waterfall/Gold/2yHdNNEFOZr9jAe4gHS7
?tagsToFilter=UnitPrice&usageType=Rating
```

**API Version:** 62.0

**Description:**
Get the persisted rating waterfall that stores the process logs. Rating waterfall provides insights into the internal rating process.

**Path Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `lineItemId` | String | Line item ID for which price is being calculated | Yes |
| `executionId` | String | Execution ID of a particular execution of rating procedure | Yes |

**Query Parameters:**

| Parameter | Type | Description | Required | API Version | Valid Values | Default |
|-----------|------|-------------|----------|-------------|--------------|---------|
| `tagsToFilter` | String | Comma-separated tags to filter | No | 62.0 | - | - |
| `usageType` | String | Usage type of waterfall log record | No | 62.0 | Rating, Pricing | Pricing |

**Response Body Type:** Line Item Waterfall Response

**Notable Response Fields:**
- `currencyCode` (String): Currency code (e.g., USD, INR)
- `error` (Rating Error Response): Details of any errors
- `executionEndTimestamp` (String): End timestamp of procedure execution (ISO 8601)
- `executionId` (String): Execution ID of the rating procedure
- `executionStartTimestamp` (String): Start timestamp of procedure execution
- `lineItemId` (String): Line item ID for which price was calculated
- `success` (Boolean): Indicates if API request was successful
- `usageType` (String): Usage type of waterfall log record
- `output` (Map<String, Object>): Output of the rating procedure
- `waterfall` (Rating Waterfall Response[]): Details of the rating waterfall

---

## Product Configurator Business APIs

**Pages:** 646-752

Use the Product Configurator Business APIs to customize a product or service according to business-specific requirements. Integrate these APIs with any front-end application to access configurator capabilities.

### 1. Configuration (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/configure`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/configure
```

**API Version:** 60.0

**Description:**
Retrieve and update a product's configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of sales transaction being configured (Quote or Order) | Yes | 60.0 |
| `transactionLineId` | String | ID of top-level line item being configured | No | 60.0 |
| `correlationId` | String | ID for traceability of logs | No | 60.0 |
| `configuratorOptions` | ConfiguratorOptionsInput[] | Options to pass to configurator (executePricing, returnProductCatalogData, etc.) | No | 60.0 |
| `qualificationContext` | UserContextInput | Account ID, contact ID for executing qualification rules | No | 60.0 |
| `contextResponseType` | String | Response type: Full, Delta, None, or Product | No | 65.0 |
| `transactionContextId` | String | ID of transaction context | No | 60.0 |
| `addedNodes` | ConfiguratorAddedNodeInput[] | List of added context nodes | No | 60.0 |
| `updatedNodes` | ConfiguratorUpdatedNodeInput[] | List of updated context nodes | No | 60.0 |
| `deletedNodes` | ConfiguratorDeletedNodeInput[] | List of deleted context nodes | No | 60.0 |

**Response Body Type:** Configuration Details

---

### 2. Saved Configuration - List & Create (GET, POST)

**Endpoint:** `GET, POST /services/data/v66.0/connect/cpq/configurator/saved-configuration`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration
```

**API Version:** 63.0

**Description:**
Save and reuse a record's configurations, and get a list of the saved configurations for a record.

#### GET Request

**Request Parameters:**

| Parameter | Type | Description | Required | API Version |
|-----------|------|-------------|----------|-------------|
| `referenceRecordId` | String | ID of record whose saved configurations must be retrieved | Yes | 63.0 |

**Response Body Type:** Configuration List

#### POST Request

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `data` | String | Configuration data as JSON string | Yes | 63.0 |

**Response Body Type:** Configuration Details

---

### 3. Saved Configuration Details - Update & Delete (DELETE, PUT)

**Endpoint:** `DELETE, PUT /services/data/v66.0/connect/cpq/configurator/saved-configuration/{configurationId}`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/saved-configuration/5KPxx0025063GSmSAX
```

**API Version:** 63.0

**Description:**
Update or delete a record's saved configuration by using the configuration ID.

**Path Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `configurationId` | String | ID of saved configuration to update or delete | Yes |

**DELETE Operation:**
Delete a saved configuration. Response: Configuration Details

**PUT Operation:**
Update a saved configuration.

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `data` | String | Updated configuration data as JSON string | Yes |

**Response Body Type:** Configuration Details

---

### 4. Configuration Get Instance (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/get-instance`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/get-instance
```

**API Version:** 60.0

**Description:**
Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `transactionContextId` | String | ID of the transaction context | No | 60.0 |

**Response Body Type:** Configuration Details

---

### 5. Configuration Load Instance (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/load-instance`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/load-instance
```

**API Version:** 60.0

**Description:**
Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `correlationId` | String | ID for traceability of logs | No | 60.0 |

**Response Body Type:** Configuration Details

---

### 6. Configuration Save Instance (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/save-instance`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/save-instance
```

**API Version:** 60.0

**Description:**
Save a configuration instance after a successful product configuration.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `transactionContextId` | String | ID of the transaction context | No | 60.0 |

**Response Body Type:** Configuration Details

---

### 7. Configuration Set Instance (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/set-instance`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/set-instance
```

**API Version:** 60.0

**Description:**
Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `configurationData` | Object | Configuration data from external system | Yes | 60.0 |
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |

**Response Body Type:** Configuration Details

---

### 8. Configurator Add Nodes (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/add-nodes`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/add-nodes
```

**API Version:** 60.0

**Description:**
Add a node to the context through the runtime system without using the Salesforce user interface.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `nodesToAdd` | ConfiguratorAddedNodeInput[] | Nodes to add to configuration | Yes | 60.0 |

**Response Body Type:** Configuration Details

---

### 9. Configurator Delete Nodes (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/delete-nodes`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/delete-nodes
```

**API Version:** 60.0

**Description:**
Delete nodes from a product configuration.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `nodesToDelete` | ConfiguratorDeletedNodeInput[] | Nodes to delete from configuration | Yes | 60.0 |

**Response Body Type:** Configuration Details

---

### 10. Configurator Update Nodes (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/update-nodes`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/update-nodes
```

**API Version:** 60.0

**Description:**
Update nodes in a product configuration.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `nodesToUpdate` | ConfiguratorUpdatedNodeInput[] | Nodes to update in configuration | Yes | 60.0 |

**Response Body Type:** Configuration Details

---

### 11. Product Set Quantity (POST)

**Endpoint:** `POST /services/data/v66.0/connect/cpq/configurator/actions/set-product-quantity`

**Example URL:**
```
https://yourInstance.salesforce.com/services/data/v66.0/connect/cpq/configurator/actions/set-product-quantity
```

**API Version:** 60.0

**Description:**
Set the quantity of a product through the runtime system.

**Request Body Fields:**

| Field | Type | Description | Required | API Version |
|-------|------|-------------|----------|-------------|
| `transactionId` | String | ID of the sales transaction | Yes | 60.0 |
| `transactionLineId` | String | ID of line item whose quantity is being set | Yes | 60.0 |
| `quantity` | Number | New quantity value for the product | Yes | 60.0 |

**Response Body Type:** Configuration Details

---

## Summary

### Rate Management Business APIs (2 endpoints)
- **Rate Plan** (GET) - Retrieve rate cards and entries
- **Rating Waterfall** (GET) - Get rating process logs

### Product Configurator Business APIs (11 endpoints)
- **Configuration** (POST) - Configure products with rules and pricing
- **Saved Configuration** (GET/POST) - List and create saved configurations
- **Saved Configuration Details** (DELETE/PUT) - Update and delete configs
- **Configuration Get Instance** (POST) - Fetch configuration JSON
- **Configuration Load Instance** (POST) - Create configuration session
- **Configuration Save Instance** (POST) - Save configuration
- **Configuration Set Instance** (POST) - Set config from external system
- **Configurator Add Nodes** (POST) - Add nodes to configuration
- **Configurator Delete Nodes** (POST) - Delete nodes from configuration
- **Configurator Update Nodes** (POST) - Update nodes in configuration
- **Product Set Quantity** (POST) - Set product quantity

**Total: 13 REST API endpoints across both Business API chapters**
