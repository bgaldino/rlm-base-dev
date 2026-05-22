---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Product Catalog Management"
document_version: 0.2
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag) — 162 products across 28 PCM objects"
  - "Product Catalog Management enabled and Product Discovery Settings configured"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — internal Solution Overview deck (CONFIDENTIAL)"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory"
  - "datasets/sfdmu/qb/en-US/qb-pcm/ — QuantumBit catalog data plan"
---

# Revenue Cloud — Product Catalog Management

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. Documentation and product references are transitioning. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded — 162 products across 28 PCM objects, with 18 product classifications and 39 attribute definitions.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 release notes, Solution Overview deck, and master Help PDF.** Configuration steps reflect what's in the master PDF as of 2026-01-15. Items still needing user input are flagged inline with `[NEEDS REVIEW]`. Author should walk through each feature in a 260 org to confirm steps and capture screenshots before flipping `status: draft` → `status: review`.

---

## Carry-forward inventory (from prior releases)

The following features were introduced in 256 (Su'25) or 258 (W'26). They remain valid for 260 unless flagged otherwise. Readers should reference the prior-release exercise PDFs for full walkthroughs.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Scaling Product Attributes (up to 200 per product) | 256 | `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` | ✅ no change |
| Scaling Products per Product Classification (up to 10K) | 256 | same | ✅ no change |
| Product Discovery — Configurability (list page in Lightning App Builder) | 256 | same | ✅ no change |
| Product Discovery — Default Catalog | 256 | same | ✅ no change |
| Product Discovery — Invocable Actions | 256 | same | 🔄 **enhanced** in 260 — Product Detail Cache management (Feature 1 below) extends the invocable action |
| Cart Visibility on Product List Container Page | 256 | same | ✅ no change |
| Visibility of Guided Product Selection on Product List Page | 256 | same | ✅ no change |
| Search Products in Large Catalogs (up to 20M) | 256 | same | 🔄 **enhanced** in 260 — Filterable/Searchable Field limits expanded (Feature 2) |
| Simplified Quote Bundles (hide non-essential children) | 256 | same | ✅ no change |
| Auto-Renewals for Term-Based Products | 256 | same | ✅ no change |
| AgentForce — Generate Product Description | 256 | same | ✅ no change |
| Category Based Faceted Search | 258 | `docs/enablement/258/Product Catalog Management - Winter'26 Revenue Cloud - External.pdf` | ✅ no change |
| Dynamic Product Facets | 258 | same | ✅ no change |
| Display Order of Categories | 258 | same | ✅ no change |
| Data Translation — Multilingual Search | 258 | same | ✅ no change |
| Faster Product Detail Retrieval with Cache (initial caching layer) | 258 | same | 🔄 **enhanced** in 260 — Feature 1 below adds management actions on top of the 258 caching layer |
| Product Classification Hierarchy (3 levels of subclassification + attribute inheritance) | 258 | same | ✅ no change |
| Product Centric Constraint Rules UX (Constraint tab in PCM) | 258 | same | ✅ no change |

---

## Upgrade Guidance from Winter '26

> Customers upgrading from 258 (Winter '26) to 260 (Spring '26) — review these transitional actions before assuming the carry-forward features in this area work as expected. Source: master PDF "Upgrade Guidance for Spring '26" section (p 115–117).

### Discover Products Flow Update

If you didn't update the Discover Products flow during Winter '26, Spring '26 requires it for Groups in quotes/orders to keep working.

**Affected:** customers using Groups in quotes/orders, with a custom Discover Products flow not updated in 258.

**Steps:**

1. From Setup, in the Quick Find box, enter `Flows` and select it.
2. Open the custom **Discover Products** flow.
3. In the flow builder, check if the Apex-Defined variable `discoverProductsContext` is available.
4. If the variable exists, edit it and select **Available for Input**.
5. If the variable doesn't exist, click **New Resource**, select **Variable**, enter `discoverProductsContext` as the API name, set **Apex-Defined** as the data type, and select `ProductConfig__DiscoverProductsContext` as the Apex class. Mark **Available for Input**. Click Done.

### Custom Permission Set Groups Update

If you didn't recalculate licenses during Winter '26, Spring '26 requires recalculation to fix net-aggregate Field-Level Security (FLS) calculation on the `OverriddenInheritedAttributeId` field of `ProductClassificationAttr`.

**Affected:** customers with custom permission set groups containing any of:
- Product Catalog Management Designer
- Product Catalog Management Viewer
- Product Catalog Management Customer Community User
- Product Catalog Management Partner Community User

**Steps:**

1. From Setup, in the Quick Find box, enter `Permission Set Groups` and select it.
2. Open the affected custom permission set group.
3. Click **Recalculate** to update the permissions inside the group.

Without recalculation, users in these pre-existing groups may lack required permissions for new fields, causing product data to not fetch correctly.

---

## Release Overview

Salesforce Revenue Cloud Product Catalog Management includes the following net-new features in Spring '26:

1. **Product Detail Caching Enhancements** — Manage the Product Detail Cache via expanded invocable actions: re-generate cache for existing products, clear cache, or sync all products. Builds on the 258 caching layer.
2. **Filterable & Searchable Field Configuration** — Indexed Products supports up to **100 combined searchable + filterable fields** (was 25 searchable + 40 filterable). Higher limits available via support.
3. **Multi-Selection in Product Listing** — Multi-select up to **100 products** (was 20) from Product Listing for bulk addition to Quotes/Orders.

Plus, in cross-area scope but PCM-relevant — **Spring '26 B2B Commerce Interoperability** for Revenue Cloud Advanced + Commerce Cloud Advanced/Growth customers:

- **Dynamic Attributes** *(enhanced)* — sell configurable products with attributes in B2B storefronts
- **Request for Quote** *(new)* — initiate a Quote request from a Cart
- **Unified Pricing** *(new)* — single setup/management of the pricing engine between RCA and B2B
- **Qualification Rules** *(new)* — product eligibility on storefront based on qualification criteria
- **Amend, Renew & Cancel** *(new)* — self-serve experience for amendments, renewals & cancellations

> *B2B Commerce details are documented separately in the B2B Commerce Spring '26 Solution Overview. The PCM exercise should call out these capabilities exist for cross-channel selling, but full configuration walkthroughs live in the B2B Commerce enablement materials.*

---

## Feature 1: Product Detail Caching Enhancements

> **Source:** master PDF "Manage Product Details in the Cache" (p 160). Solution Overview "Product Detail Caching Enhancements" page. Feature builds on the 258 caching layer — readers unfamiliar with that layer should review the 258 PCM exercise first.

### Business Objective

Customers need better control over product detail caching to ensure sales reps always see the most accurate data. The 258 caching layer made retrieval fast, but couldn't be refreshed or cleared on demand. Spring '26 adds **invocable management actions** so admins can intentionally invalidate or warm the cache during major catalog updates — without waiting for time-based expiry.

### Use Cases

**Catalog Admin persona:**

- **Major catalog refresh** — when a wave of product updates (price changes, attribute revisions, new bundles) lands in the org, the admin runs the cache action to ensure sales reps instantly see the new information when configuring quotes — instead of seeing stale cached entries until the cache expires naturally.
- **Targeted invalidation** — after a single product fix, the admin clears the cache for that scope so the next quote attempt fetches fresh data.

### Design Time Configuration

> **Permission required:** Product Catalog Management Designer

**Step 1 — Confirm PCM Cache is enabled** (one-time, may already be in place from the 258 setup):

1. From Setup, in the Quick Find box, enter `Product Discovery`, then select **Product Discovery Settings**.
2. Enable **Product Catalog Management Cache**.

**Step 2 — Configure the cache management flow:**

1. From Setup, in the Quick Find box, enter `Flows`, then select **Flows**.
2. Create a flow (e.g., a Schedule-Triggered Flow for periodic refresh, or an Autolaunched Flow for ad-hoc admin invocation).
3. Add an **Action** element. In the action picker, find and select the `Runtime_industries_epc_ProductCatalogCacheRefresh` batch job.
4. Configure the action by selecting one of these options:
   - **Clear Cache** — empty the cache entirely.
   - **Refresh Existing Products** — re-pull current cached records from the database.
   - **Cache All Products** — sync all products from the database into the cache, including products newly added since the last refresh.
5. Save and activate the flow.

**Step 3 — Monitor execution:**

- From Setup, in the Quick Find box, find and select **Monitor Workflow Services**.
- Confirm the batch job ran to completion.

### How the cache resolves at runtime

When a user requests information for a specific product:

1. The system first checks the cache.
2. If the details are present, they're returned instantly.
3. If not, the system fetches from the database and writes the result back to the cache for future requests.

### QuantumBit walkthrough scenario

After loading the QB catalog (162 products) and enabling PCM cache:

1. Open a product like the `Q-Rack` family (`PC-QB-Q-Rack` classification, multiple SKUs) in Product Discovery — note the load time (uncached).
2. Open it again — note the speed improvement (cached).
3. Run a `Cache All Products` action via the configured flow.
4. Modify a product description directly in the QB catalog (e.g., update one of the QuantumShell rack accessories).
5. Without the new feature, the cached version would be stale until expiry. With the `Refresh Existing Products` action, run it now.
6. Re-open the product in Product Discovery and confirm the updated description appears.

### Configuration and Runtime Video

📹 **"Product Detail Caching Demo"** — recorded demo confirmed in the Solution Overview licensing matrix. [NEEDS REVIEW — get URL.]

---

## Feature 2: Filterable & Searchable Field Configuration

> **Source:** Solution Overview "Filterable & Searchable Field Configuration" page. Master PDF "Product Catalog Management Limits" (p 325) confirms the new limit ("up to 100 combined searchable and filterable fields and attributes").

### Business Objective

Revenue Cloud customers with very large product catalogs (4M–20M items) need search and filtering capabilities that scale with their business. The prior limits — 25 searchable fields + 40 filterable fields — were too restrictive for catalogs at that size; admins had to choose between accurate discovery and performance. The Spring '26 limit raise to **100 combined searchable + filterable fields** lets admins make more product attributes indexable and surfaced to sales reps without hitting the prior cap.

### Use Cases

**Catalog Admin persona:**

- **Surface more product attributes for narrowing search** — make additional standard fields and dynamic attributes filterable so sales reps can refine product discovery beyond the prior 40-field ceiling.
- **Make more text fields searchable** — extend keyword search beyond the prior 25-field limit to cover more SKU codes, descriptions, and attribute strings.

### Design Time Configuration

[NEEDS REVIEW] — confirm exact navigation path in 260. The master PDF section starts around line 16618 ("Standard or custom fields on the Product object can be filterable…") with an Add Filterable Fields procedure that should still apply. Higher-limit gating likely happens at field-configuration time rather than as a separate setting.

Approximate flow (from prior-release pattern; verify in 260 org):

1. From Setup, in the Quick Find box, find and select **Product Discovery Settings**.
2. Open the **Indexed Products** configuration.
3. Add filterable fields (Product2 standard or custom fields, Attribute Definitions). Up to 100 combined searchable + filterable.
4. Save and trigger product index regeneration if required.

> Higher limits beyond 100 require a Salesforce Customer Support request.

### QuantumBit walkthrough scenario

The QB catalog has 39 attribute definitions across 18 product classifications — well under the 100-combined limit. The exercise can demonstrate adding a comprehensive set of filterable + searchable attributes without artificial constraints. Suggested demo:

1. Add 3 standard fields as searchable: `Name`, `ProductCode`, `StockKeepingUnit`, `Description`.
2. Add 3 standard fields as filterable: `Family`, `Status`, `IsActive`.
3. Add 5+ Attribute Definitions as both searchable and filterable: select from the QB attributes (e.g., processor type, memory size, rack units).
4. Trigger index regeneration.
5. From Product Discovery, demonstrate refined search using the newly-indexed attributes.

### Configuration and Runtime Video

📹 **"Filterable & Searchable Field Demo"** — recorded demo confirmed. [NEEDS REVIEW — get URL.]

> **Note from licensing matrix:** This feature requires "Contact Salesforce to enable" (toggle gated by Support).

---

## Feature 3: Multi-Selection in Product Listing

> **Source:** Solution Overview "Multi-selection in Product Listing" page. Configurable via Page Size / multi-select properties on the Product List Page Flow Component / Product List Container Flow Component / Lightning App Builder.

### Business Objective

Product Discovery previously allowed multi-selecting up to **20** products to add to a Quote or Order in a single action. Customers — especially in industries with high-line-count quotes (manufacturing, telecom, distributors) — needed the ability to bulk-add far more than 20 products at once.

### Use Cases

**Sales Rep persona:**

- **Bulk-add products to a Quote** — search for a category (e.g., all `QuantumBit Rack PDUs`) and multi-select 50+ matching products to add to the quote in one action, instead of adding them in batches of 20.
- **Bulk replenishment Orders** — select up to 100 SKUs from a saved filter and add them all to an Order at once.

### Design Time Configuration

> **Permission required:** Product Catalog Management Designer or equivalent for editing the Product Discovery flow / Lightning App Builder configuration.

The multi-select limit is a property on the **Product List Page Flow Component**, **Product List Container Flow Component**, and the equivalent Lightning App Builder component. (See master PDF p 297 — Product List Page property table.)

[NEEDS REVIEW] — confirm exact property name in 260 (likely `Maximum selections` or similar). Walk-through steps:

1. Open the **Discover Products** flow in Flow Builder (or your custom version).
2. Locate the **Product List Page** component.
3. Set the multi-selection limit property to a value up to 100.
4. Save and activate the flow.
5. Verify in Product Discovery: the maximum number of products selectable in one batch should match the configured value.

> Higher limits beyond 100 require a Salesforce Customer Support request.

### QuantumBit walkthrough scenario

1. From the QB catalog, navigate to the `Software` family — multiple subscription products available.
2. Filter the Product List view to show software-family products only.
3. Multi-select up to 100 products.
4. Add them all to a draft Quote in a single action.
5. Confirm Quote Line Items reflect the full selection.

### Configuration and Runtime Video

📹 **"Enhanced Multi-Selection Demo"** — recorded demo confirmed. [NEEDS REVIEW — get URL.]

> **Note from licensing matrix:** This feature requires "Contact Salesforce to enable" (toggle gated by Support).

---

## Cross-Area: B2B Commerce Interoperability

The Spring '26 release expands B2B Commerce ↔ Revenue Cloud interop with five capabilities that affect how PCM data surfaces in B2B Commerce storefronts. **Primary home:** B2B Commerce Spring '26 Solution Overview (separate enablement track). PCM readers should know these exist; full configuration walkthroughs live in B2B Commerce enablement materials.

| Feature | Tier | Why it matters to PCM readers |
|---|---|---|
| **Dynamic Attributes** | Enhanced | PCM-defined attributes now flow into B2B storefronts — sales reps and buyers see consistent attribute values across assisted and self-serve channels. |
| **Request for Quote** | New | Buyers can initiate a Quote request directly from a B2B Cart, generating a quote that PCM-defined products populate via the standard catalog flow. |
| **Unified Pricing** | New | Single pricing-engine setup serves both RCA and B2B Commerce — the pricing procedures admins build for PCM products apply across channels. |
| **Qualification Rules** | New | Product eligibility on the storefront uses qualification criteria defined in PCM — customer entitlements automatically gate B2B catalog visibility. |
| **Amend, Renew & Cancel** | New | Self-serve buyer experience for asset lifecycle actions on PCM-defined subscription products. |

→ **Full configuration:** B2B Commerce Spring '26 Solution Overview (request from B2B Commerce enablement team).

---

## QuantumBit data reference

When authoring step-by-step instructions, reference QuantumBit records by name. Source: `datasets/sfdmu/qb/en-US/qb-pcm/`.

### Product Classifications (18 active)

Selected examples from `ProductClassification.csv`:

| Code | Name | Notes |
|---|---|---|
| `PC-QB-SERVER` | Server | Hardware infrastructure |
| `PC-QB-CPU` | Processor | Hardware — sub-component |
| `PC-QB-MEMORY` | Memory | Hardware — sub-component |
| `PC-QB-NIC` | Network Adapter | Hardware — sub-component |
| `PC-QB-STORAGE` | Hard Drive | Hardware — sub-component |
| `PC-QB-CABLES` | Cables | Hardware — accessory |
| `PC-QB-API` | API Type | Software |
| `PC-QB-SOFTWARE` | Software | Software (Draft status) |
| `PC-QB-DB` | QuantumBit Database | Software |
| `PC-QB-SUB` | Subscription | Selling model classification |
| `PC-QB-COMPLETE` | QuantumBit Complete | Bundle classification |
| `PC-QB-STARTER` | QuantumBit | Bundle classification |
| `PC-QB-SERVICES` | Services | Professional services |
| `PC-QB-PSBUNDLE` | Professional Services Bundle | PS bundle |
| `PC-QB-PS-RESOURCES` | Engineering Resources | PS T&M |
| `Q-Rack PC` | Q-Rack PC | Rack accessories |
| `PCIe PC` | PCIe PC | Hardware — sub-component |
| `HDD PC` | HDD PC | Hardware — sub-component |

### Sample Products for Walkthroughs

Selected by family — pick representative products for the type of demonstration needed:

- **Bundle examples**: products with `BasedOn.Code` referring to bundle classifications (e.g., `PC-QB-COMPLETE`, `PC-QB-STARTER`)
- **Single SKU examples**: PowerSwerve servers, QuantumShell rack accessories
- **Subscription/term-defined examples**: QuantumBit Automation subscription with QB Credits quota
- **Bundle with deep child structure**: QB Complete bundles with nested classifications

[Author: select 3–5 canonical SKUs from `Product2.csv` and document them here as the "use this product" reference.]

### Attribute Definitions (39 total)

39 attributes loaded across the 18 classifications. Use these for demonstrating Filterable/Searchable Field Configuration.

[Author: list 5–10 representative attribute codes here from `AttributeDefinition.csv`.]

### Catalogs

[Author: list catalog names from `ProductCatalog.csv`.]

### Categories

[Author: list category names + parent relationships from `ProductCategory.csv`.]

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview confirms three recorded demos for 260 PCM: *Product Detail Caching Demo*, *Filterable & Searchable Field Demo*, *Enhanced Multi-Selection Demo*. Need actual URLs to embed/link.
2. **Field configuration UI navigation in 260** — confirm exact path for Filterable & Searchable Field Configuration; pattern from prior releases is approximate. Likely under Indexed Products or Product Discovery Settings.
3. **Multi-selection property name** — confirm in 260 what the multi-select-max property is called (likely `Page Size` or `Max Selections` per master PDF p 297).
4. **B2B Commerce features inclusion** — defer to B2B Commerce enablement for full walkthroughs, or include short walkthroughs in the PCM exercise? Recommend defer.
5. **Spring '26 Discover Products flow update** — should the 260 PCM exercise include the `discoverProductsContext` Apex-Defined variable migration as a "First time you see this org after upgrade" callout? It's upgrade guidance, not a feature, but readers will hit it if they're upgrading from W'26.
6. **Permission Set Group recalculation** — same upgrade guidance question. Worth a callout?
7. **Attribute Picklist values data** — the QB catalog has 87 picklist values; should the exercise demonstrate Filterable Field Configuration against attribute picklists specifically, or just any custom field?
8. **AgentForce features for PCM in 260** — Solution Overview Salesforce Go section mentions Agent support. Is there a 260 PCM-specific Agentforce capability we should call out, or do we wait for 262 (which has Constraint Rules in Product Discovery and Product Variants as headline items)?

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
