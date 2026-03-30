# Salesforce Rate Management APIs - Complete Endpoint Reference
## Revenue Lifecycle Management API v66.0 (Spring '26)

This document provides a comprehensive reference of all REST API endpoints for the Salesforce Rate Management APIs, extracted from the Agentforce Revenue Management APIs Postman collection and the Revenue Cloud Developer Guide v260. Endpoints are organized by functional area and include HTTP method, URI path, description, and notable request/response fields.

The Rate Management APIs support usage-based billing scenarios by exposing the rating engine's rate plans and waterfall calculation details. Rate plans define how usage is priced (tiers, flat rates, per-unit), and the rating waterfall shows the step-by-step application of rate card rules during billing. These APIs are most relevant in orgs with usage-based products (Platform Usage Resources, PURs).

---

## RATE APIs

### 1. Get Rate Plan (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-rating/rate-plan`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/core-rating/rate-plan`
- **Description:** Retrieve the rate plan configuration from the rating engine. A rate plan defines the pricing model for usage-based products — including flat rates, tiered pricing, and volume-based adjustments. Use this endpoint to inspect the active rate plan before performing usage calculations or debugging unexpected billing amounts.
- **Available Version:** 63.0

---

### 2. Get Rating Waterfall (GET)
- **HTTP Method:** GET
- **URI Path:** `/connect/core-pricing/waterfall/{lineItemId}/{executionId}`
- **Full URL:** `https://yourInstance.salesforce.com/services/data/v66.0/connect/core-pricing/waterfall/{lineItemId}/{executionId}?ratingParameters=true`
- **Description:** Retrieve the detailed waterfall breakdown of how a price or rating was calculated for a specific line item and execution. Shows each step in the pricing/rating process — including which rate card tiers were applied, adjustments made, and the final computed price. Essential for debugging pricing discrepancies or auditing bill calculation.
- **Available Version:** 63.0
- **Path Parameters:**
  - `lineItemId` (String, Required): Salesforce ID of the quote, order, or billing line item
  - `executionId` (String, Required): ID of the specific pricing process execution (returned by pricing APIs)
- **Query Parameters:**
  - `ratingParameters` (Boolean, Optional): When `true`, includes rating-specific parameters in the waterfall output (usage amounts, tier boundaries, rate multipliers). Defaults to `false`.

---

## Rate Management Architecture

Rate Management in Revenue Cloud operates across three tiers:

**Rate Cards** define pricing rules for usage dimensions. Each Rate Card Entry specifies a dimension (e.g., GB, API calls, minutes), a rate, and optional tiered breakpoints.

**Platform Usage Resources (PURs)** are the products that consume usage according to a rate plan. PURs are linked to Rate Cards and Platform Usage Resource Policies (PURPs).

**Rating Waterfall** shows the execution trace of how usage was measured and priced — from raw consumption data through rate card matching, tier application, and final charge calculation.

---

## Prerequisites

These APIs require usage-based billing to be configured in the org. Before using Rate Management APIs:

1. Load rate card data using `insert_qb_rates_data` (or equivalent CCI task)
2. Load rating data using `insert_qb_rating_data`
3. Activate rating records via `activate_rating_records` (runs `activateRatingRecords.apex`)
4. Ensure `rates` and `rating` feature flags are enabled in `cumulusci.yml`

**Deletion order:** Always run `delete_qb_rates_data` before `delete_qb_rating_data` — rate card entries have foreign key relationships to PURs.

---

## Related SFDMU Data Plans

| Plan | CCI Task | Description |
|------|----------|-------------|
| `qb-rates` | `insert_qb_rates_data` | Rate cards, rate card entries, adjustment tiers |
| `qb-rating` | `insert_qb_rating_data` | Platform Usage Resources (PURs), PURPs, PUGs |

---

## Environment Variables Used

| Variable | Description | Set By |
|----------|-------------|--------|
| `{{_endpoint}}` | Salesforce org base URL | Manual setup |
| `{{version}}` | API version (e.g., `66.0`) | Manual setup |

---

## Related Domains

- **[Usage Management APIs](usage-management-apis-reference.md)** — Retrieve usage details for assets, orders, and quotes. Usage data feeds into the rating engine.
- **[Pricing APIs](pricing-business-apis-v66.md)** — Pricing waterfall for non-usage line items (list price, discount adjustments, etc.).
- **[Billing APIs](billing-business-apis-reference.md)** — Billing invoices and payments that are generated from rated usage data.
- **[Transaction Management APIs](transaction-management-apis-reference.md)** — Order and asset lifecycle that generates the consumption records rated by this engine.

---

*Reference for: Agentforce Revenue Management APIs v66.0 (Spring '26) | Salesforce Revenue Cloud Developer Guide v260*
