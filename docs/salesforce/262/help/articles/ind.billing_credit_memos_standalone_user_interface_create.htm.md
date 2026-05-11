---
article_id: ind.billing_credit_memos_standalone_user_interface_create.htm
title: Create and Apply Standalone Credit Memos
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_credit_memos_standalone_user_interface_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Create and Apply Standalone Credit Memos

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Create and Apply Standalone Credit Memos

Create individual credit memos to efficiently provide credits to your customers. Apply these credits to the relevant customer invoice.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create and apply credit memos:	

Billing Admin permission set

OR

Credit Memo Operations User permission set

Create Standalone Credit Memos
From the App Launcher, find and select Credit Memos.
Click Create Credit Memo.
Enter an account name.
Select Draft as the status.
You can create a credit memo in both draft and posted status.
Select the credit memo effective date.
Choose a tax strategy to define your tax calculation approach.
To skip the creation of tax lines, select Ignore.
To manually specify a tax amount, select Manual Override.
To compute tax lines by using a tax treatment, select Calculate.
If your tax strategy is Calculate, select a tax treatment.
If needed, provide a description for the credit memo.
Select the ID of the product that are creating the credit memo for. If the product isn't in your Salesforce org, enter the product name.
Either a product ID or product name is required to create a credit memo.
Enter the credit amount.
If your tax strategy is Manual Override, enter a manual override tax amount.
Select the currency of your credit amount.
If needed, enter the billing and shipping address.
Click Create.

The credit memo generation is initiated, and you'll receive a notification after the credit memo is generated.

If you create the credit memo in ‌draft status, obtain the necessary approvals and click Post Credit Memo. After the credit memo is posted, apply it to the required invoice.

Apply Standalone Credit Memos to Invoice or Invoice Lines
From a posted credit memo, click Apply Credit Memo.
The system uses the default credit memo flow to retrieve invoices associated with the same billing account as the credit memo.
Enter the credit amount you want to apply from the available credit memo balance, and select the required invoice.
Click Apply.

The system automatically applies the credit to the invoice or invoice line based on the credit application level. If the total amount of the invoice lines exceeds the credit memo amount to be applied, the system applies the credit to matching invoice lines in descending order. If the invoice line amount is higher than the remaining credit, a partial credit amount is applied to the invoice line. You can view the remaining credit balance from the Balance field on the Credit Memo record. The Balance field isn’t available by default and you can add it from Page Layouts.

Alternatively, you can apply credit memos by using Apply Credit Memo API or Apply Credit Memo Line API.
