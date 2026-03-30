# Salesforce Context Service APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Context Service APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Context Service is the backbone of Revenue Cloud's pricing and entitlement system. A context definition describes the input data structure for a pricing or configuration operation, and a context mapping binds Salesforce object fields to that structure. Together, they allow the pricing engine to hydrate a context instance at runtime — pulling account attributes, product characteristics, and transaction data into the input record that pricing procedures operate on.

---

## CONTEXT DEFINITION APIs

### 1. Create Context Definition (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/context-definitions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions`
- **Description:** Create a new context definition in the org. A context definition specifies the schema of the context input record — the fields and data types that will be populated at pricing time. Context definitions are referenced by pricing procedures and context mappings.
- **Available Version:** 59.0
- **Request Body Fields:**
  - `name` (String, Required): API name for the context definition (used in pricing procedures and mappings)
  - `description` (String, Optional): Human-readable description of the context and its intended use
  - `contextType` (String, Required): The type of operation this context supports — e.g., `"PRICING"`, `"CONFIGURATION"`, `"QUALIFICATION"`

---

### 2. List Context Definitions (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/context-definitions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions`
- **Description:** Retrieve all context definitions configured in the org. Returns definition names, IDs, types, and associated node and mapping counts. Use to find the IDs needed for pricing API calls or to audit the context configuration.
- **Available Version:** 59.0

---

### 3. Get Context Definition (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/context-definitions/{contextDefinitionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions/{{contextDefinitionId}}`
- **Description:** Retrieve the full details of a specific context definition, including its nodes, attributes, and all associated mappings. Use when you need to inspect the complete schema of a context before writing data to hydrate it.
- **Available Version:** 59.0
- **Path Parameters:**
  - `contextDefinitionId` (String, Required): Salesforce ID of the context definition. Use `{{contextDefinitionId}}` from the Setup Runner.

---

## CONTEXT NODE APIs

Context nodes define the hierarchical structure within a context definition — they represent the discrete data entities (e.g., Account, Product, Order) that contribute fields to the context input.

### 4. Create Context Nodes (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/context-definitions/{contextDefinitionId}/context`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions/{{contextDefinitionId}}/context`
- **Description:** Add one or more nodes to a context definition. Each node represents a logical grouping of attributes within the context schema. Nodes can represent Salesforce objects (e.g., Account), custom data structures, or classification hierarchies. After creating nodes, use Create Context Mappings to bind them to Salesforce object fields.
- **Available Version:** 59.0
- **Path Parameters:**
  - `contextDefinitionId` (String, Required): Salesforce ID of the context definition to add nodes to. Use `{{contextDefinitionId}}`.
- **Request Body Fields:**
  - `nodes` (Array, Required): List of node objects to create, each containing:
    - `name` (String): Node name (used as a key in the context data)
    - `value` (String): Node value or identifier
    - `attributes` (Object, Optional): Additional metadata for the node (e.g., `{"tier": "HIGH"}`)

---

## CONTEXT MAPPING APIs

Context mappings define how Salesforce object field values are bound to context definition nodes at runtime. When a pricing API call is made, Revenue Cloud evaluates the mappings to populate the context instance automatically.

### 5. Create Context Mappings (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/context-definitions/{contextDefinitionId}/context`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/context-definitions/{{contextDefinitionId}}/context`
- **Description:** Define field-to-context mappings for a context definition. Each mapping specifies which Salesforce object and field provides a value for a given context attribute. Mappings are evaluated at runtime to hydrate the context instance before pricing procedures execute.
- **Available Version:** 59.0
- **Path Parameters:**
  - `contextDefinitionId` (String, Required): Salesforce ID of the context definition to add mappings to. Use `{{contextDefinitionId}}`.
- **Request Body Fields:**
  - `mappings` (Array, Required): List of mapping objects, each containing:
    - `objectName` (String): API name of the Salesforce object providing the value (e.g., `"Account"`, `"Order"`, `"QuoteLineItem"`)
    - `fieldName` (String): API name of the field on the object (e.g., `"Industry"`, `"AnnualRevenue"`, `"Quantity"`)
    - `contextAttribute` (String): The context attribute name this mapping populates

---

## Context Service Architecture

### Key Concepts

**Context Definition** — The schema for a context instance. Defines what input data the pricing engine expects. Referenced by name in pricing procedure configurations and in the `contextDefinitionId` field of pricing API calls.

**Context Node** — A structural unit within a context definition. Nodes represent logical groupings (e.g., buyer attributes, product attributes, transaction attributes) that are populated independently.

**Context Mapping** — A binding rule that tells the runtime engine which Salesforce object field to read when populating a context attribute. Mappings eliminate the need to manually pass every field in every API call.

**Context Instance** — The runtime-hydrated record created when a pricing API call is executed. The instance contains the actual field values resolved by the mappings, which the pricing procedure then processes.

### Context Types in the Setup Runner

The Setup Runner populates four context variable sets, each corresponding to a different pricing scenario:

| Variable Prefix | Context Type | Use Case |
|-----------------|--------------|----------|
| `contextDefinitionId` | Default | Standard pricing context |
| `customContextDefinitionId` | Custom | Custom pricing rules |
| `cartContextDefinitionId` | Cart | eCommerce cart pricing |
| `pdContextDefinitionId` | Product Discovery | Catalog context |

Each has a paired `contextMappingId` and `pricingProcedureId` variable populated by the Setup Runner.

---

## Typical Context Service Workflow

```
1. List Context Definitions  → Find the contextDefinitionId for your scenario
2. Get Context Definition    → Inspect the schema (nodes, mappings, attributes)
3. Pricing API call          → Pass contextDefinitionId + contextMappingId in the request body
                               (Runtime automatically hydrates the context instance)
```

For new context definitions (admin setup, not runtime):
```
1. Create Context Definition → Define the schema type
2. Create Context Nodes      → Add structural nodes to the definition
3. Create Context Mappings   → Bind Salesforce fields to context attributes
4. Configure Pricing Procedure → Reference the new definition
```

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{contextDefinitionId}}` | Default context definition ID | Setup Runner |
| `{{contextMappingId}}` | Default context mapping ID | Setup Runner |
| `{{customContextDefinitionId}}` | Custom context definition ID | Setup Runner |
| `{{customContextMappingId}}` | Custom context mapping ID | Setup Runner |
| `{{cartContextDefinitionId}}` | Cart context definition ID | Setup Runner |
| `{{cartContextMappingId}}` | Cart context mapping ID | Setup Runner |
| `{{pdContextDefinitionId}}` | Product Discovery context definition ID | Setup Runner |
| `{{pdContextMappingId}}` | Product Discovery context mapping ID | Setup Runner |
| `{{pricingProcedureId}}` | Default pricing procedure ID | Setup Runner |

---

## Related Domains

- **[Pricing APIs](pricing-business-apis-v66.md)** — All pricing calls consume context definitions and mappings. The `contextDefinitionId` and `contextMappingId` are required fields in most pricing requests.
- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Product Discovery uses context to apply buyer-specific entitlements and pricing.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Sales transactions use the pricing context to calculate line item prices.
- **[Usage Management APIs](usage-management-apis-reference.md)** — Usage-based pricing uses context to interpret consumption dimensions.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
