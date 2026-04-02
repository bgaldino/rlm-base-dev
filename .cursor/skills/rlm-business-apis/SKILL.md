---
name: rlm-business-apis
description: >-
  Revenue Cloud Business API reference for RLM v66.0. Use when working with
  Revenue Cloud REST APIs, building integrations, writing Apex callouts, or
  answering questions about RLM API endpoints. Covers PCM, Product Discovery,
  Configurator, Pricing, Rate Management, Transaction Management, Usage
  Management, Billing, and Context Service APIs.
---

# Revenue Cloud Business APIs

API v66.0 (Spring '26, Release 260). All endpoints use `/services/data/v66.0/connect/` prefix.

## Quick Rules

1. All endpoints: `/services/data/v66.0/connect/<domain>/`.
2. Auth: Bearer token from `org_config.access_token`.
3. Context Service: must activate context definition before use.
4. Pricing API computes prices — never write PBE records directly via API.
5. Load per-domain reference docs from `postman/docs/` for full endpoint details.

## API Domain Index

| Domain | Base Path | Key Operations | Reference Doc |
|--------|-----------|---------------|---------------|
| **PCM** | `/connect/pcm/` | Catalogs, categories, products, attributes, bundles, classifications | [pcm-business-apis-reference.md](../../postman/docs/pcm-business-apis-reference.md) |
| **Product Discovery** | `/connect/product-discovery/` | Context-aware product search with pricing, entitlements, guided selling | [product-discovery-apis-reference.md](../../postman/docs/product-discovery-apis-reference.md) |
| **Product Configurator** | `/connect/product-configurator/` | Configuration flows, rule validation, attribute resolution | [product-configurator-apis-reference.md](../../postman/docs/product-configurator-apis-reference.md) |
| **Pricing** | `/connect/core-pricing/` | Calculate prices, waterfalls, adjustments, promotion evaluation | [pricing-business-apis-v66.md](../../postman/docs/pricing-business-apis-v66.md) |
| **Rate Management** | `/connect/core-rating/` | Rate plans, rating waterfalls, usage pricing | [rate-management-apis-reference.md](../../postman/docs/rate-management-apis-reference.md) |
| **Transaction Mgmt** | `/connect/transaction-management/` | Quotes, orders, assets, amendments, renewals, cancellations | [transaction-management-apis-reference.md](../../postman/docs/transaction-management-apis-reference.md) |
| **Usage Mgmt** | `/connect/usage-management/` | Usage events, summaries, entitlements, grants | [usage-management-apis-reference.md](../../postman/docs/usage-management-apis-reference.md) |
| **Billing** | `/connect/billing/` | Invoice generation, credit memos, payments, billing schedules | [billing-business-apis-reference.md](../../postman/docs/billing-business-apis-reference.md) |
| **Context Service** | `/connect/context-service/` | Context definitions, mappings, context CRUD | [context-service-apis-reference.md](../../postman/docs/context-service-apis-reference.md) |

## Common Patterns

### Authentication
All APIs use standard Salesforce OAuth. Use `Authorization: Bearer <access_token>` header.

### PCM vs Product Discovery
- **PCM APIs** (`/connect/pcm/`): Direct catalog CRUD with standard REST semantics (GET/POST/PUT/PATCH). Admin/integration use cases.
- **Product Discovery APIs** (`/connect/product-discovery/`): Context-aware, buyer-session-scoped catalog operations. All operations use POST. Apply context filters, entitlements, and pricing rules. Storefront/CPQ use cases.

### Transaction Lifecycle APIs
The transaction management APIs follow a standard lifecycle:

```
Create Quote → Add Line Items → Configure → Price → Place Order → Create Assets
                                                         ↓
                                              Amend / Renew / Cancel
```

Key endpoints:
- `POST /connect/transaction-management/quotes` — Create quote
- `POST /connect/transaction-management/quotes/{quoteId}/line-items` — Add line items
- `POST /connect/transaction-management/quotes/{quoteId}/actions/place-order` — Place order
- `POST /connect/transaction-management/assets/{assetId}/actions/amend` — Amend asset
- `POST /connect/transaction-management/assets/{assetId}/actions/renew` — Renew asset

### Pricing APIs
- `POST /connect/core-pricing/calculate` — Calculate prices for a transaction
- `GET /connect/core-pricing/waterfall/{lineItemId}/{executionId}` — Pricing waterfall (audit trail)
- Rate Management uses `/connect/core-rating/rate-plan` for usage-based pricing

### Billing APIs
- Invoice generation, credit/debit memos, payment application
- Billing batch operations for bulk processing

### Context Service
Context definitions store session state and configuration across API calls. Used by Product Discovery, Pricing, and Configuration APIs to maintain buyer context.

## Master Reference

For the complete cross-domain API reference extracted from the v260 developer guide:
[rlm-v260-business-apis-reference.md](../../postman/docs/rlm-v260-business-apis-reference.md)

## Interactive Viewer

Open `docs/api/index.html` in a browser for a searchable, collapsible API reference with dark/light theme toggle.

## Postman Collection

The `postman/` directory contains the full Agentforce Revenue Management Postman collection for hands-on API testing.
