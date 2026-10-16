---
article_id: ind.billing.htm
title: Manage Billing in Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
fetched_at: 2026-09-04
---

# Manage Billing in Revenue Management

Monetize all the sales models of your business with Billing. Generate invoices for diverse scenarios, such as customer milestones, product usage, amendments, cancellations, or early renewal of evergreen subscriptions. Bill in advance or in arrears, or bill for external transactions. Consolidate invoices with custom grouping, automate and scale invoice generation, and suspend or resume billing for specific accounts or billing schedule groups as needed.

Process payments for invoices, issue refunds, and track payments for unpaid invoices. Collect payment promises from customers and write off unpaid or partially paid invoices if the balance is deemed uncollectible. Automate the conversion of negative invoice lines to credit memos and the application of credits to invoices. Preview upcoming invoices and create PDFs for previews and actual invoices by using customized templates.

Configure multiple legal entities, tax engines, and billing profiles to support your business operations and customer requirements. Keep business records accurate and improve financial reporting by using accounting periods and a chart of accounts for legal entities, automating journal entries, and managing multi-currency transactions. Get real-time visibility into invoices, credit memos, and billing schedules.

Set Up Billing
Enable Billing, assign the required permission sets, and set up features.
Set Up Additional Billing Features
Beyond the core functionality, you can set up and configure various additional Billing features to extend its capabilities. This allows you to tailor Billing to your specific business requirements.
Considerations When Setting Up and Using Billing
Before you set up and use Billing, keep these considerations in mind.
Define Billing Policies and Billability Rules
Define billing policies, treatments, and treatment items to generate invoices that suit your sales models. Specify product billability rule criteria to define whether you want to bill your products in advance or in arrears, whether specific products are billed, and other conditions.
Create Payment Terms
Negotiate and define payment terms to set a due date for payments and collect payments in a timely manner. You can anticipate or enforce the date by when payments for outstanding invoices must be paid.
Manage Billing Arrangements
Billing arrangements facilitate precise invoicing for business scenarios such as parent account billed for subsidiary accounts, cross-departmental charge allocations, or services or assets shared among multiple parties. Use billing arrangements to configure the allocation of billing amounts to a specific billing account or distribute costs among several billing accounts based on fixed percentages.
Configure Milestone Billing
Bill projects in installments based on milestone achievements or predefined dates. Align payments with project progress and enhance customer satisfaction through timely invoicing.
Tax Calculation for Invoices
Configure how taxes are calculated on the billing amounts of your taxable products or services, or import tax amounts calculated by an external system.
Create Billing Profiles
Cater to your customers' billing preferences and business needs by creating billing profiles for their accounts. Define multiple billing profiles for an account to manage diverse billing needs, each with its own billing details, payment terms, and contacts. Set a default billing profile for accounts to easily access your customers' preferred billing day of the month, billing address, billing contact, and other details. With billing profiles, sales representatives no longer need to enter this information for each transaction, saving time and effort.
Manage Financial Accounting in Revenue Management
Streamline the financial accounting process for your organization with accounting periods for legal entities, chart of accounts, journal entries for your billing transactions, and by capturing transaction amounts in corporate currency.
Preview Invoices
Preview invoices for the next two billing periods of orders, quotes, accounts, or billing schedule groups to verify order products, discounts, amendments, cancellations, and tax calculations.
Manage Billing Schedules and Billing Schedule Groups
Billing schedules define when and how an order product is invoiced. Billing schedule groups contain one or more billing schedules. Both of these are created and updated as a result of creating, amending, and canceling orders. You can generate billing schedules directly from transactions in external systems, or from any Salesforce object by using Create Standalone Billing Schedules API. To generate billing schedules from orders, use the Order to Billing Schedule flow, Create Billing Schedules for Orders API, or Create Standalone Billing Schedules API.
Suspend and Resume Billing
Pause invoicing temporarily for an account or billing schedule group without canceling its billing schedules. Suspensions defer charges, they don’t waive them.
Billing Forecast
Billing Forecast estimates upcoming invoice charges before invoices are created. Review projected charges to understand expected billing and discuss estimates with customers.
Generate Invoices in Revenue Management
Schedule invoice runs to generate invoices from billing schedules or generate invoices directly from accounts or orders. Create standalone invoices or import invoices from an external system.
Invoice Risk Score (Pilot)
Invoice Risk Scoring uses invoice data and predictive AI to estimate the likelihood that payment for an open invoice will be delayed beyond its due date. Learn how risk scores and risk levels are displayed on invoice records to help identify potential payment risks.
Generate Invoice PDF Documents
After invoices are generated, generate PDF documents for a batch of invoices or a single invoice.
Send Invoices Through Email
Ensure regional compliance by sending invoices through emails to your customers after the invoices are posted and before the payment due date. Customize your preferences at various levels in your Salesforce org to choose the way emails are delivered to your customers.
Manage Credit Memos in Revenue Management
Create and apply credit memos to decrease the balance of invoices when the quantity or price of orders are amended.
Configure Sequential Numbering for Invoices and Credit Memos
Use a sequence policy to configure automated sequential numbering for your invoices and credit memos. Generate unique, gapless numbers to create fully traceable records for financial audits.
Manage Debit Memos in Revenue Management
Create debit memos when you undercharge your customer or want to add additional charges. When debit memo lines are converted to invoice lines, the balance of the related invoices increases.
Process Payments and Issue Refunds in Revenue Management
Complete your cash journey by making payments for posted invoices and issuing refunds when needed. Settle open invoice balances in a timely manner and accurately report cash flow by collecting and applying payments. Refund your customers if they change or cancel products or services that they paid for.
Manage Collections for Accounts in Billing
To recover overdue invoices, your collections reps use Collections workflow to track payments, record customer payment promises, and send personalized, automated dunning emails to minimize bad debt and maintain healthy cash flow.
Write Off Invoices
Write off unpaid or partially paid invoices when the balance on the invoice is deemed uncollectible. To maintain accurate accounting, the system automatically creates and applies credit memos to write off the uncollectible balance on the invoice.
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
