# Release 260 (Spring '26) — Feature Index

Per-area inventory of net-new features in Spring '26 / Release 260, extracted from primary sources. This is the authoring input for `docs/enablement/260/{area}-hands-on.md` files.

## Sources

| File | Description |
|---|---|
| `revenue-cloud-spring-26-2026-01-15.pdf` | Master Help compendium, 1,460 pages. Definitive reference for configuration steps. |
| `solution-overview-spring-26.pdf` | Internal Solution Overview deck — Revenue Cloud Advanced (CONFIDENTIAL), 127 pages. Per-feature Customer Need / Solution / Use Case / Impact. Most digestible primary source. |
| `solution-overview-spring-26-billing.pdf` | Internal Solution Overview deck — Revenue Cloud Billing (CONFIDENTIAL), 60 pages. Per-feature content for the 30+ Billing features (Customer 360, Debits & Credits, Advanced Amendments, Taxes, Payments & Collections, Accounting, Consumption & Wallets). |
| `release-notes-pricing.md` | Captured Spring '26 Salesforce Pricing release notes (web, via Chrome MCP). |
| https://help.salesforce.com/s/articleView?id=release-notes.rn_revenue.htm&release=260&type=5 | Public release notes — Revenue Management overview. |

> **Branding note:** Salesforce has rebranded Revenue Cloud as **Agentforce Revenue Management** in Spring '26. Internal materials still use "Revenue Cloud" — recommendation is to keep "Revenue Cloud" in 260 enablement until the product UI catches up.

> **Release-wide highlights** from Solution Overview: Simplified user experiences, B2B Commerce interop, Swaps & upgrades, Promotions (Beta), End-to-end scale 15K (Beta), Nested groups & price propagation, Enhanced ramp deal management, Rule-based auto approvals, Enhanced data true-up for CLM.

---

## Product Catalog & Discovery

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Product Detail Caching Enhancements** | GA | Invocable action expanded to manage Product Detail Cache: Re-generate Cache for existing products to reflect updates; Clear Cache. Lets sales reps see most accurate data after major catalog updates. | Product Detail Caching Demo |
| **Filterable & Searchable Field Configuration** | GA | Indexed Products supports configuring up to **100 combined searchable + filterable fields** (was 25 searchable + 40 filterable). Higher limits available via support. For customers with 4M–20M item catalogs. | Filterable & Searchable Field Demo |
| **Multi-Selection in Product Listing** | GA | Multi-select up to **100 products** from Product Listing (was 20) for bulk addition to Quotes/Orders. Higher limits via support. | Enhanced Multi-Selection Demo |

**Cross-area items affecting PCM (from highlights):**
- B2B Commerce interop adds: Dynamic Attributes (enhanced), Request for Quote (new), Unified Pricing (new), Qualification Rules (new), Amend/Renew/Cancel self-serve (new). See B2B Commerce Spring '26 Solution Overview for details.

---

## Salesforce Pricing

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Promotions — Define and Apply** | Beta | Define product- and category-based promotions using a definition template. Promotions visible during product browse and in Quote line item details panel. Pricing applies relevant promotions at run time via the new **Promotion Execution Element**. Carryover behavior: Last Transaction Price preserves promotions across asset lifecycle; List Price re-evaluates current eligible promotions during Amendments/Renewals. | Promotions Demo |
| **Promotion Visibility at Runtime** | Beta | Companion to Promotions: active product/category promotions visible during browse; automatic promotions auto-apply, manual/coupon-code require seller selection; assets carry promotion info via AssetActionSource → PriceAdjustment. | (with Promotions Demo) |
| **Price Propagation** | GA | Calculate prices for nested group line items + group-level aggregates. Up to 5 levels of nesting. Combines **Ascending Propagation** (rollup totals from children to parents) with **Horizontal Propagation** (sequential field-to-field formulas within a line/group). Constraints: one Price Propagation element per procedure, not compatible with Derived Pricing or Promotions in the same procedure, not supported inside List Group. | Price Propagation Demo |
| **Pricing Propagation Preview — Nested Groups** | GA | Design-time tooling: create a propagation table, configure formulas, preview the metadata structure with joined nodes and merged columns before activating. | (with Price Propagation Demo) |
| **Easier Debugging for Multiple Occurrences (Auto-Numbered Element Names)** | GA | Each new element added to a pricing procedure gets an auto-generated name reflecting its occurrence count. Reflects in the Revenue Cloud Operations Console for unambiguous element identification during debugging. **No configuration required.** | If Else Formula, Auto-numbering Demo |
| **If-Else Formula** | GA | `IF()` formula support in Formula-Based Pricing element. Three parameters: logical condition, value-if-true, value-if-false. Nested IFs supported. Example: `IF(SaleType = "Premium", ItemListPrice__c * ItemPremium__c / 10000, ItemListPrice__c)` | (with Auto-numbering Demo) |
| **Advanced Logging** | GA | Detailed logs for **attribute pricing, promotions, propagation, and derived pricing** elements. Enables root-cause troubleshooting. Performance impact — recommended for selective debugging only. Enable from Salesforce Pricing Setup. | (no demo) |
| **Pricing Operations Console → Revenue Cloud Operations Console** | GA | Rename only — no functional change. App, navigation, and Help docs all use new name. | n/a |

**Public release notes referenced one additional Pricing item not in Solution Overview:**

| Feature | Tier | Description | Source |
|---|---|---|---|
| **Package Your Pricing Workflow Seamlessly** | GA | Add procedure plans directly to deployment packages — migrate complete pricing solutions across orgs. **Important:** the master PDF (dated 2026-01-15, *before* GA) still contains a Note saying "You can't migrate Procedure Plans from one org to another" (master PDF p 342, "Considerations for Importing and Exporting Pricing Data"). The release notes confirm this limitation has been removed in 260 GA. **Action for exercise:** explicitly call out that 260 lifts this prior restriction. Pricing recipes, decision tables, and context definitions could already be packaged before 260; procedure plans are the new addition. | https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing.htm&release=260&type=5 |

**Spring '26 upgrade guidance / known issues affecting Pricing:**

- *Limitation with Price Propagation Element* — intermittent Pricing API failures when Price Propagation + Pricing Setting elements run together (procedure without change set, context reuse disabled). Throws `ClassCastException`. Workaround: retry. (master PDF p 117)
- *Instant Pricing API returns additional records for ARC* (with API v66.0) — cancellation lines, ARC breakdown lines, ARC detail lines, quote summary fields. Don't upgrade API version if integration depends on prior response shape. (master PDF p 118)
- *Canceling derived pricing products results in incorrect net total price* — known issue, no workaround. (master PDF p 118)

---

## Product Configurator

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **New Streamlined Compact Layout** | GA | Compact mode toggle: Product Name, Quantity, Selling Model, Price are fixed-position; additional custom fields accessed by expanding option cards. For large bundles requiring scroll. | (TBD) |
| **Fixed Position "Sticky" Error Messages** | GA | Error Message component available by default; messages persistently displayed at top of configurator modal; severity-tiered (Error/Warning/Info); expandable/collapsible. | (TBD) |
| **Edit Transaction Line Context Fields** | GA | Sales users can directly set/modify Sales Transaction Item context fields within the configurator option card. Custom fields added to flow setup are editable based on data type. | (TBD) |
| **Inline Attribute Configuration for Bundle Components** | GA | Configure component attributes directly within the option card (no separate-screen navigation). Enabled via Flow setting (Admin). For bundles with several components and <5 attributes each. | (TBD) |
| **Enhanced Instance Selection and Cloning** | GA | Create multiple instances with one click (specify desired quantity); clone a configured instance to reuse selections. Enabled in option groups in product configurator flow setup. | (TBD) |
| **Translation Support for Error Messages** | GA | Localized configurator error messages. | (TBD) |
| **Configuration Logs** | GA | Set up logs to monitor and troubleshoot product configuration performance. **Setup steps (master PDF p 1452):** (1) Create a permission set with `Product Configuration User` license; (2) Enable `Read and write configuration logs` user permission; (3) Assign permission set to users; (4) From Setup, open **Decision Explainer** and configure setup objects: Application Subtype Definition, Business Process Type Definition (both = `SolverPath`); Application Usage Type = `Explainability Service`; (5) Configure Explainability Action Definition (`SolverPath` for Label/Developer Name/Business Process Type, Application Type = `Industry Service Excellence`, Application Subtype = `SolverPath`, Action Log Schema Type = `Other`); (6) Create active Explainability Action Version with `SolverPath`. Logs viewed in Revenue Cloud Operations Console. | (TBD) |

---

## Transaction Management

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **15K Transactions** | Beta (Closed) | Built-in support for 15K quote/order transactions. Same UX as 1K. For manufacturers (multi-component quotes), insurance providers (multi-policy), industrial distributors (high-volume SKU quotes). | (TBD) |
| **Advanced and Pre-Set Filters** | GA (1K) / Beta-Closed (15K) | Predefined and user-defined filters for quote line lists. AND/OR logic. For navigating large multi-product/multi-service quotes. | (TBD) |
| **Multiple Ramp Schedules Per Transaction** | GA | Org Pref "Multiple Ramp Schedules Per Transaction" in Revenue Settings. Quote Line Group Type = `RampScheduleGroup`; SubGroups with `IsRamped=True`, `SegmentType = Custom or Yearly`. Independent ramp schedules per office location, distinct product suites with overlapping/concurrent ramp-up plans on a single quote. | (TBD) |
| **Multiple Ramped Asset Amendments in Single Transaction** | GA | Same Org Pref. Select multiple ramped + non-ramped assets together for amendment. Amend with varied timelines in one transaction. | (TBD) |
| **Approval Notification with Email Templates** | GA | (in Advanced Approvals subsection) | (TBD) |
| **Rule Based Auto Approvals** | GA | (in Advanced Approvals subsection) | (TBD) |
| **Swaps, Upgrades & Downgrades** | GA / Enhanced | (in Advanced Amendments subsection) | (TBD) |
| **Amend Asset for Future Dated Transactions** | GA | (in Advanced Amendments subsection) | (TBD) |
| **Enhanced Price Waterfall UX Hover** | GA | Better hover-state UX in the Price Waterfall component. | Price Waterfall Enhancements Demo |
| **Always On Instant Pricing** | GA | "Instant Pricing Active by Default" Org Pref in Revenue Settings — toggle stays on across sessions. | Always On Instant Pricing Demo |
| **Enhanced Import CSV to Quote with Auto-Loading of Defaults** | GA | Bundles import with default child products auto-selected; products with default attributes import with attributes preset. Requires Advanced CSV Data Import permission + Data Processing Engine "Create Quote Line Items from CSV File". | Import Quote Line Enhancements |
| **Elevated Data Access for Pricing Quotes and Orders** | GA | Org Pref. Sales reps can act on pricing without direct access to all underlying data inputs. | (no demo) |
| **Automated Predictable Line Sequencing** | Pilot | BT org perm "Revenue Cloud: Automated Predictable Line Sequencing" + customer toggle "Automatic Line Item Sequencing" in Revenue Settings. Order line items reflect Quote line item sequence consistently. | (TBD) |
| **Quoting Agent Enhancements** | (per highlights) | (Details TBD — listed in section header) | (TBD) |

---

## Contracts & Doc Gen

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Profile-Based Section Locking** | (TBD) | (per highlights) | (TBD) |
| **Data True-Up for Line Items** | (TBD) | Enhanced data true-up for CLM (per release-wide highlights) | (TBD) |
| **Migration of MS 365 Contract Templates** | (TBD) | (per highlights) | (TBD) |
| **Doc Gen Large File Size Support** | (TBD) | (per highlights) | (TBD) |
| **Doc Gen Template Context Services Filter** | (TBD) | (per highlights) | (TBD) |

> *[NEEDS DEEPER EXTRACTION] — Solution Overview Contracts/DocGen section not yet fully indexed. Read pp ~1700–2000 of solution-overview.txt extracted text.*

---

## Dynamic Revenue Orchestration (DRO)

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Decomposition Workspace Enhancements** | GA | (per highlights) | Decomposition Workspace Demo |
| **Pause External Callouts During Downtime** | GA | (Orchestration improvement) | Pause External Callouts Demo |
| **Custom Logic Hook Between Decomposition and Plan Generation** | GA | Hook custom logic into DRO flow | Custom Logic Hook Demo |
| **Orchestrate Business Process** | GA | (Generic order orchestration) | Orchestrate Business Process Demo |
| **Integrate DRO with Industries CPQ (CME Interop)** | Pilot → GA | Submit orders from CME package to DRO for orchestration. Steps: Enable DRO, create + activate `CMESalesTransaction` context definition, set up Sales Transaction Context for DRO w.r.t CMESalesTransaction CD, Order Routing Rules. | CME Interop Demo |
| **Orchestrate Asset Move and Change of Plan (MACD)** | Pilot | MACD orders from Industries CPQ. Service location moves, plan upgrades. Prevents churn, improves CSAT. | Demo of Move and Change Plan |
| **Managed Package Interop** | (per highlights) | (Details TBD) | (TBD) |
| **Change and Move Orders** | (per highlights) | (Details TBD — likely overlaps with MACD above) | (TBD) |

---

## Usage Management

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Salesforce GO: Automation of Usage Selling & Rate Management Setup** | GA | One-click Rate Management + Usage Selling enablement via Salesforce Go. Triggers full setup sequence (feature toggles, rate discovery procedure setup). | (TBD) |
| **Usage Product Validator** | GA | Design-time validator on Product details page. Cross-entity validation between product usage resources and rate card entries. Validator API supports up to 10 products per query. **Setup:** add the Usage Product Validator component to the product record page (product must have a usage model type). **Run:** App Launcher → Products → select product → on record page, under Usage Product Validator, click `Validate`. **Permissions:** `Usage Management Design Time User` + `Rate Management Design Time User`. **Validation rules:** effectivity from product usage resource start date; warning at 12-hour gaps for product-usage-resource pairs, rate-card-entry pairs, initial gap, and terminal gap. **Note:** if the usage model type changed after associated objects were created, manually verify before running validator. (master PDF p 1050+) | (TBD) |
| **Usage Selling: Save Quote/Order Rates** | GA | New `TransactionProcessingType.catalogRatePerf` setting. When enabled, rate card entries auto-saved with quote/order — preserves rates against subsequent catalog changes. When disabled, rates always read from catalog. | (TBD) |
| **Usage Assets From Order Item Action** | GA | (per highlights — automate creation of usage assets from order items) | (TBD) |
| **Consumption Agent (Agentforce)** | GA | Agentforce-powered agent that manages token resources to identify and act on token overages and generate quotes. **Capabilities:** (1) Identifies token overages at the account level; (2) Assists in creating targeted quotes with token packs; (3) Enables sales teams to upsell token packs. **Example utterances:** "I would like to get account usage details for Acme and Cloud Kicks", "What is the current consumption on my account?", "How many assets from Acme are with Overages?". **Prerequisites:** Einstein generative AI + Agentforce + Rate Management + Usage Management. **Permissions:** Wallet Management User + Usage Runtime user personas need same object permissions as Traceability. **Limitation:** available to authenticated Lightning Experience users only — Experience Cloud customers/partners not yet supported. (master PDF p 1329+) | (TBD) |

---

## Invoice Management & Revenue Cloud Billing

> 260 Billing is documented in a dedicated Solution Overview deck (`solution-overview-spring-26-billing.pdf`). 30+ features grouped into Customer 360, Debits & Credits, Advanced Amendments Support, Taxes, Payments & Collections, Accounting, and Consumption & Wallets.
>
> **License columns:** RCA = Revenue Cloud Advanced (includes Invoice Management); RCB = Revenue Cloud Billing (separate license). When a feature is marked "RCA + RCB" it works under both licenses.

### Customer 360 / Service

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Billing Service Requests & Dispute Management** | GA | RCB | Unified intake + automated resolution of billing service requests / disputes. **Setup:** enable "Manage Billing Disputes and Service Requests" in Billing Settings → assign Unified Catalog permission sets → configure sharing → install Billing Service Process templates from Unified Catalog → publish self-service portal with Catalog. **Use case:** community users navigate to Help Center on the self-service portal to raise billing inquiries. | Yes |
| **On Demand Invoice PDF generation** | GA | RCB | Account-specific invoice templates + on-demand single-invoice doc generation. **Setup:** DocGen Setup is a prerequisite. Enable "Document Generation" in Billing Settings; select org-default invoice doc template. Billing Ops can override per-account via billing profile templates. Use the **Generate Invoice Document** quick action on Invoice record page. | Yes |
| **'All Invoices' Related List on Order** | GA | RCA + RCB | Drag and drop the related list on Order page layout via Lightning App Builder. Unified view of invoices for an order regardless of creation path (Batch Run / Generate Invoices / Ingestion API). | (TBD) |

### Debits & Credits

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Credit Memo Sequencing** | GA | RCB | Unique gapless sequence numbers on posted Credit Memos for legal compliance, audit, reconciliation. **Setup:** enable "Configure Gapless Sequential Numbering for Billing" + "Mandate Sequence Policy for Posted Credit Memos" in Billing Settings. Create Sequence Policies for Credit Memos with selection conditions and regional patterns. | (TBD) |
| **Credit Memo Void & Debit Memo Creation** | GA | RCB | Void a credit memo → system auto-creates an offsetting debit memo to nullify the transaction. Closes accounting cleanly. | Credit Memo Void & Debit Memo Creation Demo |
| **Convert Debit Memos to Invoices** | GA | RCB | Use Invoice Ingestion API to convert a debit memo into an Invoice for collection of additional charges. | Convert Debit Memos to Invoices Demo |

### Advanced Amendments Support (cross-area with Transaction Management)

> ⚠️ **Cross-area note:** TM Features 7 (Swaps/Upgrades/Downgrades) and 8 (Future-Dated Amendments) have **billing-side implications**. Each amendment type triggers automatic billing schedule adjustments — even though there's typically "no billing setup required" beyond core RCA + RCB enablement. These are documented here so the TM exercise can cross-reference billing behavior.

| Feature | Tier | License | Billing-Side Behavior | Demo |
|---|---|---|---|---|
| **Upgrades, Downgrades, Swaps** | GA | RCA + RCB | On amendment, billing creates **negative BSG** to adjust the old asset and **new BSG** for the swapped/upgraded/downgraded product. No billing setup needed beyond enablement. Perform Swaps from Assets Viewer; Upgrades and Downgrades via IA + API. | (TBD) |
| **Amend & Renew with Future-Dated Order (ARC before FDO)** | GA | RCA + RCB | New amendments allowed even when future-dated transactions are already scheduled. Billing **evaluates existing billing schedules** and **creates adjustment Billing Schedules** to reflect changes accurately. No billing setup needed. | (TBD) |
| **Change End Date** | GA | RCA + RCB | Modify subscription term (extend or shorten) without performing a renewal. Billing autonomously evaluates existing schedules and creates adjustment Billing Schedules. | (TBD) |
| **Undo Future Dated ARC** | GA | RCA + RCB | Reverse a future-dated renewal/amendment/cancellation via **Rollback** action in Managed Assets Viewer. On order activation, billing creates **negative billing schedules** to counterbalance the previously created schedules. | (TBD) |
| **Price Amendments** | GA | RCA + RCB | Adjust pricing on an active subscription **without changing quantity, term, or product configuration**. Initiate from Managed Assets Viewer. On activation, billing creates negative BS for old pricing + new BS for updated price. (Previously, a price change required a quantity change to trigger an amendment.) | (TBD) |
| **Multiple Ramp Schedules** | GA | RCA + RCB | Independent ramp schedules per product/location on a single quote. Billing creates **BSG for individual products** and **BS for all terms** ramped. No billing setup needed. | (TBD) |

### Taxes

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Standard Tax Engine** | GA | RCA + RCB | Native configurable tax rates (table-driven) for simple tax use cases. Captures tax calculation table without requiring third-party tax engine integration. | Yes |
| **Tax Treatment Resolution** | GA | RCB | Supports taxation in countries like Brazil and India. Enhances existing Treatment Selection with Information + Legal Entity. Existing tax treatment resolution stops at certain depths; this extends it. | (TBD) |
| **Header Taxes** | GA | RCA + RCB | Tax calculation at transaction header level (in addition to line-level). | Yes |
| **Support VAT** | GA | RCA + RCB | VAT support for LATAM & APAC regions. | Yes |
| **Void Taxes / Recovery Enhancements** | GA | RCB | Void tax on a posted-then-canceled credit memo. | (TBD) |

### Payments & Collections

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Import & Save Externally Generated Tokens** | GA | RCB | Import already-saved payment tokens from existing merchant gateway accounts into "Save Payment Method" records for use in payments processing + batch processing. **Critical for migration** — customers don't need to re-collect their customers' payment method details. Supports CC, ACH, SEPA, BACS, BECS, BanContact, Digital Wallet, BNPL (Affirm/Klarna/AfterPay), UPI (India), PIX (Brazil). | (TBD) |
| **Rule-Based Cash Application** | GA | RCB | Define rules to prioritize how cash/credits/payments settle invoices. Define rule priority order. Applies to invoices generated via Invoice Batch Run + Bill Run. | Rule Based Cash Application Demo |
| **Payment Retry Rules** | GA | RCB | Define retry rules for failed payments based on **error category** or **raw error code**. System auto-retries based on rule criteria. Reduces involuntary churn from automated payment failures. | Payment Retry Rules Demo |
| **Edit Default Payment Method against Account** | GA | RCB | EDIT API to declare a saved token / payment method as **default** against the customer account. Used as fallback for subsequent payments when chosen method fails. | (TBD) |

### Accounting

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Summarize using Functional Currency** | GA | RCA + RCB | Full use of legal entity currency for accounting summaries (FX gain/loss, period-end summaries). Functional currency support across journal entries and AR. | (TBD) |

### Consumption & Wallets

| Feature | Tier | License | Description | Demo |
|---|---|---|---|---|
| **Consumption Traceability — API** | GA | RCB | New API exposes per-resource consumption traceability — total consumption, overage quantity/amounts, final unit rate per period, plus consumption sources (drawdown from grant vs. commitment). Pass `LiableSummaryId` to retrieve. No configuration needed. Renders in invoice at usage-resource level. | Yes |
| **Consumption Agent — View Overages in Tokens** | GA | RCA + RCB (both required) | Customers with token-rated resources can now view overages **in tokens** (not just native UoM). Example: storage rated at 2 Flex Credits/GB + compute at 3 Flex Credits/hour → overages displayed in Flex Credits at resource level. No configuration needed. | Yes |
| **Wallets Support for Partners** | GA | RCB | Expose wallet details (balances, consumed units per usage resource) + statements + consumption entities for partner/customer community users on Experience Cloud. **Setup:** Configure and add "Wallet Details" tab on Account page; Drill down via Wallet Statement on UsageEntitlementBucket; Access via Billing Self-Service portal template (Wallet flexipage OOTB). | Yes |

---

## Advanced Approvals (subsection of Transaction Management)

> Master PDF section starts at line 46694+. Multiple sub-features documented under "Design an Approval Workflow" and "Smart Approvals in Approval Flows".

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Approval Notification with Email Templates** | GA | New email templates for: (a) Approval Work Item Assignment Emails to Approvers, (b) Approval Submission Status Email Notifications to Submitters. Configurable via org settings `Send Approval Work Item Assignment Emails` and `Send Approval Submission Status Email Notifications` (master PDF p 46694). | (TBD) |
| **Rule-Based Auto Approvals (Smart Approvals)** | GA | Smart Approvals routes requests by **auto-approving pre-qualified data changes** and **not re-reviewing unchanged data**. When a record is resubmitted for approval, Smart Approvals compares new conditions against the previous submission — if values stay within defined range, it skips re-approval. Implementation via Autolaunched Flow Approval Process or Record-triggered flow in Flow Builder. **Setup steps:** (1) Create a Draft Autolaunched Flow Approval Process; (2) Define Rules and Conditions for Auto-Approval Resubmissions; (3) Use Stage Exit Condition for serial workflows. (master PDF lines 47030–47493) | (TBD) |
| **Override Approval Work Item** | GA | Flow Core Action that updates the status of an approval work item to reflect the approval admin's decision — admins can override decisions for any assignee. | (TBD) |
| **Stage Exit Condition** | GA | Configures when a stage exits in serial/approval workflows. Solves deadlocks when stages wait for steps that conditional logic never triggered. | (TBD) |

---

## Subscription Lifecycle

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Multiple Ramp Schedule + Multiple Ramped Asset Amendments** | GA | (Cross-listed under Transaction Management — same feature) | (TBD) |

---

## Cross-Area: Salesforce Go (Revenue Cloud Setup Automation)

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Salesforce Go for Revenue Cloud** | GA | Automated set-up experience for RCA. Adds support in 260 for: DocGen, Contracts (CLM), DRO, Usage Selling, Agents. Discover features and complete setup with minimal clicks. | Salesforce Go |

---

## Packaging Updates (Metering / Licensing)

| Item | Description |
|---|---|
| **API calls from Experience Cloud are metered** | Revenue Cloud meters external API calls. Community Cloud (Partner Community & Customer Community Plus) now counts as external API calls and is metered as Revenue Cloud Events. |
| **Revenue Cloud Growth customers cannot access Revenue Cloud features from Experience Cloud** | RCG customers do not get API access. Accessing RC features from Experience Cloud counts as API access. RCG → upgrade to RCA required. |

---

## Cross-Area: Agentforce for Billing Employee Assistance

Distinct from the Consumption Agent (which is for usage selling). This is the customer-service-focused billing agent.

| Feature | Tier | Description | Demo |
|---|---|---|---|
| **Agentforce for Billing — Invoice Line Explanation** | GA | Helps users understand invoice lines by providing detailed explanations of each charge — reasons + calculation methods. **API Name:** `InvoiceLineExplanation`. **Included Agent Actions:** `Get Invoice Line Records`, `Explain Invoice Line`. **Prerequisites:** Set Up Agentforce for Revenue Cloud. **License:** Revenue Cloud Billing + Agentforce Employee Agent add-on (additional $). (master PDF p 1330+) | (TBD) |

---

## Status of extraction

After the deeper master-PDF research pass:

| Open item from initial pass | Status |
|---|---|
| Contracts & Doc Gen detail | Still pending — solution-overview.txt pp ~1700–2000 |
| DRO complete features (MACD, etc.) | Most captured from licensing tables; Move/Change Plan detail pending |
| Invoice Management details | Still pending — solution-overview.txt pp ~2400–3000 |
| Approvals full detail | ✅ extracted (Smart Approvals, Auto-Approval Resubmissions, Override Work Item, Stage Exit) |
| Configuration Logs for Configurator | ✅ extracted (full setup steps) |
| Quoting Agent Enhancements | Pending — appears as header item only |
| Consumption Agent for Usage Management | ✅ extracted (capabilities, utterances, prerequisites) |
| Procedure Plan packaging | ✅ resolved — master PDF (1-15-2026) said "can't migrate", release notes confirm 260 GA lifts that restriction |
| Usage Product Validator setup details | ✅ extracted (full setup, permissions, validation rules) |
| Agentforce for Billing | ✅ extracted (Invoice Line Explanation agent topic) |

These remaining items can be filled in incrementally as we move into per-area authoring beyond Pricing. None are blocking the Pricing exercise.
