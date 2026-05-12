# Module 4: Invoicing and the Invoice Line Explanation Subagent

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; grounded against the 262 Summer '26 Help portal capture covering Billing and Agentforce for Revenue Management)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Salesforce Help portal (Billing area `ind.billing_*`, Agents area `ind.rev_agent_*`), project metadata (`.sfdx/tools/sobjects/standardObjects/`), and the ARM Billing L2 Outline (Mike's revised LOs). See `modules-4-5-262-lo-validation-report.md` for the per-claim citation log.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.
**Style notes for editorial:** This draft bolds product object names (Billing Arrangement, Invoice Batch Run, etc.) for technical clarity. That matches the convention established across Modules 1, 2, 3, and 5 of the L2 mix.

---

**Badge Description:** Configure billing arrangements, drive invoice production at scale, and apply the Invoice Line Explanation subagent to make complex charges legible to your customers.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Configure Billing Arrangements and Drive the Invoice Batch Run | Quiz | |
| 2 | Manage Invoice Delivery, Credit Memos, and the Invoice Line Explanation Subagent | Quiz | |

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

# Unit 1: Configure Billing Arrangements and Drive the Invoice Batch Run

## Learning Objectives

After completing this unit, you'll be able to:

- Configure billing arrangements to allocate invoice amounts across multiple billing accounts.
- Identify the cadence fields that drive when the bill run picks up a billing schedule.
- Map how the bill run produces invoices from ready-to-bill billing schedules.
- Analyze the automated conversion of Debit Memo Lines into Invoice Lines, driven by `NextBillingDate` on the Debit Memo record.

Modules 1 through 3 set up the contracts, the data model, and the rating pipeline. Module 4 turns to the part of the lifecycle finance teams care about most: actually producing the invoice. Unit 1 covers the configuration that determines *who gets billed for what* and the mechanics of the recurring batch process that produces invoices at scale.

## Configure Billing Arrangements to Allocate Charges

In simple deals, the customer who owns a service is the customer who gets the bill. In enterprise deals, that's rarely the case. A parent account might own three subsidiaries that should each receive a portion of one invoice. A single shared asset might split across departments. A subscription might be paid by a partner rather than the end user. **Billing Arrangements** are how Agentforce Revenue Management Billing handles these patterns without requiring the seller to re-key each scenario manually.

The Billing Arrangement data model has three terms worth knowing:

- **Owning Account** — the account that uses or owns the service or asset.
- **Billing Account** — the account that receives the bill.
- **Billing Arrangement** — the configuration record that decides whether the total amount is invoiced to the owning account, a different billing account, or split among multiple billing accounts. Carries one or more **Billing Arrangement Lines**.
- **Billing Arrangement Line** — the billing account, billing profile, and percentage of the billing amount to be invoiced. Each line results in a separate invoice addressed to the selected billing account.

The relationship is straightforward: a Billing Arrangement carries Billing Arrangement Lines. Each Line carries a billing account and a percentage. When the Invoice Batch Run processes a Billing Schedule Group with a related Billing Arrangement, the system generates one invoice per Line. If a Billing Arrangement has a 100% allocation to a single account, the system generates one invoice. If it has multiple Lines with various percentages, the system generates a **split invoice** for each Line.

The billing profile selected on each Line takes precedence over the Billing Schedule Group's default profile. That means each split invoice can carry its own payment terms, bill-to contact, billing address, and invoice template — without forcing the seller to override fields at the BSG level.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** "**Split Billing**" is the seller-facing concept; "**Billing Arrangements**" is the actual product name and the underlying object set (`BillingArrangement` + `BillingArrangementLine`). Both terms show up in the Help docs. Use Split Billing when explaining the customer benefit, Billing Arrangements when explaining the configuration. |

A few operational details that matter in field deals:

- **Post, void, or delete behavior** — all split invoices from the same Billing Arrangement share the same post/void/delete fate. If you post one, you post them all.
- **Amend, renew, cancel** — the Billing Arrangement configuration persists across the transaction lifecycle. Percentage allocations and account assignments stay intact even when the underlying contract changes.
- **Suspend billing** — if the BSG or any billing account in the Arrangement is suspended, all the accounts in the Arrangement defer their billing during the suspension window.
- **Write-off** — if any split invoice is written off, the others can't be voided.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers sometimes ask "I just want one invoice for the whole account" — and that's fine, it's a 100% Billing Arrangement Line. The deeper proof point is the opposite case: enterprises with subsidiaries, departments, or cross-charged services need split invoices that respect each billing account's payment terms, addresses, and templates. Billing Arrangements give them that without forcing seller-side workarounds. |

## Describe Bill Cycle Day and Next Billing Date

Two date fields drive when the Invoice Batch Run picks up a Billing Schedule:

- **Bill Cycle Day** (`BillDayOfMonth` on `BillingSchedule`, `BillingScheduleGroup`, and `UsageEntitlementAccount`) — the day of the month the customer is configured to be billed. Most commonly 1, 15, or the order anniversary day. Inherited from the billing profile when the BSG is generated.
- **Next Billing Date** (`NextBillingDate` on `BillingSchedule` and `DebitMemo`) — the next date on which the system expects to bill this schedule. The Invoice Batch Run uses Next Billing Date to decide whether the schedule is ready to bill.

The Bill Cycle Day governs the *cadence*. The Next Billing Date governs *eligibility for the next run*. After an invoice is produced, the system advances the Next Billing Date by one billing period — so the schedule will be re-eligible the following cycle.

## Map the Invoice Batch Run

The recurring engine that turns Billing Schedules into Invoices is the **Invoice Batch Run** — also called the **Bill Run** in seller-facing conversation. The configuration record is the **Invoice Scheduler** (which Module 2 covered in detail). At run time, the system creates an Invoice Batch Run record that processes Billing Schedules in parallel through these stages:

1. Identify Billing Schedules where Next Billing Date is at or before the target date and the schedule is Ready for Invoicing.
2. Assign each eligible schedule a grouping key.
3. Process schedules simultaneously across multiple threads.
4. Calculate taxes — estimated taxes for draft invoices, actual taxes for posted invoices.
5. Generate Invoices and Invoice Lines.
6. Update Next Billing Date and related fields on the underlying Billing Schedules and BSGs.
7. Summarize the run on the Invoice Batch Run record.

Each grouping key is processed independently, so completed invoices are available for review as soon as they're generated — finance teams don't have to wait for the entire batch to complete. The Invoice Batch Run record carries a status (Completed or Failed) and a status subtype that reflects which stage the run is currently in (Billing Schedules Filtering In Progress, Invoice Generation In Progress, and so on). Status subtypes give Billing Operations users visibility into a run mid-flight, which matters when a high-volume run is in progress and finance wants to know how far along it is.

## Describe How Debit Memos Convert to Invoice Lines

A **Debit Memo** is what you issue when you want to add charges to a customer that weren't part of the original order — late payment fees, cancellation fees, or undercharged amounts you need to recover. When **Debit Memo Lines** are converted to Invoice Lines, the balance of the related Invoice increases.

The connector between a Debit Memo and the Invoice Batch Run is the Debit Memo's own `NextBillingDate`. The system uses this field to decide when the Debit Memo Lines flow into the next invoice. This makes Debit Memos schedule-aware — you can issue a Debit Memo today and have it land on next month's invoice cycle automatically, without manual reconciliation.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Debit Memos answer the customer question "what about charges we discover after the contract is signed?" The standard pattern is late fees and adjustment charges. Position Debit Memo + Next Billing Date together: the seller doesn't have to manually thread the new charge into a specific invoice — the system schedules it. |

## Key Takeaways

**Billing Arrangements** define how a transaction's billable amount is split across billing accounts. Each Billing Arrangement Line produces a separate invoice with its own billing profile and percentage allocation. **Bill Cycle Day** (`BillDayOfMonth`) and **Next Billing Date** (`NextBillingDate`) drive when the Invoice Batch Run picks up a Billing Schedule. The **Invoice Batch Run** processes ready-to-bill schedules in parallel through identification, grouping, tax calculation, invoice generation, and summarization stages. **Debit Memos** carry their own `NextBillingDate` so Debit Memo Lines flow into the next invoice automatically.

## Resources

- [*Salesforce Help:* Manage Billing Arrangements](https://help.salesforce.com/s/articleView?id=ind.billing_billing_arrangements.htm&type=5)
- [*Salesforce Help:* Invoice Batch Run Process](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_batch_run.htm&type=5)
- [*Salesforce Help:* Manage Debit Memos in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_debit_memo.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Configure Billing Arrangements.** | An enterprise account has three subsidiaries. The customer wants each subsidiary to receive its own invoice for 30%, 30%, and 40% of the total billable amount. What object structure supports this? | A single Billing Schedule per subsidiary / **One Billing Arrangement with three Billing Arrangement Lines, each assigned a percentage** / Three separate Orders / Three separate Billing Accounts with no shared configuration |
| **Map how the Invoice Batch Run works.** | A Billing Schedule has Next Billing Date set to July 1 and a target date filter of July 15. What happens during the next Invoice Batch Run? | The schedule is skipped because Next Billing Date is in the past. / **The schedule is included because Next Billing Date is at or before the target date.** / The schedule is included only if the customer's Bill Cycle Day is July 15. / The schedule is moved to error status. |

---

# Unit 2: Manage Invoice Delivery, Credit Memos, and the Invoice Line Explanation Subagent

## Learning Objectives

After completing this unit, you'll be able to:

- Configure the invoice delivery flow from scheduled generation through document rendering to customer email.
- Apply the automatic conversion of negative invoice lines into credit memo lines, and the application of those credits to outstanding invoices.
- Position the Self-Service Billing Portal as the customer-facing surface for viewing invoices and downloading PDFs.
- Apply the invoice-line-explanation capability to give customers plain-language breakdowns of complex charges.

> **Agent naming note:** The body content below uses **Subagent: Invoice Line Explanation** (per the current 262 Help portal naming under "Agentforce for Revenue Management"). Pending Annie + Mike alignment on subagent vs. "Billing Agent" vocabulary, names may be revised. Content stays the same.

Unit 1 covered how invoices are *produced*. Unit 2 covers what happens after production: how the invoice gets to the customer, how negative charges turn into credit memos automatically, where the customer interacts with the invoice, and how an AI subagent explains complex charges in natural language.

## Configure the Invoice Delivery Flow

Invoice delivery has three distinct features that run in sequence. Each is configurable independently. Each owns one part of the chain:

1. **Invoice Scheduler** — already configured in Module 2. Creates the invoice data on a cadence by running an Invoice Batch Run, producing Invoices and Invoice Lines.
2. **Document Generation Service** — renders the invoice records into a customer-facing PDF document. Built on OmniStudio Document Generation. Uses Document Templates (Word or HTML based) to merge account, contact, and invoice data into the final PDF.
3. **Send Invoices Through Email** — delivers the PDF to the customer's Bill to Contact at the cadence configured per Legal Entity, Billing Account, or scheduler.

The separation matters. Finance can produce invoices on one cadence (say, end-of-month) and deliver them on another (say, ten business days later, after internal review). PDF rendering is decoupled from email delivery, and both are decoupled from invoice generation.

The Document Generation Service runs through a **Document Generation Process** record that tracks progress. When the status moves to Success, the PDF is attached to the Invoice record. Admins can customize the layout, logos, and legal disclosures through Document Builder — a low-code approach that doesn't require touching the Invoice generation engine.

Email delivery prerequisites include turning on Document Generation for Billing, configuring email delivery settings, defining email preferences on Legal Entity records, and ensuring each Invoice has a valid Bill to Contact. A platform limit to know: emails to non-customer-community Bill to Contacts cap at 5,000 per day. Customers can be enabled as customer community users to bypass this cap.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** A common technical-eval question: "Do you handle PDFs natively or do we need a third-party add-on?" The answer is native — the Document Generation Service is built into Agentforce Revenue Management Billing. Customers don't need Conga, DocuSign Gen, or any other PDF integration to produce invoice documents. They customize templates through Document Builder. |

## Auto-Create Credit Memos from Negative Invoice Lines

When an order amendment reduces quantity, or when a product has a negative price, the Invoice Batch Run can produce **Invoice Lines with negative amounts**. Without automation, finance teams have to manually convert these into Credit Memos and apply the credits to the underlying invoices — slow, error-prone, and unscalable at high invoice volume.

The **Convert Negative Invoice Lines to Credit Memo Lines** feature in Billing Settings automates this entirely. When the admin turns the feature on, the system handles three steps automatically:

1. Identify Invoice Lines on **posted invoices** with negative amounts that haven't already been converted.
2. Convert each negative Invoice Line into a corresponding Credit Memo Line within a new posted Credit Memo.
3. Apply the resulting Credit Memo to the original invoice, reducing its balance.

Each Invoice Line tracks the converted amount in its `Converted Negative Amount` field. The total per invoice rolls up to `Total Converted Negative Amount`. The credit applied to the original invoice is the smaller of the invoice's remaining balance or the credit memo's balance. If the Credit Memo balance exceeds the invoice balance, the Credit Memo fully settles the invoice and the remaining Credit Memo balance must be manually applied to other invoices.

A worked example: a customer amends a subscription from 4 units to 3, creating an amended Order Product with a price of -$100. The next Invoice Batch Run produces a -$100 Invoice Line. The feature auto-creates a +$100 Credit Memo Line in a new posted Credit Memo, and applies the $100 credit to reduce the original invoice's $400 balance to $300. No manual intervention.

## Describe the Self-Service Billing Portal

Customers don't always want to email finance to ask about an invoice. The **Self-Service Billing Portal** is a customer-facing Experience Cloud site where end users and community users can:

- View and download invoice PDFs from the Home tab (which lists settled, partially settled, and unsettled invoices).
- Pay outstanding balances using supported payment methods (covered in Module 5).
- Raise billing inquiries and disputes from the Help Center tab.
- Track case status from the Cases tab.

For Module 4, the relevant scope is the *viewing* surface — the portal as the place where customers see their invoices. The *paying* surface is Module 5 territory.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a prospect asks how their customers will access invoices, the Self-Service Billing Portal is the answer that removes the support-ticket cycle. Most customers will use email delivery and the portal interchangeably — email for the notification, portal for download, history, and payment. Selling the portal also de-risks the support team's workload, which is a CFO-level conversation. |

## Apply the Invoice Line Explanation Subagent

The **Subagent: Invoice Line Explanation** lives under the **Agentforce for Revenue Management** agent suite. Its job is narrow and useful: when an internal user or customer service representative is looking at an invoice line that's complex or confusing, the subagent provides a plain-language explanation of the charge — including the reasons and the calculation methods.

The subagent's two named agent actions:

- **Get Invoice Line Records** — surfaces the invoice line records that match a user's question (or presents a selectable list if there are multiple matches).
- **Explain Invoice Line** — produces the plain-language explanation, walking through the math behind the charge (proration, amendments, overages, taxes).

The agent's API name is `InvoiceLineExplanation`. It's available to authenticated users in Lightning Experience and requires the Agentforce Revenue Management Billing license with the Agentforce Employee Agent add-on. Customers and partners on Experience Cloud don't yet have direct access to this subagent — the customer-facing equivalent is the **Agentforce for Billing Service Assistance Agent**, which runs in the Experience Cloud billing portal.

Example user prompts that trigger this subagent:

- "Explain the Slack line for the invoice DOC-00089."
- "Why am I charged for 10 monitors when I only ordered 6?"
- "Why is there an overage charged in the invoice DOC-0075?"
- "I see charges for Professional Services on this invoice, but the service wasn't fully delivered. Can you explain the charge breakdown?"

The agent retrieves the relevant invoice line, traces the order activity (original order, amendments, proration, tax, overage), and assembles a clear narrative. The Help docs note a customer example: an admin at Acme used the subagent to explain an invoice for 10 monitors when the original order was for 6. The agent showed that the original order was for 6 units, an amendment had added 4 more, and taxes had been applied. The agent assembled the explanation in moments rather than the hours an admin would have spent piecing the story together manually.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The Invoice Line Explanation subagent is one of the most concrete wins in the L2 Billing demo. It turns a recurring source of customer friction — confusing invoice lines — into a self-serve conversation. For a Service Cloud audience, position it as the way to deflect billing inquiries from the support queue. For a Finance audience, position it as the way to give the team conversational access to the data behind every charge without writing reports. |

## Key Takeaways

The invoice delivery flow is **Invoice Scheduler → Document Generation Service → Send Invoices Through Email** — three independently configurable features. The **Convert Negative Invoice Lines to Credit Memo Lines** feature auto-creates Credit Memo Lines from negative Invoice Lines and applies the credit to the original invoice. The **Self-Service Billing Portal** is the customer-facing Experience Cloud surface for viewing invoices and downloading PDFs. The **Subagent: Invoice Line Explanation** under the Agentforce for Revenue Management agent suite provides plain-language explanations of complex charges through two agent actions: Get Invoice Line Records and Explain Invoice Line.

## Resources

- [*Salesforce Help:* Generate Invoices in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_generation.htm&type=5)
- [*Salesforce Help:* Automatic Conversion of Negative Invoice Lines into Credit Memo Lines](https://help.salesforce.com/s/articleView?id=ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines.htm&type=5)
- [*Salesforce Help:* Self-Service Billing Portal](https://help.salesforce.com/s/articleView?id=ind.billing_self_service_portal.htm&type=5)
- [*Salesforce Help:* Subagent: Invoice Line Explanation](https://help.salesforce.com/s/articleView?id=ind.rev_agent_billing_topic_invoice_line_explanation.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Configure the invoice delivery flow.** | A finance team wants to generate invoices on the 1st of each month and deliver them to customers on the 10th, after a review period. How does the architecture support this? | They have to write a custom flow to delay email delivery. / The Invoice Scheduler bundles PDF generation and email delivery into one step. / **The Invoice Scheduler, Document Generation Service, and Send Invoices Through Email are three independent features that can run on different cadences.** / The system delivers invoices immediately upon generation. |
| **Apply the Invoice Line Explanation subagent.** | A customer service rep is reviewing invoice DOC-00089 and a customer asks why a "Slack" line shows 10 units when the original order was for 6. Which subagent action produces the plain-language explanation? | Get Account Billing Summary / **Explain Invoice Line** / Get Invoice Line Records / Get Dunning Strategy |

---

# Appendix: Open Questions and Parking Lot

## Open question for Mike

**Parent agent name consistency.** Module 4 uses **Agentforce for Revenue Management** as the parent for the Invoice Line Explanation subagent. Module 5 LO 2.2 has been updated to use the same parent name. Module 1 v2 also references this parent. Confirming this is the chosen umbrella name across the L2 mix (vs. the Billing-area-scoped "Agentforce for Billing Employee Assistance"). See `modules-4-5-262-lo-validation-report.md` Open Question 1 for the full discussion.

## Topics deliberately routed elsewhere

For audit completeness:

- **Milestone billing as an invoicing pattern.** Module 2 v2 covers both milestone configuration (on the BTI) and milestone runtime (`BillingMilestonePlan` and `BillingMilestonePlanItem`). Module 4 doesn't repeat the milestone coverage — the forward reference in Module 2 v2 ends at "executing the milestone." That execution is implicit in the Invoice Batch Run mechanics covered in Unit 1 LO 1.3.
- **Billing Disputes management.** Moved to Module 5 (per Mike's comment 23). Disputes route through the Collections workflow.
- **Conga / Word vs HTML template comparisons.** Out of scope. Document Generation Service is the native answer; there's no need to compare it against legacy third-party PDF integrations.

## Cross-module observations

The **Subagent: Invoice Line Explanation** referenced in Unit 2 is one of seven subagents under the **Agentforce for Revenue Management** suite documented across the L2 mix:

- Module 1 v2 references Subagent: Invoice Line Explanation + Subagent: Billing Inquiries + the customer-facing Agentforce for Billing Service Assistance Agent for Experience Cloud.
- Module 3 v2 references Subagent: Consumption Management.
- Module 4 (this module) covers Subagent: Invoice Line Explanation in depth.
- Module 5 references Subagent: Billing Collections Management.

Keeping the subagent naming and parent agent name consistent across all four modules is important for learner coherence.

---

*Prepared by Brian Galdino with AI assistance; grounded against the latest Salesforce Help portal (Billing area, Agentforce for Revenue Management area). Per-claim citation log: `docs/trailhead-l2-review/modules-4-5-262-lo-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
