---
article_id: ind.billing.htm
title: Manage Billing in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.revenue_lifecycle_management.htm
fetched_at: 2026-05-11
---

# Manage Billing in Agentforce Revenue Management

Monetize all the sales models of your business with Billing. Generate invoices for diverse scenarios, such as customer milestones, product usage, amendments, cancellations, or early renewal of evergreen subscriptions. Bill in advance or in arrears, or bill for external transactions. Consolidate invoices with custom grouping, and suspend and resume billing for specific accounts or billing schedule groups as needed. Automate and scale invoice generation. Preview upcoming invoices, and create PDFs for invoice previews and actual invoices by using customized templates. Adjust billing parameters to suit your business requirements. Configure multiple legal entities and tax engines to best support your business operations and structure. Cater to your customer requirements by configuring billing profiles. Automate the conversion of negative invoice lines to credit memos and the application of credits to invoices. Process payments for your invoices and issue refunds if required. Track payments for unpaid invoices and collect payment promises from customers. Write off unpaid or partially paid invoices if the balance on the invoice is deemed uncollectible. Get real-time visibility into invoices, credit memos, and billing schedules. Keep business records accurate and improve financial reporting by using accounting periods and a chart of accounts for legal entities, automating journal entries, and managing multi-currency transactions.

Set Up Billing
Enable Billing, assign the required permission sets, and set up features.
Set Up Additional Billing Features
Beyond the core functionality, you can set up and configure various additional Billing features to extend its capabilities. This allows you to tailor Billing to your specific business requirements.
Considerations When Setting Up and Using Billing
Before you set up and use Billing, keep these considerations in mind.
Define Billing Policies and Billability Rules
Define billing policies, treatments, and treatment items to generate invoices that suit your sales models. Specify product billability rule criteria to define whether you want to bill your products in advance or in arrears, whether specific products are billed, and other conditions.
/apex/HTViewHelpDoc?id=ind.Chunk1078736980.htm#billing_payment_terms

Manage Billing Arrangements
Billing arrangements facilitate precise invoicing for business scenarios such as parent account billed for subsidiary accounts, cross-departmental charge allocations, or services or assets shared among multiple parties. Use billing arrangements to configure the allocation of billing amounts to a specific billing account or distribute costs among several billing accounts based on fixed percentages.
Configure Milestone Billing
Bill projects in installments based on milestone achievements or predefined dates. Align payments with project progress and enhance customer satisfaction through timely invoicing.
Define Tax Calculation for Invoices
Configure tax calculation on the billing amounts of your taxable products or services, or import tax amounts calculated by an external system.
Create Billing Profiles
Cater to your customers' billing preferences and business needs by creating billing profiles for their accounts. Define multiple billing profiles for an account to manage diverse billing needs, each with its own billing details, payment terms, and contacts. Set a default billing profile for accounts to easily access your customers' preferred billing day of the month, billing address, billing contact, and other details. With billing profiles, sales representatives no longer need to enter this information for each transaction, saving time and effort.
Manage Financial Accounting in Agentforce Revenue Management
Streamline the financial accounting process for your organization with accounting periods for legal entities, chart of accounts, journal entries for your billing transactions, and by capturing transaction amounts in corporate currency.
Preview Invoices
Preview invoices for the next two billing periods of orders, quotes, accounts, or billing schedule groups to verify order products, discounts, amendments, cancellations, and tax calculations.
Manage Billing Schedules and Billing Schedule Groups
Billing schedules define when and how an order product is invoiced. Billing schedule groups contain one or more billing schedules. Both of these are created and updated as a result of creating, amending, and canceling orders.
Period Boundary and Proration in Billing Cycles
You can adjust when billing periods start and how charges are calculated by using flexible date settings that align with your business model and customer preferences.
Suspend and Resume Billing
When temporary challenges such as billing errors, disputes, or payment disruptions occur, you can suspend billing for customer accounts or billing schedule groups for a specific period. You can resume billing after the suspension period, without restarting the entire billing cycle.
Generate Invoices in Agentforce Revenue Management
Schedule invoice runs to generate invoices from billing schedules or generate invoices directly from accounts or orders. Create standalone invoices or import invoices from an external system.
Generate Invoice PDF Documents
After invoices are generated, generate PDF documents for a batch of invoices or a single invoice.
Send Invoices Through Email
Ensure regional compliance by sending invoices through emails to your customers after the invoices are posted and before the payment due date. Customize your preferences at various levels in your Salesforce org to choose the way emails are delivered to your customers.
Manage Credit Memos in Agentforce Revenue Management
Create and apply credit memos to decrease the balance of invoices when the quantity or price of orders are amended.
Configure Sequential Numbering for Invoices and Credit Memos
Use a sequence policy to configure automated sequential numbering for your invoices and credit memos. Generate unique, gapless numbers to create fully traceable records for financial audits.
Manage Debit Memos in Agentforce Revenue Management
Create debit memos when you undercharge your customer or want to add additional charges. When debit memo lines are converted to invoice lines, the balance of the related invoices increases.
Process Payments and Issue Refunds in Agentforce Revenue Management
Complete your cash journey by making payments for posted invoices and issuing refunds when needed. Settle open invoice balances in a timely manner and accurately report cash flow by collecting and applying payments. Refund your customers if they change or cancel products or services that they paid for.
Manage Collections for Accounts in Billing
Use Collections to proactively address overdue invoices, reduce bad debt, and maintain a healthy cash flow. Your collections reps can easily track payments for unpaid invoices, and collect payment promises from customers, which helps streamline payments and reduce the risk of overdue invoices. Collections reps can also send personalized, automated dunning emails for effective debt recovery.
/apex/HTViewHelpDoc?id=ind.Chunk1737636662.htm#billing_write_off_invoice_balance

Manage Billing Disputes
Fragmented billing dispute processes often lead to payment delays and poor customer experience. By using the dispute management feature, you can streamline the intake and resolution process for common billing requests and disputes. Install pre-built service process templates by using Unified Catalog. Your billing specialists and customer service representatives can initiate cases directly from the Account record page, and quickly capture, validate, and resolve common inquiries, all from a single catalog. Billing portal users can raise service requests through the self-service Billing portal.
Billing Account Overview
View and manage customer billing information from a single page. Track billing transactions, generate and preview invoices, suspend and resume billing, create credit memos, and resolve billing inquiries. Get a complete view of the customer's billing status by accessing key billing actions, account details, and related account records.
Statement of Account
Account statements consolidate billing activity for accounts over a time period so customers see transactions and outstanding balances in one statement.
Billing Settlements Central
Access invoices, payments, credit memos, and debit memos with ease from a single console. Perform settlements and adjustments, track balances, and act from a single console. Reduce navigation, gain visibility into outstanding balances, and support efficient billing through in-context actions and customizable views.
Billing Operations Console
Monitor invoices, credit memos, and invoice schedules with ease. Manage billing transactions effectively with timely insights into revenue transaction log errors and failed invoices.
Limits in Billing
Review the default limits for Billing features.
