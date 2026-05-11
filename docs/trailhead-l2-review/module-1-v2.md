# Module 1: The Agentforce Revenue Management Billing Foundation

**Status:** v2 draft for SME review (pulled from Mike Aaron's "Copy of Module 1 v2" Google Doc, 2026-05-11; validated against the latest Salesforce Help portal)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Salesforce Help portal (Billing area), project metadata (qb-billing, qb-tax, ERD). See `module-1-v2-262-validation-report.md` for the per-claim citation log.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.

**Badge Description:** Explore how Billing connects the revenue lifecycle to build an Agentic Enterprise.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Get Started with Agentforce Revenue Management Billing | Quiz | |
| 2 | Map the Revenue Cloud Billing Data Model | Quiz | |
| 3 | Master Invoice Production and Backend Services | Quiz | |

## AI Usage

Did you use AI to help you write this badge content?

- [x] Yes
- [ ] No

If yes, what AI tool did you use? Gemini and Slackbot + TH Writer Gem and TH PMM Grader Gem

## Suggested Category

- **Role**: Sales Professional
- **Level**: Intermediate
- **Trailhead Products/Features**: Revenue
- **Industry**: None
- **[For internal use only: Primary Product/Feature**: Select a Primary Product/Feature **]**

## Supporting Documents

- ARM Billing L2 Outline Proposal — FY27
- Placeholder for Demo Challenge
- Placeholder for ROI Pitch Challenge

---

# Unit 1: Get Started with Agentforce Revenue Management Billing

## Learning Objectives

After completing this unit, you'll be able to:

- Define how Billing completes the "Lead-to-Cash" journey within the Salesforce platform.
- Articulate the value of a unified customer record using value-based storytelling for AEs and SEs.
- Identify primary business problems solved by ARM Billing: revenue leakage, manual reconciliation, slow cashflow.

Imagine a row of dominoes stretching across your office. The first domino is your marketing campaign. As it falls, it hits sales, then contracting, then orders. In many companies, the last domino—the invoice—is missing or placed too far away. The chain stops, and someone has to manually restart it.

Revenue Cloud Billing, the billing component of Agentforce Revenue Management, is that final, critical domino. It serves as the connective tissue that ensures the energy from your first customer touchpoint carries all the way through to cash in the bank. By unifying your front and back office natively on the Salesforce platform, you transform a series of disconnected events into a single, flowing journey called Lead-to-Cash.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** Agentforce Revenue Management Billing and Revenue Cloud Billing are used interchangeably. The SKU is called Revenue Cloud Billing, while Agentforce Revenue Management elevates Agentforce as the primary brand presence. |

## Complete the Lead-to-Cash Journey

The Lead-to-Cash journey is the entire process of finding a customer, selling a product, and collecting payment. In legacy systems, this journey is often a "risky patchwork." Data lives in different silos, forcing teams to use digital labor—manual data entry—to shuttle information from a contract to an invoice.

Revenue Cloud Billing changes this by sitting natively on the Salesforce platform. It doesn't just "talk" to your sales tools; it shares the same DNA. When a deal closes, the Billing system already knows:

- Who to bill (the account record)
- What was sold (the product catalog and Billing Schedules)
- When to charge (the contract terms, Charge Frequency including one-time, recurring, milestone, and usage-based charge types, Start Dates, End Dates, Bill Dates)

This native integration means Billing isn't just an accounting task — it's the completion of the customer relationship. In fact, the critical bridge is the Order to Billing Schedule flow: a core automation that stages order data for invoicing without any manual handoff.

> **[Graphic Suggestion: Lead-to-Cash Flow]** A horizontal chevron diagram showing: Lead → Opportunity → Quote → Contract → Order → Billing Schedule → Invoice (Highlighted) → Cash. Adding "Billing Schedule" between Order and Invoice reflects the actual RCB data model.

## Storytelling with a Unified Customer Record

The "Unified Customer Record" is the most powerful story you can tell. In a disconnected world, a customer might call Support about an invoice error, but the Support Agent can't see the billing data. This creates friction and a poor customer experience.

With Revenue Cloud Billing, every team sees the same Source of Truth:

- Sales sees if a customer has outstanding balances before attempting to upsell.
- Service uses the Invoice Explanation Agent to query Invoice Lines and Usage Summaries, while the Billing Inquiries topic pulls real-time data from the Payment and Credit Memo objects.
- Finance sees real-time revenue reporting without waiting for a month-end sync from an external ERP.
- Partners can access the full Quote-to-Cash lifecycle — including billing — directly through the Experience Cloud portal, extending the unified record beyond your four walls.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When talking to stakeholders, you'll often hear, "Our ERP already does billing." ERPs are built for static transactions (selling a widget once). They struggle with recurring relationships (subscriptions, usage, and milestone billing). Use this pivot to show how sub-ledger data stays in Salesforce for relationship management, while the final Accounting Bookings sync to the ERP General Ledger. |

## Solve Critical Business Problems

When you move to an agentic billing model, you aren't just buying new software — you're fixing leaks in the business bucket. Agentforce Revenue Management Billing targets three primary pain points:

- **Revenue Leakage:** Many companies lose 1–5% of their earnings because they forget to bill for everything they deliver, especially in complex usage and milestone models. Because RCB is connected to actual order and usage data, it ensures no dollar is left behind — including through Consumption Management, which handles complex, high-volume, and multi-dimensional usage billing.
- **Manual Reconciliation:** Legacy billing often requires teams to "swivel chair" — copying data from one system to another. This is slow and error-prone. Automation reduces billing errors by up to 50%. For high-volume scenarios (e.g., hundreds of thousands of invoices per month with complex billing lines), RCB's batch invoice generation and standalone API simplification scale to meet enterprise demands.
- **Slow Cash Flow (High DSO):** Days Sales Outstanding (DSO) measures how long it takes to get paid. Disconnected systems lead to disputes and delayed payments. Agentforce actively works on your behalf to prioritize collections through the Agentforce Collections Agent — using Dunning Orchestration and automated refund workflows to resolve disputes faster and reduce DSO by 20–30%.

> **[Video Suggestion: The Power of Agentforce Revenue]** Insert a short (2-minute) demo video showing the "Invoice-to-Cash Reimagined" flow — from an activated Order to a generated Invoice to a Collections Agent resolving a dispute.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When demoing, don't start with the "Invoice" object. Start with the "Contract" or "Order." Show how the invoice is a natural byproduct of a well-structured deal — generated automatically from a Billing Schedule. This proves to the customer that they don't need "digital labor" to get paid. |

## Key Takeaways

In this unit, you learned how Billing completes the Salesforce ecosystem by bridging the gap between sales and finance.

- **The Connective Tissue:** Revenue Cloud Billing (RCB) — the billing component of Agentforce Revenue Management — is the final step in the Lead-to-Cash journey, bridging the Order to a Billing Schedule to an Invoice without manual intervention.
- **The Unified Record:** Shared data across Sales, Service, Finance, and Partners reduces customer friction and powers agentic experiences like the Invoice Explanation Agent, the Billing Inquiries agent, and the Collections Agent.
- **The Bottom Line:** By addressing revenue leakage, manual errors, and slow cash flow — through Consumption Management, batch processing, and Dunning Orchestration — organizations protect their margins and improve liquidity.

## Resources

- *Salesforce Help:* Explore the Revenue Cloud Data Model
- *Salesforce Help:* Billing Essentials
- *Salesforce Help:* Usage Management Essentials
- *Salesforce Resource:* FY27 Revenue Cloud Billing Value Book
- *Salesforce Resource:* Billing Technical Enablement 2026
- *Salesforce Resource:* DF 5904: Invoice to Cash Reimagined: Revenue Cloud Billing

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| (LO 1.1) | How does Revenue Cloud Billing (RCB) complete the "Lead-to-Cash" journey within the Salesforce platform? | A. By acting as a standalone accounting software that replaces the company's General Ledger. / B. By requiring manual data entry to ensure that contract terms are accurately reflected on invoices. / **C. By serving as native connective tissue that automates the flow from Order to Billing Schedule to Invoice without manual handoffs.** / D. By focusing solely on the marketing and lead generation phase of the customer relationship. |
| (LO 1.3) | Agentforce Revenue Management Billing is specifically designed to solve which set of primary business problems? | A. High marketing costs, low lead conversion rates, and poor website traffic. / B. Difficulty in hiring new employees, lack of office space, and slow internal email communications. / **C. Revenue leakage in complex models, manual reconciliation errors, and slow cash flow (High DSO).** / D. Lack of social media presence, shipping delays for physical goods, and hardware maintenance. |

---

# Unit 2: Map the Revenue Cloud Billing Data Model

## Learning Objectives

After completing this unit, you'll be able to:

- Distinguish between core objects including Orders, Billing Profiles, Billing Schedule Groups (BSGs), and Billing Schedules (BS).
- Map usage-based and milestone-based charges to their respective representations within the core Billing data model.
- Explain the "on-platform" advantage of shared data across Sales, Service, and Finance.

In the previous unit, we looked at how Revenue Cloud Billing serves as the connective tissue of the Customer 360. But how does a "Closed-Won" deal actually turn into an invoice? To understand that, we need to look under the hood at the data model.

The data model isn't just a technical map — it is the blueprint for automation. It's what allows Salesforce to move from a sales agreement to a financial record without "digital labor" or manual data entry.

## The Sales-to-Finance Hand-off

The journey from a deal to a dollar follows a specific path. In Revenue Cloud Billing, three core objects act as the bridge between the Sales team and the Finance team: Orders, Billing Schedules, and Invoices.

- **The Order:** When a deal closes, an Order is activated. Think of the Order as the "Change Agent." It contains the details of what changed with your relationship. A new purchase, the price, and the start date.
- **The Billing Schedule Group:** The Billing Schedule Group (BSG) represents what the customer owns. It establishes the billing relationship between an Account and a Product, and remains consistent throughout the lifecycle—even if the customer adds units or changes their plan. The BSG is what keeps a customer's history intact. If a customer doubles their licenses mid-contract, the BSG doesn't start over—it evolves.
- **The Billing Schedule:** While the BSG is the "parent," the Billing Schedule contains the specific details of how we bill. One Order Item can create multiple Billing Schedules to handle complex scenarios like quantity increases, price changes, or renewals.

> **[Graphic Suggestion: The Golden Path]** A three-step flow diagram: Activated Order → Order Product → Billing Schedule Group → Billing Schedule (the "brain"). Add a callout under Billing Schedule: "Created automatically by the Order to Billing Schedule flow."

## Managing Complex Charge Types: Usage and Milestone Based Charges

Modern businesses use hybrid models that include different types of charges such as Usage or Milestones. RCB augments the Billing Schedule Group data model to support these charges.

**Usage-Based Charges:** These are variable charges (like paying for API calls or data units consumed). When an order is activated with Usage based order products, RCB creates additional records to handle the usage resources included with that product.

| OBJECT | DESCRIPTION |
|:--|:--|
| **Usage Entitlement Account** | A usage entitlement account is a customer instance of the purchased product. Like the Billing Schedule Group, RCB creates this record after an order is activated for Usage based products. The object record includes the billing cycle details for the product, such as billing frequency, billing day of the month, start and end date of billing period and the service. A usage entitlement account has individual usage entitlement buckets for each usage resource. However, while the BSG manages the billing relationship for the usage product, the UEA manages the binding relationship for the usage product. Binding is how usage products can pool their resources together to support complex usage use cases. |
| **Usage Entitlement Bucket** | A usage entitlement bucket represents a wallet that records the credits and debits of a usage resource. If grants are rolled over or renewed, units are added to the bucket balance. When the customer consumes the usage resource, units are debited from the bucket balance. |
| **Usage Entitlement Entry** | A usage entitlement entry represents a transaction entry that records each credit and debit entry for the usage entitlement bucket. |

**Milestone-Based Charges:** Common in professional services, these charges are only triggered when a specific goal is met (like "Project Kickoff" or "Go-Live"). When an order is activated with Milestone based order products, RCB creates additional records to handle the Milestones included with that product.

Billing Milestone Plan acts as a container that groups various payment stages together, while the Milestone Plan Items define the specific timing and financial distribution—either by percentage or flat amount—for each stage. These records can be created in two ways: automatically or manually. For standardized processes, the system generates them automatically when an Order Product is activated, provided it is associated with a Billing Treatment where milestone billing is enabled. Alternatively, for bespoke deals, users can manually create a custom Billing Milestone Plan and associate it directly with the Order Product to override default treatments.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers often fear usage-based pricing because it feels "unpredictable." Position RCB as the solution to that fear. Because the usage data lives on the same platform as the customer record, the customer can see their consumption in real-time. You aren't just selling a "meter" — you're selling transparency. This prevents "bill shock" and builds trust. For customers with extremely complex usage scenarios (billions of records, multi-attribute pricing, near real-time rating), Salesforce has a strategic partnership with m3ter to complement RCB's native Consumption Management. Pull m3ter in early on those deals. |

## Grouping and Organizing with Billing Schedule Groups

In complex enterprise deals, a customer might want one invoice for their London office and a separate one for their New York office — even if they're part of the same Order.

This is where Legal Entities and Billing Profiles come into play:

- **Legal Entity:** Billing from different business units.
- **Billing Profile:** Billing to different addresses or recipients.

In Salesforce Billing, Legal Entities act as the fundamental organizational unit that governs the structure and segregation of Billing Schedule Groups. When an order is processed, the Legal Entity assigned to the Order Product dictates the financial context for all subsequent billing activities, including tax calculation and General Ledger reporting. The Legal Entity ensures that every invoice generated is legally and financially compliant with the specific entity's requirements, preventing the co-mingling of financial data across different branches or subsidiaries of the business.

An Account in Salesforce can support multiple Billing Profiles (commonly known as Billing Accounts), which serve as the central source of truth for an automated billing relationship. Each Billing Profile dictates the "how" and "where" of financial transactions by capturing specific customer preferences—such as payment terms, invoice templates, and preferred payment methods. While Billing Schedule Groups (BSGs) can manage these details at a granular level, the Billing Profile provides a master control record. By associating multiple BSGs with a single Billing Profile, you ensure that all related billing activities inherit the same governing rules, streamlining administration and ensuring consistency across the customer's various projects or service lines.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** A common "gotcha" in the field is a customer saying, "I just want one invoice for everything." While that sounds simple, large enterprises actually need the flexibility to split invoices. When demoing, show how Billing Schedule Groups allow them to be "customer-centric" — we aren't forcing the customer into our structure; we are mapping our billing to their business structure. A real example: National Satellite Service needed to bridge separate bills for satellite and streaming products into a unified model. BSGs are precisely the object that solves this. |

## Key Takeaways

In this unit, you learned how the data model automates the transition from Sales to Finance.

- **The Golden Path:** Data flows from the Order to the Billing Schedule (created by the Order to Billing Schedule flow) to the Invoice.
- **Automation Over Manual Work:** Billing Schedules allow the system to "pre-plan" future revenue, eliminating the need for monthly manual intervention.
- **Four Charge Types:** One-Time, Recurring, Usage-Based (Consumption Management), and Milestone charges give businesses the flexibility to monetize any model.
- **Flexibility is King:** Objects like Billing Schedule Groups and Usage Summaries allow businesses to handle complex, modern revenue models at scale, including support for billing frequency changes at the BSG level.

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| (LO 2.1) | Which object in the Revenue Cloud Billing data model serves as the "parent" that establishes the long-term billing relationship and keeps a customer's history intact, even if they change plans mid-contract? | The Order / **The Billing Schedule Group (BSG)** / The Billing Milestone Plan / The Usage Entitlement Entry |
| (LO 2.2) | When managing usage-based charges, which specific record acts as a "wallet" to record the credits and debits of a usage resource? | Usage Entitlement Account / **Usage Entitlement Bucket** / Billing Treatment / Legal Entity |

---

# Unit 3: Master Invoice Production and Backend Services

In the previous units, we explored the "Why" and the "How" of the data model. Now, it's time to look at the engine in motion. For a Revenue Specialist, understanding how an invoice is actually produced — and the backend services that power it — is the difference between a "good" demo and a "winning" demo.

When we talk about invoice production in Revenue Cloud Billing, we are talking about moving from a plan (the Billing Schedule) to a legal demand for payment (the Invoice).

## The Mechanics of Invoice Production

The system provides three primary ways to generate invoices, depending on the business need. Think of these as different "gears" in the billing engine:

- **The Billing Preview:** Before creating an actual invoice, users can run a preview. This is a critical safety net. It allows Finance teams to see exactly what the system plans to bill without actually creating a permanent record. This is especially valuable for customer service inquiries and request for proforma invoices.
- **"Bill Now" Functionality:** This is the manual "override." If a customer needs an invoice immediately — perhaps for a one-time service or a mid-month request — a user can trigger "Bill Now" directly from the Account.
- **The Billing Batch Scheduler:** This is the automated high gear. It allows the system to run in the background, picking up thousands of Billing Schedules and converting them into Invoices based on a configured frequency.

## Powering the Backend: Scaling and Integration

While the user sees an invoice, the Salesforce Platform is doing heavy lifting behind the scenes.

- **Data Processing Engine (DPE):** In RCB the Data Processing Engine (DPE) acts as the high-performance orchestration layer that transforms complex billing schedule data into accurate invoices. While traditional billing systems often rely on rigid, pre-defined batch jobs, the DPE allows for highly scalable and customizable data aggregation. When the invoice generation process is triggered—either through a scheduled run or a manual "Bill Now" action—the system invokes a specific DPE definition. This engine queries relevant records, such as Billing Schedules, Usage Entitlement Accounts and Milestone Plan Items, applies logic to calculate the billable amounts creating Billing Period Items. The DPE creates invoice records and groups like BPIs into Invoice Lines.
- **Billing Period Items** serve as the granular execution records that bridge the gap between a Billing Schedule and the final Invoice. While a Billing Schedule outlines the broad plan for how an Order Product should be billed over time, the Billing Period Item represents the specific, individual charge.
- **Tax Adapter:** Tax is complicated and ever-changing. While RCB does have standard tax tables for simple tax use cases, most customers will choose to utilize the tax adaptor. The Tax Adaptor allows customers to connect RCB's high scale bill run directly to the external tax engine of their choice (like Avalara or Vertex). The output of the tax adaptor is stored in the Invoice Line Taxes object and linked directly to the corresponding Invoice Line.
- **Document Generation:** The transition from raw invoice data to a customer-facing PDF is handled by the Document Generation Service. Unlike traditional systems that may require third-party add-ons, RCB leverages native Document Templates to define the layout, branding, and data mapping for the final document. Once the Data Processing Engine has finalized the Invoice and Invoice Line records, the actual PDF creation is triggered automatically.

This process utilizes Omnistudio Document Generation capabilities to merge account, contact, and invoice data into predefined Word or HTML-based templates. When the generation process begins, the system creates a Document Generation Process record to track the progress; once this status moves to "Success," the finalized PDF is attached to the Invoice record. This architecture allows administrators to easily customize invoices—such as adding company logos or specific legal disclosures—using a "low-code" approach via the Document Builder, ensuring that the final output is professional, accurate, and ready for distribution.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a customer asks if Salesforce can handle their volume, point to the Data Processing Engine and High Scale Billing. Because RCB is native to the Salesforce Platform, we're not sending data back and forth to a separate tool. We're using the same high-scale infrastructure that powers the world's largest CRM — and now backing it with documented, signed-off release notes. |

## The Downstream Output: What Happens After the Run?

Once the billing engine finishes its work, it leaves behind a clear trail of financial records. Knowing these objects helps Revenue Specialists explain the "Source of Truth" to a CFO or Finance team:

- **Billing Period Items:** The ready to bill details of a Billing Schedule that were processed in this run.
- **Invoices:** The header record representing the total amount due from the customer.
- **Invoice Lines:** The individual line items which aggregate Billing Period Items (e.g., "Software Subscription — June").
- **Invoice Tax Lines:** The specific tax breakdown for each line item, calculated via the Tax Adapter.

## Securing the Operation on the Salesforce Platform

Trust is our number one value. By running billing on the Salesforce Platform, organizations benefit from enterprise-grade security:

- **Encryption:** Protecting sensitive financial data at rest and in transit.
- **Audit Trails:** Knowing exactly who triggered a "Bill Now," when a Batch Run was completed, or when a Dispute action was invoked.
- **Single Identity:** Users don't need a separate login for a billing tool — their Salesforce credentials provide secure, role-based access.
- **Compliance:** The Tax Adapter integration and Invoice Tax Line objects ensure that billing outputs are legally compliant across jurisdictions — a critical proof point for global companies.

## Key Takeaways

In this unit, you learned how to move from a Billing Schedule to a finalized Invoice — and the backend services that make it scale.

- **Multiple Gears:** Use Billing Previews for accuracy, "Bill Now" for speed, and the Batch Scheduler for scale, with holiday and weekend exclusions for smarter scheduling.
- **High Performance:** The DPE and Consumption Management handle complex usage at scale; the Tax Adapter handles global compliance; and the Document Generation Service handles document delivery.
- **Agentic Upgrades:** High Scale Billing, Refunds Orchestration, and Dispute Management's automated resolution actions make invoice production more powerful and more agentic.
- **Platform Power:** Running on Salesforce means billing operations are as secure, scalable, and trusted as your CRM.

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| (LO 3.1) | What is the role of the Data Processing Engine (DPE) in the invoice generation process? | It acts as an external tax engine to calculate global compliance fees. / **It serves as the high-performance orchestration layer that transforms complex billing schedule data into accurate invoices and invoice lines.** / It is a manual override tool used by sales agents to change product prices after an order is activated. / It replaces the need for the Salesforce Platform by moving data to an external third-party server for processing. |
| (LO 3.2) | When a company needs to handle complex, ever-changing global taxes, how does Revenue Cloud Billing (RCB) typically manage this? | RCB requires the manual entry of tax rates on every individual Invoice Line. / The system uses a rigid, pre-defined batch job that cannot be changed. / **RCB utilizes a Tax Adapter to connect directly to external tax engines like Avalara or Vertex, storing the results in Invoice Line Taxes.** / The Document Generation Service automatically calculates taxes based on the company's logo and branding. |

---

*Source: pulled from Mike Aaron's "Copy of Module 1 v2" Google Doc on 2026-05-11. Validated against the latest Salesforce Help portal (Billing area). Per-claim citation log: `docs/trailhead-l2-review/module-1-v2-262-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
