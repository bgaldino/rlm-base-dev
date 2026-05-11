---
article_id: ind.billing_guided_setup.htm
title: Guided Setup for Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_guided_setup.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup.htm
fetched_at: 2026-05-11
---

# Guided Setup for Billing

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Guided Setup for Billing

Admins can use the Billing Guided Setup for a ‌step-by-step guidance to complete key tasks that are required to set up Billing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


The Billing Advanced Features setup assistant and the Payment Configurations setup assistant are available only with the the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

All the other setup assistants are available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

How It Works

The guided experience is structured to help Billing admins complete each step sequentially, ensuring that the Billing setup is accurate and fully operational. The guided setup includes these setup assistants:

Billing Prerequisites—Set up billing users, assign relevant permission sets, and define billing rules for your products. This step makes sure that authorized personnel manage the billing operations according to clearly defined rules, which boosts both security and accuracy.
Tax Configurations—Set up the tax engine and configure tax policies to ensure accurate tax calculations and compliance with regional regulations.
Invoice Configurations—Schedule and manage invoice runs to streamline the invoicing process.
Accounting Configurations—Streamline the accounting process for your billing transactions by creating accounting periods and legal entity accounting periods.
Currency Conversion Configurations—View transaction amounts not only in the transactional currency but also in your corporate currency. Enable multiple currencies and Advanced Currency Management. Then, turn on the Billing feature to convert and store transaction amounts in your corporate currency.
Billing Advanced Features—Turn on the generation and email delivery of invoice documents. Manage the document template and email template that are used to generate and email invoice documents. You can also set up a chart of accounts for your legal entities, assign appropriate general ledger accounts to transaction journals, and automatically create dual transaction journals for your billing transactions.
Payment Configurations—Set up payment processing for your billing transactions. Configure native payment gateways, payment schedule policies, payment schedules, and related payment records. Then, schedule payment batch runs to process payments and apply them to invoices or invoice lines.
NOTE

For Salesforce orgs that are created in Winter ’26, the Configure Payment Gateways button in Step 7: Payment Configurations of the Billing Guided Setup, which redirects users to the Payment Gateway Configuration tab, is available by default. For Salesforce orgs that are created before Winter ’26, the Payment Gateway Configuration tab isn’t available by default. To fix this issue, change the settings of the Payment Gateway Configuration tab to Default On.

How to Do This

From Setup, enter Billing Guided Setup in the Quick Find box, and then select the required setup assistant.

SEE ALSO
Assign Permissions to Access Billing Features
Define Billing Policies and Billability Rules
Define Tax Calculation for Invoices
Automated Invoice Generation with Invoice Batch Runs
Manage Accounting Periods in Agentforce Revenue Management
Capture Transaction Amounts in Multiple Currencies
Turn On Invoice PDF Document Generation
Turn On Email Delivery of Invoices
Manage Chart of Accounts and Transaction Journals in Agentforce Revenue Management
Process Payments and Issue Refunds in Agentforce Revenue Management
