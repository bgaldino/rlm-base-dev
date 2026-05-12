# Modules 3, 4, 5 — Proposed LO Revisions v2

**Status:** Updated 2026-05-12 to incorporate Mike Aaron's second-pass review comments on the post-validation LO doc (Google Docs ID `19KU5T7S33nfryKg1pEn-hmdnTEeSkRRb9ZstiCVzpQs`). Mike's style direction: keep LO statements high-level and seller-facing; concrete object/field/product names go in the body content, not in the LO. Vary the verbs — "Describe" is overused. See `mike-comments-on-modules-3-4-5-los.md` and `mike-comments-resolution.md` for the full discussion thread.

**⚠️ Pending Annie's input — agent naming.** Mike wants "Billing Agent" universally. The 262 Help portal documents the agent suite as "Agentforce for Revenue Management" with named subagents (Subagent: Billing Collections Management, Subagent: Invoice Line Explanation, etc.). Brian flagged this as a conversation to have with Annie — new Agentforce materials apparently use subagent + superagent vocabulary. Until Annie confirms direction, **agent naming in LOs and body drafts is on hold** — the LO statements below use neutral phrasing where agent names would otherwise appear, with the chosen terminology to be slotted in after Annie's call.

**Companion documents:**
- [`module-2-v2.md`](./module-2-v2.md) — the reference v2 for voice and structure
- [`mike-comments-on-modules-3-4-5-los.md`](./mike-comments-on-modules-3-4-5-los.md) — Mike's 22 suggestions on the post-validation LO doc
- [`mike-comments-resolution.md`](./mike-comments-resolution.md) — Mike's responses to the comment-resolution proposal + the agent-naming question Brian raised for Annie
- v1 of this proposal (replaced) — see git history if needed

**Terminology corrections applied after verification against project metadata** (`/Users/brian/Documents/GitHub/bgaldino/_bgaldino/rlm-base-dev/.sfdx/tools/sobjects/standardObjects/`):

| Mike's term | Project-metadata-grounded term | Notes |
|:--|:--|:--|
| Transactional Usage Assignment | **TransactionUsageEntitlement** | Object name in standard schema |
| Payment Gateway Adaptor | **Payment Gateway Adapter** | Apex interface; `PaymentGatewayProvider` is the bridge SObject |
| Billing Agent | **Collections Agent** in 260; "Billing Agent" naming appears in 262 | Forward-looking rename |
| Credit prorate | **"Convert Negative Invoice Lines to Credit Memo Lines"** | The real feature name |
| Binding on Usage Entitlement Bucket | Binding configured on `TransactionUsageEntitlement.GrantBindingTargetId` and `UsageEntitlementAccount.GrantBindingTargetId` | Impacts the Bucket indirectly through `ParentId` |

---

# Module 3 — Usage, Rating, and Consumption Agents

**Mike's headline direction:** Split v1 Unit 1 into two distinct units — Usage Data Model and Usage Rating Pipeline. Drop "mediation" as something Revenue Cloud Billing does; clarify that mediation is customer-side. Refocus from Rate Card to **Asset Rate Card Entry** and **Asset Rate Adjustment** (the objects RCB actually consumes). Note that Digital Wallets and their entries create automatically — they're not configured. Move m3ter to the agents/extensions unit. Narrow the Usage Agent's scope to overage reporting.

**Shape:** v1 had 4 units. v2 has 3 units — Mike's Unit 1 split adds one unit, but the v1 Unit 2 + Unit 3 consolidate into proposed Unit 3.

## Current LOs (verbatim from v1 draft)

**Unit 1: Define Consumption Foundations and Data Models**
- Differentiate between Pure Consumption and Hybrid revenue models.
- Identify the key objects in the consumption lifecycle and how they connect.
- Explain how Liable Summaries bridge the billing engine for accurate invoicing.
- Map the flow of usage data from ingestion in the Transaction Journal to final invoicing.
- Recognize when native Agentforce Revenue Management capabilities apply and when high-scale usage scenarios may require additional support.

**Unit 2: Navigate Ingestion and Mediation at Scale** — 4 LOs (mediation pipeline, scale tiers, ERP competitive scenarios).

**Unit 3: Configure Complex Rating and Digital Wallets** — 5 LOs (Digital Wallet, Drawdown Policies, Rating Procedures, Rate Cards, third-party rating).

**Unit 4: Explore Agentforce and The Usage Experience** — 3 LOs (Usage Agent, Usage App, full Agent family).

## Proposed LO revisions (v2, incorporating Mike)

**Unit 1: Map the Usage Data Model**
- 1.1 Identify the headline objects in the usage data model and the role each one plays.
- 1.2 Explain how the usage data model is populated automatically at order activation for usage-based products.
- 1.3 Map how the binding mechanism determines what a usage entitlement bucket can draw from.

**Unit 2: Navigate the Usage Rating Pipeline**
- 2.1 Identify the required fields on a usage record entering the Transaction Journal.
- 2.2 Map the flow of usage data through the rating pipeline.
- 2.3 Apply rating procedures to convert raw usage into invoice-ready summaries.

**Unit 3: Apply the Usage Subagent and Drawdown Policies**
- 3.1 Apply the usage-management subagent to derive overage consumption insights and remediate them with generated quotes. (Agent-naming pending Annie — see status banner.)
- 3.2 Apply Drawdown Policies and Rollover Policies to govern how usage entitlement buckets are consumed and renewed.
- 3.3 Extend rating with third-party engines for high-volume scenarios.

## Rationale

**Why split Unit 1.** Mike's direction: the data model (what objects exist and how they connect at order activation) and the pipeline (how usage data flows through the system) are two distinct stories that the v1 conflated. Splitting them gives each its own focus.

**Why drop "Pure Consumption vs. Hybrid" as an LO.** It's ambient market context, not a learning outcome for a seller-level technical module. The Hybrid/Pure framing can appear in the prose without becoming an LO.

**Why drop the mediation pipeline as a Module 3 topic.** Mike's exact words: "The system does not support Mediation, remove this." Mediation is what the customer's data engineering team does before usage records reach the Transaction Journal. Module 3 can mention mediation as concept-level context but should make clear it's not part of Revenue Cloud Billing. LO 2.4 surfaces this directly.

**Why Asset Rate Card Entry and Asset Rate Adjustment lead the rating story.** Mike: "The config of rate cards isnt an RCB task. What RCB cares about is the Transaction Usage Entitlement, Asset Rate Card Entry, and the Asset Rate Adjustment." Rate Cards are list prices (catalog-side, Module 2 territory). Asset Rate Card Entries are the customer-specific negotiated rates, and Asset Rate Adjustments handle tiered/banded adjustments on top — both verified as real objects in the project metadata, both first-class concerns of RCB.

**Why "Digital Wallets create automatically" rather than "Configure Digital Wallets."** Mike: "You dont configure these, they create automatically." Drawdown Policies are similar — the system applies them, the user doesn't configure their behavior per Bucket. Reframing the LO as "describe and recognize" rather than "configure" is the right verb match.

**Why narrow the Usage Agent LO.** Mike: "The usage agent. its job is to report on overage." V1 had the Usage Agent doing much more (overage detection, upsell signals, natural-language queries). Mike's narrower scope is the accurate scope.

## Notes for v2 authoring

Rating Procedures and Rating Discovery Procedures are two distinct concepts in 262:
- **Rating Procedures** — customizable, ordered stacks of rating elements that calculate the final net rate for a usage resource. Implemented as `ExpressionSetDefinition` metadata at `force-app/main/default/expressionSetDefinition/RLM_DefaultRatingProcedure.expressionSetDefinition-meta.xml`.
- **Rating Discovery Procedures** — separate from rating procedures; their job is to fetch the binding objects, rate cards, rate card entries, and rate adjustments associated with sellable products. Used by Quote and Order Capture and Asset Lifecycle to get rate context for usage products. See `docs/salesforce/262/help/articles/ind.rm_rate_management.htm.md`.

Worth flagging both in the v2 prose since admins will look for "Rating Procedure" in the standard object browser and not find it (it's metadata), and they may conflate the two procedure types. The 2026-05-11 validation against the 262 Rate Management snapshot also surfaced that the "Negotiable Rating Procedure" naming used in the FY27 outline doesn't appear in the Help docs — only "Default Rating Procedure" does. Use Help-portal naming in LO/body content and reserve the file-name framing for developer asides.

Binding lives on `TransactionUsageEntitlement.GrantBindingTargetId` (the customer's per-product entitlement) and `UsageEntitlementAccount.GrantBindingTargetId` (the per-account binding). The Bucket inherits binding through `ParentId`. The `UsagePrdGrantBindingPolicy` object holds the policy itself. Mike's framing was close but the v2 prose should locate the binding accurately.

**Help-portal validation status: complete coverage of all 10 RC functional areas (838 articles total, 4.3 MB).** Captured 2026-05-11 / 2026-05-12 across:

- **Usage Management** (`ind.um_*`, 52 articles) — owns TransactionUsageEntitlement, Usage Entitlement Account / Bucket / Entry, ProductUsageResource / ProductUsageGrant, Drawdown Policies, Wallets. Covers Unit 1 + Unit 3 LOs.
- **Rate Management** (`ind.rm_*`, 35 articles) — owns RateCard, RateCardEntry, AssetRateCardEntry, AssetRateAdjustment, Rating Procedures + Rating Discovery Procedures. Covers Unit 2 LOs.
- **Agentforce for Revenue Management** (`ind.rev_agent_*`, 13 articles) — 7 subagents including Consumption Management. Covers Unit 3 LO 3.1.
- Plus PCM, Pricing, Configurator, Transaction Mgmt, DRO, Billing, Approvals for cross-module validation.

The Module 3 LOs above have been validated against the snapshots. See `module-3-262-lo-validation-report.md` for the per-LO findings. The three clear-cut corrections (Usage Ratable Summary naming, Rating Procedures vs Rating Discovery Procedures naming, Consumption Management subagent identification) are already applied to the LO list above. The Wallet Management question remains open for Mike.

**LO 3.1 resolved against a previously-missing area: Agentforce for Revenue Management.** Mike pointed out the agent suite lives at `ind.rev_agent_overview.htm` — a Help-portal area I had missed in my initial sidebar walk. That area is the "Agentforce for Revenue Management" agent suite, which contains 7 subagents spanning every functional domain:

- **Subagent: Product Selection** (PCM)
- **Subagent: Product Description Generation** (PCM)
- **Subagent: Quote Management** (Transaction Mgmt)
- **Subagent: Consumption Management** (Usage) — this is the one M3 LO 3.1 cares about
- **Subagent: Invoice Line Explanation** (Billing)
- **Subagent: Billing Collections Management** (Billing)
- **Subagent: Billing Inquiries** (Billing)

Mike's "Consumption Agent" hint was directionally right — the actual product name is **Subagent: Consumption Management** under the **Agentforce for Revenue Management** parent. LO 3.1 is rewritten above to use the verified product names, pairing the subagent with the Usage Overage Policy (governance) and Unified Usage Dashboard (monitoring surface) for a complete overage story.

The dedicated agents snapshot (`snapshot_agents_help_262`, root `ind.rev_agent_overview.htm`, prefix `ind.rev_agent`) is queued in `cumulusci.yml` and ready to run. Once captured, the body-content authoring pass for M3 Unit 3 can cite the agent's exact capabilities directly.

**Agent content is cross-cutting** — the Billing snapshot already has 4 `ind.billing_agentforce_*` articles covering area-specific operating context for the Billing subagents. When Transaction Mgmt and PCM snapshots run, expect similar `ind.qocal_agentforce_*` and `ind.product_catalog_agentforce_*` how-to articles to surface. Grep across all snapshots when validating agent claims (see `revenue-cloud-docs` skill for the validation pattern).

---

# Module 4 — Invoicing and Invoice Explanation Agents

**Mike's headline direction:** Drop the Milestone Application LO entirely — Module 2 v2 already covers milestone configuration and runtime, and Mike says we don't need to cover it again here. Replace v1's "Order to Billing Schedule pipeline" reference with the **Bill Run** (the v1 used the wrong term). Add **Debit Memos**, **Bill Cycle Day** (`BillDayOfMonth`), and **Next Billing Date** (`NextBillingDate`) as drivers of Invoice execution. Move **Credit Memos** to Unit 2 since they're post-invoice-production; correct the Credit Memo description (real mechanism: the "Convert Negative Invoice Lines to Credit Memo Lines" feature auto-creates Credit Memos when invoice lines go negative). Use **Billing Arrangements** as the term for Split Billing — it's the actual object name (`BillingArrangement` + `BillingArrangementLine`). Drop the Conga-to-DocGen migration callout entirely. Move Billing Disputes to Module 5.

**Confirmed flow for invoice production:** Invoice Scheduler creates the invoice data → DocGen renders the PDF → Send Invoices Through Email delivers it to the customer.

**Shape:** v2 stays at 2 units; structure shifts.

## Current LOs (verbatim from v1 draft)

**Unit 1: Manage Complex Invoicing with Agentforce** — 4 LOs (split/milestone billing, Invoice Schedulers, Invoice Line Explanation Agent, Invoice PDFs).

## Proposed LO revisions (v2, incorporating Mike)

**Unit 1: Configure Billing Arrangements and Drive the Bill Run**
- 1.1 Configure billing arrangements to allocate invoice amounts across multiple billing accounts.
- 1.2 Identify the cadence fields that drive when the bill run picks up a billing schedule.
- 1.3 Map how the bill run produces invoices from ready-to-bill billing schedules.
- 1.4 Analyze the automated conversion of Debit Memo Lines into Invoice Lines, driven by NextBillingDate on the Debit Memo record.

**Unit 2: Manage Invoice Delivery, Credit Memos, and the Invoice Line Explanation Subagent**
- 2.1 Configure the invoice delivery flow from scheduled generation through document rendering to customer email.
- 2.2 Apply the automatic conversion of negative invoice lines into credit memo lines, and the application of those credits to outstanding invoices.
- 2.3 Position the Self-Service Billing Portal as the customer-facing surface for viewing invoices and downloading PDFs.
- 2.4 Apply the invoice-line-explanation capability to give customers plain-language breakdowns of complex charges. (Agent-naming pending Annie — see status banner.)

## Rationale

**Drop Milestone Application.** Mike: "i dont think we need to cover milestones again, remove." Module 2 v2 covers both milestone configuration (on the BTI) and milestone runtime (`BillingMilestonePlan` and `BillingMilestonePlanItem`). Duplicating that coverage in Module 4 doesn't earn its space.

**Correct the Bill Run terminology.** Mike: "This is the bill run and not the Order to BS pipeline. Where did that come from?" The v1 mistakenly referenced "the Order to Billing Schedule pipeline" as the mechanism for invoice production. The actual mechanism is the Bill Run (`BillingBatchScheduler` / `InvoiceScheduler`). Order to Billing Schedule is the flow that turns activated Orders into Billing Schedules; it doesn't produce Invoices.

**Formal product name is "Invoice Batch Run."** Verified against the Salesforce Help portal (article `ind.billing_invoice_batch_run.htm`, titled "Invoice Batch Run Process"). "Bill Run" is acceptable seller-facing shorthand; body content should cite the formal name once for grounding.

**Add Debit Memos.** Mike: "We should add debit memos here." Debit Memos exist as a first-class object (`DebitMemo`) and carry `NextBillingDate`, which "determines when Debit Memo Lines are converted to invoice lines." This is a real product behavior worth surfacing in the Bill Run unit.

**Add Bill Cycle Day and Next Billing Date.** Mike: "And also how the Bill Cycle Day and the Next Bill Date play a roll in Invoice execution." Both are real fields. `BillDayOfMonth` is on `BillingSchedule`, `BillingScheduleGroup`, and `UsageEntitlementAccount`. `NextBillingDate` is on `BillingSchedule` and `DebitMemo`. They're the dates that drive when the Bill Run picks up a schedule.

**Use "Billing Arrangements" rather than "Split Billing."** Mike confirmed Billing Arrangements is the term in the Help compendium. The objects are `BillingArrangement` and `BillingArrangementLine`. "Split Billing" is the seller-facing concept; "Billing Arrangements" is what the system calls it. Both can appear in the prose.

**Correct the Credit Memo mechanism.** Mike: "Credits are created when invoice lines are negative, called a credit prorate. This needs to be updated." The verified feature name is **"Convert Negative Invoice Lines to Credit Memo Lines"** (enabled in Billing Settings). LO 2.2 leads with this mechanism rather than the v1's vaguer "when invoiced amounts decrease" framing.

**Move Credit Memos to Unit 2.** Mike: "This needs to move to Unit 2 as its really post invoice production." Configuration of Billing Arrangements and the Bill Run mechanics belong in Unit 1; what happens *after* an invoice is produced (delivery, credit memo creation, the Explanation Agent) belongs in Unit 2.

**Drop the Conga callout.** Mike: "Remove this. Focus on DocGen as the way that billing creates invoices." The v1 included the dated Conga End-of-Renewal note as a Seller Sidebar. Cut it.

**Move Billing Disputes to Module 5.** Mike: "In module 5." Disputes route through the Collections workflow; they belong adjacent to Dunning and the Collections Agent.

**Invoice Line Explanation Agent licensing.** Mike: "Its available in both." The v1 flagged a licensing question; resolved — the agent is available with both Revenue Cloud Advanced and Revenue Cloud Billing.

## Notes for v2 authoring

The invoice production chain is: **Invoice Scheduler → Document Generation Service → Send Invoices Through Email**. Each link is a distinct feature with its own configuration. The Invoice Scheduler is `BillingBatchScheduler` / `InvoiceScheduler`; the formal product name for the PDF step is **Document Generation Service** (often shortened to DocGen, built on OmniStudio); Send Invoices Through Email is a separate Billing feature. Worth naming all three explicitly so learners understand they're separate.

`DebitMemo.NextBillingDate` "determines when Debit Memo Lines are converted to invoice lines" — this is the connector between Debit Memos and the Bill Run.

Self-Service Portal coverage splits between Module 4 (invoice viewing) and Module 5 (payment surface). Each module owns its half.

---

# Module 5 — Payments and Collections

**Mike's headline direction:** Stripe and other third-party processors integrate via the **Payment Gateway Adapter** pattern (not generic "tokenization APIs"). Salesforce Payments and Adyen confirmed as natively supported gateways. The Collections and Dispute Agent name should be **Collections Agent** in 260 (with "Billing Agent" coming in 262), with capabilities **Dunning Strategy Recommendations** and **Account Billing Summaries** (both plural). Competitor examples should be **Oracle and Zuora** rather than Tacton and NetSuite. Add **Manage Billing Disputes** as an LO (moved from Module 4 per comment 23).

**Shape:** v2 stays at 2 units. Adding Disputes pushes Unit 2 to 5 LOs.

## Current LOs (verbatim from v1 draft)

**Unit 1: Automate Payments and Collections** — 5 LOs (gateways, dunning, Collections and Dispute Agent, Self-Service Portal, CFO positioning).

## Proposed LO revisions (v2, incorporating Mike)

**Unit 1: Configure Payment Gateways, Methods, and Payment Retry**
- 1.1 Establish integrations between the billing system and payment gateways to enable secure payment processing.
- 1.2 Extend payment processing to additional third-party gateways through a payment gateway adapter pattern.
- 1.3 Set up Payment Runs to sweep posted invoices automatically against connected gateways.
- 1.4 Implement a Payment Retry strategy that optimizes recovery rates by gateway error category.

**Unit 2: Automate Collections, Disputes, and Customer Self-Service for Payments**
- 2.1 Set up the Self-Service Portal's payment surface for customer-managed payments and updates.
- 2.2 Execute automated Dunning workflows that reduce Days Sales Outstanding (DSO) by deploying tiered communications across multiple channels.
- 2.3 Manage Billing Disputes — capture, validate, and resolve common billing requests from the Self-Service Portal or directly through the Collections workflow.
- 2.4 Articulate the Payments and Collections capability's impact on Days Sales Outstanding (DSO) for a Finance audience.
- 2.5 Apply the collections-management subagent to assess account health and recommend dunning strategies. (Agent-naming pending Annie — see status banner.)

## Rationale

**Payment Gateway Adapter, not "tokenization APIs."** Mike's correction: the integration pattern is the Payment Gateway Adapter, identical in shape to the Tax Engine Adapter from Module 2. `PaymentGatewayProvider` is the SObject that holds the `ApexAdapterId` linking to the Apex implementation. Stripe-style integrations are explicit in the Help compendium as named examples ("Stripe3P" in retry-rule sample data). LO 1.2 reflects the real architectural pattern.

**Billing Collections Management subagent — corrected against the Salesforce Help portal.** The pre-GA naming Mike worked from ("Collections Agent → Billing Agent rename" with capabilities "Account Billing Summaries" and "Dunning Strategy Recommendations") doesn't match what actually shipped. The product taxonomy is a parent agent — **Agentforce for Billing Employee Assistance** (internal users, with a customer-facing counterpart called **Agentforce for Billing Service Assistance Agent** in the Experience Cloud portal) — with three subagents underneath:

- **Subagent: Invoice Line Explanation** — explains individual invoice charges in plain language.
- **Subagent: Billing Collections Management** — at-a-glance view of financial standing, highlights high-risk invoices based on payment history / disputes / outstanding balances, surfaces recommended next actions. This is the subagent the LO 2.2 covers.
- **Subagent: Billing Inquiries** — answers natural-language questions about account balances, payment plans, upcoming payment dates, invoice details, and downloadable invoice documents.

The LO is rewritten to use the verified product names. Per Mike's evergreen style rule, the body content shouldn't reference "260" or "262" — the agent is just the agent.

**Add Manage Billing Disputes (moved from Module 4).** Per Mike's comment 23. Disputes use a service-process template-based intake/resolution workflow and are tightly coupled with Collections. Adding it as LO 2.3 keeps the dispute story adjacent to the Collections Agent.

**Reword the v1's "Position to CFOs" LO.** The v1 verb "Position" is value-prop language Mike's pattern would replace. LO 2.5 retains the Finance audience but anchors to DSO as the specific metric — keeping a positioning skill without softening it into puffery.

## Notes for v2 authoring

Competitor examples in any Seller Sidebar should be **Oracle and Zuora**, not Tacton/NetSuite. Mike: "Tacton is a poor choice."

Pay Now link is a real product capability — a shareable direct-payment URL that customers can use without logging into the portal. Worth one sub-bullet in LO 2.4's body.

The Self-Service Portal's payment surface is distinct from its invoice surface (Module 4 LO 2.3). Module 5 covers payment activities only — the same portal, scoped to the payment workflow.

---

# Cross-Module Notes

## Topics Mike directed to remove from the parking lot

Mike's comment 29 directed removal of the entire "orphaned topics" list from the v1 proposal. The following were in v1 with no current home; per Mike, they should be dropped from L2 scope entirely:

- The "Big Four Flows" replacement story.
- DRO Settings.
- Pricing Setup.
- Multi-currency and Localization as a standalone topic.
- ERP Integration / System of Execution / PLG-vs-Enterprise Bifurcation Pattern.

## Standalone Billing APIs

Mike's comment 30 directs that "Standalone Billing APIs as a 'headless commerce' topic" belongs in Module 2 — already covered in Module 2 v2 LO 2.1. No further orphaning needed.

## Voice and style for v2 drafts

When v2 drafts are authored against the confirmed LOs, the same patterns established in Module 1 v2 and Module 2 v2 apply: imperative-verb unit titles, concrete object names leading the explanations, metaphors used once at the cold-open and dropped, "Salesforce / Agentforce actively works on your behalf" phrasing avoided, Seller Sidebars sparse with named pivots, AI Review Checklist applied (sentence length, comparison patterns, modals, generic phrases). Object-name bolding maintained for cross-module consistency.

Module 4's Resources section is still placeholder text from the Trailhead template. The actual resources need to be authored.

---

## Recommended next steps

1. Mike reviews this v2 proposal and confirms or edits the LOs.
2. v2 drafts for Modules 3, 4, 5 authored against the confirmed LOs, using Module 1 v2 / Module 2 v2 voice patterns.
3. AI Review Checklist pass on each v2 draft.
4. Module 1 v2 checklist pass (Module 1 v2 has been content-reviewed but not formally checklist-reviewed).

---

*Prepared by Brian Galdino with AI assistance, 2026-05-08. LOs anchored to Module 1 v2 and Module 2 v2 patterns; new terminology verified against `.sfdx/tools/sobjects/standardObjects/` and the Spring '26 Help compendium at `docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`.*
