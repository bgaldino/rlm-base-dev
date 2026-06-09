---
mode: master
area: "Salesforce Pricing"
file_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
scenario_anchor: infinitech-cloud-deal
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog + pricing data loaded (`qb=true`, `prepare_pricing_data` flow run)"
  - "QuantumBitBundle CML constraint model active (default in QB orgs)"
  - "Standard Price Book + 3 Price Adjustment Schedules active"
sources:
  - "docs/enablement/master/qb-scenario-reference.md — canonical QB scenario reference"
  - ".cursor/skills/release-enablement/authoring-patterns.md — Patterns 9 (Scenario Threading) + 10 (Version-Aware Section Metadata)"
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — Spring '26 master Help PDF"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — internal Solution Overview deck"
  - "docs/enablement/{248,252,254,256,258}/ — read-only historical exercises (carry-forward source material)"
sections:
  - {id: pricing-overview, introduced: foundational, available: all, scenario_step: "Pricing Foundation 1"}
  - {id: price-books, introduced: foundational, available: all, scenario_step: "Pricing Foundation 2"}
  - {id: pricing-procedures, introduced: foundational, available: all, scenario_step: "Pricing Foundation 3"}
  - {id: selling-models, introduced: foundational, available: all, scenario_step: "Pricing Foundation 4"}
  - {id: volume-adjustment, introduced: foundational, available: all, scenario_step: "Adjustment Demo 1"}
  - {id: bundle-adjustment, introduced: foundational, available: all, scenario_step: "Adjustment Demo 2"}
  - {id: attribute-adjustment, introduced: foundational, available: all, scenario_step: "Adjustment Demo 3"}
  - {id: derived-pricing, introduced: foundational, available: all, scenario_step: "Adjustment Demo 4"}
  - {id: multiple-output-resolution, introduced: 254, available: "254+", enhanced_in: [256], scenario_step: "Output Resolution 1"}
  - {id: stacking-sequencing, introduced: 256, available: "256+", scenario_step: "Output Resolution 2"}
  - {id: header-adjustments, introduced: 254, available: "254+", enhanced_in: [258], scenario_step: "Header Adjustment 1"}
  - {id: apex-hook, introduced: 256, available: "256+", scenario_step: "Custom Logic 1"}
  - {id: enhanced-formula, introduced: 258, available: "258+", scenario_step: "Custom Logic 2"}
  - {id: if-else-formula, introduced: 260, available: "260+", scenario_step: "Custom Logic 3"}
  - {id: price-propagation, introduced: 260, available: "260+", scenario_step: "Propagation 1"}
  - {id: propagation-preview, introduced: 260, available: "260+", scenario_step: "Propagation 2"}
  - {id: price-revision-cpi, introduced: 258, available: "258+", scenario_step: "Revision 1"}
  - {id: promotions, introduced: 260, available: "260+", tier: beta, scenario_step: "Promotions 1"}
  - {id: operations-console, introduced: 254, available: "254+", enhanced_in: [260], scenario_step: "Operations 1"}
  - {id: pricing-simulation, introduced: foundational, available: all, enhanced_in: [256], scenario_step: "Operations 2"}
  - {id: advanced-price-logs, introduced: 260, available: "260+", scenario_step: "Operations 3"}
  - {id: auto-numbered-elements, introduced: 260, available: "260+", scenario_step: "Operations 4"}
  - {id: price-history, introduced: 252, available: "252+", scenario_step: "Operations 5"}
  - {id: procedure-plan-packaging, introduced: 260, available: "260+", scenario_step: "Operations 6"}
  - {id: end-to-end-synthesis, introduced: foundational, available: all, scenario_step: "Synthesis"}
---

# Master Exercise: Salesforce Pricing

**Workshop format · Living document** · Version 0.1 (draft), 2026-05-06

> **About this exercise:** This is the **master Pricing exercise** — designed for in-person enablement sessions and self-paced workshops. It progresses through Salesforce Pricing concepts in a logical narrative arc, anchored to the **Infinitech cloud deal** workshop scenario. Foundational and release-specific content live together; per-release extracts (e.g., `docs/enablement/260/`) are filtered views of this master.
>
> **Reading paths:**
> - **Workshop attendees:** read top to bottom. Each Part builds on the previous.
> - **Specific feature lookup:** jump to a section. Each is self-contained but cross-references prior parts when foundational concepts apply.
> - **Per-release training:** see `docs/enablement/260/260-salesforce-pricing-hands-on.md` (auto-extracted) for 260-only content.

---

## Workshop Scenario Anchor

This exercise threads through a single deal: **Infinitech consolidates cloud infrastructure on QuantumBit, with QB-COMPLETE bundles for software and QB-QRack-750 server racks for hardware.**

For the full scenario context — customer accounts (Infinitech, Global Media), partner channel (Robot Resellers), bundles, CML constraint models, multi-LE setup — see `docs/enablement/master/qb-scenario-reference.md`.

**Pricing-feature anchor on the QB catalog:**

| Demo concept | QB product / wiring |
|---|---|
| Volume Adjustment | `QB-MSG-STRT` (Additional Messages) — tiered: 5–10 → 10% · 11–15 → 15% · 16+ → 25% |
| Bundle-Based Adjustment | `QB-API` inside `QB-COMPLETE` — automatic 5% Percentage |
| Attribute-Based Adjustment | `QB-API` with `ATTR-QB-API` attribute → Override prices: Flex $10K · Pre-Prod $12K · Prod $15K · Gov $8.5K |
| Constraint validation | `QuantumBitComplete` CML enforces required usage product, valid software combinations |
| Nested-bundle pricing (260) | `QB-QRack-750` Computing → Cooling, Storage → Hard Drives, PCIe → GPUs/I/O/Networking |
| Customer | Infinitech (San Francisco, US LE) — sourced from `scratch_data` |

---

## Status of this document

🚧 **DRAFT — first master exercise authored.** This is the pilot validating the two-tier model (master + per-release extracts) and the new authoring patterns (Pattern 9 Scenario Threading, Pattern 10 Version-Aware Section Metadata). All 24 sections + synthesis section are scaffolded with version metadata; foundational and 260-specific sections have full content; intermediate-release sections (252–258) reference prior-release exercise PDFs for deep-dive walkthroughs and document the *behavior* in line.

---

# Part 1: Foundations

> **Why start here:** every Pricing feature builds on Price Books, Pricing Procedures, and Selling Models. Workshop attendees who already know these concepts can skim Part 1 and still benefit from the Infinitech anchoring; new admins should walk through carefully.

## Section 1: Salesforce Pricing — what it is and why it matters {#pricing-overview}

> **Version:** introduced foundational · available all · *Scenario step: Pricing Foundation 1*

Salesforce Pricing is the engine that calculates what a customer pays for a product on a quote, order, or asset. It runs at three moments in the revenue lifecycle:

1. **Quote authoring** — sales rep adds products to a quote; pricing computes per-line and total
2. **Order activation** — pricing locks rates onto order line items
3. **Asset amendment / renewal** — pricing recomputes based on whether the customer's quote uses Last Transaction Price or List Price as the source

The engine is **procedure-driven**: instead of a single "calculate price" rule, you compose **Pricing Procedures** from reusable **Pricing Elements** that each apply one kind of price modification. This makes complex pricing — multi-product discounts, attribute-driven prices, volume tiers, custom formulas — composable and inspectable.

**Why this matters for Infinitech's deal:** Infinitech's QB-COMPLETE bundle has multiple discount mechanisms applying simultaneously — the bundle itself triggers a 5% bundle adjustment on QB-API; the QB-API environment attribute sets a base override price; the Volume tier on QB-MSG-STRT applies a percentage by quantity. Understanding Pricing Procedures and how their elements interact is what lets you trace which adjustments fired in which order, why the final price is what it is, and how to debug when it's not what you expect.

---

## Section 2: Price Books and Pricing Entries {#price-books}

> **Version:** introduced foundational · available all · *Scenario step: Pricing Foundation 2*

A **Price Book** (`Pricebook2`) is a catalog of prices. Each price book has many **Price Book Entries** (`PricebookEntry`), one per Product × Selling Model × Currency combination.

QB orgs ship with the **Standard Price Book** (the default and only price book in QB) and **114 PricebookEntry records** spanning the QB catalog × applicable selling models. The catalog supports 9 selling models, so a single product like QB-API has multiple entries (one per Term-Defined frequency, one per Evergreen frequency, etc.).

**Walkthrough — Inspect Infinitech-relevant pricing entries:**

1. Open **App Launcher → Pricing → Price Books**.
2. Open the **Standard Price Book**.
3. View the related **Price Book Entries** list. Filter for `QB-API` to see all the entries.
4. You'll see entries for Term Annual, Term Monthly, Evergreen Annual, etc., each with a UnitPrice. The Term Annual entry is the one that matters for Infinitech's standard 3-year deal.

**Cost Books** (`CostBook`) track internal costs and are linked to Price Books via the `CostBook2.CostBookId` field. QB doesn't load cost data by default — `CostBookEntry` is `excluded: true` in the data plan — but the schema is in place for customers who want to track internal margins.

---

## Section 3: Pricing Procedures and Pricing Elements {#pricing-procedures}

> **Version:** introduced foundational · available all · *Scenario step: Pricing Foundation 3*

A **Pricing Procedure** is an ordered sequence of **Pricing Elements**, each of which either reads a price input, computes a derived price, or applies an adjustment. The procedure runs top-to-bottom, with each element's output feeding the next.

**Common Pricing Elements (foundational):**

| Element | What it does |
|---|---|
| **List Price** | Reads the unit price from the Price Book Entry |
| **Volume Adjustment** | Applies a tier-based percentage or fixed-amount discount based on quantity |
| **Bundle-Based Adjustment** | Applies a percentage or fixed-amount discount when the product is sold inside a bundle |
| **Attribute-Based Adjustment** | Applies a price modification driven by an attribute value (e.g., environment) |
| **Derived Pricing** | Computes a price from one product based on another product in the bundle |
| **Formula-Based Pricing** | Computes a price using a formula expression |
| **Pricing Setting** | Configures procedure-wide settings (used with Price Propagation in 260+) |
| **Map Line Items** | Routes multiple inputs through one transformation |
| **Aggregate** | Rolls up totals across line items (with optional Rollup Price — added in 252) |

**Workshop attendees should expect:** when you build a procedure, you order these elements deliberately. List Price runs first to establish the base; Volume runs next to apply tier discounts to that base; Bundle-Based runs after to apply bundle context; Attribute-Based applies environment overrides last. The order **matters** — it's how Stacking and Sequencing work (covered later in Part 3).

---

## Section 4: Selling Models and Their Effect on Pricing {#selling-models}

> **Version:** introduced foundational · available all · *Scenario step: Pricing Foundation 4*

The QB org provisions **9 Selling Models** that define how pricing relates to time:

| Selling Model | Type | Effect on price |
|---|---|---|
| One-Time | OneTime | Single price, single charge — used for hardware and Professional Services |
| Term Annual | TermDefined | Annual price across a fixed term (e.g., 3-year contract: 3 × annual price) |
| Term Monthly | TermDefined | Monthly price × term length |
| Term Based - Quarterly | TermDefined | Per-quarter price |
| Term Based - Semi-Annual | TermDefined | Per-half-year price |
| Evergreen Annual | Evergreen | Annual price, no defined end date |
| Evergreen Monthly | Evergreen | Monthly price, no defined end date |
| Evergreen - Quarterly | Evergreen | Quarterly price, no defined end date |
| Evergreen - Semi-Annual | Evergreen | Per-half-year price, no defined end date |

For Infinitech's deal:
- **QB-COMPLETE software components**: Term Annual (3-year term)
- **QB-QRack-750 hardware**: One-Time
- **QB-DB usage product**: Term Annual (with usage rating layered on top via Usage Management)

The selling model is a **dimension of the PricebookEntry** — that's why QB-API has separate entries for Term Annual ($X) and Term Monthly ($X/12). When pricing runs, it picks the entry matching the selling model on the line item.

---

# Part 2: Adjustment Types — anchored to QB-COMPLETE

> **Why grouped:** these four adjustment types are the foundation of pricing logic in Salesforce. The standing QB data wires each one to a specific QB-COMPLETE component, so you'll see all four firing on the same Infinitech quote line.

## Section 5: Volume Adjustments — QB-MSG-STRT tiered demo {#volume-adjustment}

> **Version:** introduced foundational · available all · *Scenario step: Adjustment Demo 1*

A **Volume Adjustment** uses a **Price Adjustment Schedule** of type `Volume` to apply tiered discounts based on quantity. The standing QB data wires three Volume tiers onto **QB-MSG-STRT** (Additional Messages QB Starter, Term Annual):

| Quantity | Adjustment |
|---|---|
| 5 – 10 | 10% off |
| 11 – 15 | 15% off |
| 16 + | 25% off |

(All `Range`-type tiers, USD, configured against the **Standard Price Adjustment Tier** schedule.)

**Walkthrough — Apply Volume Adjustment to Infinitech's QB-MSG-STRT order:**

1. From the App Launcher, open **Quotes**.
2. Create or open Infinitech's quote (built earlier in the workshop). Open the **Quote Line Editor**.
3. Add `QB-MSG-STRT` to the quote at quantity **8**. Run pricing. Observe the unit price gets 10% off.
4. Edit the line and increase quantity to **13**. Run pricing. Observe the discount steps up to 15%.
5. Edit the line again to quantity **20**. Run pricing. Observe the discount steps up to 25%.

**Where to inspect the schedule:** Setup → Pricing → **Price Adjustment Schedules** → Standard Price Adjustment Tier → Tiers tab.

**Critical concept:** Volume tiers apply to the *line's* quantity. If Infinitech buys 8 units of QB-MSG-STRT in one line and 8 in a separate line, neither qualifies for the 11–15 tier. Use **Cumulative Quantity** (added in 256, see Section 10) to roll up across lines.

---

## Section 6: Bundle-Based Adjustments — QB-API in QB-COMPLETE {#bundle-adjustment}

> **Version:** introduced foundational · available all · *Scenario step: Adjustment Demo 2*

A **Bundle-Based Adjustment** modifies the price of a child product based on its position in a bundle hierarchy. The standing QB data has **2 Bundle-Based Adjustments**, both targeting **QB-API** when sold inside the **QB-COMPLETE** root bundle:

- **Adjustment Type:** Percentage
- **Adjustment Value:** 5%
- **Selling Model:** Term Annual
- **Schedule:** Standard Bundle Based Adjustment

The adjustment fires automatically when QB-API appears in a bundle whose `RootBundle.StockKeepingUnit = 'QB-COMPLETE'`.

**Walkthrough — Demonstrate Bundle Adjustment for Infinitech:**

1. Add **QB-COMPLETE** to Infinitech's quote, configure it (the QB-COMPLETE bundle, with its required usage product per the QB-PCG-USAGE component group min/max=1).
2. The configurator lets you pick QB-API as a Software component. Select it.
3. Run pricing on the quote.
4. Open the **Pricing Waterfall** for the QB-API line. Observe:
   - List Price element → reads the QB-API Term Annual price
   - Bundle-Based Adjustment element → applies the 5% Percentage discount because QB-API is inside QB-COMPLETE

**Standalone QB-API:** if you add QB-API to a quote *not* inside QB-COMPLETE, the bundle adjustment does NOT fire. The waterfall shows only List Price.

> **Why this matters in the Infinitech narrative:** Infinitech is buying QB-COMPLETE for several offices. The 5% bundle adjustment compounds across all those bundles — a meaningful structural discount that rewards bundle adoption.

---

## Section 7: Attribute-Based Adjustments — QB-API environment override {#attribute-adjustment}

> **Version:** introduced foundational · available all · *Scenario step: Adjustment Demo 3*

An **Attribute-Based Adjustment** modifies the price of a product based on the value of one of its attributes. The standing QB data wires **4 Attribute-Based Adjustments** onto **QB-API** keyed by the `ATTR-QB-API` attribute (environment):

| `ATTR-QB-API` value | Adjustment Type | Adjustment Value |
|---|---|---|
| Flex | Override | $10,000 |
| Pre-Prod | Override | $12,000 |
| Prod | Override | $15,000 |
| Gov | Override | $8,500 |

(All `Override` type, all Term Annual, USD.)

**Override type** means: the attribute value *replaces* the listed price entirely, not adjusts it by a percentage. So when QB-API has its environment attribute set to `Prod`, the price becomes $15,000/year regardless of the underlying List Price.

**Walkthrough — Configure Infinitech's environments:**

1. On Infinitech's quote with QB-COMPLETE configured, add **multiple QB-API instances** (one per environment).
2. For each instance, set the `ATTR-QB-API` attribute (environment) — Pre-Prod for the staging instance, Prod for production, Gov for federal-tier compliance.
3. Run pricing.
4. Open the Pricing Waterfall on each QB-API line:
   - Pre-Prod → $12,000 (override, ignores list price)
   - Prod → $15,000 (override)
   - Gov → $8,500 (override)
5. Confirm the Bundle Adjustment from Section 6 still fires on top — i.e., $15,000 × (1 - 5%) = $14,250 for the Prod environment instance, not just $15,000.

**Inspecting the rule:** Setup → Pricing → **Attribute-Based Adjustment Rules** → 4 rules (Rule_1724814105445 etc.) keyed to ATTR-QB-API values.

---

## Section 8: Derived Pricing {#derived-pricing}

> **Version:** introduced foundational · available all · *Scenario step: Adjustment Demo 4*

**Derived Pricing** computes one product's price from another product in the same bundle. The standing QB data has **2 PricebookEntryDerivedPrice records** that demonstrate this pattern.

The classic use case: *Software Maintenance* should always be **20% of the underlying Software's price**. Rather than maintaining separate maintenance prices, you derive maintenance from software.

**Walkthrough sketch (custom configuration required):**

1. Open the QB-COMPLETE configuration for Infinitech.
2. Add a Software product (e.g., QB-API at Prod = $15,000) and Software Maintenance.
3. The Derived Pricing element on Software Maintenance computes: `Software Maintenance price = Software price × 0.20 = $3,000`.
4. If you change the QB-API attribute from Prod to Gov ($8,500), the Maintenance price recomputes to $1,700.

> **Note:** Specific derived pricing examples wired in QB are limited to 2 entries — the foundational structure is in place but customer implementations typically extend this. For Infinitech walkthroughs, demonstrate the wiring on existing Software/Maintenance pairs, then the 260 Promotions / Price Propagation walkthroughs (later) build on this.

---

# Part 3: Multi-Output Resolution and Discount Stacking

> **Why grouped:** when multiple discounts apply to the same line, the engine has to decide which wins or how to combine them. Multi-Output Resolution (254) introduced the concept; Stacking and Sequencing (256) made it composable.

## Section 9: Multiple Output Resolution {#multiple-output-resolution}

> **Version:** introduced 254 (Spring '25) · available 254+ · enhanced_in 256 · *Scenario step: Output Resolution 1*

**The problem:** for Infinitech's QB-API at Prod ($15,000 attribute override) inside QB-COMPLETE (5% bundle), what's the final price? Without explicit resolution, multiple adjustments compete. **Multiple Output Resolution** introduced in 254 lets you choose how to resolve.

**Resolution policies:**

| Policy | Behavior |
|---|---|
| **Best Price for Customer** | Pick the lowest resulting price (or highest discount %) |
| **Worst Price for Customer** | Pick the highest resulting price (legacy / list-price-protective) |
| **Sequence** | Apply adjustments in a defined order (Section 10) |
| **Stack** | Apply all adjustments cumulatively (Section 10) |

**Configuration — Setup → Pricing → Pricing Procedures → [your procedure] → Multi-Output Resolution element → Policy.**

**Walkthrough for Infinitech:**

1. Open the active Pricing Procedure (configured during catalog setup).
2. Locate the Multi-Output Resolution element. Verify the policy.
3. For the Infinitech demo, **Stack** is most representative — all applicable adjustments (Bundle 5% + Attribute Override + Volume) cumulate.

> **Reference:** Detailed walkthrough in `docs/enablement/254/Spring '25 Pricing Hands On Exercises.pdf` § Multiple Output Resolution.

## Section 10: Stacking and Sequencing of Discounts {#stacking-sequencing}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Output Resolution 2*

**256 added:** explicit **Stack** and **Sequence** policies that let you control multi-discount application without resorting to "Best Price" / "Worst Price" heuristics.

- **Stack:** all matching adjustments fire, applied multiplicatively (or additively per configuration). Example: List $10K → Bundle 5% off → Volume 10% off → Final $8,550 (cumulative).
- **Sequence:** adjustments fire in a numbered sequence; later adjustments operate on the result of earlier ones.

**For Infinitech:** the QB-API at Prod environment with Bundle 5% adjustment uses **Stack** — both fire and compound. The Volume Adjustment on QB-MSG-STRT would also Stack onto any Bundle adjustment if QB-MSG-STRT had one (it doesn't — Bundle adjustment is wired only to QB-API in QB-COMPLETE).

**Configuration walkthrough:**

1. Open the Pricing Procedure → Multi-Output Resolution element → set Policy to `Stack`.
2. Configure each adjustment element's **Tier** (1, 2, 3...) so the order is explicit when needed.
3. Save and activate.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Salesforce Pricing.pdf` § Multiple Output Resolution - Stacking.

---

# Part 4: Header Adjustments and Discount Distribution

## Section 11: Header Adjustments / Discount Distribution Service {#header-adjustments}

> **Version:** introduced 254 (Spring '25, with Floor Price restriction) · available 254+ · enhanced_in 258 (Header Adjustments → Quote/Order header level) · *Scenario step: Header Adjustment 1*

**254 introduced** the **Discount Distribution Service** — a way to apply a single discount and have it distribute across line items. **258 elevated** this with first-class **Header Adjustments** that apply at the *transaction header level* (quote or order header), automatically propagating to eligible lines.

**The Infinitech use case:**

A sales rep negotiating with Infinitech's procurement team needs a discretionary 8% deal-wide discount in addition to the structural discounts (Bundle, Volume) that already apply per line. Instead of manually editing every line, the rep:

1. Opens the **Manage Header Adjustment** action on Infinitech's quote.
2. Selects **Percentage** type, enters **8**.
3. Submits.
4. The Discount Distribution Service distributes the 8% across all eligible line items proportionally.
5. The Pricing Waterfall on each line shows the header adjustment as an additional element below Bundle / Attribute / Volume.

**Floor Price Restriction** (254) — admins can configure that header adjustments not push any line below a defined floor price.

> **Detailed walkthrough:** `docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` § Header Adjustments.

---

# Part 5: Custom Pricing Logic

## Section 12: Pre/Post Apex Hook for Procedure Plan {#apex-hook}

> **Version:** introduced 256 (Summer '25) · available 256+ · *Scenario step: Custom Logic 1*

**256 introduced** the ability to attach Apex callouts to a **Procedure Plan** — running custom code *before* or *after* pricing/rating procedures execute.

**Use case for Infinitech:** their finance team wants to enrich each pricing call with a custom risk-tier value computed from external system data. Rather than hard-coding it in the pricing procedure, attach an Apex hook that runs first and populates the value on the line item context.

**Configuration:**

- Setup → Pricing → **Procedure Plan Definitions** → [your plan] → Add Pre-Hook or Post-Hook → Reference Apex class.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Salesforce Pricing.pdf` § Pre/Post Apex Hook.

## Section 13: Enhanced Formula Element (Multiple Formulae) {#enhanced-formula}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Custom Logic 2*

**258 enhanced** the Formula-Based Pricing element to support **up to 5 formulae in a single element**. Before 258, complex pricing logic required multiple Formula elements chained — hitting the procedure-element guardrail. With multi-formula support, complex calculations stay concise.

**Use case for Infinitech:** their software contract has tiered effective-rate formulas — base rate × tenure factor × volume factor × loyalty factor × early-payment factor. Five formulas in one element keeps the procedure clean.

> **Detailed walkthrough:** `docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` § Enhanced Formula Element.

## Section 14: Conditional IF Statements in Formula-Based Pricing {#if-else-formula}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Custom Logic 3* · ✨ **New in 260**

Spring '26 adds native `IF()` formula support inside Formula-Based Pricing. Three parameters: logical condition, value-if-true, value-if-false. **Nested IFs supported**, enabling multi-tier conditional logic in a single readable formula instead of chained elements or custom Apex.

**Concrete example for Infinitech's deal:**

```
IF(SaleType = "Premium", ItemListPrice__c * ItemPremium__c / 10000, ItemListPrice__c)
```

This formula multiplies `ItemListPrice__c` by `ItemPremium__c / 10000` (basis-point math) when `SaleType` is "Premium", and falls back to `ItemListPrice__c` for any other Sale Type. Used to apply a premium-tier markup that varies by the basis-point custom field on the line.

**Configuration walkthrough:**

1. Open the active Pricing Procedure for Infinitech.
2. Add or edit a **Formula-Based Pricing** element.
3. In the formula expression, search for the **`IF()`** function.
4. Provide three parameters: logical condition, value if true, value if false.
5. Save the procedure.

**Workshop discussion:** when you nest IF statements (e.g., to model a 4-tier discount ladder), readability matters. The Formula element supports nesting but the cleanest customer-deal stories often combine IF with the Multi-Formula element from Section 13 — IF for branching logic, Multi-Formula for parallel calculations.

📹 **Demo:** *"If Else Formula, Auto-numbering demo"* (combined demo with Section 22 Auto-Numbered Element Names).

---

# Part 6: Multi-Level / Hierarchical Pricing — anchored to QB-QRack-750

> **Why grouped:** Spring '26's Price Propagation feature lets pricing flow through nested bundle hierarchies. QB-QRack-750 has the right structural shape — Computing → Cooling, Storage → Hard Drives, PCIe → GPUs/I/O/Networking — for this demo.

## Section 15: Price Propagation — Smarter Quote Calculations {#price-propagation}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Propagation 1* · ✨ **New in 260**

**Price Propagation** in 260 lets pricing values flow through multi-level quote hierarchies with two propagation directions:

- **Ascending Propagation (Rollup):** aggregate values from child lines to parent groups (e.g., sum panel net prices into a Room total, Room into Floor, Floor into Building total)
- **Horizontal Propagation:** calculate fields sequentially within a single line or group (e.g., Net Price = List Price − Discount, computed only after Discount is determined)

**Up to 5 levels of nesting** in a single quote hierarchy.

**Why QB-QRack-750 fits:** its component groups model a multi-level hardware hierarchy:

```
QB-QRack-750 (Bundle)
├── Computing (sub-group)
│   ├── (CPU choices)
│   └── Cooling (sub-sub-group)
├── Storage (sub-group)
│   └── Hard Drives (sub-sub-group)
├── PCIe (sub-group)
│   ├── GPUs
│   ├── I/O
│   └── Networking
├── Memory
└── Power Supply
```

For Infinitech: configure a QRack-750 server with multiple SSDs, CPUs, and Cooling components. Each component has its own price; **Ascending Propagation** rolls these up into Storage / Computing / PCIe sub-totals, and finally into the QRack bundle total — with optional discount distribution at each level.

**Important constraints (260):**

- Only one Price Propagation element per pricing procedure
- Not compatible with Derived Pricing or Promotions in the same procedure
- Not supported inside a List Group
- Known issue: ClassCastException can occur with Price Propagation + Pricing Setting elements in certain configs (master PDF p 117) — workaround: retry

**Configuration walkthrough — set up Price Propagation for Infinitech's QRack purchase:**

1. Open the Pricing Procedure for Infinitech's hardware-side pricing.
2. Add a **Pricing Setting** element. Select **Enable Propagation** and map your common variables.
3. Under the Pricing Setting element, click **Configure Propagation Rules**.
4. Choose **Configure a new table** (or use the *Map sales SalesTransactionItem to SalesTransactionGroup* template).
5. **Add Nodes:** add `SalesTransactionItem` (with attributes `ListPrice`, `ItemUnitCost__std`, `ItemNetTotalPrice`, etc.) and `SalesTransactionGroup` (with attributes `GroupDiscount__std`, `SummarySubtotal`, `GroupSource`).
6. **Join Nodes:** define parent-child relationship — Parent Key = `GroupSource`, Child Key = `SalesTransactionItemGroup`, Mapping Type = `Parent-Child`.
7. **Merge Attributes:** create merged columns for shared parent/child fields (e.g., `MergedTotalCost`).
8. **Edit Attributes:** define horizontal formulas (Net Unit Price = UnitCost + Margin, sequence 1; etc.).
9. Define **Ascending Propagation** to roll up values to the parent (e.g., `Sum(!Child.ItemTotalCost)` with optional condition `SellingModelType = 'One Time'`).
10. Save the Propagation Rules.
11. Add the **Price Propagation** element to the procedure (after the Pricing Setting element).
12. Save and Activate the procedure.

**Try it:** add Infinitech's QRack-750 line with multiple components. Run pricing. Open the Pricing Waterfall and observe ascending rollups at each level of the bundle hierarchy.

📹 **Demo:** *"Price Propagation Demo"* (Solution Overview).

## Section 16: Pricing Propagation Preview — Design-Time Tooling {#propagation-preview}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Propagation 2* · ✨ **New in 260**

The **Pricing Propagation Preview** is the **design-time tool** for configuring the propagation table in Section 15. It provides:

- **Create a propagation table** from scratch or from a template
- **Configure formulas** with sequence numbers
- **Preview the metadata structure** — joined nodes, merged columns, formula sequence — before activating

For workshop attendees: the Preview lets you build the propagation rules iteratively and see the structural map before running pricing on real quote data. This reduces trial-and-error during initial setup.

**Walkthrough sequence:** the configuration steps in Section 15 ARE the Preview UI in action. Run them in your dev/sandbox first; preview the result; iterate; then activate.

📹 **Demo:** included in *"Price Propagation Demo"*.

---

# Part 7: Price Revision and CPI

## Section 17: Price Revision Policy and Element for CPI Uplifts {#price-revision-cpi}

> **Version:** introduced 258 (Winter '26) · available 258+ · *Scenario step: Revision 1*

**Price Revision Policy** lets you define how prices change over time — driven by Consumer Price Index (CPI) uplifts, contract anniversaries, or custom revision schedules.

**For Infinitech's 3-year deal:** they negotiate annual CPI-linked uplifts on their software subscriptions. Without Price Revision, you'd manually update prices each year. With it, configure a Price Revision Policy of type "Price Index" linked to CPI data, and the system applies the uplift at each policy interval.

**Configuration:**

1. Setup → Pricing → **Price Revision Policies** → New
2. Set type to **Price Index** (or **Fixed Schedule** for non-CPI-driven revisions)
3. Define the index source (Consumer Price Index records loaded into `IndexRate` object)
4. Add the **Price Revision Element** to the Pricing Procedure
5. Save and activate

> **Detailed walkthrough:** `docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` § Price Revision Policy and Element for CPI Uplifts.

---

# Part 8: Promotions (Beta — 260)

## Section 18: Promotions in Agentforce Revenue Management {#promotions}

> **Version:** introduced 260 (Spring '26) · available 260+ · tier: **Beta** · *Scenario step: Promotions 1* · ✨ **New in 260**

> ⚠️ **Beta in 260.** Some configuration may require Salesforce Support enablement and behavior may evolve toward GA.

**Promotions** in 260 (Beta) lets pricing designers configure **product- and category-based promotions** that pricing procedures evaluate at run time via the new **Promotion Execution Element**.

### Configuration

1. Define **product- and category-based promotions** using the definition template.
2. Add the **Promotion Execution Element** to the Pricing Procedure (cannot coexist with Price Propagation or Derived Pricing in the same procedure — see Section 15 constraints).
3. Configure carryover behavior for the asset lifecycle:
   - **Last Transaction Price** as pricing source — promotions carry over across asset lifecycle (amendments preserve previously applied promotions)
   - **List Price** as pricing source — promotions reset; current eligible promotions evaluate fresh during Amendments / Renewals

### Visibility at Runtime

- Active product/category promotions are **visible during product browse**.
- Quote/Order pricing applies **automatic** promotions immediately; **manual / coupon-code** promotions require seller selection. Once applied, they show in the side panel of product details.
- Assets carry applied-promotion information via **AssetActionSource → PriceAdjustment**.

### For Infinitech

A "Q4 Cloud Migration Promotion" might offer 10% off all `QB-COMPLETE` bundles purchased before December. When Infinitech's quote is in Q4, the pricing procedure detects the active promotion and applies it. If Infinitech later amends the deal:
- With **Last Transaction Price** as source → the 10% promotion is preserved
- With **List Price** as source → re-evaluation against current eligible promotions (no Q4 promotion if the amendment is in January)

📹 **Demo:** *"Promotions Demo"* (Solution Overview).

---

# Part 9: Operations and Debugging

## Section 19: Revenue Cloud Operations Console {#operations-console}

> **Version:** introduced 254 (as Pricing Operations Console) · available 254+ · enhanced_in 260 (renamed to Revenue Cloud Operations Console) · *Scenario step: Operations 1*

The **Revenue Cloud Operations Console** (renamed from Pricing Operations Console in 260) is the unified app for inspecting, debugging, and analyzing pricing operations.

### Four sections of the Console

| Section | What it shows |
|---|---|
| **Price Waterfall Storage** | Data consumed by the Price Waterfall (per line item, the trace of every adjustment that fired) |
| **Decision Tables** | Decision tables Salesforce Pricing uses to run procedures |
| **API Calls** | API calls used out of the org's allotted limit |
| **Pricing API Executions** | Logs of API runs (every headless pricing call, including discovery + pricing procedures) |

### For Infinitech

When Infinitech's pricing produces an unexpected result, the Operations Console is the first stop:

1. App Launcher → **Revenue Cloud Operations Console**.
2. Locate the pricing API execution log for the relevant quote.
3. Check **Details** + **Debug Details** tabs.
4. Identify which procedure and which element caused the issue.

### 260 rename

The console kept its functionality and four-section layout when renamed in 260. App Launcher entries, Help docs, and product UI labels all use **Revenue Cloud Operations Console** going forward.

## Section 20: Pricing Simulation {#pricing-simulation}

> **Version:** introduced foundational · available all · enhanced_in 256 (Pricing Simulation Screen Enhancement) · *Scenario step: Operations 2*

**Pricing Simulation** lets admins test a pricing procedure against synthetic or real quote data without creating a real quote.

**256 enhancement** — admins can populate the simulation context using an existing Quote/Order ID rather than manually entering every context attribute. Auto-population works when the context attribute has sObject mapping in the context definition and a value in the corresponding quote/order field.

> **Detailed walkthrough:** `docs/enablement/256/Summer '25 - Salesforce Pricing.pdf` § Pricing Simulation Screen Enhancement.

## Section 21: Advanced Price Log Settings {#advanced-price-logs}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Operations 3* · ✨ **New in 260**

**Advanced Price Log Settings** capture detailed diagnostic data for complex pricing elements — Attribute-Based Price, Derived Price, and other logic-heavy elements. Logs include input values + exception details, surfacing in the Revenue Cloud Operations Console.

### Configuration

> **Permission required:** Salesforce Pricing Admin

1. From Setup, in the Quick Find box, find and select **Salesforce Pricing**.
2. Under Salesforce Pricing, select **Advanced Price Log Settings**.
3. Enable the desired log levels per element type.

> [NEEDS REVIEW] — exact sub-step list. Master PDF section pp 1448–1450.

### Where to view the resulting logs

After Advanced Price Logs are on:

1. App Launcher → **Revenue Cloud Operations Console**.
2. Select a pricing log from the list of API executions.
3. Open the **Debug Details** tab to see element-level execution detail including the new advanced data.

## Section 22: Auto-Numbered Element Names {#auto-numbered-elements}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Operations 4* · ✨ **New in 260**

**No configuration required.** Spring '26 automatically appends an occurrence-count suffix to each pricing procedure element's name. When a procedure has 3 Formula-Based Pricing elements, you can distinguish them in the Operations Console without manual inspection.

The auto-generated name flows through to:
- Pricing procedure designer
- Revenue Cloud Operations Console
- Pricing API execution logs

📹 **Demo:** *"If Else Formula, Auto-numbering demo"* (combined with Section 14).

## Section 23: Price History Tracking {#price-history}

> **Version:** introduced 252 (Winter '25) · available 252+ · *Scenario step: Operations 5*

**Price History Tracking** persists every price change for audit and compliance. The `ProductPriceHistoryLog` object stores changes, accessible via standard reports.

For Infinitech: their finance team requires audit trails on all price modifications during the contract lifecycle. With Price History Tracking on, every adjustment, override, or amendment is logged with timestamp + user + before/after values.

> **Detailed walkthrough:** `docs/enablement/252/Winter '25 - Pricing Exercises.pdf` § Price History Tracking.

## Section 24: Procedure Plan Packaging — Promote Pricing Across Orgs {#procedure-plan-packaging}

> **Version:** introduced 260 (Spring '26) · available 260+ · *Scenario step: Operations 6* · ✨ **New in 260** (lifts a prior limitation)

**260 lifts a prior packaging limitation:** before Spring '26, pricing recipes, decision tables, and context definitions could be packaged for promotion between orgs (sandbox → UAT → production), but **Procedure Plans could not**. The master PDF dated 2026-01-15 still contains an outdated note saying "You can't migrate Procedure Plans from one org to another" (master PDF p 342) — release notes confirm 260 GA removes that restriction.

### What's now packageable

- Pricing recipes
- Decision tables
- Context definitions
- Pricing procedures
- **Procedure Plans (NEW IN 260)**

### Walkthrough

1. From Setup → Package Manager → New
2. Add components (Components tab → Add → select **Procedure Plans** + recipes + decision tables + procedures)
3. Upload package
4. Install on target org

The full pricing solution (everything Infinitech depends on) now transfers atomically.

---

# Workshop Synthesis: Putting It All Together — Infinitech End-to-End Quote {#end-to-end-synthesis}

> **Version:** introduced foundational · available all · *Scenario step: Synthesis*

The capstone exercise of the workshop. Build a single end-to-end quote for Infinitech that exercises every Pricing capability covered in the prior sections.

### The deal

Infinitech is signing a 3-year deal across 3 environments (Pre-Prod, Prod, Gov). The quote includes:

- **3 × QB-COMPLETE bundles** (one per environment), each with:
  - **QB-API** at the appropriate environment attribute (Pre-Prod = $12K override, Prod = $15K, Gov = $8.5K) — all benefit from the **5% Bundle Adjustment** (Section 6)
  - **QB-MSG-STRT** at quantity 18 — qualifies for the **25% Volume tier** (Section 5)
  - One usage product (`QB-DB`) per bundle (required by `QB-PCG-USAGE` min/max=1 — see QB Scenario Reference)
  - Software Maintenance — derived as 20% of Software (Section 8 Derived Pricing)
- **2 × QB-QRack-750 servers** for the Prod environment, configured via:
  - **Server2 CML** (port-type constraints valid)
  - **Price Propagation** (260, Section 15) — ascending rollup from individual hardware components → sub-groups → bundle total
  - Optional **Pre/Post Apex Hook** (Section 12) for risk-tier enrichment
- **Header Adjustment** (Section 11) — 8% deal-wide discount applied at quote header
- Optional **Q4 promotion** (Section 18, Beta) if active
- **Pricing Procedure** uses **Stack** policy for multi-output resolution (Section 10)
- **Multi-currency** if expanding internationally — USD for US LE, with optional GBP for UK office expansion (covered in QB Scenario Reference)

### What attendees should observe

- Each line's **Pricing Waterfall** shows a clear cascade of every element that fired
- The Bundle Adjustment + Attribute Override + Volume Tier + Header Adjustment + (optional) Promotion all stack
- The **Revenue Cloud Operations Console** logs every pricing API call
- **Auto-numbered element names** (Section 22) make complex procedures readable
- **Advanced Price Logs** (Section 21) provide diagnostic data per element
- **Price History Tracking** (Section 23) records every adjustment

### Discussion prompts for the workshop

- Trace the final price for one QB-API at Prod environment. Show the math step-by-step.
- What happens to the Header Adjustment if you set Floor Price Restriction (Section 11)?
- The Q4 promotion — what are the tradeoffs of Last Transaction Price vs List Price as the asset's pricing source?
- The Server2 CML — why doesn't a non-validated server config price out cleanly? What error fires?
- For the Price Propagation walkthrough — what if you added a third level (Server → Component sub-group → Item)?

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.

---

## Appendix: Open authoring questions

1. **Sections referencing prior-release PDFs** — currently the carry-forward sections (252, 254, 256, 258 features) summarize the *behavior* and link to the prior PDF for full configuration steps. Is that the right depth, or should master sections also include full step-by-step walkthroughs (which makes the master file ~3× longer)?
2. **Synthesis exercise scope** — currently it stitches together every prior section. Workshop time may not allow that breadth. Should there be **two** synthesis exercises (a 2-hour scoped one and a 6-hour comprehensive one)?
3. **Per-section visual guidance** — many sections benefit from screenshots. The master format should specify where these go (inline images vs. linked Highspot deck reference).
4. **Demo URLs** — three confirmed demos (Price Propagation, Promotions, IF/Auto-numbering). Need actual URLs.
5. **Pre-built starting Opportunity / Quote** — for workshop attendees, having a starter Quote saves 15 minutes of catalog navigation. See QB Scenario Reference Gap #2.
6. **CML constraint behavior on QB-COMPLETE** — Section 14 (IF/Else) and Section 15 (Price Propagation) walkthrough on QB-COMPLETE assume valid configurations. Cross-area to Configurator master exercise for constraint-violation walkthroughs.
7. **Exercise length / pacing** — first read-through suggests 4–6 hours of workshop content. Confirm with author whether to split into Part A (Foundations + Adjustments + Multi-Output) and Part B (Custom Logic + Propagation + Operations).
