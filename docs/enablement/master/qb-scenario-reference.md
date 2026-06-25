# QuantumBit Scenario Reference

The canonical reference for what a `prepare_rlm_org`-built QuantumBit org contains by default. This document grounds every master exercise — when an exercise needs to reference a product, account, legal entity, bundle, constraint model, etc., the source of truth is here, traced back to the data plan that provisions it.

> **Status:** Living document. Update when QB data plans add or remove records, or when new constraint models, customer templates, or partners are added.
> **Last Updated:** 2026-05-06
> **Source orgs:** Built via `cci flow run prepare_rlm_org` with default flag set (`qb=true`, `billing=true`, `tax=true`, `dro=true`, `rating=true`, `rates=true`, `clm=true`, `prm=true`, `docgen=true`, `constraints=true`, `constraints_data=true`).

---

## 1. Catalog Structure

### Product Catalogs (3)

| Code | Name | Type |
|---|---|---|
| `CAT-QB-HW` | QuantumBit Hardware | Sales |
| `CAT-QB-SFT` | QuantumBit Software | Sales |
| `CAT-QB-SRV` | QuantumBit Services | Sales |

Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductCatalog.csv`

### Product Categories (18 across 3 catalogs)

**Hardware (CAT-QB-HW):**
- Accessories, GPU, Hard Drive, Hardware Maintenance, Memory, PCIe, Power Supplies, Processor, Server, Solid State Drive
- Network Adapter (nested under PCIe)

**Software (CAT-QB-SFT):**
- API, Bundle, Licenses, Maintenance, Subscription, Training (sort-ordered for navigation)

**Services (CAT-QB-SRV):**
- Services

Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductCategory.csv`

### Product Classifications (18)

| Code | Name | Domain |
|---|---|---|
| `PC-QB-SERVER` | Server | Hardware |
| `PC-QB-CPU` | Processor | Hardware |
| `PC-QB-MEMORY` | Memory | Hardware |
| `PC-QB-NIC` | Network Adapter | Hardware |
| `PC-QB-STORAGE` | Hard Drive | Hardware |
| `PC-QB-CABLES` | Cables | Hardware |
| `Q-Rack PC` | Q-Rack PC | Hardware (rack) |
| `PCIe PC` | PCIe PC | Hardware (PCIe) |
| `HDD PC` | HDD PC | Hardware (HDD) |
| `PC-QB-API` | API Type | Software |
| `PC-QB-SOFTWARE` | Software | Software (Draft) |
| `PC-QB-DB` | QuantumBit Database | Software |
| `PC-QB-SUB` | Subscription | Selling model |
| `PC-QB-COMPLETE` | QuantumBit Complete | Bundle |
| `PC-QB-STARTER` | QuantumBit | Bundle |
| `PC-QB-PSBUNDLE` | Professional Services Bundle | Services |
| `PC-QB-PS-RESOURCES` | Engineering Resources | Services (T&M) |
| `PC-QB-SERVICES` | Services | Services |

Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductClassification.csv`

### Products (162 total)

**By the numbers:**
- 162 commercial products
- 17 Product Attribute Definitions linked to products
- 39 Attribute Definitions in total (39 attributes across the 18 classifications)
- 87 Attribute Picklist Values

Source: `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv` (162 rows)

### Top-Level Bundles (5)

| SKU | Name | Description |
|---|---|---|
| `QB-COMPLETE` | QuantumBit Complete Solution | Flagship multi-domain bundle (Software + Add-Ons + Services + Maintenance + Training + Usage) |
| `QB-BDL-R750` | PowerSwerve R750 Rack Server | Server bundle (CPU + Memory + HDD + NIC) |
| `QB-QRack-750` | QuantumBit Q-Rack 750 | Server bundle with **nested component groups** (Computing, PCIe, Storage, Cooling — multi-level hierarchy) |
| `QB-BDL-STND` | QuantumBit Starter | Entry-tier bundle (Maintenance + Training) |
| `QB-BDL-SRVC` | QuantumBit Services Project | Professional services bundle (Engineering Resources + PM + Solution Architecture) |

### Component Groups (27 total)

Distributed across the 5 bundles. Includes both flat groupings and nested hierarchies:

- **QB-COMPLETE** uses 7 groups: Software, Training, Add-Ons, Services, Maintenance & Support (+ a Usage component group `QB-PCG-USAGE` with min/max=1 enforcing exactly one usage selection)
- **QB-BDL-R750** uses 4 flat groups: Processor, Memory Capacity, Hard Drive, Network Adapter (each min/max=1)
- **QB-QRack-750** uses **nested groups** — Computing (with sub-groups Cooling, GPUs); Storage (with sub-group Hard Drives); PCIe (with sub-groups GPUs, I/O, Networking); plus Memory, Power Supply
- **QB-BDL-STND** uses 2 groups: Maintenance, Training (each min/max=1)
- **QB-BDL-SRVC** uses 3 groups: Engineering Resources, Project Management, Solution Architecture

Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductComponentGroup.csv` (27 rows)

### Bundle-to-Component Relationships

84 ProductRelatedComponent rows define which child products attach to which bundle in which component group. Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductRelatedComponent.csv`

---

## 2. Selling Models

9 Product Selling Models loaded as standard:

| Name | Type | Pricing Term |
|---|---|---|
| One-Time | OneTime | n/a |
| Term Annual | TermDefined | 1 Annual |
| Term Monthly | TermDefined | 1 Months |
| Term Based - Quarterly | TermDefined | 1 Quarterly |
| Term Based - Semi-Annual | TermDefined | 1 Semi-Annual |
| Evergreen Annual | Evergreen | 1 Annual |
| Evergreen Monthly | Evergreen | 1 Months |
| Evergreen - Quarterly | Evergreen | 1 Quarterly |
| Evergreen - Semi-Annual | Evergreen | 1 Semi-Annual |

115 ProductSellingModelOption rows bind products to their applicable selling models.

Source: `datasets/sfdmu/qb/en-US/qb-pcm/ProductSellingModel.csv` + `ProductSellingModelOption.csv`

---

## 3. Pricing

| Object | Records | Notes |
|---|---|---|
| `Pricebook2` | 1 (Standard Price Book) | USD-currency |
| `PriceAdjustmentSchedule` | 3 (Standard Attribute / Bundle / Volume schedules) | All USD |
| `PriceAdjustmentTier` | 3 | Range-type tiers |
| `PricebookEntry` | 114 | Products + selling-model variants |
| `AttributeBasedAdjRule` | 4 | |
| `AttributeAdjustmentCondition` | 4 | |
| `AttributeBasedAdjustment` | 4 | |
| `BundleBasedAdjustment` | 2 | |
| `PricebookEntryDerivedPrice` | 2 | Derived pricing relationships |
| `CostBook` / `CostBookEntry` | 0 (excluded) | Not provisioned by default |

Source: `datasets/sfdmu/qb/en-US/qb-pricing/`

### Pricing-feature mapping onto QB bundles

The standing pricing data wires each Salesforce Pricing **adjustment type** to specific products inside `QB-COMPLETE`:

| Pricing Feature | Records | Wired to | Behavior |
|---|---|---|---|
| **Bundle-Based Adjustment** | 2 | `QB-API` (Term Annual) inside `QB-COMPLETE` | 5% Percentage discount when QB-API is sold as part of QB-COMPLETE root bundle |
| **Attribute-Based Adjustment** | 4 | `QB-API` with `ATTR-QB-API` environment attribute (Term Annual) | Override-type prices: **Flex = $10,000 · Pre-Prod = $12,000 · Prod = $15,000 · Gov = $8,500** |
| **Volume Adjustment (PriceAdjustmentTier)** | 3 | `QB-MSG-STRT` (Additional Messages QB Starter, Term Annual) | Tiered Percentage discount: **5–10 units → 10% off · 11–15 → 15% off · 16+ → 25% off** |
| **Derived Pricing** | 2 (PricebookEntryDerivedPrice) | Configured for sub-bundle relationships | Products derive prices from contributing products in the bundle |

**For workshop authoring:** when demonstrating Salesforce Pricing features, anchor walkthroughs on these specific products.

> **Gap to flag for Spring '26 Pricing exercise:** Price Propagation (the 260 ascending/horizontal propagation feature) does NOT have pre-configured propagation rules. The structural prerequisite (nested component groups) exists in `QB-QRack-750` (Computing → Cooling, Storage → Hard Drives, PCIe → GPUs/I/O/Networking), but the propagation table itself isn't built. Workshop walkthroughs need to *configure* the propagation table during the exercise — actually a strength for in-person teaching.

---

## 4. Multi-Currency

7 active currencies:

| ISO Code | Conversion to USD | Decimal Places | Corporate |
|---|---|---|---|
| **USD** | 1 | 2 | ✅ Yes |
| EUR | 0.862388 | 2 | |
| GBP | 0.751313 | 2 | |
| CAD | 1.388244 | 2 | |
| AUD | 1.442894 | 2 | |
| CHF | 0.793889 | 2 | |
| JPY | 158.650911 | 0 | |

Source: `datasets/sfdmu/qb/en-US/qb-pricing/CurrencyType.csv`

---

## 5. Multi–Legal Entity

**4 Legal Entities provisioned:**

| Name | Region |
|---|---|
| Default Legal Entity - US | United States |
| Default Legal Entity - Canada | Canada |
| Default Legal Entity - EU | European Union |
| Default Legal Entity - UK | United Kingdom |

**Per-LE Billing Treatments** (Advance + Arrears for each LE) — total 8 BillingTreatment records covering both advance-billing and arrears-billing patterns per region.

**Per-LE Tax Treatments** also provisioned via `qb-tax`.

Source: `datasets/sfdmu/qb/en-US/qb-billing/LegalEntity.csv` + `BillingTreatment.csv` + `qb-tax/LegalEntity.csv`

---

## 6. Usage Management

### Usage Resources (4)

| Code | Name | UoM Class | Billing Policy |
|---|---|---|---|
| `QB-TOKEN` | Quantum Tokens | Token UoM Class | monthlytotal |
| `UR-CPUTIME` | Compute Time | TIME (minutes) | monthlytotal |
| `UR-DATASTORAGE` | Data Storage | DATAVOL (TB) | monthlypeak |
| `UR-DATAXFR` | Data Throughput | DATAVOL (GB) | monthlytotal |

**Plus a sub-resource:** `UR-DATASTORAGE-TKN` and `UR-CPUTIME-TKN` (token-rated variants tied to `QB-TOKEN`)

### Usage-Rated Products (9)

| SKU | Description |
|---|---|
| `QB-DB` | QuantumBit Database (CPU time + Data Storage multi-resource) |
| `QB-DB-TOKEN` | QuantumBit Database (Token-rated variant) |
| `QB-DAT-THPT` | Data Throughput product |
| `QB-TOKENS-PACK` | Token Pack (consumption tokens) |
| `QB-CMT-TKN-EACH` | Commitment Tokens (per-token rated) |
| `QB-CMT-TKN-FLAT` | Commitment Tokens (flat-rate) |
| `QB-CMT-TKN-TIER` | Commitment Tokens (tiered) |
| `QB-MTY-CMT` | Monetary Commitment |
| `QB-QTY-CMT` | Quantity Commitment |

All 9 usage products participate in the QB-COMPLETE bundle's `QB-PCG-USAGE` component group.

### Supporting Records

| Object | Records |
|---|---|
| `UnitOfMeasure` | 12 |
| `UnitOfMeasureClass` | 5 (Token, TIME, DATAVOL, etc.) |
| `UsageResourceBillingPolicy` | 3 (monthlytotal, monthlypeak, etc.) |
| `UsageGrantRenewalPolicy` | 1 |
| `UsageGrantRolloverPolicy` | 1 |
| `UsageOveragePolicy` | 2 |
| `UsageCommitmentPolicy` | 1 |

Source: `datasets/sfdmu/qb/en-US/qb-rating/`

---

## 7. CML Constraint Models (4 imported, 2 active)

`prepare_constraints` imports four CML constraint models and activates two against the QB catalog — **Server2** (hardware) and **QuantumBitBundle** (software). Only one QuantumBit *software* model can be active at a time, so **QuantumBitComplete** and **QuantumBitPCM** are imported but left **inactive** for A/B/C comparison. See `datasets/constraints/README.md` → "QuantumBitBundle (combined model)".

### QuantumBitBundle (59 ESC records = 32 Type + 27 Port, 32 products) — ACTIVE software model

A LineItem-primary union of QuantumBitComplete's configurable bundle and QuantumBitPCM's virtual-quote cart-level rules. It **preserves QuantumBitComplete's full bundle behavior** (same ports / attributes / constraints — see Type/Port semantics below) and **adds** PCM's cart-level `require` / `recommend` cross-item rules (require QuantumBit Database with API Access Requests; recommend Essentials / Fundamentals Training). Targeted products = the QuantumBitComplete set (below) plus Gold Hardware Maintenance, QuantumBit Collaboration Suite, Additional API Flex (100M), and Additional API Gov.

### QuantumBitComplete (55 ESC records = 28 Type + 27 Port, 28 products) — imported, INACTIVE

Software-focused constraints; the bundle/configuration source grafted into QuantumBitBundle. Targeted products include:
- Additional API, API Access Requests (AEH), Additional Automation QB Credits
- QuantumBit Services Project, QuantumBit Database (5 variants: base, token-based, token-commit-each/flat/tier, monetary commit, quantity commit)
- Professional Services Daily Rate, Professional Services Scope of Work, Software Maintenance
- API Management Solution, Additional Flows/Messages

### QuantumBitPCM (12 ESC records = 12 Type, 0 Port) — imported, INACTIVE

Virtual-quote (v67) cross-item source grafted into QuantumBitBundle: an `@(virtual="true") Quote` container with cart-level `require` / `recommend` rules and **no** bundle ports (its product relationships are expressed in CML via context-bound relations, not `ProductRelatedComponent`).

### Server2 (81 ESC records = 41 Type + 40 Port, 41 products) — ACTIVE, wired to QB-QRack-750

Hardware-focused constraints. Targeted products include:
- HDD: 1TB / 4TB / 8TB / 20TB NLSAS variants, 1TB / 3TB 10k RPM
- Memory: 8GB / 16GB / 32GB / 64GB / 128GB RDIMM
- CPU: Intel Xeon Gold 5318N / 6330N / 6354 + Plat 22Ghz/23Ghz/24Ghz variants
- Cooling: QB CPU Heat Sink, QB-CacheBoost 150, AirCooler / LiquidCooler
- Power: QBPowerCore (500S/800S/1600S) + QBPowerSafe (600D/1000D/2000D)
- Networking: Link 10G/25G/100G, Secure 10G
- Storage SSDs: SSD2/4/8/16/30
- Acceleration: Accel, NVExpand, Nova
- RAID: RAID500

**Constraint structure — Type vs Port semantics:**

ESC records use two `ConstraintModelTagType` values that drive how the Constraint Builder evaluates configurations:

| Tag Type | QuantumBitBundle | QuantumBitComplete | Server2 | Meaning |
|---|---|---|---|---|
| **Type** | 32 | 28 | 41 | Identifies a *kind* of product (e.g., `QuantumBitDatabase`, `Gold_22Ghz_28C56T`, `RAM64`) |
| **Port** | 27 | 27 | 40 | Identifies a *socket* into which a Type plugs (e.g., `quantumbitdatabase`, `gold22ghz`, `ram64`) |

(QuantumBitBundle's 27 Ports are inherited verbatim from QuantumBitComplete's bundle; its 32 Types = QuantumBitComplete's 28 plus 4 PCM-unique products. QuantumBitPCM contributes 12 Type tags and 0 Ports.)

**Port-type semantics in plain terms:** the Constraint Builder treats Ports as connection points. A Type tag identifies what kind of component a product is; a Port tag identifies the slot it fills. The constraint logic in the binary CML blob enforces compatibility — e.g., a `gold22ghz` CPU port can only accept Type tags compatible with that CPU socket; a `ram64` port only accepts 64GB RAM Type tags.

This is the model that powers the Spring '26 Configurator features (Compact Layout, Sticky Errors, Inline Attribute Configuration, Enhanced Instance Selection) — they all run against the constraint engine that interprets these Type/Port relationships.

**The two active models** are activated automatically by `prepare_constraints` Phase 2 when `constraints_data=true` (default). Activation sets `Server2_V1` and `QuantumBitBundle_V1` ExpressionSetVersions to `Active`. `QuantumBitComplete_V1` and `QuantumBitPCM_V1` are imported but left `Inactive` (only one QuantumBit software model can be active at a time).

Source: `datasets/constraints/qb/QuantumBitBundle/` (active) + `datasets/constraints/qb/Server2/` (active) + `datasets/constraints/qb/QuantumBitComplete/` and `.../QuantumBitPCM/` (imported, inactive)

---

## 8. Channel Partner / PRM

### Partner Account (1)

| Account | Type | Industry | Region |
|---|---|---|---|
| Robot Resellers | Partner | Technology | San Francisco, CA |

### Channel Program: Reseller Program (4 tiers)

| Tier | Discount Rate | Min Deal Size | Deal Expiration Days | Description |
|---|---|---|---|---|
| **Platinum** | 6% | — | — | Top tier — white-glove treatment, marketing reimbursement, concierge support |
| **Gold** | 15% | $20,000 | 60 | Higher caps, advanced warranty, partner marketplace, lead sharing |
| **Silver** | — | — | — | Better marketing/co-op rates, support tools |
| **Bronze** | — | — | — | Entry tier — basic deal registration + sales support |

Source: `datasets/sfdmu/qb/en-US/qb-prm/`

---

## 9. Tax Engine

| Object | Records |
|---|---|
| `TaxEngine` | Provisioned via Apex (`createTaxEngine.apex`) |
| `TaxEngineProvider` | 1 |
| `TaxPolicy` | Default Tax Policy |
| `TaxTreatment` | Per-LE treatments |
| `LegalEntity` | Same 4 LEs as billing |
| `NamedCredential` | Tax engine credential |

Source: `datasets/sfdmu/qb/en-US/qb-tax/`

---

## 10. Billing Foundation

| Concept | Records |
|---|---|
| Legal Entities | 4 (US, Canada, EU, UK) |
| Billing Treatments | 8 (Advance + Arrears per LE) |
| Billing Policies | 2 (Advance, Arrears) |
| Payment Terms | Default Payment Term, Net 45 |
| Billing Treatment Items | per-treatment line items |
| Payment Retry Rules | provisioned |

Source: `datasets/sfdmu/qb/en-US/qb-billing/`

---

## 11. Dynamic Revenue Orchestration (DRO)

`qb-dro` provisions a single-pass plan with 14 design-time DRO objects:

- FulfillmentStepDefinitionGroups
- FulfillmentStepDefinitions (with dynamic user resolution)
- FulfillmentStepDependencyDefs
- ProductFulfillmentDecompRules
- ProductDecompEnrichmentRules
- ProductFulfillmentScenarios
- FulfillmentFalloutRules + FulfillmentStepJeopardyRules
- FulfillmentTaskAssignmentRules
- FulfillmentWorkspaces + WorkspaceItems
- ValueTransform Groups + ValueTransforms

> **Known build-side bug:** 260 has a known issue where `ExecuteOnRuleId` is not generated on `INSERT` of `ProductFulfillmentDecompRule` / `ProductFulfillmentScenario` / `FulfillmentStepDefinition` / `FulfillmentTaskAssignmentRule`. The `update_product_fulfillment_decomp_rules` Apex task is run as Step 4 of `prepare_dro` to trigger ruleset generation by editing-and-resaving each PFDR record. (Confirmed in #rlm-office-hours.)

Source: `datasets/sfdmu/qb/en-US/qb-dro/`

---

## 12. Approvals

`qb-approvals` provisions:
- `ApprovalAlertContentDef` records
- `EmailTemplate` records (for approval notifications)

Source: `datasets/sfdmu/qb/en-US/qb-approvals/`

---

## 13. CLM (Contract Lifecycle Management)

When `clm=true` and `clm_data=true`, `qb-clm` provisions:
- `ClauseCatgConfiguration`
- `CustomPermission`
- `DocumentClauseSet`
- `ObjectStateActionDefinition`, `ObjectStateDefinition`, `ObjectStateTransition`, `ObjectStateTransitionAction`, `ObjectStateValue`
- `OmniProcess`

Source: `datasets/sfdmu/qb/en-US/qb-clm/`

---

## 14. Other Data Plans

| Plan | Purpose |
|---|---|
| `qb-product-images` | ContentVersion + ContentDocumentLink for product images (`/resource/RLM_quantumBit_logo_sq` + per-product images) |
| `qb-transactionprocessingtypes` | TransactionProcessingType records (loaded before `deploy_post_constraints`) |
| `qb-accounting` | GL Accounts, Journal Entry templates |
| `qb-guidedselling` | Guided selling configuration |
| `qb-rates` | RateCard + RateCardEntry records |

---

## 15. Customer Account Setup

> The `scratch_data` data plan provisions canonical **end-customer accounts** for QB workshop scenarios. Per project guidance, this is the source of truth for customers in QB-aligned exercises.

| Object | Records |
|---|---|
| Account | **Infinitech** (San Francisco, US, Technology) · **Global Media / GBM** (Toronto, Canada, Media) |
| Contact | Seth Wilson @ Infinitech · Geoff Minor + Carole White @ Global Media |
| BillingAccount | **Infinitech Billing Account** (USD, Default Payment Term, DefaultInvoiceTemplate, Bill-To: Seth Wilson) |

**Workshop role assignments:**

- **Infinitech is the primary customer** for end-to-end walkthroughs. Has full billing setup (BillingAccount + payment term + invoice template + bill-to contact) — minimal additional configuration needed to run quote-to-cash exercises.
- **Global Media** is the secondary customer. Useful for multi-account scenarios, multi-region examples (Canada-based), and demos that need a contrast to Infinitech.
- **Robot Resellers** (from `qb-prm`) is the **partner channel** — the reseller through which Infinitech can be sold to. Enables PRM walkthroughs.

Source: `datasets/sfdmu/scratch_data/Account.csv` + `Contact.csv` + `BillingAccount.csv`

---

## 16. `prepare_rlm_org` Build Flow Summary

The full 35-step build process is documented at `docs/guides/prepare-rlm-org-build-guide.md`. Phases:

1. **Foundation (1–3):** PSL/PSG assignment, context definition extension, decision tables, expression sets (deactivate)
2. **Metadata Deployment (4–7):** Payments site, deploy_full, price adjustment schedule activation, QuantumBit metadata
3. **Product Catalog & Pricing (8–9):** PCM data + product images + pricing data
4. **Business Process Configuration (10–17):** DocGen, DRO, Tax, Billing, Collections, Analytics, CLM, Rating
5. **Expression Sets & Permissions (18–22):** Expression set activation (active), TSO permissions, procedure plans, PRM, Agentforce
6. **Constraints & Guided Selling (23–24):** `prepare_constraints` (metadata + CML imports), guided selling
7. **Final Configuration & Personalization (25–32):** Revenue settings, pricing discovery, ramp builder, large STX, personas, UX assembly, In-App Learning, scratch seed data
8. **Finalization (33–35):** Decision table refresh, search index rebuild, git commit stamp

Critical feature flags driving the flow:
- `qb=true` (QuantumBit data shape, default)
- `billing=true`, `tax=true`, `dro=true`, `rating=true`, `rates=true`, `clm=true`, `prm=true`, `docgen=true`, `constraints=true`, `constraints_data=true`
- `tso=false` (Trialforce Source Org mode, off for dev orgs)

---

## Gaps + Recommendations for Master Exercise Series

The QB org is rich and well-constructed for workshops. With customers in `scratch_data` recognized as the canonical source, most prior "gaps" are resolved. The remaining items are minor and optional.

### What's already there (no gap)

- ✅ **End-customer accounts** — Infinitech (US, full billing setup) + Global Media (Canada) provisioned by `scratch_data`
- ✅ **Partner channel** — Robot Resellers in `qb-prm` with 4-tier Reseller Program (Platinum / Gold / Silver / Bronze)
- ✅ Multi-currency (7 currencies, USD corporate)
- ✅ Multi-Legal-Entity (4 LEs covering NA + EU + UK with Advance + Arrears Billing Treatments per LE)
- ✅ Two CML constraint models active: QuantumBitBundle + Server2 with full Port/Type semantics (QuantumBitBundle = QuantumBitComplete bundle + QuantumBitPCM cart rules; QuantumBitComplete and QuantumBitPCM imported but inactive)
- ✅ Component groups with min/max quantity enforcement (QB-COMPLETE Usage = exactly 1, QB-BDL-R750 components each = exactly 1)
- ✅ Nested component groups (QB-QRack-750: Computing → Cooling, Storage → Hard Drives, PCIe → GPUs / I/O / Networking)
- ✅ Pricing-feature wiring on QB-COMPLETE — Bundle (QB-API 5%), Attribute (QB-API environment override), Volume (QB-MSG-STRT tiered), Derived (2 entries)
- ✅ All 9 SellingModel records (One-Time + 4 Term-Defined frequencies + 4 Evergreen frequencies)
- ✅ All 9 usage-product variants (multi-resource, token, monetary, quantity, commitment + tiered)
- ✅ DRO fulfillment scenarios for QB products
- ✅ Tax engine + treatments per LE
- ✅ DocGen template foundation

### Remaining minor gaps (optional fills)

| Gap | Impact | Proposed fix |
|---|---|---|
| **Multi-LE BillingAccounts on the same customer** | Currently Infinitech has 1 BillingAccount (US LE). Multi-region demos need per-LE BillingAccounts on the same Account. | Optional: extend `scratch_data/BillingAccount.csv` with additional per-LE BillingAccount records for Infinitech (e.g., Canada LE for a Toronto branch, UK LE for a London branch). |
| **Pre-built starter Opportunity / Quote for Infinitech** | Master exercises need a starting Quote to demonstrate downstream features (approvals, DRO, billing) without forcing every workshop attendee to manually configure a long quote first. | Optional: add a small `qb-opportunities` plan with 1–2 sample Opportunity + Quote records that exercise bundle config + ramp + multi-product-mix. |
| **Sample contracts for CLM exercises** | Existing `qb-clm` is design-time templates; no actual customer contracts to amend. | Optional: add 1–2 sample Contract records linked to Infinitech. |
| **Non-USD PricebookEntries** | Multi-currency is provisioned, but PricebookEntries are USD-only. | Optional: per-currency PriceBookEntry overlays for sample bundles (e.g., GBP variants for UK-LE walkthroughs). |
| **Pre-built Price Propagation rules** | Price Propagation feature requires nested groups (✅ in QB-QRack-750) and a configured propagation table (no pre-built). | **Treat as a feature** — workshop attendees configure the propagation table during the Price Propagation walkthrough, exercising the Spring '26 Pricing Propagation Preview design-time tooling. |

> None of these are blocking. The workshop scenario below is fully runnable against the current QB data shape.

### Recommended workshop scenario

> **Scenario — "Infinitech consolidates cloud infrastructure on QuantumBit, with Global Media as a secondary customer for multi-account walkthroughs."**
>
> Infinitech is a Technology company headquartered in San Francisco (US). They're moving from on-prem to QuantumBit's cloud platform, deploying both software (QB-COMPLETE solution) and hardware (QB-QRack-750 servers) to support production, pre-production, and government workloads.
>
> The deal exercises:
>
> - **QB-COMPLETE** bundle as the software foundation, with the **QuantumBitBundle CML** (the active model — it contains QuantumBitComplete's full bundle configuration plus PCM cart-level rules) enforcing valid configurations
>   - **QB-API** with environment attribute set to `Prod` ($15,000/year via attribute-based pricing) for the production environment, plus additional QB-API instances at `Pre-Prod` ($12,000) and `Gov` ($8,500) attribute values
>   - **5% bundle adjustment** applied automatically via QB-COMPLETE's bundle relationship
>   - **QB-MSG-STRT** at 16+ units → **25% volume discount** for high-volume messaging
>   - One usage product (required by `QB-PCG-USAGE` min/max=1) — typically `QB-DB` for the database tier, with optional `QB-TOKENS-PACK` for AI/automation
>   - **QB-BDL-SRVC** Professional Services Bundle for migration
> - **QB-QRack-750** server racks for hardware deployment, with the **Server2 CML** enforcing valid CPU + Memory + Cooling + Power + Networking + Storage combinations across nested component groups
> - **Term Annual** selling model for software subscriptions; **One-Time** for hardware
> - Optional: secondary customer footprint via **Global Media** (Toronto, Canada LE) for multi-account demos
> - Optional: deal flowed through **Robot Resellers** (Reseller Program: Platinum tier with 6% discount) for PRM walkthroughs
>
> Per-office multi-LE billing as needed: US LE for HQ, Canada LE for Global Media demos, EU/UK LE for international expansion examples.

This scenario:

- **Threads through every master exercise** — PCM (catalog setup), Pricing (all four feature types live in QB-COMPLETE), Configurator (CML for both software + hardware bundles), Transaction Mgmt (multi-product quote with ramps + approvals), Approvals (high-value tiered approval), DRO (multi-bundle fulfillment), Usage (the QB-COMPLETE usage component group), Invoice/Billing (Infinitech BillingAccount → Default Payment Term → invoices), Context Service (the data layer powering all of this)
- **Uses every major QB capability already provisioned**
- **Requires zero data plan additions** to run end-to-end (the optional gaps above improve fidelity but aren't blocking)
- **Multi-LE demonstrable** via Global Media (Canada) as a secondary customer, or by adding per-LE BillingAccounts on Infinitech as a small `scratch_data` enhancement
