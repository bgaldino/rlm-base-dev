# Salesforce Pricing Business APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Pricing Business APIs, extracted from the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

---

## PRICING CORE APIs

### 1. PBE Derived Pricing (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/pbeDerivedPricingSourceProduct`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/pbeDerivedPricingSourceProduct`
- **Description:** Get the source product for the Price Book Entry (PBE) derived pricing.
- **Available Version:** 61.0
- **Request Body Fields:**
  - `productId` (String, Required): ID of the price book
  - `pricebookEntryId` (String, Required): ID of the price book entry
  - `effectiveFrom` (String, Required): Date from when the price book entry is effective
  - `effectiveTo` (String, Required): Date until when the price book entry is effective

---

### 2. Price Context (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/price-contexts/{contextId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/price-contexts/0U3RM00000000SR0AY`
- **Description:** Perform a pricing request by using the instance ID of a context. If price waterfall is disabled from Salesforce Pricing Setup, this API doesn't return waterfall details.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `configurationOverrides` (Configuration Override Input, Optional): Parameters to override pricing configuration
    - `skipWaterfall` (Boolean): Skip waterfall calculation
    - `useSessionScopedContext` (Boolean): Use session-scoped context
    - `persistContext` (Boolean): Persist context to database
    - `taggedData` (Boolean): Include tagged data
  - `procedureName` (String, Optional): Name of the pricing procedure

---

### 3. Pricing (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/pricing`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/pricing`
- **Description:** Create and hydrate context instance in a single request. Provides comprehensive response with final pricing details per line items and related errors.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextDefinitionId` (String, Required): ID of the context definition defining the input data structure
  - `contextMappingId` (String, Required): ID of context mapping mapping input data to context instance
  - `jsonDataString` (String, Required): JSON data to hydrate the context (must be passed as String using stringify())
  - `pricingProcedureId` (String, Optional): ID or API name of the pricing procedure
  - `configurationOverrides` (Configuration Override Input, Optional):
    - `skipWaterfall` (Boolean)
    - `useSessionScopedContext` (Boolean)
    - `persistContext` (Boolean)
    - `referenceKey` (String): Reference key for tracking
    - `displayContext` (Boolean)
    - `taggedData` (Boolean)
    - `isHighVolumeLineItems` (Boolean): Indicator for high volume operations

---

### 4. API Execution Logs (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/apiexecutionlogs/{executionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/apiexecutionlogs/29646938297972`
- **Description:** Get the log details of a pricing API execution record by using the execution ID.
- **Available Version:** 63.0
- **Path Parameters:**
  - `executionId` (String, Required): ID of the pricing process execution record

---

### 5. Pricing Process Execution (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/pricing-process-execution/{executionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/pricing-process-execution/29646938297972`
- **Description:** Get the execution details of a pricing process by using the execution ID.
- **Available Version:** 63.0
- **Path Parameters:**
  - `executionId` (String, Required): ID of the pricing process execution record (generated each time a pricing process is executed)
- **Query Parameters:**
  - `executionType` (String, Optional): Type of execution (API_Execution, Discovery, Discovery_Line, Pricing, Pricing_Line). If not specified, retrieves records for all execution types.

---

### 6. Pricing Process Execution for Line Items (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/pricing-process-execution/lineitems/{executionId}/{executionType}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/pricing-process-execution/lineitems/29646938297972/Pricing_Line`
- **Description:** Get the pricing execution details for the line items of a pricing process by using the execution ID and execution type.
- **Available Version:** 63.0
- **Path Parameters:**
  - `executionId` (String, Required): ID of the pricing process execution record
  - `executionType` (String, Required): Type of execution (Pricing_Line or Discovery_Line)

---

### 7. Pricing Data Sync (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/sync/{pricingSyncOrigin}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/sync/syncData`
- **Description:** Sync pricing data to ensure that the lookup tables contain the latest pricing data. To partially synchronize, use the Decision Table Refresh Action in a Flow.
- **Available Version:** 60.0
- **Query Parameters:**
  - `pricingRecipeId` (String, Optional, Available Version 67.0): ID of the pricing recipe whose decision tables you want to sync. If not specified, the default pricing recipe is used.

---

### 8. Pricing Recipe (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/recipe`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/recipe`
- **Description:** Get the mapping details of pricing recipes to the associated pricing recipe table.
- **Available Version:** 60.0

---

### 9. Pricing Recipe Mapping (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/recipe/mapping`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/recipe/mapping`
- **Description:** Create a mapping between the pricing recipe and the Decision Tables. Post recipes with lookup tables or procedures.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `recipeId` (String, Required): ID of the pricing recipe
  - `pricingRecipeLookUpTableInputRepresentations` (Pricing Recipe LookUp Table Input[], Required): Input representation of the recipe mapping
    - `lookupId` (String): ID of the lookup table
    - `pricingComponentType` (String): Component type (e.g., CustomDiscount)
  - `pricingRecipeProcedureInputRepresentation` (Pricing Recipe Procedure Input Representation, Required): Input representation of the procedure used in the pricing recipe
    - `procedureId` (String): ID of the procedure

---

### 10. Pricing Versioned Revision Details (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/versioned-revise-details`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/versioned-revise-details`
- **Description:** Create revisions of a pricing request with versions for adjustment entities.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `entityName` (String, Required): Name of the entity (e.g., AttributeBasedAdjustment, BundleBasedAdjustment)
  - `id` (String, Required): ID of the record
  - `priceAdjustmentId` or `priceAdjustmentScheduleId` (String, Required): ID of the price adjustment schedule record
  - `productId` (String, Required): Product ID of the record
  - `productSellingModelId` (String, Optional): Product selling model ID
  - `adjustmentType` (String, Required): Type of adjustment (percentage, amount, override)
  - `adjustmentValue` (String, Required): Value for the adjustment
  - `effectiveFrom` (String, Required): Date from when the adjustment is effective
  - `effectiveTo` (String, Optional): Date until when the adjustment is effective
  - `additionalFieldsToValueMap` (Map<String, String>, Optional): Additional fields specific to the entity

---

### 11. Pricing Waterfall (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/waterfall/{lineItemId}/{executionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/waterfall/Gold/2yHdNNEFOZr9jAe4gHS7?tagsToFilter=UnitPrice`
- **Description:** Get the persisted price waterfall that stores the process logs. Provides insights into every step of the pricing process.
- **Available Version:** 60.0
- **Query Parameters:**
  - `tagsToFilter` (String, Optional): Comma-separated tags to filter (Available Version 61.0)
  - `usageType` (String, Optional): Usage type of the waterfall log record (Pricing, Discovery, Rating; default is Pricing) (Available Version 62.0)

---

### 12. Pricing Waterfall (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/core-pricing/waterfall`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/waterfall`
- **Description:** Create a log of price waterfall. Provides insights into every step of the pricing process.
- **Available Version:** 60.0
- **Request Body Fields:**
  - `contextDefinitionVersionId` (String, Optional): Context definition version ID of the pricing procedure
  - `contextMappingId` (String, Optional): Context mapping ID of the pricing procedure
  - `currencyCode` (String): Currency code (e.g., USD)
  - `executionEndTimestamp` (String): End timestamp of execution (ISO 8601 format)
  - `executionId` (String, Required): ID of the execution
  - `executionStartTimestamp` (String): Start timestamp of execution (ISO 8601 format)
  - `lineItemId` (String, Required): ID of the line item
  - `output` (Object): Output containing Subtotal, ListPrice, NetUnitPrice, etc.
  - `waterfall` (Array of Objects): Waterfall step details with:
    - `fieldToTagNameMapping` (Map): Maps field names to tag names
    - `inputParameters` (Map): Input parameters for the step
    - `outputParameters` (Map): Output parameters (e.g., Subtotal, ListPrice, NetUnitPrice)
    - `pricingElement` (Object): Details of the pricing element with adjustments, description, elementType, name
    - `sequence` (Integer): Order in the waterfall

---

### 13. Pricing Simulation Input Variables With Data (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/simulationInputVariablesWithData`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/simulationInputVariablesWithData`
- **Description:** Get details of the pricing simulation input variables along with associated data.
- **Available Version:** 64.0
- **Query Parameters:**
  - `contextDefinitionId` (String, Required, Available Version 64.0): ID or developer name of the context definition
  - `contextMappingId` (String, Required, Available Version 64.0): ID or name of the context mapping that's used
  - `entityId` (String, Required, Available Version 64.0): ID of a quote or an order
  - `expressionSetVersionId` (String, Required, Available Version 64.0): ID of the expression set that starts with `9QM`

---

## PROCEDURE PLAN DEFINITION APIs

### 14. Procedure Plan Definitions (GET, POST)
- **HTTP Methods:** GET, POST
- **URI Path:** `/connect/procedure-plan-definitions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions?isTemplate=true`
- **Description:** Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition.
- **Available Version:** 62.0
- **Request Parameters for GET:**
  - `isTemplate` (Boolean, Optional): Indicates whether to return file-based definitions (true) or database-based definitions (false, default)
- **Request Body Fields for POST:**
  - `description` (String, Optional): Description of the procedure plan definition
  - `developerName` (String, Required if using POST): Developer name of the procedure plan definition
  - `name` (String, Optional): Name of the procedure plan definition
  - `processType` (String, Required, Available Version 63.0): Business process type (Billing, DRO, DeepClone, ProductDiscovery, Revenue Cloud; default is Default)
  - `primaryObject` (String, Required if creating a procedure with rule-based criteria (Optional otherwise)): Primary object for the definition (e.g., Quote, Account, Order). Must be a valid object name, unique on the ProcedurePlanDefinition object.
  - `procedurePlanDefinitionVersions` (Procedure Plan Definition Version Input[], Required): List of versions
    - `active` (Boolean): Active status
    - `contextDefinition` (String): Context definition reference
    - `readContextMapping` (String): Mapping for reading context
    - `saveContextMapping` (String): Mapping for saving context
    - `effectiveFrom` (String): When the version becomes effective
    - `developerName` (String): Developer name for the version
    - `rank` (Integer): Rank/priority of the version

---

### 15. Procedure Plan Definition By ID (GET, PATCH, DELETE)
- **HTTP Methods:** GET, PATCH, DELETE
- **URI Path:** `/connect/procedure-plan-definitions/{procedurePlanDefinitionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions/1FNxx0000004EsOGAU`
- **Description:** Get, update, or delete a procedure plan definition record by using the record ID. Note: Can only delete if it doesn't include any active procedure plan version.
- **Available Version:** 62.0
- **Request Body Fields for PATCH:**
  - `description` (String, Optional): Description for the procedure plan definition
  - `developerName` (String, Required if using POST API): Developer name
  - `name` (String, Optional): Name of the procedure plan definition
  - `primaryObject` (String, Required if using the POST API and creating a procedure with rule-based criteria (Optional otherwise)): Primary object
  - `procedurePlanDefinitionVersions` (Procedure Plan Definition Version Input[], Required): List of versions of a procedure plan definition
  - `processType` (String, Required, Available Version 63.0): Business process type (Billing, DRO, DeepClone, ProductDiscovery, Revenue Cloud; default is Default)
  - `recordId` (String, Required): ID of the procedure plan definition record

---

### 16. Procedure Plan Evaluation By Object (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/procedure-plan-definitions/evaluate`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions/evaluate`
- **Description:** Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details.
- **Available Version:** 62.0
- **Request Body Fields:**
  - `idList` (String[], Required): List of object IDs
  - `evaluationDate` (String, Required): Date when the evaluation is applicable (must be within the date range when the definition is effective)
  - `processType` (String, Optional, Available Version 63.0): Business process type
  - `sectionType` (String[], Optional): Section type. Valid values: PricingProcedure, ProductDiscoveryProcedure, ProductQualificationProcedure, PricingDiscoveryProcedure, DiscountSpreadServiceProcedure, RatingProcedure, Custom, RatingDiscoveryProcedure
  - `subSectionType` (String[], Optional): Sub-section type (e.g., Revenue). The combination of `sectionType` and `subSectionType` must be unique for every procedure plan version.

---

### 17. Procedure Plan Evaluation By Definition Name (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/procedure-plan-definitions/evaluate/{procedurePlanDefinitionName}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions/evaluate/procedurePlanDefinitionName`
- **Description:** Evaluate a procedure plan definition based on the name of a definition to check for prerequisites such as usage type and context mapping details.
- **Available Version:** 62.0
- **Request Body Fields:** Same as Procedure Plan Evaluation By Object

---

### 18. Procedure Plan Version (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/procedure-plan-definitions/{procedurePlanDefinitionId}/version`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions/{procedurePlanDefinitionId}/version`
- **Description:** Create records of a procedure plan version with details.
- **Available Version:** 62.0
- **Request Body Fields:**
  - `active` (Boolean): Indicates whether the procedure plan version is active. You can't edit or delete a procedure plan version that's active
  - `contextDefinition` (String): Context definition reference
  - `developerName` (String): Developer name for the version
  - `effectiveFrom` (String): When the version becomes effective (ISO 8601 format)
  - `effectiveTo` (String, Required): Date and time from when the procedure plan definition version is no longer in effect
  - `inheritedFrom` (String, read-only): Template this procedure plan definition version is created from
  - `procedurePlanSections` (Array): Array of procedure plan sections
    - `isInherited` (Boolean): Whether the section is inherited
    - `procedurePlanOptions` (Array): Options with:
      - `saveContextMapping` (String)
      - `expressionSetDefinition` (String): Reference to expression set
      - `expressionSetLabel` (String)
      - `expressionSetApiName` (String)
      - `logic` (String): Logical operators (e.g., "1 AND 2 AND 3")
      - `priority` (Integer)
      - `procedurePlanCriterion` (Array): Criteria conditions
  - `rank` (Integer): Rank of the version
  - `readContextMapping` (String, Optional): Context mapping for reading
  - `saveContextMapping` (String, Optional): Mapping used to save data from the context definition and populate the mapped object
  - `status` (String, Optional): Status of the procedure plan definition version record

---

### 19. Procedure Plan Version Details (GET, PATCH, DELETE)
- **HTTP Methods:** GET, PATCH, DELETE
- **URI Path:** `/connect/procedure-plan-definitions/versions/{procedurePlanVersionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/procedure-plan-definitions/versions/procedurePlanVersionId`
- **Description:** Get, update, or delete a procedure plan definition version record by using the record ID.
- **Available Version:** 62.0
- **Request Body Fields for PATCH:**
  - `active` (Boolean): Active status
  - `developerName` (String): Developer name
  - `effectiveFrom` (String): Effective from date (ISO 8601 format)
  - `effectiveTo` (String, Required): Date and time from when the procedure plan definition version is no longer in effect
  - `contextDefinition` (String): Context definition
  - `inheritedFrom` (String, read-only): Template this procedure plan definition version is created from
  - `procedurePlanSections` (Array): Section definitions
  - `rank` (Integer): Rank
  - `readContextMapping` (String, Optional): Mapping used to read data from the mapped object and populate the context definition
  - `recordId` (String, Required): ID of the procedure plan definition version record
  - `saveContextMapping` (String, Optional): Mapping used to save data from the context definition and populate the mapped object
  - `status` (String, Optional): Status of the procedure plan definition version record

---

## QUICK REFERENCE - API METHODS BY HTTP VERB

### GET Endpoints
- API Execution Logs
- Pricing Process Execution
- Pricing Process Execution for Line Items
- Pricing Data Sync
- Pricing Recipe
- Pricing Waterfall (retrieve persisted waterfall)
- Pricing Simulation Input Variables With Data
- Procedure Plan Definitions
- Procedure Plan Definition By ID
- Procedure Plan Version Details

### POST Endpoints
- PBE Derived Pricing
- Price Context
- Pricing
- Pricing Recipe Mapping
- Pricing Versioned Revision Details
- Pricing Waterfall (create waterfall log)
- Procedure Plan Definitions
- Procedure Plan Evaluation By Object
- Procedure Plan Evaluation By Definition Name
- Procedure Plan Version

### PATCH Endpoints
- Procedure Plan Definition By ID
- Procedure Plan Version Details

### DELETE Endpoints
- Procedure Plan Definition By ID
- Procedure Plan Version Details

---

## SUMMARY TABLE

| # | Endpoint Name | HTTP Method(s) | URI Path | API Version |
|---|---------------|--------|----------|------------|
| 1 | PBE Derived Pricing | POST | `/connect/core-pricing/pbeDerivedPricingSourceProduct` | 61.0 |
| 2 | Price Context | POST | `/connect/core-pricing/price-contexts/{contextId}` | 60.0 |
| 3 | Pricing | POST | `/connect/core-pricing/pricing` | 60.0 |
| 4 | API Execution Logs | GET | `/connect/core-pricing/apiexecutionlogs/{executionId}` | 63.0 |
| 5 | Pricing Process Execution | GET | `/connect/core-pricing/pricing-process-execution/{executionId}` | 63.0 |
| 6 | Pricing Process Execution for Line Items | GET | `/connect/core-pricing/pricing-process-execution/lineitems/{executionId}/{executionType}` | 63.0 |
| 7 | Pricing Data Sync | GET | `/connect/core-pricing/sync/{pricingSyncOrigin}` | 60.0 |
| 8 | Pricing Recipe | GET | `/connect/core-pricing/recipe` | 60.0 |
| 9 | Pricing Recipe Mapping | POST | `/connect/core-pricing/recipe/mapping` | 60.0 |
| 10 | Pricing Versioned Revision Details | POST | `/connect/core-pricing/versioned-revise-details` | 60.0 |
| 11 | Pricing Waterfall | GET | `/connect/core-pricing/waterfall/{lineItemId}/{executionId}` | 60.0 |
| 12 | Pricing Waterfall | POST | `/connect/core-pricing/waterfall` | 60.0 |
| 13 | Pricing Simulation Input Variables With Data | GET | `/connect/core-pricing/simulationInputVariablesWithData` | 64.0 |
| 14 | Procedure Plan Definitions | GET, POST | `/connect/procedure-plan-definitions` | 62.0 |
| 15 | Procedure Plan Definition By ID | GET, PATCH, DELETE | `/connect/procedure-plan-definitions/{procedurePlanDefinitionId}` | 62.0 |
| 16 | Procedure Plan Evaluation By Object | POST | `/connect/procedure-plan-definitions/evaluate` | 62.0 |
| 17 | Procedure Plan Evaluation By Definition Name | POST | `/connect/procedure-plan-definitions/evaluate/{procedurePlanDefinitionName}` | 62.0 |
| 18 | Procedure Plan Version | POST | `/connect/procedure-plan-definitions/{procedurePlanDefinitionId}/version` | 62.0 |
| 19 | Procedure Plan Version Details | GET, PATCH, DELETE | `/connect/procedure-plan-definitions/versions/{procedurePlanVersionId}` | 62.0 |

---

## Document Info
- **Source:** Revenue Cloud Developer Guide v264 (Winter '27, API v68.0)
- **Section:** Salesforce Pricing Business APIs (pages 441-528)
- **Total Endpoints:** 19 unique endpoints (with some supporting multiple HTTP methods)
- **Base URL:** `https://yourInstance.salesforce.com/services/data/v68.0`
