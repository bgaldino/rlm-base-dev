# Module 6: General Ledger Accounting

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; grounded against the 262 Summer '26 Help portal capture covering Billing — Financial Accounting area)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Salesforce Help portal (Billing area `ind.billing_*`, Financial Accounting articles). See `module-6-v2-validation-report.md` for the per-claim citation log and the v1→v2 correction list.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.
**Style notes for editorial:** This draft bolds product object names (Legal Entity, General Ledger Account, Transaction Journal, etc.) for technical clarity. That matches the convention established across Modules 1–5 of the L2 mix.

---

**Badge Description:** Configure your financial foundation to automate journal entries and close accounting periods.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Set Up the Financial Accounting Foundation | Quiz | |
| 2 | Interface with the ERP | Quiz | |

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

- [ARM Billing L2 Outline Proposal — FY27](https://docs.google.com/spreadsheets/d/11kgi-t-OVjsgtt7AlLjNUFItvovCoi2yC0UaL8cm2MY/edit?gid=670679088#gid=670679088)
- Placeholder for Demo Challenge
- Placeholder for ROI Pitch Challenge

---

# Unit 1: Set Up the Financial Accounting Foundation

## Learning Objectives

After completing this unit, you'll be able to:

- Define the role of legal entities in a corporate structure.
- Explain how accounting periods organize financial data into reporting time frames.
- Explain how the chart of accounts categorizes transactions.
- Describe how Financial Accounting connects to the Revenue Cloud Billing lifecycle.

## The Foundation of Your Financial Library

Imagine you're organizing a massive library. Before you can put a single book on a shelf, you need to know which room it goes in and what category it falls under (fiction, history, and so on). Without that structure, finding the book later is nearly impossible.

| Note | Content |
|:-:|:-:|
| icon=true | **Use Slackbot to Personalize Your Learning** The Make It Your Own Slackbot skill can reframe any concept using something you already know and love. Copy the link to the Make It Your Own Skill, paste it into your Slackbot DM, and tell Slackbot what's confusing you. For example: "Hey Slackbot, use the Make It Your Own Skill. Help me understand the Legal Entity in relation to Revenue Cloud Billing using [soccer / baking / hip hop / whatever you love]." |

In the world of finance, **Financial Accounting** in Agentforce Revenue Management is that library's master blueprint. It records and organizes every dollar that moves through Billing so your accounting team can report accurate numbers to the business. Financial Accounting acts as a *subledger*: Salesforce records the transaction-level detail, and summarized totals flow to the ERP's general ledger — the system of record for the company's consolidated books. For Revenue Cloud specialists, understanding this setup is key, because it's how Agentforce Revenue Management replaces manual reconciliation with automated, audit-ready financial data.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Financial Accounting works alongside the billing lifecycle: a Billing Schedule produces an Invoice, and the Invoice produces dual **Transaction Journals** through a General Ledger Account Assignment Rule. Position it as the bridge between "what we billed" and "what the books show." |

## Define Your Corporate Structure

Everything starts with a **Legal Entity**. A legal entity defines how your organization is structured — it's a specific company or branch that operates as a discrete financial unit. In Agentforce Revenue Management, you can create multiple legal entities, and each one governs the billing and tax information for the order products tied to it: its tax treatments, billing treatments, accounting periods, and finance books.

A legal entity also carries a **currency ISO code** — its reporting currency, such as US Dollars or Euros. The currency is set when the legal entity is created and can't be changed afterward, so it's a decision worth getting right up front.

To see this in action, look at a fictional company, Ethan's Aquariums. Sawyer is a Revenue Specialist there who manages two legal entities — one in the United States and one in Europe. Because they operate in different regions under different tax and reporting regimes, each entity requires its own configuration.

**Why it matters:** Every invoice generated by the billing engine is tagged to a legal entity. When transactions roll up for reporting, they're already attributed to the correct organizational unit — no manual sorting required.

## Establish Accounting Periods

Money is tracked in time buckets called **Accounting Periods**. An accounting period is a specific time frame — a month, a quarter, a year — for which a company prepares its financial statements. Each accounting period has a start date, an end date, and a financial period (for example, *FY 2027*). The system generates the period's name automatically from those values.

A few rules govern how periods are defined:

- An accounting period can't be longer than one year.
- Periods can't overlap or share start and end dates with an existing period.
- Periods are commonly created monthly for internal reporting, then consolidated into quarters, half-years, or years for external reporting.

Accounting periods on their own are organization-wide time frames. To tie them to a specific branch, you create a **Legal Entity Accounting Period** — a record that links one legal entity to one accounting period. Once that link exists, every invoice, credit memo, and payment is automatically assigned to the correct legal entity accounting period based on the transaction's legal entity and effective date.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The Order to Billing Schedule flow is the bridge that prepares order data for invoicing. Defining accounting periods *before* transactions start flowing keeps them from being assigned to the wrong period — a setup-order detail worth raising early with finance teams. |

## Organize the Chart of Accounts

The **Chart of Accounts (COA)** is the master list of every account where money is tracked. The COA is built from **General Ledger Accounts**, and it's structured around the five core financial-statement account types:

- **Assets** — what the company owns (for example, cash, accounts receivable).
- **Liabilities** — what the company owes (for example, deferred revenue).
- **Equity** — the net value belonging to stockholders.
- **Revenue** — money earned from sales and services.
- **Expense** — money spent to operate the business.

Each General Ledger Account has an accounting name, a unique accounting code, the financial statement it contributes to (Income Statement or Balance Sheet), a legal entity, and a **Type** that drives how opening and closing balances are calculated at period close. Companies also set up dedicated general ledger accounts to capture foreign exchange gains and losses, which the system uses during period closure.

### How General Ledger Account Assignment Rules connect

Creating the accounts is only half the setup. **General Ledger Account Assignment Rules** are what connect billing transactions to the right accounts. An assignment rule defines, for a given billing transaction type (Invoice, Invoice Line, Credit Memo, Payment, Refund, and so on) and a set of criteria, which general ledger accounts the resulting **Transaction Journals** should hit.

For example, an assignment rule can determine whether the credit from an invoice lands in a Deferred Revenue liability account or a Revenue account, based on the criteria you configure. Once the rules are in place, the system generates the journal entries automatically — no manual journal entry required.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Don't confuse the two "rule" layers. In Billing, the hierarchy of Billing Policy → Billing Treatment → Billing Treatment Item governs *how billing schedules are generated and how revenue is recognized*. General Ledger Account Assignment Rules are a separate layer that governs *which GL accounts the resulting transactions post to*. Both matter; they answer different questions. |

## How the Billing Lifecycle Feeds Financial Accounting

Financial Accounting is most powerful when you see it inside the full billing lifecycle:

| Step | What Happens |
|:--|:--|
| 1. Order Activation | A customer order is activated in Agentforce Revenue Management. |
| 2. Billing Schedule Generated | The Order to Billing Schedule flow stages the billing data. |
| 3. Invoice Created | The billing engine calculates and generates the invoice (invoice creation is not the same as invoice document generation). |
| 4. Assignment Rule Applied | General Ledger Account Assignment Rules map the transaction to the correct general ledger accounts. |
| 5. Transaction Journals Written | The system automatically generates dual transaction journals — a debit and a credit. |
| 6. Legal Entity Accounting Period Closed | Balances are calculated and the period is closed, with the closing balance carried forward automatically. |

## Key Takeaways

- Every invoice generated by Revenue Cloud Billing is tagged to a **Legal Entity** and a **Legal Entity Accounting Period** when it's created.
- A **Legal Entity** governs the tax treatments, billing treatments, accounting periods, and finance books for the order products tied to it, and carries a currency ISO code set at creation.
- The **Chart of Accounts** is built from General Ledger Accounts across five core types — Assets, Liabilities, Equity, Revenue, and Expense.
- **General Ledger Account Assignment Rules** are what actually map billing transactions to the right general ledger accounts — get these right before going live.

## Resources

- [*Salesforce Help:* Manage Financial Accounting in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_financial_accounting.htm&type=5)
- [*Salesforce Help:* Create Legal Entities in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_create_legal_entities.htm&type=5)
- [*Salesforce Help:* What are Accounting Periods?](https://help.salesforce.com/s/articleView?id=ind.billing_accounting_periods_explain.htm&type=5)
- [*Salesforce Help:* Manage Chart of Accounts and Transaction Journals in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger.htm&type=5)
- [*Salesforce Help:* General Ledger Account Assignment Rules and Related Records](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_account_assignment_rules_and_criteria.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Define the role of legal entities in a corporate structure.** | What is the primary purpose of a Legal Entity in Agentforce Revenue Management's Financial Accounting? | To create marketing campaigns for specific regions. / **To define how the organization is structured and govern the billing, tax, and accounting-period configuration for a specific branch.** / To manage the passwords of every finance user. / To set the color theme of the billing user interface. |
| **Explain how the chart of accounts categorizes transactions.** | Which accounting type categorizes money that the company owes to others? | Asset / Expense / **Liability** / Revenue |

---

# Unit 2: Interface with the ERP

## Learning Objectives

After completing this unit, you'll be able to:

- Explain the purpose of dual transaction journals in Revenue Cloud Billing.
- Describe how General Ledger Accounting Period Summaries are used to verify financial accuracy.
- Describe the process of closing a legal entity accounting period.
- Identify common integration points between Salesforce and an ERP.
- Distinguish between invoice creation and invoice document generation.

## Connect Salesforce to Your ERP

In Unit 1, you defined the core components of Financial Accounting — legal entities, accounting periods, and the chart of accounts. With that structure in place, you can process financial transactions and synchronize the data with your primary financial records.

The interface between Salesforce and an Enterprise Resource Planning (ERP) system is a critical touchpoint in the Lead-to-Cash journey. Salesforce captures the initial sale and generates the invoice, then passes the financial data to the ERP for final reporting and consolidation.

In an **agentic workflow**, this handoff isn't manual. The system automatically prepares and stages the data so it's ready for the ERP the moment a transaction occurs.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** In Revenue Cloud Billing, invoice creation (the invoice record being calculated and created) and invoice document generation (producing the actual PDF) are two distinct steps. Conflating them is a common stumbling block in customer conversations — be clear on the difference when positioning the platform to finance teams. |

## Record Twice with Dual Transaction Journals

Accuracy is the heartbeat of finance. To make sure every dollar is accounted for, Revenue Cloud Billing generates **dual transaction journals**. When a billing event occurs — for example, Sawyer's team selling a high-end coral reef tank — the system automatically creates two entries based on the General Ledger Account Assignment Rule for that transaction type:

- **The debit** — typically increases an asset (like Accounts Receivable).
- **The credit** — typically increases revenue or a liability (like Deferred Revenue).

This double-entry bookkeeping method keeps the books balanced and creates a built-in self-check: if total debits and total credits don't match, something is wrong. Because the journals are created and maintained on the Salesforce platform, specialists can show customers a real-time view of their financial health without waiting for a nightly ERP sync. You can integrate these transaction journals with any accounting system to prepare financial statements such as balance sheets and profit-and-loss statements.

**Why this matters:** Real-time subledger visibility is a key differentiator over legacy billing systems that require overnight batch reconciliation with the ERP.

## Verify Accuracy with General Ledger Accounting Period Summaries

Before Sawyer can close the books for the month, everything needs to add up. That's the job of the **General Ledger Accounting Period Summary**.

A summary record is created for each combination of general ledger account and legal entity accounting period, and it captures:

- **Opening Balance** — the amount carried forward from the previous period.
- **Total Debit and Total Credit Amounts** — the movement during the current period.
- **Closing Balance** — the final amount at period end, derived automatically based on the general ledger account's type.

Summaries are generated automatically by a Data Processing Engine definition during legal entity accounting period closure, and they can also be created manually while the period is open. If the debits and credits across accounts don't reconcile, Sawyer can drill into a specific period to pinpoint where the discrepancy lies.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Showing General Ledger Accounting Period Summaries in a live org is one of the most compelling moments in a Revenue Cloud Billing demo. Finance personas recognize the opening-balance / debits / credits / closing-balance structure immediately — it speaks their language. |

## Close the Legal Entity Accounting Period

Once the numbers are verified, it's time to **close the legal entity accounting period** — a critical step in the financial close. In traditional billing systems, this is often a heavily manual process. With Agentforce Revenue Management, the system automates the heavy lifting.

When Sawyer closes a legal entity accounting period, the system runs three Data Processing Engine definitions in sequence. The result:

1. The system calculates the final closing balance for each general ledger account.
2. It carries that amount forward as the opening balance for the next period.
3. The period status moves to **Closed**, which prevents new transactions from being posted to that time frame.

Legal entity accounting periods move through statuses — Open, Pending Closure, Closed — and a closed period can be **reopened** when receivable transactions need to be reconciled. This locking-and-reopening mechanism protects financial history while still allowing for legitimate corrections, which matters for customers preparing for an IPO or an external audit.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Closing a legal entity accounting period requires Data Pipelines to be enabled and a default DPE definition selected, along with the transaction-journal features turned on. If a customer asks why period close "isn't working" in a fresh org, the setup prerequisites are usually the answer — point them to Set Up Financial Accounting Features. |

## Connect to the ERP

While Salesforce manages the subledger, the ERP typically remains the system of record for the entire company's consolidated financials. Integration is the final piece of the puzzle.

Common integration points include:

- **Journal entry sync** — sending summarized general ledger totals from Salesforce to the ERP's general ledger.
- **Payment information** — bringing payment status back into Salesforce so sales and service teams can see whether an invoice was paid.
- **Tax calculations** — connecting to external tax engines such as Avalara or Vertex for global compliance.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** You'll frequently encounter customers running a mix of Salesforce billing and ERP reporting (NetSuite, SAP, Oracle). A common question is how different sales motions — like Product-Led Growth versus Enterprise-led revenue — can have different downstream treatment. Revenue Cloud Billing supports this through Billing Policy configurations and General Ledger Account Assignment Rules that govern how different product types post to different GL accounts and flow to different ERP destinations. |

## How a Transaction Moves Through the Lifecycle

Once Financial Accounting is set up, the system automatically creates dual transaction journals for every billing event, giving finance teams real-time visibility without waiting for an overnight ERP sync. Here's the full path:

| Step | What Happens |
|:--|:--|
| Order Activated | The Order to Billing Schedule flow stages data for invoicing. |
| Billing Schedule Generated | The system determines invoice timing and amounts. |
| Invoice Created | The invoice record is calculated and created in Revenue Cloud Billing. |
| Invoice Document Generated | The PDF or document version is produced — a separate step from invoice creation. |
| Assignment Rule Applied | The transaction is mapped to the correct general ledger accounts. |
| Transaction Journals Written | Debit and credit entries are posted as dual transaction journals. |
| Period Summary Updated | The General Ledger Accounting Period Summary reflects the new activity. |
| Period Closed | The closing balance is locked and rolls forward as the next period's opening balance. |

## Key Takeaways

- **Calculations are not documents:** invoice creation and invoice document generation are two distinct steps in Revenue Cloud Billing.
- **Dual transaction journals** record a debit and a credit for every billing event, keeping the books balanced and audit-ready in real time.
- **General Ledger Accounting Period Summaries** capture opening balance, debits, credits, and closing balance per account per period — the verification layer before close.
- **Closing a legal entity accounting period** runs three Data Processing Engine definitions in sequence, locks the period, and rolls the closing balance forward; a closed period can be reopened to reconcile receivables.

By mastering the Financial Accounting lifecycle, you enable finance teams to maintain a real-time, audit-ready view of their business directly on the Salesforce platform — bridging the gap between sales and the ERP.

## Resources

- [*Salesforce Help:* What are Chart of Accounts and Dual Journal Entries?](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_accounts_explain.htm&type=5)
- [*Salesforce Help:* Create General Ledger Accounting Period Summary Manually](https://help.salesforce.com/s/articleView?id=ind.billing_general_ledger_accounting_period_summary_create.htm&type=5)
- [*Salesforce Help:* Close Legal Entity Accounting Periods](https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_close.htm&type=5)
- [*Salesforce Help:* Manage Financial Accounting in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_financial_accounting.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Explain the purpose of dual transaction journals.** | How do dual transaction journals help ensure financial accuracy? | By automatically deleting transactions that contain errors. / **By creating both a debit and a credit entry for every billing event so the books stay balanced.** / By emailing the customer every time a journal is created. / By letting users manually edit historical tax records. |
| **Describe the process of closing a legal entity accounting period.** | What happens to the closing balance when a legal entity accounting period is closed? | It is reset to zero for the start of the next year. / It is sent to the customer as a discount code. / **It is automatically carried forward as the opening balance for the next period.** / It is archived and can't be viewed by the finance team. |

---

# Appendix: Open Questions and Parking Lot

## Open questions for Mike

**1. "Cancel not supported for in-flight batch jobs."** The v1 draft included a callout: *"Known Limitation (Release 262): Cancel is not supported for any in-flight batch jobs."* This v2 draft removed it — partly because of the evergreen-language rule (no release notations) and partly because a known limitation that may be fixed in a future release is risky to bake into evergreen Trailhead content. If Mike wants the batch-cancel behavior addressed, the better home is a seller-facing "what to expect" note without the version stamp. Mike, your call on whether it belongs in the module at all.

**2. "Accounting Rules" as a legal entity attribute.** The v1 draft listed "Accounting Rules" as a per-legal-entity attribute alongside Corporate Currency. The 262 Help portal doesn't document an attribute by that name — a legal entity governs *tax treatments, billing treatments, accounting periods, and finance books*. This v2 draft uses the documented framing. Flagging in case "Accounting Rules" is a known internal shorthand Mike wants preserved.

## v1 terminology corrections (see validation report for detail)

This module had several terms in the v1 draft that don't match the 262 Help portal:

- **"GL Treatment"** → **General Ledger Account Assignment Rule** (the v1 term doesn't exist in the product docs).
- **"Trial Balance View"** → **General Ledger Accounting Period Summary** (the v1 term doesn't exist in the product docs).
- **Accounting period "types" (Standard Monthly / 15-Day / Custom 4-4-5 calendars)** → removed; accounting periods are date-range records (max one year, no overlaps), not a fixed set of selectable calendar types.
- **"Accounting Subledger"** → reframed around **Financial Accounting**, the documented feature name, while keeping the accurate "Salesforce as subledger to the ERP's general ledger" concept.

---

*Prepared by Brian Galdino with AI assistance; grounded against the latest Salesforce Help portal (Billing — Financial Accounting area). Per-claim citation log and v1→v2 correction list: `docs/trailhead-l2-review/module-6-v2-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
