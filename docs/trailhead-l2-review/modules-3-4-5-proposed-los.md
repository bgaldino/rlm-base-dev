# Modules 3, 4, 5 — Proposed LO Revisions v2

**Status:** Updated 2026-05-08 to incorporate Mike Aaron's 30 comments on the v1 proposal.

**Companion documents:**
- [`module-2-v2.md`](./module-2-v2.md) — the reference v2 for voice and structure
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
- 1.1 Describe the key objects in the usage data model: `TransactionUsageEntitlement`, `AssetRateCardEntry`, `AssetRateAdjustment`, `UsageEntitlementAccount`, `UsageEntitlementBucket`, `UsageEntitlementEntry`.
- 1.2 Explain how these objects are populated at Order Product activation for usage products.
- 1.3 Describe the binding mechanism (`GrantBindingTargetId` on `TransactionUsageEntitlement` and `UsageEntitlementAccount`; the `UsagePrdGrantBindingPolicy` policy object) and how binding impacts what a Usage Entitlement Bucket can draw from.

**Unit 2: Navigate the Usage Rating Pipeline**
- 2.1 Identify the required fields on a usage record entering the Transaction Journal (External ID, Timestamp, Quantity, Unit of Measure, Matching Attribute).
- 2.2 Map the flow of usage data through the pipeline: Transaction Journal → Usage Summary → Ratable Summary → Liable Summary.
- 2.3 Describe how the Rating Procedure (Default Rating Procedure or Negotiable Rating Procedure, implemented as `ExpressionSetDefinition` metadata) consumes Asset Rate Card Entries and Asset Rate Adjustments to produce Ratable Summaries.
- 2.4 Recognize that mediation (cleaning and normalizing raw usage data before it reaches the Transaction Journal) is customer-side responsibility, not part of Revenue Cloud Billing.

**Unit 3: Apply the Usage Agent, Drawdown Policies, and Extensions**
- 3.1 Describe the Usage Agent's role in reporting on overage status.
- 3.2 Describe the three Drawdown Policies (Expiring First, Granted First, Granted Last) and how the system applies them automatically to Usage Entitlement Buckets — they are not user-configured.
- 3.3 Describe how to extend rating with third-party engines, including the m3ter ISV partner integration for high-volume scenarios.

## Rationale

**Why split Unit 1.** Mike's direction: the data model (what objects exist and how they connect at order activation) and the pipeline (how usage data flows through the system) are two distinct stories that the v1 conflated. Splitting them gives each its own focus.

**Why drop "Pure Consumption vs. Hybrid" as an LO.** It's ambient market context, not a learning outcome for a seller-level technical module. The Hybrid/Pure framing can appear in the prose without becoming an LO.

**Why drop the mediation pipeline as a Module 3 topic.** Mike's exact words: "The system does not support Mediation, remove this." Mediation is what the customer's data engineering team does before usage records reach the Transaction Journal. Module 3 can mention mediation as concept-level context but should make clear it's not part of Revenue Cloud Billing. LO 2.4 surfaces this directly.

**Why Asset Rate Card Entry and Asset Rate Adjustment lead the rating story.** Mike: "The config of rate cards isnt an RCB task. What RCB cares about is the Transaction Usage Entitlement, Asset Rate Card Entry, and the Asset Rate Adjustment." Rate Cards are list prices (catalog-side, Module 2 territory). Asset Rate Card Entries are the customer-specific negotiated rates, and Asset Rate Adjustments handle tiered/banded adjustments on top — both verified as real objects in the project metadata, both first-class concerns of RCB.

**Why "Digital Wallets create automatically" rather than "Configure Digital Wallets."** Mike: "You dont configure these, they create automatically." Drawdown Policies are similar — the system applies them, the user doesn't configure their behavior per Bucket. Reframing the LO as "describe and recognize" rather than "configure" is the right verb match.

**Why narrow the Usage Agent LO.** Mike: "The usage agent. its job is to report on overage." V1 had the Usage Agent doing much more (overage detection, upsell signals, natural-language queries). Mike's narrower scope is the accurate scope.

## Notes for v2 authoring

The Rating Procedure is implemented as `ExpressionSetDefinition` metadata, not an SObject — files at `force-app/main/default/expressionSetDefinition/RLM_DefaultRatingProcedure.expressionSetDefinition-meta.xml` and `Negotiable_Rating_Procedure.expressionSetDefinition-meta.xml`. Worth flagging in the v2 prose since admins will look for it in the standard object browser and not find it.

Binding lives on `TransactionUsageEntitlement.GrantBindingTargetId` (the customer's per-product entitlement) and `UsageEntitlementAccount.GrantBindingTargetId` (the per-account binding). The Bucket inherits binding through `ParentId`. The `UsagePrdGrantBindingPolicy` object holds the policy itself. Mike's framing was close but the v2 prose should locate the binding accurately.

---

# Module 4 — Invoicing and Invoice Explanation Agents

**Mike's headline direction:** Drop the Milestone Application LO entirely — Module 2 v2 already covers milestone configuration and runtime, and Mike says we don't need to cover it again here. Replace v1's "Order to Billing Schedule pipeline" reference with the **Bill Run** (the v1 used the wrong term). Add **Debit Memos**, **Bill Cycle Day** (`BillDayOfMonth`), and **Next Billing Date** (`NextBillingDate`) as drivers of Invoice execution. Move **Credit Memos** to Unit 2 since they're post-invoice-production; correct the Credit Memo description (real mechanism: the "Convert Negative Invoice Lines to Credit Memo Lines" feature auto-creates Credit Memos when invoice lines go negative). Use **Billing Arrangements** as the term for Split Billing — it's the actual object name (`BillingArrangement` + `BillingArrangementLine`). Drop the Conga-to-DocGen migration callout entirely. Move Billing Disputes to Module 5.

**Confirmed flow for invoice production:** Invoice Scheduler creates the invoice data → DocGen renders the PDF → Send Invoices Through Email delivers it to the customer.

**Shape:** v2 stays at 2 units; structure shifts.

## Current LOs (verbatim from v1 draft)

**Unit 1: Manage Complex Invoicing with Agentforce** — 4 LOs (split/milestone billing, Invoice Schedulers, Invoice Line Explanation Agent, Invoice PDFs).

## Proposed LO revisions (v2, incorporating Mike)

**Unit 1: Configure Billing Arrangements and Drive the Bill Run**
- 1.1 Configure Billing Arrangements (`BillingArrangement` and `BillingArrangementLine`) to allocate invoice amounts across multiple billing accounts.
- 1.2 Describe the role of Bill Cycle Day (`BillDayOfMonth`) and Next Billing Date (`NextBillingDate`) in Invoice execution.
- 1.3 Map how the Bill Run picks up ready-to-bill Billing Schedules and produces Invoices and Invoice Lines.
- 1.4 Describe how Debit Memo Lines convert to Invoice Lines based on Next Billing Date.

**Unit 2: Manage Invoice Delivery, Credit Memos, and the Invoice Line Explanation Agent**
- 2.1 Configure the invoice delivery flow: the Invoice Scheduler creates the invoice data, DocGen renders the PDF, and Send Invoices Through Email delivers it to the customer.
- 2.2 Describe how Credit Memo Lines are auto-created from negative Invoice Lines (via the "Convert Negative Invoice Lines to Credit Memo Lines" feature in Billing Settings) and how Credit Memos are applied to outstanding invoices.
- 2.3 Describe the Self-Service Portal as a customer-facing surface for viewing invoices.
- 2.4 Explain how the Invoice Line Explanation Agent provides plain-language breakdowns of complex charges. (Available with both Revenue Cloud Advanced and Revenue Cloud Billing — Mike confirmed.)

## Rationale

**Drop Milestone Application.** Mike: "i dont think we need to cover milestones again, remove." Module 2 v2 covers both milestone configuration (on the BTI) and milestone runtime (`BillingMilestonePlan` and `BillingMilestonePlanItem`). Duplicating that coverage in Module 4 doesn't earn its space.

**Correct the Bill Run terminology.** Mike: "This is the bill run and not the Order to BS pipeline. Where did that come from?" The v1 mistakenly referenced "the Order to Billing Schedule pipeline" as the mechanism for invoice production. The actual mechanism is the Bill Run (`BillingBatchScheduler` / `InvoiceScheduler`). Order to Billing Schedule is the flow that turns activated Orders into Billing Schedules; it doesn't produce Invoices.

**Add Debit Memos.** Mike: "We should add debit memos here." Debit Memos exist as a first-class object (`DebitMemo`) and carry `NextBillingDate`, which "determines when Debit Memo Lines are converted to invoice lines." This is a real product behavior worth surfacing in the Bill Run unit.

**Add Bill Cycle Day and Next Billing Date.** Mike: "And also how the Bill Cycle Day and the Next Bill Date play a roll in Invoice execution." Both are real fields. `BillDayOfMonth` is on `BillingSchedule`, `BillingScheduleGroup`, and `UsageEntitlementAccount`. `NextBillingDate` is on `BillingSchedule` and `DebitMemo`. They're the dates that drive when the Bill Run picks up a schedule.

**Use "Billing Arrangements" rather than "Split Billing."** Mike confirmed Billing Arrangements is the term in the Help compendium. The objects are `BillingArrangement` and `BillingArrangementLine`. "Split Billing" is the seller-facing concept; "Billing Arrangements" is what the system calls it. Both can appear in the prose.

**Correct the Credit Memo mechanism.** Mike: "Credits are created when invoice lines are negative, called a credit prorate. This needs to be updated." The verified feature name is **"Convert Negative Invoice Lines to Credit Memo Lines"** (enabled in Billing Settings). LO 2.2 leads with this mechanism rather than the v1's vaguer "when invoiced amounts decrease" framing.

**Move Credit Memos to Unit 2.** Mike: "This needs to move to Unit 2 as its really post invoice production." Configuration of Billing Arrangements and the Bill Run mechanics belong in Unit 1; what happens *after* an invoice is produced (delivery, credit memo creation, the Explanation Agent) belongs in Unit 2.

**Drop the Conga callout.** Mike: "Remove this. Focus on DocGen as the way that billing creates invoices." The v1 included the dated Conga End-of-Renewal note as a Seller Sidebar. Cut it.

**Move Billing Disputes to Module 5.** Mike: "In module 5." Disputes route through the Collections workflow; they belong adjacent to Dunning and the Collections Agent.

**Invoice Line Explanation Agent licensing.** Mike: "Its available in both." The v1 flagged a licensing question; resolved — the agent is available with both Revenue Cloud Advanced and Revenue Cloud Billing.

## Notes for v2 authoring

The invoice production chain is: **Invoice Scheduler → DocGen → Email**. Each link is a distinct feature with its own configuration. The Invoice Scheduler is `BillingBatchScheduler` / `InvoiceScheduler`; DocGen is OmniStudio DocGen; Send Invoices Through Email is a separate Billing feature. Worth naming all three explicitly so learners understand they're separate.

`DebitMemo.NextBillingDate` "determines when Debit Memo Lines are converted to invoice lines" — this is the connector between Debit Memos and the Bill Run.

Self-Service Portal coverage splits between Module 4 (invoice viewing) and Module 5 (payment surface). Each module owns its half.

---

# Module 5 — Payments and Collections

**Mike's headline direction:** Stripe and other third-party processors integrate via the **Payment Gateway Adapter** pattern (not generic "tokenization APIs"). Salesforce Payments and Adyen confirmed as natively supported gateways. The Collections and Dispute Agent name should be **Collections Agent** in 260 (with "Billing Agent" coming in 262), with capabilities **Dunning Strategy Recommendations** and **Account Billing Summaries** (both plural). Competitor examples should be **Oracle and Zuora** rather than Tacton and NetSuite. Add **Manage Billing Disputes** as an LO (moved from Module 4 per comment 23).

**Shape:** v2 stays at 2 units. Adding Disputes pushes Unit 2 to 5 LOs.

## Current LOs (verbatim from v1 draft)

**Unit 1: Automate Payments and Collections** — 5 LOs (gateways, dunning, Collections and Dispute Agent, Self-Service Portal, CFO positioning).

## Proposed LO revisions (v2, incorporating Mike)

**Unit 1: Configure Payment Gateways, Methods, and Smart Retries**
- 1.1 Configure connections to natively supported payment gateways: Salesforce Payments and Adyen.
- 1.2 Describe how third-party processors like Stripe integrate through the Payment Gateway Adapter pattern (`PaymentGatewayProvider` with an Apex adapter class implementing the Payment Gateway Adapter interface).
- 1.3 Configure Smart Retry rules to differentiate soft declines from hard declines.
- 1.4 Set up Payment Runs to sweep posted invoices automatically against connected gateways.

**Unit 2: Automate Collections, Disputes, and Customer Self-Service for Payments**
- 2.1 Configure automated Dunning workflows to escalate aging invoices through email, SMS, and portal nudges.
- 2.2 Describe the Collections Agent's role in producing **Account Billing Summaries** and **Dunning Strategy Recommendations**. (Note: the 262 release renames this to "Billing Agent.")
- 2.3 Manage Billing Disputes — capture, validate, and resolve common billing requests from the Self-Service Portal or directly through the Collections workflow.
- 2.4 Set up the Self-Service Portal's payment surface: Pay Now link, payment method updates, one-time payments.
- 2.5 Articulate the Payments and Collections capability's impact on Days Sales Outstanding (DSO) for a Finance audience.

## Rationale

**Payment Gateway Adapter, not "tokenization APIs."** Mike's correction: the integration pattern is the Payment Gateway Adapter, identical in shape to the Tax Engine Adapter from Module 2. `PaymentGatewayProvider` is the SObject that holds the `ApexAdapterId` linking to the Apex implementation. Stripe-style integrations are explicit in the Help compendium as named examples ("Stripe3P" in retry-rule sample data). LO 1.2 reflects the real architectural pattern.

**Collections Agent (not Collections and Dispute Agent or Billing Agent).** Mike said rename to "Billing Agent" — verified in the project: "Billing Agent(s)" appears in the 262 feature index, but the **260 GA naming is "Collections Agent"** with capabilities "Account Billing Summaries" and "Dunning Strategy Recommendations" (plural). Since this L2 mix is shipping against 260 GA per the FY27 outline, the LO uses "Collections Agent" with a forward-reference to the 262 rename. If the L2 mix slips to 262, the rename is mechanical.

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
