# Module 7: Strategic Selling, Discovery, and Competitive Readiness

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; product-capability claims grounded against the 262 Summer '26 Help portal capture; competitive and commercial claims flagged for PMM confirmation)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team, PMM
**Source verifications:** Salesforce Help portal (Billing area `ind.billing_*`), the ARM Billing L2 Outline, and public sources for competitive facts. See `module-7-v2-validation-report.md` for the per-claim citation log and the list of claims awaiting PMM confirmation.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.
**⚠️ Agent naming note:** The body content below refers to billing agents and subagents using the names that appear in current materials. Pending Annie + Mike alignment on subagent vs. "Billing Agent" vocabulary, names may be revised — content stays the same. This matches the hold notice on Modules 1, 3, 4, and 5.

---

**Badge Description:** Master discovery for the CFO, ROI quantification, and competitive differentiation.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Identify Top Personas and Lead Discovery | Quiz | |
| 2 | Address Objections and Differentiate the Solution | Quiz | |
| 3 | Position Value and Calculate ROI | Quiz | |

## AI Usage

Did you use AI to help you write this badge content?

- [x] Yes
- [ ] No

If yes, what AI tool did you use? Gemini Writer Gem, Slackbot, Gemini PMM Grader Gem

## Suggested Category

- **Role**: Sales Professional
- **Level**: Intermediate
- **Trailhead Products/Features**: Agentforce Revenue Management
- **Industry**: None
- **[For internal use only: Primary Product/Feature**: Agentforce Revenue Management **]**

## Supporting Documents

- [ARM Billing L2 Outline Proposal — FY27](https://docs.google.com/spreadsheets/d/11kgi-t-OVjsgtt7AlLjNUFItvovCoi2yC0UaL8cm2MY/edit?gid=670679088#gid=670679088)

---

# Unit 1: Identify Top Personas and Lead Discovery

## Learning Objectives

After completing this unit, you'll be able to:

- Identify key pain points for the CFO, Controller, and VP of Revenue Operations.
- Adapt your sales approach for different CFO profiles.
- Uncover hidden billing costs and manual "swivel-chair" processes during discovery.
- Map revenue leakage patterns to specific Revenue Cloud Billing capabilities.

Sales discussions often focus on the Chief Revenue Officer (CRO), who prioritizes pipeline growth. But when you position Revenue Cloud Billing as part of Agentforce Revenue Management, your primary partner is the Office of the CFO.

The CFO wants more than "more" revenue. They want controlled, compliant, predictable revenue. To sell effectively to finance leaders, understand their strategic priorities:

- **Revenue** — expand into new channels like consumption-based and usage-based models.
- **Profitability** — improve operational efficiency and advance AI readiness across the quote-to-cash cycle.
- **Cash flow** — maximize free cash flow and minimize revenue leakage through automation and billing accuracy.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** In Agentforce Revenue Management, **Usage Management** is the umbrella area for consumption-based products, and **Consumption Management** is the lifecycle within it that tracks consumption data and produces invoice-ready summaries. When you're talking about flexible monetization at the enterprise level, lead with Usage Management as the capability area and use Consumption Management for the rating-and-summary lifecycle specifically. |

## Meet the Key Personas

You'll encounter three key personas in a billing transformation deal.

**The CFO** — a high-level strategist focused on enterprise risk and levers of control.

- *Pain point:* Lack of agility. Legacy ERP systems are often too static to support modern consumption-based and usage-based products quickly.
- *What they want:* Revenue agility with built-in controls — not just flexibility. CFOs want speed with guardrails, not chaos.

**The Controller** — the financial scorekeeper focused on accuracy and auditability.

- *Pain point:* Manual reconciliation. They often manage a "risky patchwork" of spreadsheets to compensate for gaps in legacy ERP systems.
- *What they want:* A single, defensible source of truth from product to cash — especially when facing external audits.

**The VP of Revenue Operations** — the bridge between sales and finance, focused on process automation.

- *Pain point:* The "messy middle." Fragmented systems create data chaos, leading to billing errors, inaccurate renewals, and downstream replication issues that can create phantom line items and double-counted revenue.
- *What they want:* End-to-end automation that eliminates "swivel-chair" work across CRM, billing, and ERP. A winning proof point: Datavant replaced swivel-chair work with automated, cross-team workflows (including Slack-powered approvals) as part of its Agentforce Revenue Management deployment.

### Know Your CFO: Three Profiles to Consider

Not every CFO enters a conversation the same way. Understanding which profile you're dealing with helps you tailor your message and lead with the right value proposition.

**The Growth-Oriented CFO** is focused on scale. They're actively expanding into new markets, launching subscription or usage-based pricing models, and asking *"How do we grow without adding headcount?"* They're receptive to automation, AI, and platform consolidation. Lead with how Revenue Cloud Billing accelerates quote-to-cash and enables new monetization models.

**The Risk-Averse, Compliance-Focused CFO** leads with caution. Their primary concern is audit readiness, revenue recognition accuracy (ASC 606 / IFRS 15), and making sure billing matches what was sold. They've often been burned by billing errors or audit findings. Lead with the unified data model — what you sell is exactly what you invoice, on a single platform — and emphasize automated reconciliation and airtight controls.

**The Efficiency-Driven CFO** is laser-focused on cost reduction and operational efficiency. They're frustrated by manual, repetitive processes — finance teams reconciling quotes to invoices by hand, accountants moving data between systems, time-consuming month-end closes. They respond to concrete metrics: *"How many hours does your team spend on manual reconciliation today?"* Lead with the billing agents and usage rating that actively work to eliminate those inefficiencies.

## Conduct a Discovery Session

Discovery is your opportunity to uncover hidden costs and manual "swivel-chair" processes. A swivel-chair process happens when an employee manually moves data from one system — like a CRM — to another, like an ERP — because the systems don't communicate. This manual work is one of the leading causes of revenue leakage and delayed financial closes.

The most effective discovery sessions feel like a conversation, not an interrogation. Use these questions to surface pain:

- How does data move from a closed sale all the way to a final payment today?
- What manual steps are required to handle complex billing scenarios — subscription amendments, mid-cycle changes, usage-based pricing?
- Where do you see the most errors in your invoices, and how do your teams resolve them?
- How long does it take to close the books at month-end, and what slows that process down the most?
- When a customer disputes a charge, what does that resolution process look like — and how long does it take?

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Listen for the word "flexibility." Sales teams love flexibility, but it can scare a CFO because it implies a lack of rules. Pivot the conversation to **revenue agility** — the ability to move fast with built-in controls. Similarly, when prospects ask about competing with ERPs like SAP or NetSuite on usage and mediation capabilities, consider whether a partner-ecosystem approach (such as the m3ter partnership for high-scale, multi-dimensional usage scenarios) is the right framing. |

## Map Revenue Leakage to Capabilities

Revenue leakage is money your customer should have earned but lost to system errors, process gaps, or manual mistakes. When you identify leakage patterns during discovery, map them directly to a Revenue Cloud Billing capability.

| Leakage Pattern | What It Looks Like | Agentforce Revenue Management Capability |
|:--|:--|:--|
| Unbilled Usage | A customer uses a service, but the system fails to track and bill for it. | **Usage rating** automatically establishes a price for every usage record, so nothing goes untracked or unbilled. |
| Manual Reconciliation | Finance teams spend hours manually matching quotes to invoices across disconnected systems. | The **unified data model** ensures that what you sell is exactly what you invoice, on a single platform — no manual reconciliation required. |
| Billing Errors | Inaccurate invoices lead to disputes, delayed payments, and strained customer relationships. | **Billing agents** clarify charges and help resolve disputes before they delay cash flow. |
| Slow Month-End Close | Finance teams are bottlenecked by data that doesn't flow automatically between sales and billing systems. | **Automated billing schedules** (via the Order to Billing Schedule flow) bridge the gap between sales and finance, reducing close time. |

## Real-World Proof Points

Bring these customer stories into discovery conversations to make the narrative concrete:

- **Lightspeed** used Agentforce Revenue Management to cut quote generation from 55 clicks to 3. A custom quoting interface was built by a single developer in one week.
- **Shiftlogic.io** unified agreements with Salesforce Contracts in Agentforce Revenue Management plus Sales Cloud, generating and sending NDAs in 3 minutes — down from about an hour.
- **Datavant** replaced swivel-chair work with automated, cross-team workflows and Slack-powered approvals, plus a secure portal for cases, contracts, and invoices.

## Key Takeaways

You learned how to engage the Office of the CFO by matching specific financial personas with solutions for revenue leakage and manual process gaps. As you dive into your deals, keep these in mind:

- **Persona mapping:** tailor your pitch to what the leader values most — growth, safety, or speed.
- **Process efficiency:** target the swivel chair — the time wasted manually moving data between apps.
- **Profit protection:** stop revenue leakage by automating unbilled usage and fixing invoice errors.
- **Data integrity:** replace messy spreadsheets with a single source of truth for all financial data.

## Resources

- [*Salesforce Resource:* FY27 Revenue Cloud Billing Value Book](https://docs.google.com/presentation/d/1p2IZ3a1GFH4HYRO6usfuN-uy3uhTwvAilBVnvbsdTk8/edit)
- [*Salesforce Resource:* Revenue Cloud Billing Playbook & Internal Enablement Deck](https://docs.google.com/presentation/d/1ccfCEsNbSxyE4iXQlj6NLlrqSAXYYo8h9YMBjL5mKQg/edit)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Identify key pain points for the CFO, Controller, and VP of Revenue Operations.** | Which persona is primarily concerned with eliminating a "patchwork" of spreadsheets to ensure auditability? | Chief Executive Officer / Chief Information Officer / **Financial Controller** / VP of Sales |
| **Adapt your sales approach for different CFO profiles.** | How should a seller reframe a CFO's request for "flexibility" to address their fear of operational chaos? | Emphasize the lack of restrictive guardrails to ensure maximum sales speed. / **Pivot to revenue agility — the ability to scale quickly with built-in controls.** / Propose a partner-ecosystem approach to handle all usage-based mediation. / Recommend a legacy ERP replacement to consolidate all financial rules. |

---

# Unit 2: Address Objections and Differentiate the Solution

## Learning Objectives

After completing this unit, you'll be able to:

- Address ERP displacement and integration complexity objections.
- Resolve technical objections on data migration, multi-currency, tax scalability, and document generation.
- Articulate core differentiators against Zuora, Stripe, and in-house builds.
- Position the m3ter partnership for high-scale usage scenarios.

## Navigate the ERP-First Objection

When you propose a billing transformation, the most common pushback is: "Why not just use our ERP?" Most finance teams view the ERP (SAP, Oracle, NetSuite) as their system of record.

To pivot, help them see that while an ERP is great for accounting, it struggles with the agility modern sales requires.

### Pivot to Agility

Position Agentforce Revenue Management as the system of engagement that sits between the CRM and the ERP to handle complex, high-velocity billing changes that ERPs aren't built for. Here's the formula:

- **Validate:** "Your ERP is the perfect system of record for the general ledger — and it should stay that way."
- **Challenge:** "But ERPs are product-centric and built for static, physical goods. They struggle with the frequent, relationship-based changes of modern subscription and consumption models — mid-month upgrades, usage spikes, tiered overages."
- **Solve:** "Agentforce Revenue Management is the system of engagement. It manages the complex, messy changes in the customer relationship and sends clean, reconciled data to your ERP without touching your general ledger."

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When competing against SAP or NetSuite on usage mediation, high-volume rating, or multi-dimensional pricing, pull in the m3ter partnership early. Combining m3ter's ability to process billions of records in near real time with Revenue Cloud Billing's core functionality gives you an end-to-end solution that outperforms pure-ERP competitors. |

### Resolve Technical Roadblocks

Technical buyers — the Controller, IT Director, or Architect — need confidence the platform can scale with their global complexity. Here are the most common technical objections and how to address them.

**Data migration: "Our data is a mess in our legacy system."**
*Response:* "We don't just dump data — we align it. Because Revenue Cloud Billing is native to Salesforce, we use the same Account and Product objects you already have. We use Data Cloud to harmonize legacy billing data, so you get a complete historical view without dirty data breaking your new automation."

**Multi-currency and localization: "We operate in 40 countries."**
*Response:* "Revenue Cloud Billing is built for global scale. It supports multi-currency, localized date and address formats, and legal-entity-based billing out of the box. An invoice in Paris behaves exactly as French tax law requires, while US headquarters sees rolled-up revenue in USD."

**Tax engine scalability: "How do you handle complex tax calculations?"**
*Response:* "We don't try to be a tax company — we're tax agnostic. Revenue Cloud Billing has pre-built integrations with Avalara and Vertex. We send the transaction data, receive the tax calculation in milliseconds, and stamp it on the invoice. Total accuracy, zero manual effort."

**Document generation: "We're worried about losing our document workflows when we move off CPQ."**
*Response:* "This is a common migration concern, and we have a clear path. Customers migrating from CPQ or CPQ+ can move to Salesforce DocGen (OmniStudio), and document generation no longer consumes Revenue Events for Revenue Cloud Advanced or Revenue Cloud Billing — which improves the economics."

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** If a prospect is worried about losing an existing Conga DocGen integration, be direct: Conga's free CPQ and Billing DocGen SKUs are being wound down. Treat that as a forcing function to accelerate the migration conversation toward native Salesforce DocGen. *(Confirm current SKU and Revenue Events details with PMM before quoting specifics — see the validation report.)* |

With the technical objections handled, you're ready for the competitive conversation — and to show why a point solution can't match a complete platform.

### Differentiate Against the Competition

You aren't only selling against ERPs; you're selling against point solutions like Zuora and Stripe, and against the status quo (in-house builds). Use these "wedge" stories to differentiate:

| Competitor | Their Core Challenge | The Salesforce Advantage |
|:--|:--|:--|
| Zuora | Often acts as a silo, introducing heavy technical debt and integration complexity. | **Native execution:** no "bridge" required. Every workflow operates from the same trusted data source. |
| Stripe / Metronome | Great for simple B2C payments, increasingly entering B2B. Stripe's acquisition of Metronome blurs the B2B/B2C identity further, but the combination is still disconnected from complex B2B selling, ERP landscapes, and governed contract workflows. | **Outcome-led governance:** built for rule-dense B2B contracts where every billing action must be traceable, auditable, and tied back to the original contract terms. |
| In-House Builds | Expensive to maintain, brittle under change, and built for one-time transactions — not recurring revenue relationships. Customers like FlexRack were running 54 Excel sheets before moving to Revenue Cloud Billing. | **API-first scalability:** customize and launch new offerings across any channel without writing new code each time. |
| Nue.io / DealHub | Lightweight CPQ tools that lack billing depth, ERP integration, and agentic AI capabilities. Often positioned on cost and speed-to-implement. | **Platform depth + AI:** Revenue Cloud Billing includes GA billing agents for quoting, invoice explanation, dispute resolution, and more — all operating inside governed workflows. |

### The Agentforce Advantage

While competitors offer automated workflows, Salesforce delivers autonomous outcomes — a critical differentiator for a CFO.

**Compare the experience:**

- *Traditional billing:* A customer disputes a bill. A human agent looks across three systems. Four days later, it's resolved.
- *Agentforce billing:* An AI agent proactively spots a billing anomaly, explains the charge to the customer in real time, and offers a credit based on predefined CFO rules. That's actively working on your behalf.

**Drive efficiency with agentic capabilities.** These GA capabilities bring the advantage to life — worth calling out in a competitive conversation:

- **Billing collections automation** — automates dunning outreach, including actions like Get Dunning Strategy and Send Dunning Email.
- **Billing inquiries via the service agent** — customers can ask billing questions through the service agent and get instant answers, instead of waiting for a human rep.
- **Automated refund orchestration** — an invocable action enables refund orchestration without human intervention.
- **Billing frequency changes** — Revenue Cloud Billing supports changing from higher to lower billing frequencies on new sale orders, a key ask from CFOs managing cash flow.
- **Expanded payment methods** — the billing portal supports Apple Pay, Google Pay, SEPA Debit, BACS Debit, Klarna, and Afterpay.

## Key Takeaways

You've now learned to handle technical objections by positioning Salesforce as a flexible partner to existing ERP systems rather than a replacement:

- **Work with ERPs:** position Salesforce as the tool for customer relationships while the ERP handles the accounting books.
- **Unified data:** eliminate migration fears by using one platform where the quote, price, and invoice are always identical.
- **Platform over silos:** differentiate from competitors by offering a complete lifecycle — not a disconnected point solution that requires extra integrations.
- **Global scale:** use native tax and currency tools to help businesses expand into new markets without custom code.

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Resolve technical objections on tax scalability.** | How does Revenue Cloud Billing handle complex tax calculations across multiple global regions? | It uses a native, built-in tax calculation engine. / It requires customers to enter tax rates manually. / **It integrates with Avalara or Vertex for automated calculations.** / It only supports tax calculations within the United States. |
| **Articulate core differentiators against the competition.** | How does Agentforce billing handle invoice disputes differently from traditional systems? | It routes every dispute to a human agent for a four-day resolution. / It flags disputes and requests the customer to call support. / It pauses all billing activity until a manual review is complete. / **An AI agent identifies anomalies and explains charges in real time.** |

---

# Unit 3: Position Value and Calculate ROI

## Learning Objectives

After completing this unit, you'll be able to:

- Identify how to recover 1–5% of EBITDA by eliminating revenue leakage.
- Map the primary value levers of Agentforce Revenue Management to specific business pains.
- Calculate potential annualized business impact using the baseline ROI formula.
- Adapt your ROI story for different CFO profiles and strategic goals.

## The Leaky Bucket: Understanding Revenue Leakage

Imagine you're filling a large bucket to water your garden. If the bucket has tiny, hidden holes, you work twice as hard to keep the water level steady. In business, those holes are revenue leakage.

Revenue leakage is money a company earned but failed to collect, usually because of billing errors, unbilled usage, or manual mistakes. For most enterprises, it accounts for 1–5% of EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization).

By stopping these leaks, **Agentforce Revenue Management** helps companies recover money that flows straight to the bottom line. For a company with $100M in EBITDA, that's $1M–$5M back in the business.

### Measure the Impact

Once you've identified where the leaks are, measure their impact. To build a strong business case, speak the language of the CFO. Group the impact into these primary levers:

**Reduced Days Sales Outstanding (DSO).** DSO is the average number of days it takes a company to get paid. High DSO means cash is trapped in unpaid invoices. Agentforce Revenue Management reduces DSO by making invoices right the first time, which stops the disputes that delay payment.
*Discovery questions:* "How long does it take your team to resolve a billing dispute?" and "How many open disputes do you have right now?"

**Improved operational productivity.** Manual swivel-chair work wastes a finance team's time. By automating the flow from lead to invoice, teams stop doing data entry and start doing strategic work.
*Proof point:* At FlexRack, the team retired 54 Excel spreadsheets and achieved a $3.66M cumulative benefit through operational efficiency.

**Eliminated revenue leakage.** With a unified data model, the quote and the bill are the same, which closes the reconciliation gap where most money is lost.
*Proof point:* Genius Sports scaled invoice automation from 0% to 80%, allowing 25% of its quotes to be created and closed the same day.

## The ROI Calculation: Proving the Business Case

Knowing the levers is a start, but you must put them into a formula to prove the value. CFOs buy return on investment. Use this formula from the FY27 Value Book to show potential impact:

| ROI Lever | The Formula | Example (Acme Corp: $100M ARR) |
|:--|:--|:--|
| **Revenue Recovery** | (Annual Revenue) × (% Leakage Reduction) | $1M leakage → $500K recovered |
| **Staff Savings** | (Billing FTEs) × (% Productivity Gain) × (Salary) | 10 FTEs → 30% gain → $240K saved |
| **Cash Flow** | (Daily Revenue) × (Reduction in DSO) | $273K/day × 5 days → $1.3M freed cash |
| **Total Year 1 Potential Impact** | | **$2.04M** |

### Tailor the Story to the CFO Profile

A great business case only works if it matches what the customer cares about. In Unit 1 you learned the three CFO profiles. Because each leader has different goals, use specific "profile pivots" to keep your ROI message relevant:

- **The Growth-Oriented CFO** — focus on revenue agility. Lead with new monetization models and faster time-to-revenue. (Reference: Genius Sports.)
- **The Risk-Averse CFO** — focus on compliance and accuracy. Lead with ASC 606 accuracy and the unified data model advantage.
- **The Efficiency-Driven CFO** — focus on EBITDA recovery. Lead with headcount avoidance and month-end close speed. (Reference: FlexRack.)

## The Shift to Agentic Outcomes

Move the conversation beyond simple automation to **agentic workflows** that actively work on your behalf:

- **From manual to autonomous** — moving from human-led reconciliation to AI-driven data harmony.
- **From reactive to proactive** — identifying billing anomalies before the invoice is sent, rather than waiting for a customer complaint.
- **From fragmented to unified** — eliminating the "integration tax" by keeping all revenue data native on the Salesforce platform.
- **From cost center to growth engine** — freeing finance talent to focus on high-value initiatives that grow the business.

## Key Takeaways

You've learned to go beyond product features — by knowing who you're selling to, how to neutralize the toughest technical and competitive objections, and how to build a CFO-ready business case that ties Revenue Cloud Billing directly to bottom-line outcomes.

- **Quantify the leak:** revenue leakage runs 1–5% of EBITDA — make the hidden cost visible.
- **Speak in levers:** DSO reduction, operational productivity, and eliminated leakage are the three the CFO understands.
- **Show the formula:** the FY27 Value Book formula turns the levers into a defensible Year 1 number.
- **Match the profile:** growth, risk, or efficiency — lead with the lever that profile cares about most.

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Calculate potential annualized business impact using the baseline ROI formula.** | A prospect with $100M in EBITDA believes their billing accuracy is "good enough." According to the "leaky bucket" framework, which data point best demonstrates the hidden bottom-line impact of manual reconciliation? | **The 1–5% average revenue leakage typically found in manual systems.** / The total number of invoices generated per fiscal quarter. / The headcount cost of the existing Accounts Receivable team. / The percentage of customers using auto-pay features. |
| **Adapt your ROI story for different CFO profiles and strategic goals.** | Which proof point is most effective when speaking to an Efficiency-Driven CFO? | Accelerated time-to-market for experimental products. / **Retirement of 54 Excel spreadsheets and faster month-end close.** / Ability to customize the UI color of the billing dashboard. / Access to a comprehensive list of all billing engine buttons. |

---

# Appendix: Open Questions and Parking Lot

## Claims awaiting PMM confirmation

Module 7 carries several time-sensitive competitive and commercial claims that can't be grounded against the Salesforce Help portal (which documents product behavior, not commercial or partner-lifecycle facts). These need PMM sign-off before publication:

1. **Conga DocGen SKU lifecycle.** v1 stated Conga's free CPQ/Billing DocGen SKUs are "end-of-renewal as of March 2026." v2 keeps the point but removes the hard date and flags it. PMM to confirm current status and the right way to phrase it.
2. **Document generation and Revenue Events.** v1 stated that "as of February 2026" document generation no longer consumes Revenue Events for Revenue Cloud Advanced or Revenue Cloud Billing. v2 keeps the substance but drops the date. PMM to confirm this is still accurate and current.
3. **CPQ/CPQ+ migration to Salesforce DocGen "at $0."** A pricing/commercial claim. PMM to confirm.
4. **Customer proof-point metrics** (Lightspeed 55→3 clicks; Shiftlogic ~1 hour → 3 minutes; Datavant; FlexRack 54 spreadsheets / $3.66M; Genius Sports 0%→80% / 25% same-day). These read as reference-program metrics — PMM/reference team to confirm they're cleared for external Trailhead use and still current.

## Competitive claim — verified

- **Stripe's acquisition of Metronome** is confirmed via public reporting (the acquisition completed in January 2026; reported at roughly $1B). v2 removes the "late 2025" dating and states the acquisition as a fact without a date stamp, keeping the content evergreen.

## v1 changes applied

- **Version notations stripped.** v1's "The Spring '26 release brings this to life…" framing was removed; the GA capabilities are now presented without a release stamp, per the evergreen rule.
- **Cross-module consistency fix.** v1's Unit 1 callout described "Consumption Management" as the *broader* framework. Module 3 v2 (grounded against the snapshot) establishes the opposite: **Usage Management** is the umbrella area and **Consumption Management** is the lifecycle within it. v2 aligns Module 7's callout to that framing.
- **Agent naming.** v1 used "Agentforce Collections Agent," "Agentforce Agents," and similar names freely. v2 adds the same agent-naming hold notice carried by Modules 1, 3, 4, and 5, and softens to "billing agents" in body prose pending Annie + Mike alignment.
- **Grammar/typo cleanup** in the "Billing Inquiries via Service Agent" bullet and elsewhere.

---

*Prepared by Brian Galdino with AI assistance. Product-capability claims grounded against the latest Salesforce Help portal (Billing area); competitive and commercial claims flagged for PMM confirmation. Per-claim citation log: `docs/trailhead-l2-review/module-7-v2-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
