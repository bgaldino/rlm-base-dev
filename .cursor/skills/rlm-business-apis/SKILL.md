---
name: rlm-business-apis
description: >-
  Revenue Cloud Business API reference for RLM v68.0 (Winter '27 / Release 264). Use when working with
  Revenue Cloud REST APIs, building integrations, writing Apex callouts, or
  answering questions about RLM API endpoints. Covers PCM, Product Discovery,
  Configurator, Pricing, Rate Management, Transaction Management, Usage
  Management, Billing, and Context Service APIs.
---

# Revenue Cloud Business APIs

API v68.0 (Winter '27 / Release 264). The per-domain reference docs under `postman/docs/` and the viewer at `docs/api/index.html` cover 149 endpoints across 9 domains — 137 re-extracted (grounded) from the 264 (v68.0) developer guide, plus 12 retained/external (six external Salesforce Commerce Payments Billing endpoints under `/commerce/payments/`, outside the 264 RLM guide; five v59-carryover Context Service endpoints, for which the 264 guide has no Business-API section; and one legacy PCM route — `/connect/pcm/products/{productId}/related-records` — with no 264 snapshot article). Paths are relative to `/services/data/v68.0/` but span several resource families — `/connect/`, `/revenue/`, `/commerce/`, `/industries/`, `/global-promotions-management/`, `/asset-management/` — not a single `/connect/` prefix. 264 is pre-GA, so treat a live 264 org as ground truth over the docs. The downloadable Postman collection JSON under `postman/` is still the prior v66.0 baseline and is being regenerated against a live 264 org.

## Quick Rules

1. Paths are relative to `/services/data/v68.0/`. Endpoints span several resource families (`/connect/`, `/revenue/`, `/commerce/`, `/industries/`, `/global-promotions-management/`, `/asset-management/`) — use each endpoint's own path from the reference docs; do not assume a single `/connect/` prefix.
2. Auth: Bearer token from `org_config.access_token`.
3. Context Service: must activate context definition before use.
4. Pricing API computes prices — never write PBE records directly via API.
5. Load per-domain reference docs from `postman/docs/` for full endpoint details.

## API Domain Index

> `Base Path` values below are relative to `/services/data/v68.0` — i.e. `/connect/pcm/` is actually `/services/data/v68.0/connect/pcm/`. Domains span multiple resource families; a domain may expose endpoints under more than one base path. Use each endpoint's own path from its reference doc.

| Domain | Base Path(s) | Key Operations | Reference Doc |
|--------|-----------|---------------|---------------|
| **PCM** | `/connect/pcm/`, `/revenue/product-catalog-management/` | Catalogs, categories, products, attributes, bundles, classifications | [pcm-business-apis-reference.md](../../../postman/docs/pcm-business-apis-reference.md) |
| **Product Discovery** | `/connect/cpq/`, `/revenue/product-discovery/` | Context-aware product search with pricing, entitlements, guided selling | [product-discovery-apis-reference.md](../../../postman/docs/product-discovery-apis-reference.md) |
| **Product Configurator** | `/connect/cpq/`, `/revenue/product-configurator/` | Configuration flows, rule validation, attribute resolution | [product-configurator-apis-reference.md](../../../postman/docs/product-configurator-apis-reference.md) |
| **Pricing** | `/connect/core-pricing/`, `/connect/procedure-plan-definitions/` | Calculate prices, waterfalls, adjustments, promotion evaluation | [pricing-business-apis-v68.md](../../../postman/docs/pricing-business-apis-v68.md) |
| **Rate Management** | `/connect/core-rating/`, `/connect/core-pricing/` | Rate plans, rating waterfalls, usage pricing | [rate-management-apis-reference.md](../../../postman/docs/rate-management-apis-reference.md) |
| **Transaction Mgmt** | `/connect/rev/sales-transaction/` (current place/clone/supplemental), `/revenue/transaction-management/` & `/connect/revenue/transaction-management/` (read, place tracker, promotions, asset upgrade/downgrade/swap), `/connect/revenue-management/` (asset amend/cancel/renew, ramp deals), `/connect/advanced-approvals/`, `/industries/cpq/`, `/global-promotions-management/`, `/commerce/` (deprecated v63 place only) | Quotes, orders, assets, amendments, renewals, cancellations, ramp deals, approvals, promotions | [transaction-management-apis-reference.md](../../../postman/docs/transaction-management-apis-reference.md) |
| **Usage Mgmt** | `/revenue/usage-management/`, `/asset-management/`, `/commerce/` | Usage events, summaries, entitlements, grants | [usage-management-apis-reference.md](../../../postman/docs/usage-management-apis-reference.md) |
| **Billing** | `/commerce/` (billing, invoicing, payments, taxes), `/revenue/billing/`, `/connect/sequences/` | Invoice generation, credit memos, payments, billing schedules | [billing-business-apis-reference.md](../../../postman/docs/billing-business-apis-reference.md) |
| **Context Service** | `/connect/context-definitions/` | Context definitions, mappings, context CRUD | [context-service-apis-reference.md](../../../postman/docs/context-service-apis-reference.md) |

## Common Patterns

### Authentication
All APIs use standard Salesforce OAuth. Use `Authorization: Bearer <access_token>` header.

### PCM vs Product Discovery
- **PCM APIs** (`/connect/pcm/`): Direct catalog CRUD with standard REST semantics (GET/POST/PUT/PATCH). Admin/integration use cases.
- **Product Discovery APIs** (`/connect/cpq/`, `/revenue/product-discovery/`): Context-aware, buyer-session-scoped catalog operations. Apply context filters, entitlements, and pricing rules. Storefront/CPQ use cases.

### Transaction Lifecycle APIs
The transaction management APIs follow a standard lifecycle:

```
Create Quote → Add Line Items → Configure → Price → Place Order → Create Assets
                                                         ↓
                                              Amend / Renew / Cancel
```

Key endpoints (see the reference doc for exact request shapes):
- `POST /connect/rev/sales-transaction/actions/place` — Place Sales Transaction (the current quote/order entry point; supersedes the v63-deprecated `/commerce/quotes/actions/place` and `/commerce/sales-orders/actions/place`, which are retained only for backward compatibility and cap at 300 line items)
- `POST /connect/rev/sales-transaction/actions/clone` — Clone a sales transaction
- `POST /connect/revenue-management/assets/actions/amend` — Amend asset
- `POST /connect/revenue-management/assets/actions/renew` — Renew asset
- `POST /industries/cpq/quotes/actions/get-instant-price` — Instant pricing

### Pricing APIs
- `POST /connect/core-pricing/pricing` — Calculate prices for a transaction
- `GET /connect/core-pricing/waterfall/{lineItemId}/{executionId}` — Pricing waterfall (audit trail)
- Rate Management uses `/connect/core-rating/rate-plan` for usage-based pricing

### Billing APIs
- Invoice generation, credit/debit memos, payment application
- Billing batch operations for bulk processing

### Context Service
Context definitions store session state and configuration across API calls. Used by Product Discovery, Pricing, and Configuration APIs to maintain buyer context.

## Reference

The cross-domain API reference lives as per-area markdown under
[`postman/docs/`](../../../postman/docs/) — 149 endpoints across 9 domains (PCM,
Product Discovery, Product Configurator, Pricing, Rate Management, Transaction
Management, Usage Management, Billing, Context Service). Of these, 137 are
re-extracted (grounded) from the Release 264 (Winter '27, v68.0) developer guide;
12 are retained/external (six external Commerce Payments Billing endpoints under
`/commerce/payments/`; five v59-carryover Context Service endpoints, for which
the 264 guide has no Business-API section; and one legacy PCM route —
`/connect/pcm/products/{productId}/related-records` — with no 264 snapshot
article). 264 is pre-GA, so treat a live 264 org as ground truth over the guide.

## Interactive Viewer

Open `docs/api/index.html` in a browser for a searchable, collapsible API reference with dark/light theme toggle.

## Postman Collection

The `postman/` directory contains the full Agentforce Revenue Management Postman collection for hands-on API testing.
