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

API v68.0 (Winter '27 / Release 264). The per-domain reference docs under `docs/api/` cover 155 endpoints across 9 domains — 143 re-extracted (grounded) from the 264 (v68.0) developer guide, plus 12 retained/external (six external Salesforce Commerce Payments Billing endpoints under `/commerce/payments/`, outside the 264 RLM guide; five v59-carryover Context Service endpoints, for which the 264 guide has no Business-API section; and one legacy PCM route — `/connect/pcm/products/{productId}/related-records` — with no 264 snapshot article). Paths are relative to `/services/data/v68.0/` but span several resource families — `/connect/`, `/revenue/`, `/commerce/`, `/industries/`, `/global-promotions-management/`, `/asset-management/` — not a single `/connect/` prefix. 264 is pre-GA, so treat a live 264 org as ground truth over the docs. The downloadable Postman collection JSON under `postman/` is still the prior v66.0 baseline and is being regenerated against a live 264 org. The viewer at `docs/api/index.html` shows all 155 endpoints, including the six v68 additions (Pricing Recipe Clone and Valid Elements, Unlock Transaction, Billing Checkout, Composite Collection Plan, Refund Credit Memo); its data is hand-maintained, so the Markdown references win on any disagreement.

## Quick Rules

1. Paths are relative to `/services/data/v68.0/`. Endpoints span several resource families (`/connect/`, `/revenue/`, `/commerce/`, `/industries/`, `/global-promotions-management/`, `/asset-management/`) — use each endpoint's own path from the reference docs; do not assume a single `/connect/` prefix.
2. Auth: Bearer token from `org_config.access_token`.
3. Context Service: must activate context definition before use.
4. Pricing API computes prices — never write PBE records directly via API.
5. Load per-domain reference docs from `docs/api/` for full endpoint details.

## API Domain Index

> `Base Path` values below are relative to `/services/data/v68.0` — i.e. `/connect/pcm/` is actually `/services/data/v68.0/connect/pcm/`. Domains span multiple resource families; a domain may expose endpoints under more than one base path. Use each endpoint's own path from its reference doc.

| Domain | Base Path(s) | Key Operations | Reference Doc |
|--------|-----------|---------------|---------------|
| **PCM** | `/connect/pcm/`, `/revenue/product-catalog-management/` | Catalogs, categories, products, attributes, bundles, classifications | [pcm-business-apis-reference.md](../../../docs/api/pcm-business-apis-reference.md) |
| **Product Discovery** | `/connect/cpq/`, `/revenue/product-discovery/` | Context-aware product search with pricing, entitlements, guided selling | [product-discovery-apis-reference.md](../../../docs/api/product-discovery-apis-reference.md) |
| **Product Configurator** | `/connect/cpq/`, `/revenue/product-configurator/` | Configuration flows, rule validation, attribute resolution | [product-configurator-apis-reference.md](../../../docs/api/product-configurator-apis-reference.md) |
| **Pricing** | `/connect/core-pricing/`, `/connect/procedure-plan-definitions/` | Calculate prices, waterfalls, adjustments, promotion evaluation | [pricing-business-apis-v68.md](../../../docs/api/pricing-business-apis-v68.md) |
| **Rate Management** | `/connect/core-rating/`, `/connect/core-pricing/` | Rate plans, rating waterfalls, usage pricing | [rate-management-apis-reference.md](../../../docs/api/rate-management-apis-reference.md) |
| **Transaction Mgmt** | `/connect/rev/sales-transaction/` (current place/clone/supplemental), `/revenue/transaction-management/` & `/connect/revenue/transaction-management/` (read, place tracker, promotions, asset upgrade/downgrade/swap), `/connect/revenue-management/` (asset amend/cancel/renew, ramp deals), `/connect/advanced-approvals/`, `/industries/cpq/`, `/global-promotions-management/`, `/commerce/` (deprecated v63 place only) | Quotes, orders, assets, amendments, renewals, cancellations, ramp deals, approvals, promotions | [transaction-management-apis-reference.md](../../../docs/api/transaction-management-apis-reference.md) |
| **Usage Mgmt** | `/revenue/usage-management/`, `/asset-management/`, `/commerce/` | Usage events, summaries, entitlements, grants | [usage-management-apis-reference.md](../../../docs/api/usage-management-apis-reference.md) |
| **Billing** | `/commerce/` (billing, invoicing, payments, taxes), `/revenue/billing/`, `/connect/sequences/` | Invoice generation, credit memos, payments, billing schedules | [billing-business-apis-reference.md](../../../docs/api/billing-business-apis-reference.md) |
| **Context Service** | `/connect/context-definitions/` | Context definitions, mappings, context CRUD | [context-service-apis-reference.md](../../../docs/api/context-service-apis-reference.md) |

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
- `POST /connect/revenue-management/assets/actions/cancel` — Cancel asset
- `POST /industries/cpq/quotes/actions/get-instant-price` — Instant pricing

**Place PATCH request shape.** A graph with no `Quote` record is refused ("No quote found in the
record list"), so include the Quote record (a PATCH on it) alongside the line PATCHes. Sending
`executeConfigurationRules` in `configurationPref`, as these requests did (the requests were not
kept; the documented place is under `configurationOptions`), was rejected by the request parser
(a JSON parser error, nothing written); those PATCHes ran with `configurationMethod` only, so
this says nothing about rules-on requests that use the other nesting
[Measured: 2026-11-12, 264, scratch].

**Line discounts in a Place PATCH.** Measured on 264 scratch orgs (2026-11-12) whose pricing
procedures were customised, with Place PATCHes on existing `QuoteLineItem`s (`pricingPref: Force`,
`configurationMethod: Skip`):

- `DiscountAmount` is **per unit**: on a line with a quantity above 1 it lowered `NetUnitPrice`
  by the amount sent, not the line total by it. The shipped default procedure's Manual Discount
  step is per unit as well [Platform behaviour, traced].
- A PATCH sending `DiscountAmount: 0` with `Discount: 5` was refused, both on a fresh line and on
  one that carried a `DiscountAmount` (`isSuccess` false, FIELD_INTEGRITY_EXCEPTION "You can't
  specify a discount both as a percentage and an amount...") and the line was unchanged. `0` counts as a value, and `Discount: 5`
  alone was refused the same way while the stored amount remained. Sending `DiscountAmount: null`
  with `Discount: 5` cleared the amount and the 5 % applied [Measured: 2026-11-12, 264, scratch].
  Check `isSuccess` in the response body: an unread refusal looks like a no-op.
- Send one discount field per line. To switch type, send the other as `null` in the same PATCH, then
  read the line back. A quote line with both fields non-null is refused at save [Platform
  behaviour, traced].

**Other Place results.**

- Place does not derive `SubscriptionTerm` from dates [Platform behaviour, traced]. The trace shows
  Place filling a missing term context tag with the selling model's pricing term when the line's
  selling model option is Term Defined, but not that fill reaching the saved line. In the measured
  requests (price book entry only, no `ProductSellingModelId` in the request; the saved line's selling model was Term Defined) the saved unit was
  `Annual` but `SubscriptionTerm` stayed null: a dates-only Term Defined Annual line
  (System pricing, configuration method Force, rules on) was priced from its dates alone (a whole-year term count) and came out higher by exactly the missing commitment-term step, because the term-keyed discount never ran. That step is one the measured org's customised pricing procedure adds when a header switch is on (it was on; not a shipped step). The result held both standalone and as a bundle component, against a line sent with `SubscriptionTerm` and unit `Annual` instead of an end date
  [Measured: 2026-11-11, 264, scratch]. Why the term was not filled was not established. Send the
  term explicitly.
- A second measurement matches the dates-only create above: a line created with dates only had
  `SubscriptionTerm` null, the unit filled from the selling model, and the term count taken from
  the dates [Measured: 2026-11-12, 264, scratch]. A dates-only PATCH on an existing line (one
  measurement; configuration method Skip, System pricing, a Term Defined Annual line created
  with a term) left `SubscriptionTerm` at its old value (stale), while the pricing term count
  followed the new dates and the total repriced from them [Measured: 2026-11-12, 264, scratch].
- **Milestone Plan on bundle components.** Place with `configurationMethod: Force` and
  configuration rules on left `BillingFrequency` blank on component service lines (`billing-setup` → M11). A second Place PATCH
  with `configurationMethod: Skip` setting `BillingFrequency` Milestone Plan and the milestone
  `BillingTreatmentId` on those lines kept both, moved no price, and both were on the order products
  after `createOrdersFromQuote` [Measured: 2026-11-12, 264, scratch; one org]. Why the first Place drops it is not
  established.

**Backdated asset changes** (amend, cancel, renew, transfer, swap, upgrade, downgrade with an
effective date in the past; rollback's refusal): the invocable inputs, activation prerequisites,
UI-flow (`RLM_ARC_Assets`) behaviour, and invoice/credit-memo verification are in
[backdated-asset-lifecycle.md](backdated-asset-lifecycle.md), with the end-to-end verifier
`scripts/backdated_arc/verify_backdated_billing.py`.

**Where an ARC line's price lives.** On a renewal, a cancel or a negative-quantity amendment, the
platform moves the unit price to the child **`QuoteLineDetail`** / **`OrderItemDetail`** rows
("Order Product Detail") and leaves `UnitPrice` and `NetUnitPrice` **null** on the parent
`QuoteLineItem` / `OrderItem`. Totals on the parent stay correct.

- Integrations, document templates, formulas and Apex must read the detail rows (or coalesce)
  and must never trust the parent's `NetUnitPrice` on these lines (renewal, cancel, negative
  amendment).
- A positive-quantity amendment placed through the API and new business keep the price on the
  parent and have no detail rows. A positive amendment edited inline in the quote UI was measured
  with its price on detail rows (`asset-lifecycle-changes` → Quick Rule 4).
- This repo keeps **as-is renewals on** (`enableAsIsRenewals=true` in
  `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`), so renewals behave this way
  too. Turning it off moves a plain renewal's price back to the parent, but leaves cancels and
  negative amendments unchanged (measured). Per-lot as-is pricing also needs a
  last-transaction pricing source on the renewal (a price book list price source does not qualify;
  which asset or line field supplies it for a renewal was not traced, so a blank `PricingSource`
  on the asset or line is not proof either way); no ramp; no derived-price product; no price or
  attribute change; and not an early renewal [Platform behaviour, traced]. Otherwise the line is not priced per lot. Early renewals get
  cancel-and-add detail rows [Platform behaviour, traced]; whether a renewal with a price or
  attribute change does is not settled [Platform behaviour, traced in part].
- Advanced Detail Line Pricing does not change any of it.

```bash
sf data query -o <sf-alias> -q "SELECT QuoteLineItemId, Quantity, UnitPrice, NetUnitPrice, \
    TotalPrice FROM QuoteLineDetail WHERE QuoteLineItem.QuoteId = '<quote>'"
sf data query -o <sf-alias> -q "SELECT OrderItemId, Quantity, UnitPrice, NetUnitPrice, \
    TotalPrice FROM OrderItemDetail WHERE OrderItem.OrderId = '<order>'"
```

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
[`docs/api/`](../../../docs/api/) — 155 endpoints across 9 domains (PCM,
Product Discovery, Product Configurator, Pricing, Rate Management, Transaction
Management, Usage Management, Billing, Context Service). Of these, 143 are
re-extracted (grounded) from the Release 264 (Winter '27, v68.0) developer guide;
12 are retained/external (six external Commerce Payments Billing endpoints under
`/commerce/payments/`; five v59-carryover Context Service endpoints, for which
the 264 guide has no Business-API section; and one legacy PCM route —
`/connect/pcm/products/{productId}/related-records` — with no 264 snapshot
article). 264 is pre-GA, so treat a live 264 org as ground truth over the guide.

## Interactive Viewer

Open `docs/api/index.html` in a browser for a searchable, collapsible API reference with dark/light theme toggle. It covers all 155 endpoints; the per-domain Markdown in `docs/api/` is authoritative.

## Postman Collection

The `postman/` directory contains the full Agentforce Revenue Management Postman collection for hands-on API testing.
