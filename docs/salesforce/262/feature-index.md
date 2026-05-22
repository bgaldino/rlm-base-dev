# Release 262 (Summer '26) — Feature Index

Per-area inventory of features in Summer '26 / Release 262, extracted from the Solution Overview decks, the public preview release notes, and the captured Salesforce Help portal snapshot. **Status: Active — Summer '26 in development.** Help snapshot captured 2026-05-11 / 2026-05-12 across all 10 RC functional areas (838 articles, ~4.3 MB markdown — see [`help/`](help/)).

> **Preview status reminder:** Per Salesforce Release Notes preamble — "Features described in this document don't become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can't guarantee general availability within any particular time frame or at all."

## Sources

| File | Description |
|---|---|
| `solution-overview-summer-26-rca.pdf` | Internal Solution Overview deck — Revenue Cloud Advanced (97 pp, CONFIDENTIAL, gitignored) |
| `solution-overview-summer-26-billing.pdf` | Internal Solution Overview deck — Revenue Cloud Billing (48 pp, CONFIDENTIAL, gitignored) |
| `salesforce-release-notes-summer-26-2026-05-07.pdf` | Full Salesforce Release Notes (996 pp, public — preview status, gitignored). Revenue Management section starts at p 720. |
| [`help/`](help/) | Per-article Salesforce Help portal snapshot for 262 (838 articles across 10 RC areas; captured 2026-05-11 / 2026-05-12 via `tasks/rlm_snapshot_help.py`). Replaces the older PDF compendium as the grep-friendly, diffable AI grounding source. See the `revenue-cloud-docs` skill. |

> **Branding note for 262:** Solution Overview decks still use "Revenue Cloud Advanced" / "Revenue Cloud Billing". The Spring '26 rebrand to "Agentforce Revenue Management" continues to propagate.

> **Release-wide highlights** (RCA): Accelerated Deal Approvals in Slack · Guided Ramp Creation with Trials · Constraint Rules in Product Discovery · AI-Supported Bulk Contract Extraction · Enhanced B2B Commerce Interop · Streaming Invoice Processing · Advanced Approvals with Preview UX · Advanced Approvals for Contracts · Large Transaction Scale (Beta) · DRO Templates.

> **Release-wide highlights** (Billing): Upgraded Invoice Batch Run · Billing Settlements Central · Advanced Amendments · Amendments with Milestone Billing · Refund Orchestration · Collections Agent · OOB Dunning Template.

---

## Product Catalog & Discovery

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Product Discovery with Constraint Rules** | GA | Constraint Rules enforce product compatibility and surface recommendations in real time. Auto Save & Non-Blocking UI: products added directly to a transaction without leaving discovery. Transaction Preview shows existing quote lines inside discovery. | Product Discovery with Constraint Rules |
| **Product Variants** | GA | Define and manage base products with their specific product variants (color, size, material). Enables consistent variant experience across B2B Commerce ↔ Revenue Cloud quote-to-cash. | Product Variants |
| **Enhanced Currency Display Precision (Decimal Currency Value Scale)** | GA | Configure up to 6 decimal places for unit-level prices and discount fields on Product Discovery, Quote, and Order pages. Default and minimum is 2. **Note:** only Unit Pricing and Unit Adjustment fields support high scale; final total fields still truncate to 2. | Unit Currency Decimal Scale |

---

## Salesforce Pricing

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **CSV Based Decision Tables** | GA | Decision tables sourced from CSV uploads. Supports >30 inputs and >5 outputs (was limited). **Limitations:** no versioning in initial release; sObject-dependent pricing elements (Attribute-Based Pricing, multi-output resolution) not supported; max 100,000 rows per CSV DT, max 500 CSV DTs per org, max 10 versions per DT, max 10,000 rows per version. **Setup:** Create Decision Table with `Type = CSV` → upload CSV → Activate → add to pricing recipe → map to pricing element → activate procedure. | CSV Based DT Demo |
| **Pricing General Enhancements** | GA | (1) Hover added to Revenue Operations Console showing Date/Time. (2) Currency column added to Revenue Ops Console display. (3) 100 default tags supported in Map Line Items element (was 50). (4) Map Line Item element now allowed in Parallel Execution. | TBA |

---

## Product Configurator

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Group and Ramp Segment Scope Rules** | GA | Extends Advanced Configurator to support transaction scope rules applicable to Quote Groups and Ramp Segments. Previously, scope rules failed to work when groups were present on quotes — particularly impactful for group ramps. | Group Scope Rules |
| **Product Loader and Default Component** | GA | (1) Automatic inclusion of default components from product catalog when importing product bundles. (2) New `@productField` annotation to load standard or custom Product fields directly into CML attributes — supports constraints on standard & custom product fields. | Product Loader |

---

## Transaction Management

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Guided Ramp Schedule Generation with Trial and Prorated Segments** | GA | Replaces slow manual cloning for multi-year ramp deals. Supports free/trial segments + stub periods at start/end. **Setup:** Revenue Settings → Turn On "Multiple Ramp Schedules per Transaction" + "Trial Segments for Group Ramp Schedules". Sales Reps initiate via "Create Ramp Schedule" Action. **Example use case:** 60-month yearly deal with 30-day trial; 1-month trial + 11-month subscription. | (TBD) |
| **Product Ramp Selection** | GA | OOTB discovery flow updated — Ramp Selection moved to start of process. Users define scope (Add to Current vs Subsequent segments) before entering Product List Page. Fixes the prior limitation where "Save and Exit" only persisted products to current segment group. | (TBD) |
| **Early Renewal for Ramped Asset** | GA | Renew a ramped asset ahead of schedule — start a new (often larger/longer) subscription. Specify a future "Renewal Start Date" even mid-segment; renewal quote replaces remainder of existing ramp schedule with new ramp segments. **Use cases:** end 3-year ramp after 2 years for renegotiated 2-year contract; consolidate ramped + non-ramped assets in single renewal quote. | (TBD) |
| **Slack Approvals (Accelerated Deal Approvals)** | New | Advanced Approvals now usable directly in Slack. New Preview UX. | (TBD) |
| **Approval Preview Enhancements** | Enhanced | (per highlights) | (TBD) |
| **Responsive & Maximized Quoting UX** | Enhanced | (per highlights) | (TBD) |
| **Increased Display Count of Attributes** | Enhanced | (per highlights — details TBD) | (TBD) |
| **Deep Clone Enhancements** | Enhanced | (per highlights — details TBD) | (TBD) |
| **Decimal Currency Support** | Enhanced | (cross-listed under PCM) | (TBD) |
| **Quote Extensibility Enhancements** | Enhanced | (per highlights — details TBD) | (TBD) |
| **Product Variants in Quotes & Orders** | New | (cross-listed under PCM) | (TBD) |
| **Large Transactions Scale** | Beta | Successor to 260's 15K (Beta closed). 262 expands scale further. | (TBD) |

---

## Contracts & Doc Gen

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **AI-Supported Bulk Contract Extraction** | New | Extract metadata at scale from existing contract PDFs (legacy). Protect margins, increase renewal revenue by unlocking historical data trapped in PDFs. | (TBD) |
| **Advanced Approvals for Contracts** | New | Multi-stakeholder serial-approval workflows on Contracts (now leveraging the Approvals framework). | (TBD) |
| **DocGen Client-Side LWC** | Enhanced | (per highlights — details TBD) | (TBD) |
| **DocGen Context-DPE Transformations** | Enhanced | (per highlights — details TBD) | (TBD) |
| **Dynamic Watermarks** | Enhanced | Create watermarks using tokens (per release highlights — exact scope TBD). | (TBD) |

---

## Dynamic Revenue Orchestration (DRO)

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **DRO Templates** | Beta | Pre-built DRO orchestration templates. | (TBD) |
| **DRO & OMS Interop** | Beta | Real-time synchronization between DRO and OMS (Order Management System) — addresses gaps where teams previously had to manage two non-synced platforms. | (TBD) |
| **Support for Future-Dated and Backdated Amendments and Renewals** | Enhanced | (per highlights — details TBD) | (TBD) |

---

## Usage Management Design & Selling

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Usage Product Guided Setup** | Enhanced | Streamlined setup flow for usage products. | (TBD) |
| **Usage Product Activation API** | (TBD) | Exposes activation programmatically. | (TBD) |
| **Consumption Agent** | Enhanced | (continues from 260; requires both RCB and Agentforce) | (TBD) |

---

## Invoice Management & Revenue Cloud Billing

> Solution Overview Billing deck has the comprehensive list. Highlights table groups features by area:

### Usage Management (in Billing context)

| Feature | Tier | Description |
|---|---|---|
| Usage Product Guided Setup | Enhanced | (cross-listed under Usage Management Design & Selling) |
| Consumption Agent | Enhanced | (cross-listed) |

### Billing Foundation

| Feature | Tier | Description |
|---|---|---|
| **Billing Frequency High-Low Support for New Orders** | (TBD) | Support new ordering models with different frequency cadences. |
| Early Renewal for Ramped Assets | (cross-listed under Transaction Management) | |
| Ramp Schedule Generation with Trial Segment | (cross-listed under Transaction Management) | |
| **Standalone — Simplified Standalone API** | (TBD) | Standalone billing API simplification. |

### Invoice Management

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Upgraded Invoice Batch Run** | (TBD) | (per highlights) | (TBD) |
| **Milestone Billing Amendments** | (TBD) | Amend bills tied to milestones. | (TBD) |
| **Statement of Account** | (TBD) | Consolidated view that summarizes all billing transactions (invoices, payments, credits, debits, refunds) for an account in a given time period. **Setup:** Enable Document Generation in Billing Settings (DocGen Setup required). Billing Ops can generate statements on demand from the Account page. | (TBD) |
| **Service Requests & Disputes — Assisted** | (TBD) | (per highlights) | (TBD) |
| **Streaming Invoice Processing** | Enhanced | (per RCA highlights) — Advanced & Billing | (TBD) |

### Payments & Collections

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Billing Settlements Central** | (TBD) | (per highlights) | (TBD) |
| **OOB Dunning Template** | (TBD) | Out-of-the-box dunning template (also a Salesforce Go: Accelerate setup item). | (TBD) |
| **Single Payment Request for Multiple Invoices** | (TBD) | (per highlights) | (TBD) |
| **Pass L2/L3 Data** | (TBD) | (per highlights — likely interchange optimization) | (TBD) |
| **Leverage Pay Now for Quick Payments** | (TBD) | (per highlights) | (TBD) |
| **Refund Orchestration** | (TBD) | (per release-wide highlights) | (TBD) |

### AI & Agentforce (Billing)

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Billing Service Catalog (Assisted & Simplified)** | New | Configure on Action Launcher. Case Assignment Rules auto-route new dispute cases. Service Reps raise disputes from a single Account view; Billing Ops track open cases with new UI components; Finance builds custom dispute reports using the Case Service Process Extension entity. | (TBD) |
| **Billing Service Assistance Agent** | New | New Service Agent topic. Setup: deploy MIAW (Messaging for In-App and Web) on Experience Cloud portal to route billing inquiries to the Billing Service Assistance Agent. Handles "What is the current outstanding balance?", "Get my latest bill details & invoice document", "What is the payment plan for this invoice?", "When is my next payment due?" | (TBD) |
| **Collections Agent — Dunning Strategy Recommendations + Account Billing Summaries** | (per highlights) | Agentforce-powered dunning recommendations and account-level billing summaries. | (TBD) |
| **Billing Inquiry Resolution via Service Agent** | (per highlights) | (Details TBD) | (TBD) |

---

## Cross-Area: Salesforce Go (Setup Automation)

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Salesforce Go Accelerate: Dunning Template** | Enhanced | Adds Dunning Template to Salesforce Go automated setup. | (TBD) |

---

## RCA + RCB Feature Comparison (262)

The Billing Solution Overview deck includes a comparison matrix:

| Capability | Invoice Mgmt (in RCA) | Revenue Cloud Billing |
|---|---|---|
| One-Time & Subscription Charges | ✅ | ✅ |
| Billing Arrangement, Usage Invoicing & Milestone Charges | | ✅ |
| Usage Rating & Consumption calculation | | ✅ |
| Tax Interface* & Standard Taxes | ✅ | ✅ |
| Invoicing, Credits | ✅ | ✅ |
| More Invoicing — Grouping, Write-off | | ✅ |
| Debit Memos | | ✅ |
| Standalone Billing for any object or external transaction | | ✅ |
| Invoice Doc Gen & Email Delivery^ | | ✅ |
| Accounting Periods & Closure | ✅ | ✅ |
| GL Accounts, Journal Entries (AR), FX Gain/Loss, Period end summaries | | ✅ |
| Payments, Refunds, Collections & Dunning | | ✅ |
| Analytics & Ops Console | ✅ | ✅ |
| Billing Agents | | ✅ |

`*` Tax calculations using tax integrations or external systems or API ingestion. `^` Email delivery is both on demand and batch using platform emails.

---

## Items still pending master-PDF arrival

When the 262 master Help compendium PDF becomes available (not yet published by Salesforce as of 2026-05-22), use it to fill in:

- All `(TBD)` feature descriptions and configuration steps
- Demo URLs for every feature row
- Upgrade guidance for 262 (post-Spring-'26 → Summer-'26 transition)
- Known issues and limitations for 262
- Detailed configuration for items currently described only by their high-level highlight

The structure of this index is set; the gaps are content-only. Once the master arrives, this becomes the authoring input for `docs/enablement/262/` exercises.

> **Partial substitute available now:** the per-article Help snapshot at `docs/salesforce/262/help/articles/` (838 articles, captured 2026-05-11 / 2026-05-12 — see `.cursor/skills/revenue-cloud-docs/SKILL.md`) covers most of what the compendium PDF will eventually consolidate. Where a `(TBD)` row in this index has an obvious matching Help article, agents grounding new content should cite the snapshot article rather than waiting for the PDF.
