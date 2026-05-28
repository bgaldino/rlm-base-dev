# Revenue Cloud Postman Collections

API collections for Salesforce Revenue Cloud — Spring '26 (Release 260, API v66.0).

---

## Collections

**Agentforce Revenue Management APIs (v66.0)** — The primary, comprehensive collection containing every documented Revenue Cloud Business API endpoint (204 endpoints across 13 API domains). Includes three pre-configured runners for end-to-end workflows: Quote-to-Cash, eCommerce, and Billing.

**RLM.postman_collection.json** — Foundational collection focused on core CPQ workflows: Product Catalog Management, Product Discovery, Salesforce Pricing, Asset Lifecycle, and Context Service (108 endpoints). See `archive/` for original analysis documentation.

**RCA APIs - Winter'25 (258) Latest.postman_collection.json** — Extended collection from a separate contributor covering the full Revenue Cloud surface including Billing, Usage Management, Rate Management, DRO, and Product Configurator (237 endpoints). Includes demo scenario folders. See `archive/` for original analysis documentation.

---

## Environment

**Agentforce Revenue Management v66.0.postman_environment.json** — Canonical environment file for the Agentforce collection with 174 variables covering all API domains. Configure `url`, `clientId`, and `clientSecret` for your org, then run the Setup Runner to auto-populate all remaining variables.

The two original environment files (`RLM QuantumBit Default Environment.postman_environment.json` and `RCA APIs - Composable MQ25 Latest.postman_environment.json`) are retained in `archive/` for backward compatibility with the RLM and RCA collections.

---

## Setup

1. Import `Agentforce Revenue Management APIs (v66.0).postman_collection.json` and `Agentforce Revenue Management v66.0.postman_environment.json` into Postman
2. Set `clientId` and `clientSecret` for your Connected App (client_credentials flow)
3. Set `url` (defaults to `https://login.salesforce.com`)
4. Run the **⚙️ Setup Runner** folder using Postman's Collection Runner — this auto-discovers your org's products, catalogs, pricing procedures, and context definitions, populating all 35 environment variable entries
5. Start making API calls

---

## Reference Guides

Per-domain endpoint references are in `docs/`. Each guide covers HTTP method, URI path, full URL, request body fields, and environment variables.

- [Product Catalog Management (PCM)](docs/pcm-business-apis-reference.md) — Catalogs, categories, products, index management, unit of measure (19 endpoints)
- [Product Discovery](docs/product-discovery-apis-reference.md) — Context-aware catalog access, global search, guided selection, qualification (10 endpoints)
- [Product Configurator](docs/product-configurator-apis-reference.md) — Configure bundles, manage saved configurations, node operations (13 endpoints)
- [Pricing](docs/pricing-business-apis-v66.md) — Core pricing engine, price contexts, waterfall, API execution logs (10 endpoints)
- [Rate Management](docs/rate-management-apis-reference.md) — Rate plans and rating waterfall for usage-based billing (2 endpoints)
- [Transaction Management](docs/transaction-management-apis-reference.md) — Sales transactions, instant pricing, asset lifecycle, ramp deals (17 endpoints)
- [Usage Management](docs/usage-management-apis-reference.md) — Asset/order/quote usage details, consumption traceability, usage product validation (6 endpoints)
- [Billing (Quick Reference)](docs/billing-apis-quick-reference.md) — Billing quick reference cheat sheet
- [Billing (Full Reference)](docs/billing-business-apis-reference.md) — Invoices, payments, credit memos, billing schedules, billing runs (full coverage)
- [Context Service](docs/context-service-apis-reference.md) — Context definitions, nodes, and mappings that power pricing and entitlements (5 endpoints)
- [Overall API Reference](docs/rlm-v260-business-apis-reference.md) — Master reference covering all v260 Business API endpoints across all domains

---

## Utilities

Located in `utilities/`:

- `build_agentforce_collection.py` — Generates the Agentforce collection from source. Run with `python3 utilities/build_agentforce_collection.py`.
- `validate_collection.py` — Validates all collections for structural integrity, API version compliance, request body validity, and completeness against the v260 API inventory. Run with `python3 utilities/validate_collection.py`.
- `update_existing_collections.py` — Applies v260 updates to the RLM and RCA collections. Idempotent.

---

## Reference Documentation

The legacy per-release PDF compendiums (Revenue Cloud Developer Guide, Salesforce
Industries Developer Guide, CML User Guide) have been replaced by the
**Salesforce Help snapshot** workflow — grep-friendly, diffable per-article
markdown captured per release.

- Snapshots live at `docs/salesforce/{release}/help/` (e.g. `docs/salesforce/262/help/`).
- Refresh them per release via the `snapshot_{area}_help_{release}` CCI tasks
  in `cumulusci.yml`.
- Authoring guidance: `.cursor/skills/revenue-cloud-docs/SKILL.md`.

---

## Authentication

All requests use OAuth 2.0 client credentials flow. The collection-level pre-request script handles token acquisition and automatic refresh:

1. The pre-request script checks whether the cached token is expired
2. If expired, it calls `{{url}}/services/oauth2/token` with your `clientId` and `clientSecret`
3. The token is stored in the environment and injected as a Bearer header
4. All endpoints inherit authentication from the collection level — no per-request configuration needed

On first run, provide `clientId`, `clientSecret`, and `url`. Subsequent requests refresh automatically. A `401 Unauthorized` response means the credentials are invalid or the token endpoint URL is incorrect.

---

## Environment Variables

### Required (configure manually)

| Variable | Description | Example |
|----------|-------------|---------|
| `url` | Salesforce login URL | `https://login.salesforce.com` |
| `clientId` | Connected App consumer key | *(from your org)* |
| `clientSecret` | Connected App consumer secret | *(from your org)* |
| `_endpoint` | Salesforce org instance URL | `https://your-org.my.salesforce.com` |
| `version` | API version | `66.0` |

### Auto-populated by Setup Runner

The Setup Runner queries your org and populates all of the following:

| Category | Variables |
|----------|-----------|
| Account & Contact | `defaultAccountId`, `defaultAccountName`, `contactId` |
| Catalog | `defaultCatalogId`, `defaultCatalogName` |
| Category | `defaultCategoryId`, `defaultCategoryName` |
| Products (by type) | `defaultOneTimeProductId`, `defaultEvergreenMonthlyProductId`, `defaultEvergreenAnnualProductId`, `defaultTermMonthlyProductId`, `defaultTermDefinedAnnualProductId` |
| Product Selling Models | `defaultOneTimePSMId`, `defaultEvergreenMonthlyPSMId`, `defaultEvergreenAnnualPSMId`, `defaultTermMonthlyPSMId`, `defaultTermDefinedAnnualPSMId` |
| Pricebook | `standardPricebookId` |
| Pricebook Entries (by type) | `defaultOneTimePBEId`, `defaultEvergreenMonthlyPBEId`, `defaultEvergreenAnnualPBEId`, `defaultTermMonthlyPBEId`, `defaultTermDefinedAnnualPBEId` |
| Context (Default) | `contextDefinitionId`, `contextMappingId`, `pricingProcedureId` |
| Context (Custom) | `customContextDefinitionId`, `customContextMappingId` |
| Context (Cart) | `cartContextDefinitionId`, `cartContextMappingId` |
| Context (Product Discovery) | `pdContextDefinitionId`, `pdContextMappingId` |
| Qualification | `qualificationProcedureId` |
| Transactions | `quoteId`, `orderId`, `assetId` |
| Billing | `invoiceId`, `paymentId`, `creditMemoId`, `billingScheduleId` |
| Usage | `bindingObjectId` |

---

## API Path Patterns

All endpoints follow this structure:

```
{{_endpoint}}/services/data/v{{version}}/[service]/[resource]
```

Services used in this collection:

| Service Path | Domain |
|-------------|--------|
| `/connect/pcm/` | Product Catalog Management |
| `/connect/cpq/` | Product Discovery and Configurator |
| `/connect/core-pricing/` | Pricing Engine |
| `/connect/core-rating/` | Rate Management |
| `/connect/revenue-management/` | Asset Lifecycle |
| `/connect/context-definitions/` | Context Service |
| `/commerce/sales-transactions/` | Transaction Management (v63+) |
| `/industries/cpq/` | Instant Pricing |
| `/asset-management/` | Usage Management (assets) |
| `/revenue/usage-management/` | Usage Management (consumption, v66) |
| `/sobjects/` | Direct SObject API |
| `/actions/standard/` | Salesforce Standard Actions |
| `/composite` | Composite API |

---

## Common Workflows

### Discover → Price → Order (Simple)
1. Run Setup Runner
2. Product Discovery > List Products
3. Pricing > Instant Pricing
4. Transaction Management > Place Sales Transaction
5. Asset Lifecycle > Asset Amendment / Renewal (as needed)

### Full Quote-to-Cash
1. Run Setup Runner
2. Product Discovery → Guided Selection → Qualification
3. Product Configurator → Configure → Add/Update Nodes
4. Pricing → Price Context → Review Waterfall
5. Transaction Management → Place Sales Transaction → Preview Approval
6. [Approval workflow if triggered]
7. Transaction Management → Place Sales Transaction (order)
8. Billing → Create Invoice → Create Payment

### Asset Lifecycle
1. Transaction Management → Asset Amendment / Cancellation / Renewal
2. Usage Management → Asset Usage Details (to verify consumption)
3. Rate Management → Rating Waterfall (to audit pricing)
4. Billing → Create Invoice (from amended asset)

### Billing End-to-End
1. Place Sales Transaction (creates order and contract)
2. Billing → Create Invoice (from order)
3. Billing → Create Payment (pays invoice)
4. Billing → Apply Payment (allocates to invoice)
5. Billing → Finalize Invoice (closes)

---

## Troubleshooting

**401 Unauthorized**
- Verify `clientId` and `clientSecret` are correct for your Connected App
- Confirm `url` is set to the correct login endpoint
- Check that the Connected App has the OAuth scopes `api` and `refresh_token`
- Try running the first request again to trigger a fresh token fetch

**Missing Variables (blank `{{variable}}` in request)**
- Run the Setup Runner first — all product, catalog, and context variables are populated by it
- Check the Postman console for test script errors during the Setup Runner run
- Ensure the correct environment (`Agentforce Revenue Management v66.0`) is selected in the dropdown

**404 Not Found**
- Verify `_endpoint` is set to your org's instance URL (not the login URL)
- Confirm `version` is set to `66.0` (or the version your org supports)
- Check that the endpoint name matches a supported API path for your org edition

**400 Bad Request**
- Inspect the request body JSON for syntax errors (use the Postman console)
- Verify all required variables are populated (not empty strings)
- Check the Postman console > Response tab for the error message from Salesforce

**pn.execution / pm.execution errors in test scripts**
- The collection uses `pm.execution.setNextRequest(null)` — if you see `pn.execution` references, regenerate the collection with `build_agentforce_collection.py`

---

## Archive

`archive/` contains:
- Previous analysis documents (POSTMAN_COLLECTIONS_ANALYSIS.md, POSTMAN_ENDPOINT_REFERENCE.md, QUICK_REFERENCE.md)
- v258 reference PDF
- Original environment files for the RLM and RCA collections
- `discussion-log.md` — items flagged during the v260 optimization

---

*Spring '26 (Release 260, API v66.0) — Last updated: 2026-03-26*
