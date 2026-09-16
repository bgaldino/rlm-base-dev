# Salesforce Transaction Management APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v68.0 (Winter '27)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Transaction Management APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v264. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

Transaction Management covers the full quote-to-cash lifecycle: placing and managing sales transactions (quotes and orders), managing asset lifecycle events (amendments, cancellations, renewals, upgrades, downgrades, swaps), and creating and updating ramp deals. As of API v63.0, the **Place Sales Transaction** API (`/connect/rev/sales-transaction/actions/place`) supersedes the deprecated `/commerce/quotes/actions/place` and `/commerce/sales-orders/actions/place` paths. Grounded against the 264 (Winter '27) Developer Guide snapshot, the actual superseding resource lives under the `/connect/rev/sales-transaction/`, `/connect/revenue/transaction-management/`, and `/connect/revenue-management/` resource families — not under a `/commerce/sales-transactions/` path as a prior extraction of this document assumed. Path corrections below are cited per endpoint.

---

## SALES TRANSACTION ACTIONS

The Sales Transactions APIs are the primary interface for creating and managing quotes and orders in Revenue Cloud. A single "sales transaction" represents either a quote or an order depending on the context.

### 1. Place Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/rev/sales-transaction/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/rev/sales-transaction/actions/place`
- **Description:** Create a sales transaction — a quote or an order — with integrated pricing and configuration. Also update an order or a quote, and insert/update/delete order or quote line items to calculate estimated tax. Supports grouping quote/order lines by location, work type, or department when groups are enabled. Up to 1000 quote line items per quote and 1000 order products per order; up to 3000 line item attributes per quote or order. This API does **not** support creating an amendment, renewal, or cancellation quote/order — use the dedicated amendment/renewal/cancellation APIs or invocable actions instead. The API saves and commits the quote/order header first, then processes configuration, pricing, and persistence for line items and groups; if a later step fails, the header is not rolled back.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `contextDetails` (Context Input, Required if `graph` is not specified): Context details created for the sales transaction.
  - `graph` (Object Graph Input, Required if `contextDetails` is not specified): The sObject graph of the sales transaction to ingest — create, update, or delete operations against Quote, QuoteLineItem, Order, OrderItem, QuoteLineGroup, OrderItemGroup, and extended-context custom objects.
  - `pricingPref` (String, Optional): Pricing preference — `Force`, `Skip`, or `System` (default `System`).
  - `catalogRatesPref` (String, Optional): `Fetch` or `Skip` (default `Skip`) — retrieval of rate card entries for usage-based sales items. Available when Usage-Based Selling is enabled.
  - `configurationPref` (Configurator Preference Input, Optional): Configuration preference during the quote/order process.
  - `taxPref` (String, Optional, **Available Version 65.0**): Valid value `Skip` — skips tax calculation for the request. Tax calculation runs by default if omitted.
  - `groupRampAction` (String, Optional, **Available Version 65.0**): Action to perform on group ramp segments — `AddProducts`, `DeleteProducts`, `EditGroup`, `EditRampSchedule`, `DeleteSegment`, or `ConvertToNonRampedGroup`. Converts a non-ramped group into a ramped group and vice versa.

*Grounded against: `connect_resources_place_sales_transaction.htm.md`, `connect_requests_place_sales_transaction_input.htm.md`*

---

### 2. Read Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue/transaction-management/sales-transactions/actions/read`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue/transaction-management/sales-transactions/actions/read`
- **Description:** Retrieve sales transaction data efficiently from an initialized or hydrated context. Use when you need a full transaction snapshot rather than individual field reads via SOQL.
- **Available Version:** 65.0
- **Request Body Fields:**
  - `contextId` (String, Required): ID of the context to retrieve data records from.
  - `queryTags` (List<String>, Optional): List of objects to retrieve from the context (e.g., `Quote`, `QuoteLineItem`, `Product`).
  - `sobjectFieldMap` (Map<String, List<String>>, Optional, **Available Version 67.0**): Maps an sObject name to a list of field names to query; an empty list queries all fields on that object.
  - `filters` (List<Sales Transaction Filter Condition Input>, Optional, **Available Version 67.0**): Filter conditions (sObjectName, fieldName, operator, operands) to query the context data.

*Grounded against: `connect_resources_read_sales_transaction.htm.md`, `connect_requests_read_sales_transaction_input.htm.md`*

---

### 3. Clone Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/rev/sales-transaction/actions/clone`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/rev/sales-transaction/actions/clone`
- **Description:** Create a clone of a sales transaction — a quote or an order. Supports cloning `Quote`, `QuoteLineItem`, `OrderItem`, `QuoteLineGroup`, `Order`, and `OrderItemGroup` records with their related records and configurations. Cloning a quote line group or order item group record clones all items within that group.
- **Available Version:** 64.0
- **Request Body Fields:**
  - `recordIds` (String[], Required): ID of the record to clone. Only a single record ID is supported despite the array type.
  - `salesTransactionId` (String, Required): ID of the sales transaction related to the record IDs to clone.
  - `options` (Clone Options Input, Optional, **Available Version 65.0**):
    - `recordTypeId` (String, Optional): Record type ID for the cloned record.
    - `lineScope` (String, Optional): `AllLines` — clone all line items in a ramped group; `RampedLinesOnly` — clone only ramped line items, generating a new segment identifier with date continuity. Only the last ramp segment can be cloned.

*Grounded against: `connect_resources_clone_sales_transaction.htm.md`, `connect_requests_clone_sales_transaction_input.htm.md`, `connect_requests_clone_options_input.htm.md`*

---

### 4. Instant Pricing (POST)
- **HTTP Method:** POST
- **URI Path:** `/industries/cpq/quotes/actions/get-instant-price`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/industries/cpq/quotes/actions/get-instant-price`
- **Description:** Fetch instant pricing data for the quote/order line data grid and associated summary component. Creates a new pricing context or updates an existing one based on the provided `contextId`. Also supports grouping quote/order lines by criteria (create, delete, move, ungroup).
- **Available Version:** 60.0 *(corrected — a prior extraction of this document stated 57.0)*
- **Request Body Fields:**
  - `contextId` (String, Optional): ID generated by the context service; a new context is created if omitted.
  - `correlationId` (String, Optional): Client-generated ID for tracking multiple related API requests.
  - `records` (Object with Reference Input[], Required): List of quote/order/line-item pricing data to fetch, expressed as sObject-graph-style records with `referenceId` and `record.attributes.type`/`method`.

*Grounded against: `connect_resources_cpq_instant_pricing.htm.md`*

---

### 5. Preview Approval (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/advanced-approvals/approval-submission/preview`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/advanced-approvals/approval-submission/preview`
- **Description:** Preview the approval levels of a record and associated level details, approval chains, approvers, and conditions before submitting the record for approval — for example, previewing approval levels for a quote before submission. **Note:** this endpoint's canonical domain in the 264 Developer Guide is **Advanced Approvals**, not Transaction Management; it is retained here because it is part of the quote-to-cash workflow.
- **Available Version:** 65.0
- **Request Body Fields:**
  - `flowApiName` (String, Required): API name of the auto-launched flow.
  - `objectApiName` (String, Required): API name of the object to preview approvals for (e.g., `Quote`).
  - `recordId` (String, Required): ID of the record to preview approvals for.
  - `inputParameters` (Map<String, Object>, Optional, **Available Version 67.0**): Input parameters to preview (e.g., `approverComments`, `requestType`).

*Grounded against: `connect_resources_preview_approvals.htm.md`, `connect_requests_preview_approval_input.htm.md`*

---

### 6. Get Eligible Promotions (POST)
- **HTTP Method:** POST
- **URI Path:** `/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions`
- **Description:** Get eligible promotions for line items within a quote or an order. Accepts line item IDs and a sales transaction ID, then initializes the promotion-evaluation context by filtering on the specified line items. Introduced in Spring '26 (v66.0).
- **Available Version:** 66.0
- **Request Body Fields:**
  - `salesTransactionId` (String, Required): The sales transaction ID (order ID or quote ID) for the promotion evaluation.
  - `lineItemIds` (String[], Required): List of line item IDs to evaluate for promotions; the object type is auto-determined from the sales transaction ID.

*Grounded against: `connect_resources_get_eligible_promotions.htm.md`, `connect_requests_get_eligible_promotions_input.htm.md`*

---

### 7. Retrieve Sales Transaction API Errors (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/revenue/transaction-management/sales-transactions/actions/place/{trackerId}/errors`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue/transaction-management/sales-transactions/actions/place/16PRM0000004DBq/errors`
- **Description:** Retrieve asynchronous error details associated with a sales transaction request placed via the [Place Sales Transaction](#1-place-sales-transaction-post) API. Returns detailed error status and a retryable payload, plus the list of `rollbackedReferenceIds` — synthetic or reference IDs rolled back when the batch fails. Does not return non-blocking warnings such as configuration or tax warnings.
- **Available Version:** 66.0
- **Path Parameters:**
  - `trackerId` (String, Required): The async tracker/batch ID returned by the Place Sales Transaction request.
- **Request Parameters (query):**
  - `includeRetryablePayload` (Boolean, Optional, default `false`): Whether to return a subset of the original Place Sales Transaction payload errors.

*Grounded against: `connect_resources_retrieve_place_sales_transaction_error.htm.md`*

---

### 8. Place Supplemental Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/rev/sales-transaction/actions/place-supplemental-transaction`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/rev/sales-transaction/actions/place-supplemental-transaction`
- **Description:** Create a supplemental order or change orders after they've been submitted for processing — for example, during fulfillment. The original order must not be assetized. If Billing is enabled and configured for the order, the original order must not already be billed. If Dynamic Revenue Orchestration (DRO) is enabled and configured, the original order must not have reached the point-of-no-return milestone (if not reached, the fulfillment plan is frozen).
- **Available Version:** 64.0
- **Request Body Fields:**
  - `relatedSalesTransactionId` (String, Required): ID of the related/original sales transaction to supplement.
  - `pricingPref` (String, Optional): `Force`, `Skip`, or `System`. If `Force` or `System`, the supplemental order can differ in pricing from the original order.
  - `supplementalGraph` (Object Graph Input, Optional): sObject graph with the additional changes to ingest. The record `attributes.method` must be `PATCH`, and the record ID must be the ID of the original order/order item being supplemented.

*Grounded against: `connect_resources_place_supplemental_transaction.htm.md`*

---

## ASSET LIFECYCLE APIs

Asset Lifecycle APIs manage changes to existing assets after an order has been activated and assets have been created. These operations generate new sales transactions (quotes/orders) representing the requested change.

### 9. Asset Amendment (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/amend`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/assets/actions/amend`
- **Description:** Initiate and execute the amendment of a quote or an order. Requires the **InitiateAmend** API permission set. For usage products, creating an order directly (`outputRecordType` = `Order`) is not currently supported, since the direct-to-order flow can create Order Products without required Rate Card Entry records and cause order activation to fail — use a two-step flow instead: call this API with `outputRecordType` = `Quote`, then create an order from that amendment quote.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 57.0)*
- **Request Body Fields:**
  - `assetIds` (String[], Required): IDs of the assets to add to the amendment record.
  - `amendmentStartDate` (String, Required): Start date of the amendment (ISO 8601 datetime).
  - `contractId` (String, Optional): ID of the Contract record to sync with the amendment quote.
  - `opportunityId` (String, Optional): ID of the Opportunity record to sync with the amendment quote.
  - `outputRecordId` (String, Optional): ID of the quote or order record to add the assets to.
  - `outputRecordType` (String, Required): Type of amendment record to create, e.g. `Quote`. For usage products, set to `Quote` — usage-related records are copied in the quote action flow, not the amend order flow.
  - `quantityChange` (Double, Required): Quantity to add to or reduce from the asset's existing quantity.

*Grounded against: `connect_resources_assets_amend.htm.md`, `connect_requests_amend_input.htm.md`*

---

### 10. Asset Cancellation (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/cancel`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/assets/actions/cancel`
- **Description:** Initiate and execute the cancellation of an asset. Requires the **InitiateCancellation** API permission set.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 57.0)*
- **Request Body Fields:**
  - `assetIds` (String[], Required): IDs of the assets to cancel. All assets in a request must belong to the same price book.
  - `cancellationDate` (String, Required): Effective date of the cancellation (ISO 8601 datetime).
  - `contractId` (String, Optional): ID of the Contract record to sync with the cancellation quote.
  - `opportunityId` (String, Optional): ID of the Opportunity record to sync with the cancellation quote.
  - `outputRecordId` (String, Optional): ID of the quote or order to cancel.
  - `outputRecordType` (String, Required): Type of cancellation record to create.

*Grounded against: `connect_resources_assets_cancel.htm.md`, `connect_requests_cancel_input.htm.md`*

---

### 11. Asset Renewal (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/renew`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/assets/actions/renew`
- **Description:** Initiate and execute the renewal of an asset. Requires the **InitiateRenewal** API permission set.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 57.0)*
- **Request Body Fields:**
  - `assetIds` (String[], Required): IDs of the assets to renew.
  - `contractId` (String, Optional): ID of the Contract record to sync with the renewal.
  - `opportunityId` (String, Optional): ID of the Opportunity record to sync with the renewal quote.
  - `outputRecordId` (String, Optional): ID of the Quote or Order record to renew.
  - `outputRecordType` (String, Required): Type of renewal record to create.
  - `renewalEndDate` (String, Optional): End date of the renewal process for the assets.
  - `renewalStartDate` (String, Optional): Start date of the renewal process. Required for early asset renewals and for renewing expired assets (today's date or a future date).

*Grounded against: `connect_resources_assets_renew.htm.md`, `connect_requests_renew_input.htm.md`*

---

### 12. Initiate Upgrade (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/transaction-management/assets/actions/upgrade`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/upgrade`
- **Description:** New in Spring '26 (v66.0). Move a lower-tier product to a higher-tier product. Tracked as an upgrade request with linked asset actions and quote/order line linkage for reporting and auditing. Creates an amendment quote and order with order actions and quote action subtypes. On assetization, the original asset receives an asset action with an `Upgrade` (or equivalent) business category, and the new asset is created with a linked "upgraded to" asset action.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `swapStartDate` (String, Required): Amendment start date for the upgrade action.
  - `outputRecordType` (String, Required): Record type of the output for the upgrade.
  - `swapGroups` (Swap Group[], Required): Groups containing the outgoing asset(s) (`outGroup.swapAssets`, each with `assetId`/`quantity`) and the incoming product graph (`inGroup.graphId`/`records`).
  - `contractId` (String, Optional): ID of the contract record to upgrade.
  - `opportunityId` (String, Optional): ID of the opportunity record to upgrade.

*Grounded against: `connect_resources_initiate_upgrade.htm.md`. Added — not present in the prior v66.0 extraction of this document.*

---

### 13. Initiate Downgrade (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/transaction-management/assets/actions/downgrade`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/downgrade`
- **Description:** New in Spring '26 (v66.0). Move to a lower-tier or lower-value product. Tracked as a downgrade request with linked asset actions and quote/order line linkage for reporting and auditing. Creates an amendment quote and order with downgrade-specific order actions and quote action subtypes. On assetization, the original asset receives a `Downgrade` (or equivalent) asset action, linked to a "downgraded to" asset action on the new asset.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `swapStartDate` (String, Required): Amendment start date for the downgrade action.
  - `outputRecordType` (String, Required): Record type of the output for the downgrade.
  - `swapGroups` (Swap Group[], Required): Groups containing the outgoing asset(s) (`outGroup.swapAssets`) and the incoming product graph (`inGroup.graphId`/`records`).
  - `contractId` (String, Optional): ID of the contract record to downgrade.
  - `opportunityId` (String, Optional): ID of the opportunity record to downgrade.

*Grounded against: `connect_resources_initiate_downgrade.htm.md`. Added — not present in the prior v66.0 extraction of this document.*

---

### 14. Initiate Swap (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/revenue/transaction-management/assets/actions/swap`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/swap`
- **Description:** New in Spring '26 (v66.0). Exchange one product for another of equivalent or different value. Tracked as a swap request with linked asset actions and a net-zero order total where applicable. Creates an amendment quote and order with order actions and quote action subtypes. Supports use cases such as trading unused licenses for credits or moving spend between products while preserving contract intent. On assetization, the source asset receives a `Swap` (reduced quantity) asset action, linked to a "swapped in" asset action on the new asset.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `swapStartDate` (String, Required): Amendment start date for the swap action.
  - `outputRecordType` (String, Required): Record type of the output for the swap.
  - `swapGroups` (Swap Group[], Required): Groups containing the outgoing asset(s) (`outGroup.swapAssets`) and the incoming product graph (`inGroup.graphId`/`records`).
  - `contractId` (String, Optional): ID of the contract record to swap.
  - `opportunityId` (String, Optional): ID of the opportunity record to swap.

*Grounded against: `connect_resources_initiate_swap.htm.md`. Added — not present in the prior v66.0 extraction of this document.*

---

## RAMP DEAL APIs

Ramp deals allow structured, multi-period pricing commitments on a single quote/order line — for example, a customer who starts with a free trial segment and then commits to a yearly term. These APIs are applicable to **line ramps**; for **group ramps**, use the Place Sales Transaction API's `groupRampAction` property instead (see [Place Sales Transaction](#1-place-sales-transaction-post)).

### 15. Create Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-create`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CfIGAU/actions/ramp-deal-create`
- **Description:** Create a ramp deal for a customer on a product, generating segments based on term, segment type, and trial details. The response includes the context ID and updated context object for the sales transaction; call [Place Sales Transaction](#1-place-sales-transaction-post) with that context ID to apply the ramp deal updates.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 63.0 and a `/commerce/sales-transactions/ramp-deals` path)*
- **Path Parameters:**
  - `resourceId` (String, Required): ID of the quote line item, order item, or context.
- **Request Body Fields:**
  - `transactionId` (String, Required): ID of the sales transaction being configured (quote or order).
  - `transactionLineId` (String, Required): Quote line item ID or order item ID the price ramp is created for.
  - `subscriptionTerm` (Integer, Required): Subscription length of the term-defined product.
  - `subscriptionTermUnit` (String, Required): Unit of time for the subscription length. Valid value: `MONTHS`.
  - `segmentType` (String, Required): `FREE_TRIAL`, `CUSTOM`, or `YEARLY`.
  - `trialTerm` (Integer, Optional): Length of the trial period, if any.
  - `trialTermUnit` (String, Optional — required if `trialTerm` is specified): Valid value: `DAYS`.
  - `executionSettings` (Execution Settings Input[], Optional): Settings to run pricing or configuration rules (`executePricing`, `executeConfigRules`).

*Grounded against: `connect_resources_create_ramp_deal.htm.md`, `connect_requests_create_ramp_deal_input.htm.md`*

---

### 16. Update Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-update`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9/actions/ramp-deal-update`
- **Description:** Modify a ramp deal when a segment has quantity, discount, or (for a trial or custom segment) a date change. Custom segments can be updated during the initial sale, before assetization. Returns the updated context; call [Place Sales Transaction](#1-place-sales-transaction-post) with the context ID to apply the updates.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 63.0 and only supported a flat `commitment` update)*
- **Request Body Fields:**
  - `addedNodes` (Context Node Input[], Required): Nodes to add, each keyed by a `contextNodePath` (context ID → quote/order ID → line item ID) with a `contextNode` payload (e.g. `Discount`, `Quantity`, `ItemSegmentName`, `StartDate`, `EndDate`).
  - `updatedNodes` (Context Node Input[], Required): Nodes to update, addressed the same way.
  - `deletedNodes` (Context Node Input[], Required): Nodes to delete, addressed the same way.
  - `executionSettings` (Execution Settings Input[], Optional): Settings to run pricing or configuration rules.

*Grounded against: `connect_resources_update_ramp_deal.htm.md`, `connect_requests_update_ramp_deal_input.htm.md`*

---

### 17. Delete Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-delete`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CfIGAU/actions/ramp-deal-delete`
- **Description:** Delete a ramp deal to convert a ramped product back to a single quote line item or order item. Returns the updated context; call [Place Sales Transaction](#1-place-sales-transaction-post) with the context ID to apply the deletion.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 63.0)*
- **Path Parameters:**
  - `resourceId` (String, Required): ID of the context.
- **Request Body Fields:**
  - `rampDealIds` (String[], Required): Ramp identifier(s) on the quote line item or order item.

*Grounded against: `connect_resources_delete_ramp_deal.htm.md`, `connect_requests_delete_ramp_deal_input.htm.md`*

---

### 18. View Ramp Deal (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-view`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CSOGA2/actions/ramp-deal-view?transactionId=0Q0xx0000004CDxCAM&transactionLineId=0QLxx0000004CSOGA2`
- **Description:** View a ramp deal related to a quote line item or an order item, retrieving its segments if the ramp deal already exists.
- **Available Version:** 62.0 *(corrected — a prior extraction of this document stated 63.0 and described a filterable list GET on `/commerce/sales-transactions/ramp-deals` rather than a per-resource view)*
- **Path Parameters:**
  - `resourceId` (String, Required): ID of the quote line item, order item, or context.
- **Request Parameters (query):**
  - `transactionId` (String, Required): ID of the quote or order, needed to hydrate the context and retrieve the quote/order lines.
  - `transactionLineId` (String, Required): ID of the quote or order line to retrieve segmented details for.

*Grounded against: `connect_resources_view_ramp_deal.htm.md`*

---

## PROMOTIONS API

### 19. Create Promotions (GET, POST, PUT) — v66.0
- **HTTP Method:** GET, POST, PUT
- **URI Path:** `/global-promotions-management/promotions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/global-promotions-management/promotions`
- **Description:** New in Spring '26 (v66.0). Create, retrieve, or update a Unified Promotion — including `promotionDetails` (eligibility, limits, rule library) and `rules` (event configuration, reward configuration, selling-model discounts). Get rewards based on a product selling model template. Listed alongside the Transaction Management REST references in the 264 Developer Guide; full property reference lives under the Loyalty/Unified Promotions Connect API.
- **Available Version:** 66.0
- **Request Body Fields (POST/PUT — create/update a promotion):**
  - `promotionDetails` (Object, Required): Promotion header — `displayName`/`name`, `isAutomatic`, `isEmailActivated`, `startDateTime`, `promotionEligibility` (eligible customer events, enrollment period, eligible products), `promotionLimits`, `ruleLibrary` (`id`/`name`), `additionalFieldValues`.
  - `rules` (Object[], Required): Promotion rules — `journalType`, `priority`, `ruleName`, `templateName`, `eventConfiguration` (Array), `rewardConfiguration` (Array of `scope`/`scopeDetails`/`rewardDetailsList`/`childProducts`/`type`/`isPrimaryReward`).
  - The snapshot doesn't document distinct Path/Query parameters for GET or PUT, or a separate Properties table for this resource — it defers the full request/response schema to the [Loyalty/Unified Promotions Connect API](https://developer.salesforce.com/docs/atlas.en-us.264.0.loyalty.meta/loyalty/connect_resources_unified_promotions.htm).

*Grounded against: `connect_resources_create_promotions.htm.md`. Added — not present in the prior v66.0 extraction of this document.*

---

## DEPRECATED APIs (v63.0+)

The following endpoints were deprecated in v63.0 and replaced by the [Place Sales Transaction](#1-place-sales-transaction-post) API. They are retained in the collection for backward compatibility but should not be used in new integrations. Both endpoints cap at 300 transaction line items.

### 20. Place Order [DEPRECATED v63] (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-orders/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/commerce/sales-orders/actions/place`
- **Description:** **Deprecated as of API v63.0.** Place a sales order. Requires the PlaceOrder API permission set. Replaced by [Place Sales Transaction](#1-place-sales-transaction-post) (`/connect/rev/sales-transaction/actions/place`).
- **Available Version:** 60.0 (Deprecated as of v63.0 — use `/connect/rev/sales-transaction/actions/place` instead)

*Grounded against: `connect_resources_place_order.htm.md`*

---

### 21. Place Quote [DEPRECATED v63] (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/quotes/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v68.0/commerce/quotes/actions/place`
- **Description:** **Deprecated as of API v63.0.** Create a quote to discover and price products/services; insert, update, or delete quote line items. Requires the "Create on Quotes" user permission. Replaced by [Place Sales Transaction](#1-place-sales-transaction-post) (`/connect/rev/sales-transaction/actions/place`).
- **Available Version:** 60.0 (Deprecated as of v63.0 — use `/connect/rev/sales-transaction/actions/place` instead)

*Grounded against: `connect_resources_place_quote.htm.md`*

---

## Typical Transaction Workflows

### Quote-to-Cash (Simple)
```
1. Instant Pricing           → Preview prices for selected products
2. Place Sales Transaction   → Create quote with line items
3. Preview Approval          → Check if discounts require approval
4. [Approval workflow]       → If triggered, wait for approval
5. Place Sales Transaction   → Convert approved quote to order
```

### Asset Lifecycle (Amendment)
```
1. Query assets              → Find the customer's active asset (SOQL)
2. Asset Amendment           → Submit amendment request (assetIds, amendmentStartDate, quantityChange)
3. Read Sales Transaction    → Review the generated amendment quote/order
4. [Activate order]          → Asset is updated upon activation
```

### Asset Lifecycle (Upgrade / Downgrade / Swap)
```
1. Query assets              → Find the customer's active asset (SOQL)
2. Initiate Upgrade/Downgrade/Swap → Submit swapGroups (outgoing asset + incoming product graph)
3. Read Sales Transaction    → Review the generated amendment quote/order and linked asset actions
4. [Activate order]          → Source asset is relinked and the new asset is assetized
```

### Ramp Deal
```
1. Create Ramp Deal          → Define segments on a quote/order line (term, segment type, trial)
2. Place Sales Transaction   → Apply the returned context ID to persist the ramp
3. View Ramp Deal            → Track segment status over time
4. Update Ramp Deal          → Adjust segments (added/updated/deleted nodes) if renegotiated
```

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `68.0`) | Manual setup |
| `{{defaultAccountId}}` | Default account record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |
| `{{assetId}}` | Asset record ID for lifecycle operations | Set by test scripts after order activation |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Discover and price products before placing transactions.
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Configure complex bundles before placing.
- **[Pricing APIs](pricing-business-apis-v68.md)** — Pricing procedures and waterfall details.
- **[Billing APIs](billing-business-apis-reference.md)** — Invoices, payments, and credit memos generated after order activation.
- **[Usage Management APIs](usage-management-apis-reference.md)** — Track usage against assets created by transaction orders.

---

*Reference for: Agentforce Revenue Management APIs v68.0 (Winter '27) | Salesforce Revenue Cloud Developer Guide v264*
