---
mode: master
area: "Product Catalog Management"
file_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
scenario_anchor: infinitech-cloud-deal
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true`) — 162 products, 18 classifications, 3 catalogs, 18 categories, 5 bundles, 27 component groups"
  - "QuantumBitComplete + Server2 CML constraint models active (default in QB orgs with `constraints=true`, `constraints_data=true`)"
sources:
  - "docs/enablement/master/qb-scenario-reference.md — canonical QB scenario reference"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help PDF § Product Catalog Management (pp 130–326)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf"
  - "docs/enablement/{248,252,254,256,258}/ — historical exercises (carry-forward references)"
sections:
  - {id: pcm-overview, introduced: foundational, available: all, scenario_step: "PCM Foundation 1"}
  - {id: products, introduced: foundational, available: all, scenario_step: "PCM Foundation 2"}
  - {id: catalogs-categories, introduced: foundational, available: all, scenario_step: "PCM Foundation 3"}
  - {id: product-classifications, introduced: foundational, available: all, enhanced_in: [256], scenario_step: "PCM Foundation 4"}
  - {id: classification-hierarchy, introduced: 258, available: "258+", scenario_step: "PCM Foundation 5"}
  - {id: attributes, introduced: foundational, available: all, enhanced_in: [256], scenario_step: "Attributes 1"}
  - {id: selling-models, introduced: foundational, available: all, scenario_step: "Attributes 2"}
  - {id: bundles-overview, introduced: foundational, available: all, scenario_step: "Bundles 1"}
  - {id: component-groups, introduced: foundational, available: all, scenario_step: "Bundles 2"}
  - {id: nested-component-groups, introduced: foundational, available: all, scenario_step: "Bundles 3"}
  - {id: constraint-rules-pcm, introduced: 258, available: "258+", scenario_step: "Bundles 4"}
  - {id: simplified-quote-bundles, introduced: 256, available: "256+", scenario_step: "Bundles 5"}
  - {id: product-discovery-overview, introduced: foundational, available: all, scenario_step: "Discovery 1"}
  - {id: product-discovery-configurability, introduced: 256, available: "256+", scenario_step: "Discovery 2"}
  - {id: default-catalog, introduced: 256, available: "256+", scenario_step: "Discovery 3"}
  - {id: search-large-catalogs, introduced: 256, available: "256+", scenario_step: "Discovery 4"}
  - {id: filterable-searchable-fields, introduced: 256, available: "256+", enhanced_in: [260], scenario_step: "Discovery 5"}
  - {id: multi-selection, introduced: 256, available: "256+", enhanced_in: [260], scenario_step: "Discovery 6"}
  - {id: cart-visibility, introduced: 256, available: "256+", scenario_step: "Discovery 7"}
  - {id: guided-product-selection-visibility, introduced: 256, available: "256+", scenario_step: "Discovery 8"}
  - {id: category-faceted-search, introduced: 258, available: "258+", scenario_step: "Discovery 9"}
  - {id: dynamic-product-facets, introduced: 258, available: "258+", scenario_step: "Discovery 10"}
  - {id: display-order-categories, introduced: 258, available: "258+", scenario_step: "Discovery 11"}
  - {id: invocable-actions, introduced: 256, available: "256+", scenario_step: "Discovery 12"}
  - {id: catalog-caching, introduced: 258, available: "258+", enhanced_in: [260], scenario_step: "Caching 1"}
  - {id: data-translation-multilingual, introduced: 258, available: "258+", scenario_step: "Localization 1"}
  - {id: auto-renewals-term, introduced: 256, available: "256+", scenario_step: "Subscription 1"}
  - {id: agentforce-product-description, introduced: 256, available: "256+", scenario_step: "Agentforce 1"}
  - {id: b2b-commerce-interop, introduced: 260, available: "260+", scenario_step: "Cross-Area 1"}
  - {id: end-to-end-synthesis, introduced: foundational, available: all, scenario_step: "Synthesis"}
---

# Master Exercise: Product Catalog Management

**Workshop format · Living document** · Version 0.1 (draft), 2026-05-06

> **About this exercise:** This is the **master Product Catalog Management exercise** — designed for in-person enablement sessions and self-paced workshops. It progresses through PCM concepts in a logical narrative arc, anchored to the **Infinitech cloud deal** workshop scenario. Foundational and release-specific content live together; per-release extracts (e.g., `docs/enablement/260/`) are filtered views.
>
> **Reading paths:**
> - **Workshop attendees:** read top to bottom. Each Part builds on the previous.
> - **Specific feature lookup:** jump to a section. Each is self-contained but cross-references prior parts when foundational concepts apply.

---

## Workshop Scenario Anchor

This exercise threads through Infinitech's adoption of QuantumBit's product catalog. Infinitech needs to:

1. Browse the QuantumBit Software, Hardware, and Services catalogs to understand what's available
2. Configure the right **QB-COMPLETE** Software bundle for each environment (Pre-Prod, Prod, Gov)
3. Configure the right **QB-QRack-750** Hardware bundle for the Prod environment server racks
4. Add Professional Services (`QB-BDL-SRVC`) for migration
5. Add Software Maintenance (Term Annual) for ongoing support

For the full scenario context — customer accounts, partner channel, multi-LE setup — see `docs/enablement/master/qb-scenario-reference.md`.

**PCM-feature anchor on the QB catalog:**

| Demo concept | QB record / wiring |
|---|---|
| Product Catalogs | `CAT-QB-HW` (Hardware) · `CAT-QB-SFT` (Software) · `CAT-QB-SRV` (Services) |
| Product Categories | 18 categories — Software, Hardware, Services with hierarchies |
| Product Classifications | 18 classifications — Server, Memory, CPU, NIC, Storage, API Type, Software, Database, Subscription, Bundles, Services |
| Top-level bundles | `QB-COMPLETE` (Software flagship) · `QB-QRack-750` (Hardware with nested groups) · `QB-BDL-R750` (Server) · `QB-BDL-STND` (Starter) · `QB-BDL-SRVC` (Pro Services) |
| Component groups | 27 groups, including nested (Computing → Cooling, Storage → Hard Drives, PCIe → GPUs/I/O/Networking) |
| Constraint Rules | **QuantumBitComplete CML** (43 ESC, 22 software products) + **Server2 CML** (81 ESC, 41 hardware products) — active on default |
| Attributes | 39 Attribute Definitions, 17 Product Attribute Definitions, 87 Picklist Values |
| Sample products | 162 commercial products, 5 bundles |

---

## Status of this document

🚧 **DRAFT — second master exercise authored.** Validates the two-tier model + Patterns 9 + 10 against PCM. The QB catalog provides much richer demo material for PCM than for Pricing — every section has concrete QB anchors. Foundational and 260-specific content has full walkthroughs; intermediate-release sections (252–258) reference prior-release exercise PDFs for deep-dive walkthroughs.

---

# Part 1: Foundations — Catalog Structure

> **Why start here:** before Infinitech can buy anything, the catalog must be modeled. This Part walks through how QuantumBit's catalog is structured — products, classifications, catalogs, categories, hierarchies — so attendees understand the building blocks every later capability depends on.

## Section 1: Product Catalog Management — what it is and why it matters {#pcm-overview}

> **Version:** introduced foundational · available all · *Scenario step: PCM Foundation 1*

**Product Catalog Management (PCM)** is the system of record for products in Revenue Cloud. It defines:

- **What products exist** — products, bundles, services, subscriptions, usage-rated entitlements
- **How they're organized** — catalogs, categories, classifications, attribute hierarchies
- **How they relate** — bundle composition, component groups, derived/contributing relationships
- **What rules govern them** — constraint rules (port/type), configuration flows, qualification rules

The PCM data model has 11 core objects (Product2, ProductCategory, ProductClassification, AttributeDefinition, ProductRelatedComponent, ProductSellingModel, etc.) — see `.cursor/skills/revenue-cloud-data-model/domains/pcm.md` for the full schema.

**Why this matters for Infinitech's deal:** every product on Infinitech's quote (QB-COMPLETE bundles, QB-QRack-750 servers, Professional Services, usage products) lives in PCM. The catalog admin's job is to model these well enough that downstream processes — Pricing, Configurator, Transaction, Invoicing — can do their jobs without hand-coding. A well-modeled catalog enables the rest of Revenue Cloud to "just work"; a poorly-modeled one causes ripple-effect issues for every quote, order, and invoice.

---

## Section 2: Products (`Product2`) {#products}

> **Version:** introduced foundational · available all · *Scenario step: PCM Foundation 2*

The QuantumBit org provisions **162 commercial products** across hardware, software, services, and usage-rated entitlements. Every product is a `Product2` record with:

- **`StockKeepingUnit`** — the SKU, used as the externalId for cross-system references
- **`Name`** — display label
- **`Family`** — high-level grouping (Software / Hardware / Services / etc.)
- **`Type`** — `Bundle` for top-level bundles, blank for individual products
- **`ConfigureDuringSale`** — `Allowed` / `Not Allowed` (whether sales reps can configure it on a quote)
- **`CanRamp`** — whether the product supports ramp deals
- **`Status`** — Active / Draft / Archived
- **`DisplayUrl`** — image resource path

**Walkthrough — inspect Infinitech's product candidates:**

1. From the App Launcher → **Products**.
2. Search for `QB-API`. Open the record.
3. Note the SKU (`QB-API`), Family (`Software`), and that it has the `PC-QB-API` classification (which we'll explore in Section 4).
4. Search for `QB-COMPLETE`. Note Type = `Bundle`, ConfigureDuringSale = `Allowed`.
5. Search for `QB-DB`. Note that it has usage-rated configuration — we'll cover usage in the Usage Management master exercise.

**Key concept:** each Product2 is a *commercial* (transactable) record. Sub-bundles (like sub-groups within QB-QRack-750) are also Product2 records with `Type = Bundle`. The structure of *which* products plug into *which* bundle is captured in `ProductRelatedComponent` — covered in Section 9.

---

## Section 3: Catalogs and Categories {#catalogs-categories}

> **Version:** introduced foundational · available all · *Scenario step: PCM Foundation 3*

QB provisions **3 Sales Catalogs** with **18 Categories** distributed across them:

| Catalog | Code | Categories |
|---|---|---|
| **QuantumBit Hardware** | `CAT-QB-HW` | Accessories, GPU, Hard Drive, Hardware Maintenance, Memory, PCIe, Power Supplies, Processor, Server, Solid State Drive · Network Adapter (nested under PCIe) |
| **QuantumBit Software** | `CAT-QB-SFT` | API, Bundle, Licenses, Maintenance, Subscription, Training (sort-ordered for navigation) |
| **QuantumBit Services** | `CAT-QB-SRV` | Services |

Each Product2 is associated to one or more categories via `ProductCategoryProduct`. QB has **98 product-category associations** wiring 162 products into the 18 categories.

**Walkthrough — explore the catalog hierarchy:**

1. From the App Launcher → **Product Catalog Management**.
2. Open the **QuantumBit Hardware** catalog (`CAT-QB-HW`).
3. Navigate the category tree — note that **Network Adapter** is nested under **PCIe** (a parent category).
4. Click into the **Server** category. Filter to see Server-classification products (PowerSwerve R750, Q-Rack 750, etc.).
5. Switch to the **QuantumBit Software** catalog. Note the sort-ordered categories (Bundle = sort 10, API = sort 20, Training = sort 40, etc.).

**Why three catalogs:** Infinitech's procurement team sees the 3 catalogs as separate purchase tracks. Hardware procurement runs through one workflow (with capex approval); software through another (term-based budgeting); services through a third (T&M billing). The catalog separation enables this even as all three end up on the same Infinitech master agreement.

---

## Section 4: Product Classifications {#product-classifications}

> **Version:** introduced foundational · available all · enhanced_in 256 (scaling: 200 → 10K products per classification) · *Scenario step: PCM Foundation 4*

A **Product Classification** is a template that defines a *kind* of product — a Server class, a CPU class, an API class. Classifications carry attributes that products inherit. QB has **18 classifications**:

| Code | Name | Domain |
|---|---|---|
| `PC-QB-SERVER` | Server | Hardware |
| `PC-QB-CPU` | Processor | Hardware |
| `PC-QB-MEMORY` | Memory | Hardware |
| `PC-QB-NIC` | Network Adapter | Hardware |
| `PC-QB-STORAGE` | Hard Drive | Hardware |
| `Q-Rack PC` | Q-Rack PC | Hardware (rack chassis) |
| `PCIe PC` | PCIe PC | Hardware (PCIe sub-slot) |
| `HDD PC` | HDD PC | Hardware (HDD sub-slot) |
| `PC-QB-API` | API Type | Software |
| `PC-QB-DB` | QuantumBit Database | Software |
| `PC-QB-COMPLETE` | QuantumBit Complete | Bundle |
| `PC-QB-PSBUNDLE` | Professional Services Bundle | Services |
| (and 6 more...) | | |

**Why classifications matter:** when you create a new product (e.g., a new Server SKU like `QB-Server-XYZ-2027`), classifying it as `PC-QB-SERVER` automatically inherits all attributes that the Server classification defines (rack form factor, power draw, etc.). This is **inheritance** — covered in Section 5.

### 256 enhancement: Scaling Products per Classification

Pre-256, a single classification could only hold **200 products**. **Spring '25 (256)** raised this to **10,000 products per classification**. This unblocks customers with very large catalogs (e.g., consumer electronics retailers with thousands of SKUs per category).

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Scale Product Creation with Enhanced Product Classification.

---

## Section 5: Product Classification Hierarchy {#classification-hierarchy}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: PCM Foundation 5*

**258 introduced** Product Classification Hierarchies — up to **3 levels of subclassification** with automatic attribute inheritance from parent to child. A subclassification inherits all attributes from its parent and can add its own unique attributes.

**For QuantumBit:**

- `PCIe PC` (parent) → `PC-QB-NIC` (subclassification: Network Adapter inherits all PCIe-PC attributes + adds NIC-specific attributes)
- `Q-Rack PC` (parent) → could subclassify into rack types
- `HDD PC` (parent) → could subclassify into HDD form factors

**Workshop walkthrough:**

1. Setup → **Product Classifications** → New
2. Create a parent classification: `PC-QB-EnterpriseServer` (or use existing `PC-QB-SERVER`)
3. Add 3–5 attributes to the parent (rack U, max power draw, etc.)
4. Create a subclassification: `PC-QB-EnterpriseServer-Tower` → set ParentClassification to PC-QB-EnterpriseServer
5. The subclassification inherits all attributes; add tower-specific attributes (chassis type)
6. Create a Product2 record classified as `PC-QB-EnterpriseServer-Tower` and observe both inherited and unique attributes are available

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Product Classification Hierarchy.

---

## Section 6: Attributes and Attribute Definitions {#attributes}

> **Version:** introduced foundational · available all · enhanced_in 256 (scaling: 15 → 200 attributes per product) · *Scenario step: Attributes 1*

QuantumBit has **39 Attribute Definitions** across the 18 classifications, with **87 Attribute Picklist Values** powering dropdown selections.

Attributes have:
- **`Code`** — the externalId (e.g., `ATTR-QB-API`)
- **`Name`** — display label (e.g., "API Environment")
- **`DataType`** — Picklist, Number, Text, Boolean, Date
- **`AttributeCategory`** — groups related attributes (18 categories)

Pricing-relevant note: **`ATTR-QB-API`** (the API Environment attribute) drives the attribute-based pricing for QB-API — see master Pricing exercise § Attribute Adjustment.

### 256 enhancement: Scaling Product Attributes

Pre-256, a single product could only have **15 attributes**. **Spring '25 (256)** raised this to **200 attributes per product**. With this enhancement, complex product configurations (e.g., a server bundle with rack U, power draw, network speed, storage type, redundancy level, geographic region, compliance tier, etc.) can be modeled directly.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Scaling Product Attributes.

---

## Section 7: Selling Models {#selling-models}

> **Version:** introduced foundational · available all · *Scenario step: Attributes 2*

QuantumBit has **9 Selling Models** that define how products relate to time and how they're priced/billed:

- **One-Time** — single price, single charge (Hardware, Professional Services)
- **Term Annual** — annual price across a fixed term (3-year SaaS contract = 3 × annual price)
- **Term Monthly / Quarterly / Semi-Annual** — same pattern with different cadence
- **Evergreen Annual / Monthly / Quarterly / Semi-Annual** — same cadence, no defined end date

Each Product2 has a `ProductSellingModelOption` for each applicable selling model — QB has **115 PSMO records** wiring products to their applicable models.

For Infinitech's deal:
- **QB-COMPLETE software**: Term Annual (3-year)
- **QB-QRack-750 hardware**: One-Time
- **QB-BDL-SRVC Professional Services**: One-Time or T&M
- **QB-DB usage product**: Term Annual + usage rating

**Cross-reference:** the master Pricing exercise § Section 4 covers selling models from a pricing perspective; this section covers them from a catalog perspective.

---

# Part 2: Bundles and Component Groups

> **Why grouped:** bundles are how QuantumBit packages products for sale. The 5 top-level bundles (especially QB-COMPLETE and QB-QRack-750) are the demo anchors for almost every PCM and Pricing capability.

## Section 8: Bundles Overview — QB's 5 top-level bundles {#bundles-overview}

> **Version:** introduced foundational · available all · *Scenario step: Bundles 1*

A **Bundle** is a Product2 with `Type = Bundle` that groups other products together via `ProductRelatedComponent` rows. QB has **5 top-level bundles**:

| SKU | Name | Profile |
|---|---|---|
| `QB-COMPLETE` | QuantumBit Complete Solution | Flagship multi-domain (Software + Add-Ons + Services + Maintenance + Training + Usage). 7 component groups, ~25 child products. **Constraints: QuantumBitComplete CML applied.** |
| `QB-QRack-750` | QuantumBit Q-Rack 750 | Hardware bundle with **nested component groups** (Computing, PCIe, Storage, Cooling — multi-level). **Constraints: Server2 CML applied.** |
| `QB-BDL-R750` | PowerSwerve R750 Rack Server | Single-server bundle (4 flat groups: CPU, Memory, HDD, NIC, each min/max=1) |
| `QB-BDL-STND` | QuantumBit Starter | Entry-tier bundle (Maintenance + Training, each min/max=1) |
| `QB-BDL-SRVC` | QuantumBit Services Project | Pro Services bundle (Engineering Resources + PM + Solution Architecture) |

**For Infinitech's deal:** they configure 3 × QB-COMPLETE (one per environment), 2 × QB-QRack-750 (Prod environment server racks), and 1 × QB-BDL-SRVC (Pro Services migration).

**Walkthrough — explore QB-COMPLETE structure:**

1. App Launcher → **Products** → search `QB-COMPLETE`.
2. Open the record. Note Type = `Bundle`, Family = `Software` (parent classification).
3. Open the **Bundle** tab. See the 7 component groups: Software, Add-Ons, Services, Maintenance, Training, Usage, Maintenance & Support.
4. Expand each group. The Usage group (`QB-PCG-USAGE`) has min/max = 1 — **exactly one** usage product is required per bundle.

**Walkthrough — explore QB-QRack-750 nested structure:**

1. Search `QB-QRack-750`. Open the record.
2. Open the **Bundle** tab. Note nested groups:
   - Computing → Cooling (sub-group)
   - Storage → Hard Drives (sub-group)
   - PCIe → GPUs / I/O / Networking (sub-groups)
   - Memory, Power Supply (top-level)
3. Each sub-group enforces its own min/max constraints (e.g., Cooling requires 1–2 components selected).

---

## Section 9: Component Groups and Min/Max Enforcement {#component-groups}

> **Version:** introduced foundational · available all · *Scenario step: Bundles 2*

A **Component Group** (`ProductComponentGroup`) defines a *slot* within a bundle — what kinds of products can go in, how many, and in what order.

QB has **27 Component Groups** distributed across the 5 bundles. Key fields:

- `Code` — externalId
- `MaxBundleComponents` — upper bound (blank = unlimited)
- `MinBundleComponents` — lower bound (blank = optional)
- `Name`, `Sequence`
- `ParentGroup` (for nested groups — see next section)

**For Infinitech's QB-COMPLETE bundle:**

| Component Group | Min | Max | Purpose |
|---|---|---|---|
| `PCG-QB-SOFTWARE` | (open) | (open) | Software components: QB-API, QB-API-MGMT, QB-API-REQT, QB-AUT-CRED, QB-FLO-STRT |
| `PCG-QB-ADDONS` | (open) | (open) | Optional add-ons |
| `PCG-QB-SERVICES` | (open) | (open) | Professional services products |
| `PCG-QB-MAINT` | (open) | (open) | Software Maintenance |
| `PCG-QB-TRAINING` | (open) | (open) | Training products |
| **`QB-PCG-USAGE`** | **1** | **1** | **Exactly one usage product required (e.g., QB-DB)** |

**Walkthrough — verify min/max enforcement:**

1. Open Configurator → start configuring QB-COMPLETE.
2. Try to save without selecting a Usage component → error: "Usage requires 1 selection".
3. Try to save with 2 Usage components → error: "Usage allows max 1 selection".
4. Select exactly 1 Usage product → save succeeds.

---

## Section 10: Nested Component Groups {#nested-component-groups}

> **Version:** introduced foundational · available all · *Scenario step: Bundles 3*

QB-QRack-750 demonstrates **multi-level nested component groups** — groups within groups, up to several levels deep. The structure:

```
QB-QRack-750 (Bundle)
├── Computing (group, sequence 1)
│   └── Cooling (sub-group, sequence 2, min 1, max 2)
├── Memory (group, sequence 2)
├── PCIe (group, sequence 4)
│   ├── GPUs (sub-group)
│   ├── I/O (sub-group)
│   └── Networking (sub-group)
├── Storage (group)
│   └── Hard Drives (sub-group)
└── Power Supply (group, sequence 5)
```

**Why nesting matters:** lets the catalog admin model real-world hardware structures (a server has slots; some slots have sub-slots; each level can have its own constraints). And — critically for the master Pricing exercise — it provides the structural prerequisite for **Price Propagation** (Pricing § Section 15).

**Walkthrough — Configure a QB-QRack-750 server for Infinitech's Prod environment:**

1. Open Configurator → start configuring QB-QRack-750.
2. The configurator surfaces nested groups. In the Computing group, select an Intel Xeon CPU (one of the variants from Server2 CML).
3. Inside Cooling sub-group, select 1–2 cooling components (Air Cooler + CacheBoost, or Liquid Cooler).
4. In the Storage group, navigate into Hard Drives sub-group. Select 1+ HDDs.
5. In PCIe → GPUs/I/O/Networking, select components per Infinitech's spec.
6. Save. The Server2 CML enforces port-type compatibility (e.g., a Gold 22Ghz CPU requires `gold22ghz` port; an SSD2 fills the `ssd2` port).

---

## Section 11: Constraint Rules in PCM (UX) {#constraint-rules-pcm}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Bundles 4*

258 introduced the **Constraint tab in PCM** for viewing constraint rules associated with a product directly from the product record. This complements the Configurator-side constraint authoring.

**For Infinitech:** the catalog admin can open `QB-COMPLETE` → Constraint tab and see all rules from the **QuantumBitComplete CML** that apply to it. Same for `QB-QRack-750` → Constraint tab → all **Server2 CML** rules.

**Cross-area pointer:** detailed constraint authoring lives in the **master Configurator exercise** (`docs/enablement/master/03-product-configurator.md`). This section in PCM covers the *visibility* of constraints in the product record context.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Product Centric Constraint Rules UX.

---

## Section 12: Simplified Quote Bundles — hide non-essential children {#simplified-quote-bundles}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Bundles 5*

Large bundles (like QB-COMPLETE with 25+ children, or QB-QRack-750 with even more sub-components) can clutter the Transaction Line Editor on Infinitech's quote. **256 introduced** the ability to **hide non-essential bundle children** in the TLE display.

For Infinitech: catalog admins can mark certain QB-COMPLETE child products (e.g., low-cost add-ons, internal-only flags) as "hidden in TLE". The quote still has them; the sales rep just doesn't see them in the line list. Quote documents render the full bundle but the focus is on essential products.

**Configuration:**

1. Open the bundle (e.g., QB-COMPLETE).
2. Open the Bundle tab → component groups.
3. For each child product, set `IsVisibleInTransactionLineEditor` (or equivalent — exact field name varies; consult Help).
4. Save.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Simplify Quotes and Quote Documents.

---

# Part 3: Product Discovery

> **Why grouped:** Product Discovery is the user interface that sales reps use to find and add products to quotes/orders. It surfaces the catalog Infinitech configured in Parts 1–2.

## Section 13: Product Discovery Overview {#product-discovery-overview}

> **Version:** introduced foundational · available all · *Scenario step: Discovery 1*

**Product Discovery** is the runtime UI that lets sales reps:
- Browse the catalog by category
- Search for products by name, SKU, attribute
- Filter the result list by faceted attributes
- Multi-select products to add to a quote in one action

It surfaces in:
- The **Browse Catalogs** quick action on Quote/Order pages
- The **Add Products** flow during Transaction Management
- Customer self-service portals (when configured for community users)

For Infinitech: their sales rep at Robot Resellers uses Product Discovery to navigate the QuantumBit Software catalog, find QB-COMPLETE, and add it to Infinitech's quote.

The Product Discovery experience is **highly configurable** — Sections 14–24 cover specific configuration options.

---

## Section 14: Product Discovery — Configurability {#product-discovery-configurability}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 2*

256 made the Product Discovery list page configurable in **Lightning App Builder** (no-code) or **Discover Products flow** (admin code). Customers can configure which fields display, page size, sort order, default filters, and more without modifying source.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Product Discovery — Configurability.

---

## Section 15: Default Catalog {#default-catalog}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 3*

When sales reps open Product Discovery, they should land on a sensible default catalog rather than seeing an empty selector. **256 introduced** the **Default Catalog** setting.

For Infinitech: the Robot Resellers sales rep handles primarily Software deals, so set the Default Catalog to `CAT-QB-SFT`. The rep lands on QuantumBit Software automatically; they can switch to Hardware or Services if needed.

**Configuration via Lightning App Builder:**

1. Edit the Discover Products flow's list page in Lightning App Builder.
2. On the Product List Page component, set the **Default Catalog** property to `CAT-QB-SFT`.
3. Save and activate.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Effortlessly Manage Catalogs on Your Product List Page.

---

## Section 16: Search Products in Large Catalogs {#search-large-catalogs}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 4*

256 added **Indexed Products** support for catalogs up to **20 million products**. Sales reps can search by name, description, product code, and stock keeping unit at scale.

For QuantumBit: with only 162 products today, the scaling concern is minor. But as customer customers (like manufacturers with 100K+ SKU catalogs) adopt PCM, this is critical.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Search Products in Large Catalogs Faster.

---

## Section 17: Filterable & Searchable Field Configuration {#filterable-searchable-fields}

> **Version:** introduced 256 (Summer '25) · available 256+ · enhanced_in 260 (limit raised: 25+40 → 100 combined) · *Scenario step: Discovery 5*

A **Filterable Field** appears as a facet in the Product Discovery filter sidebar. A **Searchable Field** is included in keyword search index. Pre-260, you could configure up to **25 searchable + 40 filterable**. **260 raised this to 100 combined searchable + filterable fields**, with higher limits available via Salesforce Customer Support.

**Walkthrough for Infinitech:**

1. Setup → Product Discovery Settings → Indexed Products.
2. Add filterable fields: `Family`, `Status`, `IsActive`, plus 5+ Attribute Definitions (e.g., `ATTR-QB-API`, environment-related attributes).
3. Add searchable fields: `Name`, `ProductCode`, `StockKeepingUnit`, `Description`.
4. Trigger index regeneration.
5. From Product Discovery, demonstrate refined search using the newly-indexed attributes.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` (256 base) + `docs/enablement/260/260-product-catalog-management-hands-on.md` § Feature 2 (260 enhancement).

---

## Section 18: Multi-Selection in Product Listing {#multi-selection}

> **Version:** introduced 256 (Summer '25) · available 256+ · enhanced_in 260 (limit raised: 20 → 100) · *Scenario step: Discovery 6*

Pre-260, sales reps could multi-select up to **20 products** at a time. **260 raised this to 100 products**, with higher limits via support.

For Infinitech: bulk-add 50+ Software products from a saved filter to a quote in one action.

**Configuration:** Discover Products flow → Product List Page component → Maximum Selections property → 100.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` (256 base) + `docs/enablement/260/260-product-catalog-management-hands-on.md` § Feature 3 (260 enhancement).

---

## Section 19: Cart Visibility on Product List Container Page {#cart-visibility}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 7*

256 added the ability to control whether a **product cart** is visible on the Browse Catalogs page during Transaction Management. The cart lets sales reps preview their selected products before adding to a quote/order.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Manage Cart Visibility on Product List Container Page.

---

## Section 20: Visibility of Guided Product Selection {#guided-product-selection-visibility}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 8*

**Guided Product Selection** (a guided-questions flow that helps reps pick products) can be enabled or disabled per-deployment via Lightning App Builder.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Control the Visibility of Guided Product Selection.

---

## Section 21: Category Based Faceted Search {#category-faceted-search}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Discovery 9*

258 added the ability to surface relevant facets in Product Discovery **based on the selected category**. When a sales rep navigates into Hardware → Server, the filter panel shows facets specific to Server (rack U, processor, memory) — not generic facets for all categories.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Category Based Faceted Search.

---

## Section 22: Dynamic Product Facets {#dynamic-product-facets}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Discovery 10*

258 added **dynamic facet selection** — instead of a fixed list of facets, the system picks the most relevant facets based on the current search results. This streamlines navigation when catalogs grow.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Dynamic Product Facets and Higher Limit.

---

## Section 23: Display Order of Categories {#display-order-categories}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Discovery 11*

258 added **predictable category sorting** for the product discovery navigation. QB software catalog already uses this — Bundle (10), API (20), Maintenance (50), Subscription (100), etc.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Display order of categories.

---

## Section 24: Invocable Actions for Product Discovery {#invocable-actions}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Discovery 12*

256 introduced **Invocable Actions** for Product Discovery — programmatic ways to add or remove products from a quote without using the UI. Useful for orchestrating bulk operations or integrating with external systems.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Product Discovery — Invocable Actions.

---

# Part 4: Catalog Caching and Performance

## Section 25: Catalog Caching {#catalog-caching}

> **Version:** introduced 258 (Winter '26) · available 258+ · enhanced_in 260 (regenerate / clear cache invocable actions) · *Scenario step: Caching 1*

**258 introduced** a Product Detail Cache layer — frequently-requested product details get served from a dedicated cache rather than re-pulling from the database every time. **260 enhanced** with management invocable actions: **Re-Generate Cache** and **Clear Cache**.

**For Infinitech:** when Robot Resellers' sales reps repeatedly browse QB-COMPLETE for product details, the cache makes the experience instant. After a major catalog update (e.g., adding a new Software component to QB-COMPLETE), the catalog admin runs `Clear Cache` so reps see the new component immediately rather than waiting for natural expiry.

### Configuration (one-time setup)

> **Permission required:** Product Catalog Management Designer

1. Setup → Quick Find → **Product Discovery Settings**.
2. Enable **Product Catalog Management Cache**.

### Cache management flow (260 — uses the new invocable actions)

1. Setup → **Flows** → Create a flow (Schedule-Triggered for periodic refresh, or Autolaunched for ad-hoc).
2. Add an **Action** element. Find the `Runtime_industries_epc_ProductCatalogCacheRefresh` batch job action.
3. Choose:
   - **Clear Cache** — empty the cache entirely
   - **Refresh Existing Products** — re-pull current cached records
   - **Cache All Products** — sync all products including newly-added
4. Save and activate.

### Runtime cache resolution

When a user requests product details:
1. System checks the cache. If present, returns instantly.
2. If absent, fetches from database and writes back to cache.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Faster product detail retrieval with cache (258 base) + `docs/enablement/260/260-product-catalog-management-hands-on.md` § Feature 1 (260 enhancement).

---

# Part 5: Localization

## Section 26: Data Translation — Multilingual Search {#data-translation-multilingual}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Localization 1*

258 added the ability to translate product names, descriptions, attribute names, and picklist values into multiple languages. Search works across translations.

For Infinitech's UK and EU offices: translate QB-COMPLETE component names and descriptions into French, German, Spanish (or others). UK office sales reps see English; French office sees French translations of the same products.

**Configuration via Translation Workbench:**

1. Setup → Translation Workbench → Translation Language Settings.
2. Enable target languages (fr, de, es, etc.).
3. Translation Workbench → Translate → select Product2 → translate names + descriptions.
4. For attribute picklists: Setup → Attribute Definitions → translate picklist values.
5. For bulk translation: Translation Workbench → Export → translate offline → Import.

> **Detailed walkthrough:** `docs/enablement/258/Product Catalog Management - Winter '26 Revenue Cloud - External.pdf` § Data translation - Multilingual Search.

---

# Part 6: Subscription Auto-Renewal

## Section 27: Auto-Renewals for Term-Based Products {#auto-renewals-term}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Subscription 1*

256 added the ability to **automatically renew Term-Defined products** when an order is assetized. Catalog admins can configure default auto-renewal on a product; sales reps can override per order.

For Infinitech: their QB-COMPLETE software subscriptions auto-renew at end of term unless explicitly canceled. Reduces administrative overhead — finance and legal don't need to chase every renewal.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Simplify Transaction Management with Auto-Renewals for Term Based Products.

---

# Part 7: Agentforce in PCM

## Section 28: Agentforce — Generate Product Description {#agentforce-product-description}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Agentforce 1*

256 introduced an Agentforce-powered feature for catalog admins: **AI-generated product descriptions** based on product name, classification, and attributes. Saves time for catalogs with thousands of products that need rich descriptions.

For QuantumBit: when adding a new product (e.g., `QB-Server-XYZ-2027`), the catalog admin uses Agentforce to generate a draft description that mentions the rack form factor, processor compatibility, and target use case. The admin reviews and refines.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Product Catalog Management.pdf` § Agentforce - Generate Product Description.

---

# Part 8: Cross-Area — B2B Commerce Interoperability

## Section 29: B2B Commerce Interoperability {#b2b-commerce-interop}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Cross-Area 1* · ✨ **New in 260**

260 expands B2B Commerce ↔ Revenue Cloud interop with five capabilities. **Primary home:** B2B Commerce Spring '26 Solution Overview (separate enablement track). PCM readers should know these exist.

| Feature | Description |
|---|---|
| **Dynamic Attributes** | PCM-defined attributes flow into B2B storefronts — sales reps and buyers see consistent attribute values across assisted and self-serve channels |
| **Request for Quote** | Buyers can initiate a Quote request directly from a B2B Cart, generating a quote that PCM-defined products populate |
| **Unified Pricing** | Single pricing-engine setup serves both RCA and B2B Commerce — pricing procedures admins build for PCM products apply across channels |
| **Qualification Rules** | Product eligibility on the storefront uses qualification criteria defined in PCM — customer entitlements automatically gate B2B catalog visibility |
| **Amend, Renew & Cancel** | Self-serve buyer experience for asset lifecycle actions on PCM-defined subscription products |

→ **Full configuration:** B2B Commerce Spring '26 Solution Overview (request from B2B Commerce enablement team).

---

# Workshop Synthesis: Putting It All Together — Infinitech Catalog Setup {#end-to-end-synthesis}

> **Version:** introduced foundational · available all · *Scenario step: Synthesis*

The capstone exercise of this master. Set up the QuantumBit catalog so it's ready to support Infinitech's deal end-to-end.

### What attendees do

1. **Catalog scoping** — confirm Infinitech's account is linked appropriately. Set Default Catalog for Robot Resellers' sales rep to `CAT-QB-SFT` (Software).
2. **Browse the catalog** — navigate Hardware / Software / Services. Use search and filter facets (262 dynamic, 260 search/filter limits).
3. **Multi-select** — bulk-add 30+ Software products in one action (260 enhancement).
4. **Configure QB-COMPLETE bundle** — for Pre-Prod environment, choose Software components, Add-Ons, Services, Maintenance, Training, exactly 1 Usage product (QB-DB).
5. **Configure QB-QRack-750 server** — exercise nested groups (Computing → Cooling, Storage → Hard Drives, PCIe → GPUs/I/O/Networking) per the Server2 CML.
6. **Translate select product names** to French and German for Infinitech's EU office.
7. **Generate product descriptions** for 5 new internal products via Agentforce.
8. **Set Auto-Renewal default** on QB-COMPLETE.
9. **Inspect the cache** — clear and re-generate after the catalog updates.

### What attendees should observe

- Catalog navigation surfaces the structured hierarchy (Catalogs → Categories → Classifications → Products)
- Bundle min/max enforcement fires on QB-COMPLETE (Usage requires 1)
- Server2 CML on QB-QRack-750 validates port-type compatibility (a Gold 22Ghz CPU plugs into the gold22ghz port; an SSD2 plugs into ssd2)
- Multi-select limits, faceted search, and filter configuration all work as expected
- Translation Workbench renders QB product names in non-English locales
- Cache management actions reflect catalog changes immediately

### Discussion prompts for the workshop

- Why does QB-COMPLETE require exactly 1 Usage product? What would change if it allowed 0 or many?
- How does the QuantumBitComplete CML differ from Server2 CML? When would you author a new CML model vs reuse an existing one?
- Walk through the search/filter configuration limits — when do customers hit the 100-combined-fields cap, and what's the workaround?
- Cache management: when do you Re-Generate vs Clear the cache?
- Auto-Renewal default — does Infinitech want it on for software, off for hardware? Why?

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.

---

## Appendix: Open authoring questions

1. **Sections referencing prior-release PDFs** — same question as master Pricing. Is "summary + link to prior PDF" sufficient depth, or should master sections include full step-by-step walkthroughs?
2. **Synthesis scope** — capstone covers a lot. Should it split into Catalog Setup (Parts 1–2) and Discovery + Operations (Parts 3–8)?
3. **Demo URLs** — three confirmed demos for 260 PCM (Product Detail Caching, Filterable & Searchable Field, Enhanced Multi-Selection). Need actual URLs.
4. **B2B Commerce inclusion** — currently a single section pointer. Is that sufficient, or should it have an inline summary table of each feature's PCM impact?
5. **Constraint Rules in PCM (Section 11)** — currently a thin pointer to Configurator master. Should it have a small in-line walkthrough showing the Constraint tab in PCM?
6. **Agentforce section** — only 1 PCM-specific Agentforce feature in 256. Will more land in 262? Worth a forward-look note.
7. **Pre-built starter Quote with QB-COMPLETE pre-configured** — would shorten the catalog-setup synthesis step significantly. Same gap as master Pricing's open question.
