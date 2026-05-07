# Modules 3, 4, 5 — Proposed LO Revisions for Mike's Review

**Purpose:** Apply the Module 1/2 LO revision pattern (concrete object/feature anchors, drop value-prop puffery, drop tangential topics, concrete verbs) to Modules 3, 4, and 5 *before* attempting full v2 rewrites. Mike confirms or edits the proposed LOs; v2 drafts follow.

**Pattern observed in Mike's revisions to Modules 1 and 2:**
- Each LO anchors to a specific product object or feature (not a value prop or capability cluster).
- Concrete verbs: Describe, Explain, Map, Configure, Understand. Weak verbs (Identify, Recognize, Utilize, Articulate) appear less often.
- Multiple v1 LOs often consolidate into a single sharper one.
- Topics that aren't core to the module's domain get cut, even if they're real.
- Audience: AE / SE / Specialist who needs to defend the technical story to a buyer or implementer — not a general practitioner.

**Verification status:**
- Items marked `[VERIFIED]` reference the Spring '26 Help compendium (`docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`).
- Items marked `[NEEDS VERIFICATION]` are taken from the v1 draft and should be confirmed before v2 authoring.
- Items marked `[OPEN QUESTION]` are framing/scoping calls I want Mike's input on before committing.

---

# Module 3 — Usage, Rating, and Consumption Agents

**Current shape:** 4 units. The v1 draft is the most extensive in the L2 mix and reaches further into product detail than the LOs strictly require. **Proposed shape:** 3 units. Consolidates v1 Units 2 and 3 into a single configuration unit, since Mediation and Rating are two halves of one operational story (clean the data → price the data) and the v1 split forces awkward "from clean data to correct charges" connective tissue.

## Current LOs (verbatim from v1)

**Unit 1: Define Consumption Foundations and Data Models**
- Differentiate between Pure Consumption and Hybrid revenue models.
- Identify the key objects in the consumption lifecycle and how they connect.
- Explain how Liable Summaries bridge the billing engine for accurate invoicing.
- Map the flow of usage data from ingestion in the Transaction Journal to final invoicing.
- Recognize when native Agentforce Revenue Management capabilities apply and when high-scale usage scenarios may require additional support.

**Unit 2: Navigate Ingestion and Mediation at Scale**
- Identify the key fields required to feed usage records into Salesforce.
- Explain the multi-step mediation process.
- Compare mediation options based on scale, including standard APIs, MuleSoft, and high-scale partners.
- Recognize competitive scenarios where ERPs may challenge Agentforce Revenue Management's usage management capabilities.

**Unit 3: Configure Complex Rating and Digital Wallets**
- Define the role of the Digital Wallet in managing credit inflows (Grants) and consumption outflows (Debits).
- Configure drawdown policies like "Expiring First" to automate how customer balances are consumed.
- Apply Rating Procedures and Rate Cards to calculate overages and pricing tiers.
- Describe how to integrate third-party rating apps or custom applications into the Agentforce Revenue Management rating engine.
- Recognize real-world deal scenarios where wallet configuration and rate locking are critical to closing.

**Unit 4: Explore Agentforce and The Usage Experience**
- Utilize the Usage Agent to identify customers in overage status and proactively surface upsell opportunities.
- Navigate the Usage App to provide customers and internal teams with a "single pane of glass" view of consumption details.
- Recognize which Agentforce agents are available within Agentforce Revenue Management and how they connect to the broader revenue lifecycle.

## Proposed LO revisions

**Unit 1: Map the Consumption Data Model and Usage Pipeline**
- 1.1 Describe the key objects in the consumption data model (Transaction Journal, Usage Summary, Ratable Summary, Liable Summary).
- 1.2 Explain how Liable Summaries bridge the rating engine to the billing engine and become Invoice Lines.
- 1.3 Map the flow of usage data from ingestion through aggregation, rating, and invoicing.
- 1.4 Differentiate the native Revenue Cloud Billing usage path from extension paths (m3ter and custom rating apps).

**Unit 2: Configure Mediation, Rating, and Digital Wallets**
- 2.1 Identify the required fields on a usage record (External ID, Timestamp, Quantity, Unit of Measure, Matching Attribute).
- 2.2 Configure Rate Cards and Rating Procedures to drive consumption pricing.
- 2.3 Configure Digital Wallet inflows (Grants) and outflows (Debits), and apply Drawdown Policies (Expiring First, Granted First, Granted Last).
- 2.4 Describe how to extend rating with third-party engines through the Rating Adapter or m3ter.

**Unit 3: Apply the Usage Agent and Usage App**
- 3.1 Describe the Usage Agent's role in surfacing overage and upsell signals from Digital Wallet and Usage Summary data.
- 3.2 Navigate the Usage App to view consumption, balances, and policy assignments in a single pane.
- 3.3 Identify which agents in the Agentforce Revenue Management family are licensed with Revenue Cloud Advanced versus require an add-on.

## Rationale

**Drop Pure-vs-Hybrid as an LO.** It's ambient context, not a learning outcome. The v1 draft uses it as a long opener; proposed Unit 1 keeps the Hybrid model story in the prose without making it an LO.

**Consolidate v1 Units 2 and 3 into proposed Unit 2.** Mediation, Rating, and Digital Wallet are the configuration surface for consumption billing. The v1 split forces a connective sentence ("from clean data to correct charges") that wouldn't be needed if the configuration story is one unit.

**Drop "Recognize competitive scenarios where ERPs may challenge..."** Pure value-prop, not a learning outcome. Sellers learn the competitive story from value cards, not from Trailhead.

**Drop "Recognize real-world deal scenarios where wallet configuration and rate locking are critical to closing."** Vague verb ("recognize"), no anchor object. The wallet-locking scenario *is* useful — it should appear as a Seller Sidebar in the Unit 2 prose, not as an LO.

**Tighten Unit 4 to Unit 3 (one unit instead of two attempts at agent coverage).** The v1's Unit 4 is short and somewhat redundant with the Module 1 v2 agent coverage. Three LOs cover what's specific to the Usage experience.

**Verb upgrades.** "Identify" and "Recognize" appear 5 times in the v1 — Mike's revisions used those weak verbs only when a real concrete verb ("Describe," "Configure," "Explain") wouldn't fit.

## Open questions for Mike

1. **`[OPEN QUESTION]` Unit count: 3 or 4?** I'm proposing 3. If you think the Mediation deep-dive (the 6-step pipeline: Collection → Normalization → Quality → Aggregation → Correlation → Usage Binding) deserves its own unit, that pushes us back to 4. Currently I have it as a sub-section under Unit 2 LO 2.1. **Your call.**

2. **`[NEEDS VERIFICATION]` Is the 6-step mediation framework Salesforce-standard or an authoring construct?** The v1 draft names six steps (Collection, Normalization, Quality, Aggregation, Correlation, Usage Binding). I haven't been able to confirm this is standard RCB doctrine vs. a generic mediation pedagogy framing. If standard, it's an LO worth including. If generic, it should be loose framing in the prose.

3. **`[NEEDS VERIFICATION]` Usage Agent vs. Agentforce Revenue Management agents naming.** The v1 calls it "Usage Agent" and lists six agents in a table (Usage, Quoting, Contract Search, Invoice Explanation, Product Description, Dispute Resolution). Are those names current? Is the Quoting Agent in Module 3's scope at all (it's quote-side, not usage-side)? I'd suggest the Module 3 agent coverage stays focused on Usage Agent + Usage App and leaves the broader agent family to Module 1's Unit 1 / Module 5.

4. **`[OPEN QUESTION]` Where does m3ter live?** Module 1 v2 mentioned it; Module 2 v2 referenced it as parked-to-Module-3; Module 3 v1 covers it heavily. I'd put the *positioning* mention in Module 1 (when to bring m3ter to a deal) and the *integration mechanics* in Module 3 LO 2.4. Cross-check with you before drafting.

5. **`[OPEN QUESTION]` Pricing detail.** The v1 covers Rate Card structure (Flat / Tiered / Ranges) and Drawdown Policies in detail. Should LO 2.2 also call out Rating Procedure as a separate object, or is "Rate Card and Rating Procedure" a paired concept students learn together? Currently grouped.

6. **`[NEEDS VERIFICATION]` Pure Consumption vs. Hybrid model framing.** The v1 attributes "64% of Forbes' next billion-dollar startups" to a market-shift narrative. If we keep the Hybrid framing in Unit 1 prose, the stat needs sourcing or replacement.

---

# Module 4 — Invoicing and Invoice Explanation Agents

**Current shape:** 1 unit. **Proposed shape:** 2 units. The v1 is under-scoped — invoicing is a much heavier topic than one unit allows, especially with split billing, milestone application, credit memos, DocGen, the Invoice Line Explanation Agent, and the Self-Service Portal as a customer-facing surface for invoices. Module 1 v2 covers *invoice production mechanics* (Billing Preview, Bill Now, Batch Scheduler, DPE pipeline, downstream objects); Module 2 v2 covers *Milestone Plan customization* and *Invoice Scheduler configuration*; this leaves Module 4 to cover *invoice patterns* (split, milestone application, credit memos) and *invoice delivery and explanation* (DocGen, email, Self-Service Portal, Explanation Agent).

## Current LOs (verbatim from v1)

**Unit 1: Manage Complex Invoicing with Agentforce**
- Configure split and milestone billing to handle complex, multi-phase revenue models.
- Automate invoice delivery across multiple channels using Invoice Schedulers.
- Explain how the Invoice Line Explanation Agent reduces billing-related service cases.
- Generate on-demand Invoice PDFs using Salesforce DocGen for customer self-service.

## Proposed LO revisions

**Unit 1: Configure Split Billing, Milestone Application, and Credit Memos**
- 1.1 Configure Split Billing to allocate invoice amounts across multiple billing accounts. *(maps to "Manage Billing Arrangements" in the Help compendium — see Open Question 1)*
- 1.2 Apply Milestone Plans to fire invoices on milestone completion (the *application* counterpart to Module 2 LO 1.4 *customization*).
- 1.3 Generate Credit Memos when invoiced amounts decrease, and apply them to outstanding invoices.
- 1.4 Describe how the Order to Billing Schedule pipeline produces Billing Period Items and Invoice Lines for each invoice.

**Unit 2: Deliver Invoices and Explain Charges with Agentforce**
- 2.1 Configure invoice delivery through the Send Invoices Through Email feature.
- 2.2 Generate on-demand Invoice PDFs through Salesforce DocGen.
- 2.3 Describe the Self-Service Portal as a customer-facing surface for viewing invoices and managing accounts.
- 2.4 Explain how the Invoice Line Explanation Agent provides plain-language breakdowns of complex charges.

## Rationale

**Two units instead of one.** A 4-LO single-unit module reads thin compared to Modules 1, 2, 3, 5. Two units (configuration patterns + delivery and explanation) gives invoicing the weight it deserves and matches the structure of the other modules.

**Split Billing maps to Help compendium "Manage Billing Arrangements."** The Help docs frame this as "billing arrangements [that] facilitate precise invoicing for business scenarios such as parent account billed for subsidiary accounts, cross-departmental charge allocations, or services or assets shared among multiple parties." If "Split Billing" is the seller-facing term and "Billing Arrangements" is the Help-doc term, the LO should use the seller-facing term and reference Billing Arrangements in the prose. **See Open Question 1.**

**Milestone Plans split between Modules 2 and 4.** Module 2 LO 1.4 covers *customizing and editing* Milestone Plans (the design-time activity). Module 4 LO 1.2 covers *applying* them (the runtime activity — what happens when a milestone completes). This boundary mirrors the Bill Run / Invoice Scheduler split you've already approved.

**Credit Memos added as new LO 1.3.** Visible in the Help compendium TOC ("Manage Credit Memos in Revenue Cloud") and absent from every other module. Belongs in Module 4 because credit memos are Invoice-adjacent.

**LO 1.4 (Order to Billing Schedule pipeline → Billing Period Items → Invoice Lines).** Module 1 v2 introduces these objects; Module 4's LO 1.4 reinforces them in the context of invoice generation. Worth keeping because it cements the data-model literacy from Module 1.

**Drop "Configure Invoice Schedulers" as a Module 4 LO.** Module 2 v2 LO 2.3 already covers Invoice Scheduler configuration. Module 4's role is *what comes out* of the scheduler, not how to configure it.

**Self-Service Portal coverage split between Modules 4 and 5.** Module 4 covers it as a customer-facing surface for *viewing invoices*; Module 5 covers it as a customer-facing surface for *making payments*. This is a real boundary — the Help compendium documents the portal across both functional areas — and it lets each module tell its own self-service story without duplicating.

## Open questions for Mike

1. **`[OPEN QUESTION]` "Split Billing" vs. "Billing Arrangements."** The Help compendium uses "Billing Arrangements" and describes the use cases the v1 calls "Split Billing." Are these the same thing? Should the LO use the seller-facing "Split Billing" term, the Help-doc "Billing Arrangements" term, or both? My instinct is to use both — Trailhead title for sellers, Help-doc term for tracing back to documentation.

2. **`[NEEDS VERIFICATION]` Conga to DocGen migration.** The v1 includes a real, dated fact: Conga Invoice Generation reached End-of-Renewal as of March 17, 2026, and customers can renew for up to 1 year or migrate to the $0 Salesforce DocGen path. Is this still accurate as of authoring date? Should it appear as a Seller Sidebar in LO 2.2?

3. **`[OPEN QUESTION]` Invoice Line Explanation Agent licensing.** The v1 says the Agent is "part of Agentforce for Billing Employee Assistance" and requires "both Revenue Cloud Billing licensing and the Agentforce Employee Agent Add-On." Is that still the licensing reality, and should the LO surface that explicitly?

4. **`[OPEN QUESTION]` "Manage Billing Disputes" placement.** The Help compendium includes a "Manage Billing Disputes" topic at the same level as "Manage Credit Memos." Should disputes appear in Module 4 (as an invoice-adjacent activity) or stay in Module 5 (as a Collections-adjacent activity)? My current proposal has them in Module 5; happy to move if you prefer.

5. **`[NEEDS VERIFICATION]` Send Invoices Through Email feature.** Verified in the Help compendium — this is a separate feature from the Invoice Scheduler. Confirm the seller-facing name; the Help docs use that exact phrase.

---

# Module 5 — Payments and Collections

**Current shape:** 1 unit. **Proposed shape:** 2 units. Same problem as Module 4 — the v1 is under-scoped for the topic. Splitting Payment configuration from Collections + Self-Service gives the module breathing room and parallels the Module 4 structure.

## Current LOs (verbatim from v1)

**Unit 1: Automate Payments and Collections**
- Identify connections between supported payment gateways and configure retry rules.
- Configure automated dunning processes to accelerate cash collection.
- Manage settlements using the Collections and Dispute Agent.
- Explain how the Self-Service Portal enables customers to manage their own accounts.
- Position the Payments and Collections capability to CFOs and Finance leaders.

## Proposed LO revisions

**Unit 1: Configure Payment Gateways, Methods, and Smart Retries**
- 1.1 Configure connections to supported payment gateways (Salesforce Payments, Adyen).
- 1.2 Describe how Stripe and other third-party processors integrate through tokenization APIs.
- 1.3 Configure Smart Retry rules to differentiate soft declines from hard declines.
- 1.4 Set up Payment Runs to sweep posted invoices automatically against connected gateways.

**Unit 2: Automate Collections, Disputes, and Customer Self-Service for Payments**
- 2.1 Configure automated Dunning workflows to escalate aging invoices through email, SMS, and portal nudges.
- 2.2 Describe the Collections and Dispute Agent's role in resolving billing disputes autonomously.
- 2.3 Set up the Self-Service Portal's payment surface (Pay Now link, payment method updates, one-time payments).
- 2.4 Articulate the Payments and Collections capability's impact on Days Sales Outstanding (DSO) for a Finance audience.

## Rationale

**Two units instead of one.** Same logic as Module 4 — a 5-LO single-unit module reads thin and forces unrelated topics together. Splitting Payment gateway/method configuration from Collections/Dispute/Self-Service mirrors Module 4's structure.

**LO 1.2 explicitly covers Stripe.** The v1 has Stripe as a footnote ("To use third-party processors like Stripe, customers must import payment tokens via API"). Stripe is one of the most-asked-about gateways in real deals, so it warrants its own LO. Salesforce Payments / Adyen as native + Stripe via token import is the full picture sellers need.

**LO 2.4 reframes the v1's "Position to CFOs" LO.** The v1 verb "Position" is value-prop language; Mike's pattern would replace it. "Articulate ... impact on DSO for a Finance audience" keeps the seller-facing skill but anchors it to a specific metric (DSO) and a specific audience (Finance). It's the closest a Module 5 LO comes to a positioning skill, and it earns its place because DSO is a real, measurable outcome.

**Disputes stay in Module 5.** The Collections and Dispute Agent operates across billing disputes and collections; keeping them together preserves the agent's full scope.

**Self-Service Portal split between Modules 4 and 5.** Module 4 covers *invoice viewing*; Module 5 covers *payment*. Each module owns the portion of the portal that's relevant to its functional area.

**Drop "Manage settlements" as a verb.** "Manage" is vague; the v1 LO becomes "Describe the Collections and Dispute Agent's role in resolving billing disputes autonomously."

## Open questions for Mike

1. **`[NEEDS VERIFICATION]` Salesforce Payments and Adyen as the native gateways.** The v1 says these are the only natively supported gateways. Confirm this is current and complete.

2. **`[NEEDS VERIFICATION]` Collections and Dispute Agent name and scope.** The v1 calls it "Collections and Dispute Agent" and attributes three capabilities: Analyze Disputes, Propose Settlements, Update the Ledger. Confirm the agent's name (it might just be "Collections Agent" or "Dispute Resolution Agent") and capability list.

3. **`[OPEN QUESTION]` Pay Now link prominence.** The v1 features the Pay Now link as a key capability. Worth a sub-bullet in LO 2.3 (currently covered) or its own LO?

4. **`[OPEN QUESTION]` "Cues from Customers" section.** The v1 closes Unit 1 with a "Cues from Customers" sales-coaching block. That's useful seller content but doesn't map to an LO. Recommend keeping it in the prose as a Seller Sidebar in Unit 2, but not making it an LO. Confirm.

5. **`[OPEN QUESTION]` Tacton/NetSuite competitive callout.** The v1 includes a Seller Sidebar comparing Revenue Cloud Billing to Tacton and NetSuite. Same recommendation — keep in prose as a sidebar, don't make it an LO. Mike's pattern across Modules 1 and 2 keeps competitive framing in sidebars rather than LOs.

6. **`[NEEDS VERIFICATION]` Days Sales Outstanding (DSO) reduction range.** Module 1 v2 cited "20–30%" DSO reduction. If we cite a number in Module 5 LO 2.4 prose, the source needs to be verified or the range omitted.

---

# Cross-Module Observations

## Topics still without a home in Modules 1–5 (from Module 2 v2 parking lot)

These came up during Module 2 v2 and remain unscoped after the proposed Module 3/4/5 LOs:

- **The "Big Four Flows" replacement story.** Mike's hint about the "context service and the flow that runs" suggests a more accurate billing-setup story exists. Currently nowhere in Modules 1–5.
- **DRO Settings and Pricing Setup.** Mike confirmed neither is billing. Likely belongs in a separate Order Lifecycle / Pricing module.
- **Multi-currency and Localization** as a standalone topic.
- **ERP Integration / System of Execution / PLG-vs-Enterprise Bifurcation Pattern.**
- **Standalone Billing APIs as a "headless commerce" topic** (separate from the ingestion use case in Module 2).

These need a scoping decision: add to existing modules, scope a Module 6, or cut from the L2 mix entirely.

## Cross-module agent coverage

Each module currently has its own agent story (Module 1: full agent family overview; Module 3: Usage Agent; Module 4: Invoice Line Explanation Agent; Module 5: Collections and Dispute Agent). Worth confirming that the agent licensing matrix is cited consistently across all five modules — particularly which agents come with Revenue Cloud Advanced versus require an Agentforce Add-On.

## Voice and style for v2 drafts

Once LOs are confirmed, the v2 drafts will apply the same patterns established in Module 1 v2 and Module 2 v2:
- Imperative-verb unit titles with concrete nouns.
- Concrete object names lead the explanations; metaphors used once for the cold-open and dropped.
- "Salesforce / Agentforce actively works on your behalf" phrasing avoided.
- Seller Sidebars sparse, with named pivots.
- Trailhead AI Review Checklist applied (sentence length, comparison patterns, modals, generic phrases).
- Object-name bolding maintained for cross-module consistency (deliberate deviation from the AI Review Checklist; flagged for editorial).

---

## Recommended next steps

1. **Mike reviews this document** and confirms / edits the proposed LOs.
2. **Scope the orphaned topics** above (Big Four / DRO / Multi-currency / ERP / Bifurcation) — add to existing modules, scope a Module 6, or drop from the L2.
3. **Verification pass** of `[NEEDS VERIFICATION]` items against the Spring '26 Help compendium.
4. **v2 drafts for Modules 3, 4, 5** authored against the confirmed LOs, using Module 1 v2 / Module 2 v2 voice patterns.
5. **Trailhead AI Review Checklist pass** on each v2 draft.
6. **Module 1 v2 checklist pass** — Module 1 v2 has been reviewed for content but not run through the AI Review Checklist; recommend doing this for consistency before the L2 mix ships.

---

*Prepared by Brian Galdino with AI assistance, May 7, 2026. LOs anchored to Module 1 v2 and Module 2 v2 voice patterns; specific objects and features verified against `docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf` where marked.*
