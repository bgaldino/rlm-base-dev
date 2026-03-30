# Salesforce Transaction Management APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Transaction Management APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

Transaction Management covers the full quote-to-cash lifecycle: placing and managing sales transactions (quotes and orders), managing asset lifecycle events (amendments, cancellations, renewals), and creating and updating ramp deals. In Spring '26 (v66.0), the `/commerce/sales-transactions/` path supersedes the deprecated `/commerce/quotes/` and `/commerce/sales-orders/` paths.

---

## SALES TRANSACTION ACTIONS

The Sales Transactions APIs are the primary interface for creating and managing quotes and orders in Revenue Cloud v66.0. A single "sales transaction" represents either a quote or an order depending on the context.

### 1. Place Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/place`
- **Description:** Create and place a new sales transaction — a quote or order — for an account. This is the primary endpoint for Quote-to-Cash flows. The request includes account context, line items with products and quantities, pricing information, and optional term and selling model overrides. Returns the created transaction record with pricing calculated.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `accountId` (String, Required): Salesforce ID of the account. Use `{{defaultAccountId}}`.
  - `effectiveDate` (String, Required): Date the transaction takes effect (ISO 8601, e.g., `"2026-03-26"`)
  - `currencyCode` (String, Optional): ISO 4217 currency code (e.g., `"USD"`)
  - `lineItems` (Array, Required): List of line item objects, each containing:
    - `productId` (String): Salesforce ID of the product
    - `quantity` (Integer): Quantity to order
    - `term` (Integer, Optional): Term length in months for subscription products
    - `sellingModelId` (String, Optional): ID of the selling model to apply

---

### 2. Read Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/read`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/read`
- **Description:** Retrieve a complete, hydrated view of an existing sales transaction including all line items, pricing breakdown, approval status, and lifecycle state. Use when you need a full transaction snapshot rather than individual field reads via SOQL.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `transactionId` (String, Required): Salesforce ID of the sales transaction to read

---

### 3. Clone Sales Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/clone`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/clone`
- **Description:** Create a copy of an existing sales transaction, optionally for a different account. Cloning preserves the original line item structure, product selections, and configuration, allowing rapid creation of similar quotes for multiple accounts.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `sourceTransactionId` (String, Required): Salesforce ID of the transaction to clone
  - `newAccountId` (String, Optional): Account ID for the cloned transaction (if different from the source)

---

### 4. Instant Pricing (POST)
- **HTTP Method:** POST
- **URI Path:** `/industries/cpq/quotes/actions/get-instant-price`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/industries/cpq/quotes/actions/get-instant-price`
- **Description:** Get real-time pricing for one or more line items without creating a persistent transaction record. Returns calculated prices based on the account, product, quantity, and current pricing configuration. Use for price previews, shopping cart totals, and pricing validations before committing to a full quote.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `accountId` (String, Required): Salesforce ID of the account context. Use `{{defaultAccountId}}`.
  - `lineItems` (Array, Required): Line items to price, each containing:
    - `productId` (String): Salesforce ID of the product
    - `quantity` (Integer): Quantity to price

---

### 5. Preview Approval (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/preview-approval`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/preview-approval`
- **Description:** Evaluate whether a sales transaction would trigger approval workflows without actually submitting for approval. Returns the approval steps that would be initiated, the approvers who would be notified, and the criteria that matched. Use to give sales reps advance notice before submitting a quote with discount violations.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `transactionId` (String, Required): Salesforce ID of the transaction to preview approval for

---

### 6. Get Eligible Promotions (POST) — v66.0
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/get-eligible-promotions`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/get-eligible-promotions`
- **Description:** Retrieve all promotions that can be applied to an existing sales transaction based on the current line items, account, and effective date. New in Spring '26 (v66.0). Returns promotion details including discount type, amount, and applicable line items. Use before finalizing a quote to surface available discounts.
- **Available Version:** 66.0
- **Request Body Fields:**
  - `transactionId` (String, Required): Salesforce ID of the transaction to evaluate promotions for
  - `effectiveDate` (String, Required): Date to use for promotion eligibility evaluation (ISO 8601)

---

### 7. Retrieve API Errors (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/sales-transactions/api-errors`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/api-errors`
- **Description:** Retrieve logged errors from recent sales transaction API calls. Use for diagnostics when a place, read, or clone operation fails without a clear error message. Returns structured error records with error codes, messages, and the associated transaction context.
- **Available Version:** 63.0

---

### 8. Place Supplemental Transaction (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/actions/place-supplemental`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/actions/place-supplemental`
- **Description:** Create a supplemental transaction against an existing parent transaction. Supplemental transactions represent changes to an in-flight quote or order — such as adding line items or updating quantities — without creating a full replacement transaction. Use for mid-cycle amendments and modifications.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `parentTransactionId` (String, Required): Salesforce ID of the parent transaction
  - `transactionType` (String, Required): Type of supplemental change — e.g., `"AMENDMENT"`, `"CANCELLATION"`, `"RENEWAL"`
  - `lineItems` (Array, Required): Line items representing the change, each containing:
    - `productId` (String): Salesforce ID of the product
    - `quantity` (Integer): Quantity for this change
    - `changeType` (String): Type of change — `"ADD"`, `"REMOVE"`, or `"UPDATE"`

---

## ASSET LIFECYCLE APIs

Asset Lifecycle APIs manage changes to existing assets after an order has been activated and assets have been created. These operations generate new sales transactions (quotes/orders) representing the requested change.

### 9. Asset Amendment (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/amend`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/revenue-management/assets/actions/amend`
- **Description:** Initiate an amendment to an existing asset — for example, changing the quantity, upgrading a product, or modifying contract terms mid-cycle. Creates a new amendment transaction that, when activated, updates the asset record. Prorates any price changes from the amendment effective date.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `assetId` (String, Required): Salesforce ID of the asset to amend. Use `{{assetId}}`.
  - `effectiveDate` (String, Required): Date the amendment takes effect (ISO 8601)
  - `changes` (Array, Required): List of field changes to apply, each containing:
    - `fieldName` (String): API name of the field to change (e.g., `"Quantity"`)
    - `newValue` (Any): New value for the field

---

### 10. Asset Cancellation (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/cancel`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/revenue-management/assets/actions/cancel`
- **Description:** Initiate a cancellation of an existing asset. Creates a cancellation transaction that, when activated, terminates the asset and triggers any applicable proration or refund calculations. The cancellation date determines the billing cutoff for usage-based products.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `assetId` (String, Required): Salesforce ID of the asset to cancel. Use `{{assetId}}`.
  - `cancellationDate` (String, Required): Effective date of the cancellation (ISO 8601)
  - `reason` (String, Optional): Reason for cancellation (e.g., `"CUSTOMER_REQUEST"`, `"NON_PAYMENT"`)

---

### 11. Asset Renewal (POST)
- **HTTP Method:** POST
- **URI Path:** `/connect/revenue-management/assets/actions/renew`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/revenue-management/assets/actions/renew`
- **Description:** Initiate a renewal of an existing asset before it expires. Creates a renewal transaction extending the asset's term. Current pricing is applied unless overridden; any price changes since the original order are reflected in the renewed asset.
- **Available Version:** 57.0
- **Request Body Fields:**
  - `assetId` (String, Required): Salesforce ID of the asset to renew. Use `{{assetId}}`.
  - `renewalDate` (String, Required): Start date for the renewed term (ISO 8601)
  - `renewalTerm` (Integer, Required): Duration of the new term in months

---

## RAMP DEAL APIs

Ramp deals allow structured, multi-period pricing commitments — for example, a customer who starts with 100 seats in year one and commits to 150 in year two. Ramp segments define each commitment period.

### 12. Create Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/ramp-deals`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/ramp-deals`
- **Description:** Create a new ramp deal with multiple commitment segments. Each segment defines a time range and quantity or revenue commitment. Returns the ramp deal record with the generated segment structure.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `name` (String, Required): Display name for the ramp deal
  - `accountId` (String, Required): Salesforce ID of the account. Use `{{defaultAccountId}}`.
  - `startDate` (String, Required): Overall ramp deal start date (ISO 8601)
  - `endDate` (String, Required): Overall ramp deal end date (ISO 8601)
  - `rampSegments` (Array, Required): List of commitment segments, each containing:
    - `segment` (Integer): Segment number (sequential, starting at 1)
    - `startDate` (String): Segment start date (ISO 8601)
    - `endDate` (String): Segment end date (ISO 8601)
    - `commitment` (Number): Commitment value for this segment (quantity or revenue)

---

### 13. Update Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/ramp-deals/actions/update`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/ramp-deals/actions/update`
- **Description:** Update the commitment values for one or more segments in an existing ramp deal. Use when a customer renegotiates their ramp schedule. Only the specified segments are updated; all other segments remain unchanged.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `rampDealId` (String, Required): Salesforce ID of the ramp deal to update
  - `rampSegments` (Array, Required): Segments to update, each containing:
    - `segment` (Integer): Segment number to update
    - `commitment` (Number): Updated commitment value

---

### 14. Delete Ramp Deal (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-transactions/ramp-deals/actions/delete`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/ramp-deals/actions/delete`
- **Description:** Permanently delete a ramp deal and all its segments. This action cannot be undone. Use only for ramp deals that have not yet been committed to an active order.
- **Available Version:** 63.0
- **Request Body Fields:**
  - `rampDealId` (String, Required): Salesforce ID of the ramp deal to delete

---

### 15. View Ramp Deal (GET)
- **HTTP Method:** GET
- **URI Path:** `/commerce/sales-transactions/ramp-deals`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-transactions/ramp-deals`
- **Description:** Retrieve all ramp deals for the org or filter to specific accounts. Returns ramp deal records with all segment details, commitment values, and status.
- **Available Version:** 63.0

---

## DEPRECATED APIs (v63.0+)

The following endpoints were deprecated in v63.0 and replaced by the Sales Transactions APIs. They are retained in the collection for backward compatibility but should not be used in new integrations.

### 16. Place Order [DEPRECATED v63] (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/sales-orders/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/sales-orders/actions/place`
- **Description:** **Deprecated in v63.0.** Place a sales order. Replaced by [Place Sales Transaction](#1-place-sales-transaction-post).
- **Available Version:** Deprecated — use `/commerce/sales-transactions/actions/place` instead

---

### 17. Place Quote [DEPRECATED v63] (POST)
- **HTTP Method:** POST
- **URI Path:** `/commerce/quotes/actions/place`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/commerce/quotes/actions/place`
- **Description:** **Deprecated in v63.0.** Place a quote. Replaced by [Place Sales Transaction](#1-place-sales-transaction-post).
- **Available Version:** Deprecated — use `/commerce/sales-transactions/actions/place` instead

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
2. Asset Amendment           → Submit amendment request (effectiveDate, changes)
3. Read Sales Transaction    → Review the generated amendment order
4. [Activate order]          → Asset is updated upon activation
```

### Ramp Deal
```
1. Create Ramp Deal          → Define multi-segment commitment schedule
2. Place Sales Transaction   → Place order referencing the ramp deal
3. View Ramp Deal            → Track segment status over time
4. Update Ramp Deal          → Adjust commitments if renegotiated
```

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |
| `{{defaultAccountId}}` | Default account record ID | Setup Runner |
| `{{defaultTermDefinedAnnualProductId}}` | Default term-defined annual product ID | Setup Runner |
| `{{assetId}}` | Asset record ID for lifecycle operations | Set by test scripts after order activation |

---

## Related Domains

- **[Product Discovery APIs](product-discovery-apis-reference.md)** — Discover and price products before placing transactions.
- **[Product Configurator APIs](product-configurator-apis-reference.md)** — Configure complex bundles before placing.
- **[Pricing APIs](pricing-business-apis-v66.md)** — Pricing procedures and waterfall details.
- **[Billing APIs](billing-business-apis-reference.md)** — Invoices, payments, and credit memos generated after order activation.
- **[Usage Management APIs](usage-management-apis-reference.md)** — Track usage against assets created by transaction orders.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
