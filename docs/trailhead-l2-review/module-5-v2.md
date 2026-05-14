# Module 5: Payments, Collections, and the Billing Collections Management Subagent

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; grounded against the 262 Summer '26 Help portal capture covering Billing and Agentforce for Revenue Management)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Salesforce Help portal (Billing area `ind.billing_*`, Agents area `ind.rev_agent_*`), project metadata (`.sfdx/tools/sobjects/standardObjects/`), and the ARM Billing L2 Outline (Mike's revised LOs). See `modules-4-5-262-lo-validation-report.md` for the per-claim citation log.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.
**Style notes for editorial:** This draft bolds product object names (Salesforce Payments, Payment Gateway Adapter, etc.) for technical clarity. That matches the convention established across Modules 1, 2, 3, and 4 of the L2 mix.

---

**Badge Description:** Configure payment gateways and retry rules, automate collections and dunning workflows, and apply the Billing Collections Management subagent to keep accounts healthy and DSO low.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Configure Payment Gateways, Methods, and Payment Retry | Quiz | |
| 2 | Automate Collections, Disputes, and Customer Self-Service for Payments | Quiz | |

## AI Usage

Did you use AI to help you write this badge content?

- [x] Yes
- [ ] No

If yes, what AI tool did you use? Gemini and Slackbot + TH Writer Gem and TH PMM Grader Gem

## Suggested Category

- **Role**: Sales Professional
- **Level**: Intermediate
- **Trailhead Products/Features**: Agentforce Revenue Management
- **Industry**: None
- **[For internal use only: Primary Product/Feature**: Agentforce Revenue Management **]**

## Supporting Documents

- [ARM Billing L2 Outline Proposal — FY27](https://docs.google.com/spreadsheets/d/1rEKPXnNWZ-X_OC5PD9XSeMnBONZsY8NnLiaQF3RAmR8/edit?gid=670679088#gid=670679088)

---

# Unit 1: Configure Payment Gateways, Methods, and Payment Retry

## Learning Objectives

After completing this unit, you'll be able to:

- Establish integrations between the billing system and payment gateways to enable secure payment processing.
- Extend payment processing to additional third-party gateways through a payment gateway adapter pattern.
- Set up **Payment Runs** to sweep posted invoices automatically against connected gateways.
- Implement a **Payment Retry** strategy that optimizes recovery rates by gateway error category.

Modules 1 through 4 covered the contract, the data model, the rating pipeline, and invoice production. Module 5 closes the lifecycle: getting paid. Unit 1 starts with how payment gateways connect, how retry rules handle the inevitable failures, and how Payment Batch Runs sweep payments against posted invoices on a cadence.

## Configure Native Gateways Through Salesforce Payments

Agentforce Revenue Management Billing supports two **native payment gateways**: **Salesforce Payments** and **Adyen**. "Native" means the integration is built in — no developer work, no Apex adapter class. Customers can create a new Salesforce Payments merchant account or connect an existing Adyen merchant account through the guided setup.

The setup flow runs through a guided configuration:

1. From the Setup menu, find **Billing Settings** and enable Payments for the org.
2. Set up an Experience Cloud site that will host the payment surfaces customers interact with.
3. Use the guided setup to create a Salesforce Payments merchant account (or connect an existing Adyen one) and define the payment methods you want to accept.

Native gateway integration is the path of least resistance for customers who haven't pre-committed to a processor. Customers who already use Adyen can connect their existing merchant account. Customers who use a different processor go to the Payment Gateway Adapter path described next.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** "Native" is the word that carries weight in a technical eval. With Salesforce Payments or Adyen, there's no Apex adapter to write, no class to maintain, and setup is guided configuration rather than a development project. When a customer asks "how much engineering work is the payment integration?" the answer for the two native gateways is essentially none. The Payment Gateway Adapter (next section) is the answer for any other processor — and even that is a documented, repeatable pattern. |

## Configure Third-Party Gateways Through the Payment Gateway Adapter

For customers who use a payment processor that isn't Salesforce Payments or Adyen, the **Payment Gateway Adapter** pattern lets them bring their own. The mechanism is intentionally similar to the Tax Engine Adapter pattern from Module 2 — same shape, different domain.

The pieces:

- **PaymentGatewayProvider** — the SObject record that points at the Apex adapter class.
- **Apex adapter class** — the developer-written implementation that handles authentication, payment requests, refunds, and notifications. Built on Salesforce's Commerce Payments namespace.
- **Named Credential** — secures and authenticates the API callouts to the third-party gateway.
- **Salesforce Site** — exposes a webhook endpoint so the third-party gateway can push notifications back into Salesforce.

The setup involves obtaining the adapter class from the gateway provider (or from AppExchange), creating the PaymentGatewayProvider record with that adapter referenced, and configuring a webhook URL in the third-party gateway's standard notification transport settings. The resulting connection processes payments, issues refunds, and supports multiple payment methods (credit cards, ACH, SEPA, BACS, BECS) through the `tokenizePaymentMethod` API.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a customer says "we use [some other processor]," the Payment Gateway Adapter pattern is what to point at. The architectural answer is identical to the Tax Engine Adapter customers saw in Module 2 — a Provider record holds a reference to an Apex adapter class. If their processor has an AppExchange adapter, the integration is mostly configuration. If they need a custom adapter, the Apex interface is documented. Either way, Salesforce isn't trying to replace their gateway — it's giving them a documented integration point. |

## Set Up Payment Runs

A **Payment Run** sweeps payments against posted invoices on a cadence. Configure one through a **Payment Scheduler** — a Billing Batch Scheduler with Job Type = Payment. The pattern matches Module 4's Bill Run / Invoice Batch Run: a configuration record (the Scheduler) creates the execution records (the Payment Runs).

You set up a Payment Scheduler from the App Launcher: find **Billing Batch Schedulers**, click **New Payment Scheduler**, and configure the cadence (Once, Daily, or Monthly). At the scheduled start time, the system creates a Payment Run record and processes the relevant payment schedule items in parallel.

The matching criteria determine which payment schedule items get processed. By default, the run processes all payment schedule items with a target payment date at or before the job run date. Customers with more specific needs can configure custom matching criteria by Payment Schedule Item with a Payment Run Matching Value.

The Payment Run record itself works like the Invoice Batch Run from Module 4: a parallel-processing engine that processes payment schedule items, applies them to invoices based on the configured payment application level, and reports a status (Completed or Failed) with detailed subtype tracking.

> The formal product name behind "Payment Run" is **Payment Batch Run**. Both names refer to the same record. The Trailhead-facing voice across the L2 mix uses Payment Run; the body content cites Payment Batch Run once for grounding when admins are looking at the underlying record type.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Payment Runs are the proof point for customers worried about manual collection effort at scale. Schedule the run, configure the retry rules, and the system sweeps payments against posted invoices automatically. The collections rep doesn't manually run retries — they handle the exception cases the rules can't recover. That's the right division of labor between automation and human judgment. |

## Implement a Payment Retry Strategy

Payment processors fail for many reasons — insufficient funds, expired cards, gateway timeouts, fraud holds. A **Payment Retry** strategy automates the recovery process so finance teams don't manually re-run failed payments. The configuration has two layers:

- **Payment Retry Rule Set** — the parent record. Defines default values for retry interval type, interval unit, and interval values that all rules in the set inherit.
- **Payment Retry Rule** — the child record, scoped to a specific gateway error category (with an optional error code). Can override the parent's default values.

Each rule defines a **retry interval type**:

- **Fixed** — consistent time period between retry attempts. Example: retry every 5 days for up to 3 attempts.
- **Staggered** — varied intervals between retry attempts. Example: retry on day 2, day 4, and day 6 with staggered values `2,4,6`.

The interval unit can be **Hours**, **Minutes**, or **Days**. The maximum retries on Fixed cap at 10. The maximum interval value caps at 60.

Three operational rules to know:

- A Payment Retry Rule Set can be marked as the default for the org. Only one default is active at a time.
- Rules within a set inherit the set's defaults, but each rule can override them for its specific error category.
- The **Use Alternate Payment Method** option, when enabled, tries an alternate payment method on the final retry attempt — a useful recovery mechanism when one payment method has clearly stopped working.

After at least one default Payment Retry Rule Set is configured, the admin enables Retry Failed Payments on the Billing Settings page. From that point, the Payment Run picks up failed payments according to the rules and retries them automatically.

## Key Takeaways

**Salesforce Payments** and **Adyen** are the two native payment gateways — built-in integrations with no Apex adapter required. Additional third-party gateways integrate through the **Payment Gateway Adapter** pattern (`PaymentGatewayProvider` + Apex adapter class). A **Payment Scheduler** creates **Payment Runs** that sweep payments against posted invoices on a cadence — same shape as the Invoice Batch Run from Module 4, scoped to payment processing instead of invoice generation. The **Payment Retry** strategy (configured through Payment Retry Rules and Payment Retry Rule Sets) automates recovery of failed payments by gateway error category with Fixed or Staggered retry intervals.

## Resources

- [*Salesforce Help:* Set Up Payment Features for Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_setup_salesforce_payments_features.htm&type=5)
- [*Salesforce Help:* Set Up Third-Party Payment Gateways](https://help.salesforce.com/s/articleView?id=ind.billing_setup_third_party_payments.htm&type=5)
- [*Salesforce Help:* Set Up Payment Retry Rules](https://help.salesforce.com/s/articleView?id=ind.billing_setup_payment_retry_rules.htm&type=5)
- [*Salesforce Help:* Schedule Payment Batch Runs to Process Payments](https://help.salesforce.com/s/articleView?id=ind.billing_payment_runs_schedule.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Configure native and third-party gateways.** | A customer wants to use a processor that isn't Salesforce Payments or Adyen. Which architectural pattern supports this? | They must migrate to Salesforce Payments or Adyen — no other processors are supported. / **They configure a Payment Gateway Adapter by creating a PaymentGatewayProvider record that references an Apex adapter class implementing the Commerce Payments namespace.** / They configure Salesforce Payments with custom credentials. / They use a third-party app from AppExchange instead of the native Billing engine. |
| **Implement a Payment Retry strategy.** | A customer wants to retry failed payments on day 2, day 4, and day 6 after the original failure. What retry interval type supports this pattern? | Fixed retry interval with max retries = 3 / **Staggered retry interval with interval values 2,4,6** / Custom retry rule with Apex / Manual retry through the Payment Operations User permission |

---

# Unit 2: Automate Collections, Disputes, and Customer Self-Service for Payments

## Learning Objectives

After completing this unit, you'll be able to:

- Set up the **Self-Service Billing Portal**'s payment surface for customer-managed payments and updates.
- Execute automated **Dunning** workflows that reduce **Days Sales Outstanding (DSO)** by deploying tiered communications across multiple channels.
- Manage **Billing Disputes** — capture, validate, and resolve common billing requests from the Self-Service Portal or directly through the Collections workflow.
- Articulate the Payments and Collections capability's impact on **Days Sales Outstanding (DSO)** for a Finance audience.
- Apply the collections-management subagent to assess account health and recommend dunning strategies through conversational interaction.

> **Agent naming note:** The body content below uses **Subagent: Billing Collections Management** (per the current 262 Help portal naming under "Agentforce for Revenue Management"). Pending Annie + Mike alignment on subagent vs. "Billing Agent" vocabulary, names may be revised. Content stays the same.

Unit 1 handled payment processing. Unit 2 handles what happens when payments don't arrive on time. Collections and Disputes are the operational heart of recovering revenue without burning customer relationships. The Self-Service Billing Portal, the Dunning Orchestration capability, and the collections-management subagent are the tools that make that recovery scalable.

## Set Up the Self-Service Billing Portal Payment Surface

Module 4 covered the **Self-Service Billing Portal** as the viewing surface. Module 5 covers the same portal as the *payment* surface. The same customer can use the same portal to view invoices and pay them, with consistent design and authentication. The payment-side capabilities include:

- **Pay Invoices from the Portal** — customers log in, view unsettled invoices, and pay through supported payment methods. The Home tab shows settled, partially settled, and unsettled invoices.
- **Pay Now Link** — a shareable, signed payment URL that customers can use without logging in. Generated by cloning the **Generate Payment Link** flow and configuring the business account ID and payment settings. Customers pay as a guest with a new payment method; the resulting payment is automatically associated with the correct business account.
- **Saved Payment Methods** — customers can save a payment method for future use, supporting credit cards, debit cards, ACH, SEPA, BACS, BECS, digital wallets, buy now pay later (BNPL), and additional methods depending on the gateway.

The Pay Now Link is particularly useful for invoice email delivery scenarios — the invoice email can include the link, the customer clicks once, completes payment, and finance has cash in the bank without a portal login or support call.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The Pay Now Link is the highest-leverage feature in the Self-Service Portal. It removes the friction of portal authentication from the payment path. For customers with a Days-Sales-Outstanding (DSO) problem, every day of friction matters. Sending an invoice email with an embedded Pay Now Link is the fastest path from "invoice generated" to "cash in the bank." |

## Execute Automated Dunning Workflows

**Dunning** is the practice of sending a sequence of escalating reminders to a customer with overdue invoices. Agentforce Revenue Management Billing supports dunning at two levels of automation:

- **Dunning Emails** — out-of-the-box email reminders that collections reps schedule on a recurring basis. Templates are configurable for tone and content.
- **Dunning Orchestration** — the full automated lifecycle. Uses **Dynamic Revenue Orchestrator (DRO)** templates to orchestrate the entire dunning sequence: when to email, when to schedule a follow-up call, when to escalate, when to send SMS reminders, when to involve a manager.

The Dunning Orchestration setup runs through Salesforce Go and installs the **Dunning Orchestration Solution** data pack — a pre-built fulfillment workspace plus three email templates. After installation, the Collections and Recovery Specialist can initiate dunning orchestration on a Collection Plan. The system follows the configured orchestration steps automatically, with each step executing at the scheduled time.

Marketing Cloud can extend the dunning process further — segmentation by customer health, scheduled reminder calls, and SMS messaging beyond email. The combination of Dunning Orchestration + Marketing Cloud is the answer for customers who want multi-channel dunning campaigns rather than email-only.

The data model underneath dunning has three records worth knowing:

- **Collection Plan** — the per-account record tracking all overdue invoices and the dunning sequence applied to them.
- **Collection Plan Item** — one per overdue invoice. The granular record collections reps work in.
- **Payment Promise** — the customer's commitment to pay, with the agreed date and amount. Triggers a Payment Schedule that the Payment Run will pick up automatically.

## Manage Billing Disputes

**Billing Dispute Management** centralizes inquiries and disputes into a single automated system. The capability runs through:

- **Unified Catalog** service process templates — pre-built workflows for the most common dispute types: Suspend Billing, Update Bill To Contact on Invoice, Extend Invoice Due Date, Incorrect Invoice Charge, and Other Billing Inquiries.
- **Self-Service intake** — customers raise disputes directly from the Self-Service Billing Portal's Help Center tab. Each submission creates a Case the collections or service rep can resolve.
- **Assisted Case Creation** — internal billing specialists initiate cases on behalf of customers directly from the Billing app. (This adds an internal-facing parallel to the customer-facing self-service flow.)
- **Automated Resolution Actions** — the Resolve Case quick action runs the appropriate billing workflow automatically. For example, the Suspend Billing template auto-runs the suspension; the Extend Invoice Due Date template extends the due date; the Incorrect Invoice Charge template issues a credit memo.

The customer experience is straightforward: log in to the portal, open the dispute template that matches the situation, submit. The service rep sees the case immediately, can validate the details, and resolves it through the Resolve Case action. Both the customer and the rep can track status from the Cases tab. Status updates flow to the customer through automated email notifications.

The architectural integration with Collections matters: disputes affect the Collection Plan, the dunning strategy, and the collections-management subagent's recommendations. A customer with an open dispute on an invoice shouldn't receive an escalation email — and the subagent's recommendation accounts for that.

## Articulate the DSO Impact for a Finance Audience

**Days Sales Outstanding (DSO)** is the most common single metric finance leaders track for accounts receivable performance. DSO measures the average number of days between invoice issuance and payment receipt. Lower DSO means faster cash conversion, healthier working capital, and less time spent on collections.

Each capability in Modules 4 and 5 lowers DSO through a specific mechanism:

- **Automated Invoice Batch Runs** (Module 4) — invoices land on time, not delayed by manual generation.
- **Send Invoices Through Email** (Module 4) — customers receive invoices the day they're generated.
- **Pay Now Link** (this unit) — removes friction between invoice receipt and payment, often pulling DSO in by several days.
- **Payment Retry strategy** (Unit 1) — recovers failed payments that would otherwise sit in collections for weeks.
- **Payment Runs** (Unit 1) — collects payments automatically rather than waiting for manual handling.
- **Dunning Orchestration** (this unit) — escalates aging invoices systematically rather than relying on collections rep memory.
- **Collections-management subagent** (this unit) — gives collections reps an at-a-glance view of account health and a recommended next action, compressing investigation time.
- **Self-Service Disputes** (this unit) — resolves common disputes through automated workflows rather than letting them age while a rep investigates manually.

The combined impact pulls DSO in significantly. In Finance conversations, position the capabilities as a coordinated stack rather than a list of features. Each one chips away at the time between invoice and cash; together they compress the cycle measurably.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a CFO asks "what's the business case?", lead with DSO. It's the single metric every Finance organization tracks, and the Module 4 + Module 5 capabilities directly compress it. Pair the DSO story with a Reduce Bad Debt story (Dunning Orchestration + the collections subagent prevent invoices from aging into write-off territory) and an Operational Efficiency story (collections reps focus on judgment cases instead of data assembly). Three angles, one conversation. |

## Apply the Collections-Management Subagent

The **Subagent: Billing Collections Management** is one of seven subagents under the **Agentforce for Revenue Management** agent suite. It's the conversational interface that lets collections teams assess account health and choose the next move without navigating through multiple records.

The subagent's API name is `BillingCollections`, and it exposes two named agent actions:

- **Get Account Billing Summary** — produces an at-a-glance view of an account's financial standing, including outstanding balances, high-risk invoice counts, late payment history, and open disputes.
- **Get Dunning Strategy** — analyzes a Collection Plan's prior customer communications, payment history, and open disputes to recommend the most effective dunning strategy for that account.

Two sample interactions that show how the subagent fits a collections rep's workflow:

> "What is the billing health summary for the Acme account?" → **Get Account Billing Summary**: The agent summarizes outstanding balances, high-risk invoice counts, and historical payment trends.

> "What dunning strategy should I use for collection plan #CP-101?" → **Get Dunning Strategy**: The agent analyzes the collection plan along with prior customer communications, payment history, and open disputes to recommend the most effective dunning strategy to expedite payment recovery.

The subagent requires the Agentforce Revenue Management Billing license with the Agentforce Employee Agent add-on, and the user needs both the Billing Collections and Recovery Specialist permission sets. It's available to authenticated users in Lightning Experience — Experience Cloud customer-facing access isn't yet available for this subagent.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The collections-management subagent is the way to reframe a collections team from a back-office function to a strategic function. Without the subagent, a collections rep spends hours per account piecing together the picture from invoice records, communications history, and dispute records. With the subagent, they ask a question and get an action-oriented recommendation. The pitch isn't "AI replaces the rep" — it's "AI replaces the data assembly so the rep can focus on customer judgment." |

## Key Takeaways

The **Self-Service Billing Portal** payment surface includes the **Pay Now Link** for the lowest-friction path from invoice to cash. **Dunning Orchestration** automates the full overdue-invoice escalation lifecycle using Dynamic Revenue Orchestrator templates, with multi-channel support through Marketing Cloud. **Billing Dispute Management** centralizes common dispute types into self-service templates with automated resolution actions. Together, these capabilities directly reduce **Days Sales Outstanding (DSO)** — the metric finance organizations track most closely. The **Subagent: Billing Collections Management** under the Agentforce for Revenue Management suite exposes two named actions — **Get Account Billing Summary** and **Get Dunning Strategy** — that compress investigation time for collections reps and recommend the next dunning step.

## Resources

- [*Salesforce Help:* Manage Collections for Accounts in Billing](https://help.salesforce.com/s/articleView?id=ind.billing_collections.htm&type=5)
- [*Salesforce Help:* Set Up Orchestrated Dunning for Collections](https://help.salesforce.com/s/articleView?id=ind.billing_dunning_orchestration_enable.htm&type=5)
- [*Salesforce Help:* Subagent: Billing Collections Management](https://help.salesforce.com/s/articleView?id=ind.rev_agent_topic_billing_collections_management.htm&type=5)
- [*Salesforce Help:* Manage Billing Disputes](https://help.salesforce.com/s/articleView?id=ind.billing_manage_disputes.htm&type=5)
- [*Salesforce Help:* Generate Pay Now Links for Business Accounts](https://help.salesforce.com/s/articleView?id=ind.billing_generate_pay_now_payment_links_for_business_accounts.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Set up the Self-Service Portal's payment surface.** | A finance team wants to maximize the speed from invoice email to cash collection. Which feature best supports this? | The customer must log in to the Self-Service Portal to pay each invoice. / Email reminders configured through Dunning Orchestration. / **The Pay Now Link — a shareable URL that lets customers pay without logging in to the portal.** / Manual payment processing through the Payment Operations User permission. |
| **Apply the collections-management subagent.** | A collections rep asks the subagent "What dunning strategy should I use for collection plan #CP-101?" Which of the subagent's two named actions answers this? | Get Account Billing Summary / **Get Dunning Strategy** / Get Invoice Line Records / Get Usage Details |

---

# Appendix: Open Questions and Parking Lot

## Open questions for Mike + Annie

**Agent naming** (open — Annie's call). Module 5 uses "Subagent: Billing Collections Management" per the current 262 Help portal naming under "Agentforce for Revenue Management." Mike prefers "Billing Agent" universally. Brian has flagged this for Annie since new Agentforce materials apparently use subagent + superagent vocabulary. Body content stays the same regardless — only the name swaps once direction is set.

**~~"Smart Retry" branding~~ RESOLVED.** Mike's second-pass review confirmed: use **Payment Retry**, not "Smart Retry." The body draft above uses "Payment Retry" as the strategy framing and cites **Payment Retry Rules** / **Payment Retry Rule Sets** as the underlying configuration records.

**~~"Payment Batch Run" naming~~ RESOLVED.** Mike confirmed: use **Payment Run** globally as the seller-facing term. The formal record name **Payment Batch Run** is cited once in the body for grounding when admins look at the underlying record type, matching the Bill Run / Invoice Batch Run dual-name pattern from Module 4.

## Topics deliberately routed elsewhere

For audit completeness:

- **Module 4 referenced Billing Disputes briefly.** Disputes belong in Module 5 because they route through the Collections workflow. Module 5's LO 2.3 owns the full dispute coverage. Module 4 doesn't repeat it.
- **Self-Service Portal viewing surface.** Covered in Module 4 LO 2.3. Module 5's LO 2.4 owns the *payment* surface of the same portal. The split is deliberate — viewing belongs with invoice production; paying belongs with payment processing.

## Cross-module observations

The **Subagent: Billing Collections Management** referenced in Unit 2 is one of seven subagents under the **Agentforce for Revenue Management** suite documented across the L2 mix:

- Module 1 v2 references Subagent: Invoice Line Explanation + Subagent: Billing Inquiries + the Agentforce for Billing Service Assistance Agent.
- Module 3 v2 references Subagent: Consumption Management.
- Module 4 v2 covers Subagent: Invoice Line Explanation in depth.
- Module 5 v2 (this module) covers Subagent: Billing Collections Management in depth.

All four modules now use **Agentforce for Revenue Management** as the parent agent name — pending Mike's confirmation per the open question in `modules-4-5-262-lo-validation-report.md`.

---

*Prepared by Brian Galdino with AI assistance; grounded against the latest Salesforce Help portal (Billing area, Agentforce for Revenue Management area). Per-claim citation log: `docs/trailhead-l2-review/modules-4-5-262-lo-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
