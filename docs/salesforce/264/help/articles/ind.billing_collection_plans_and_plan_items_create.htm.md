---
article_id: ind.billing_collection_plans_and_plan_items_create.htm
title: Create Collection Plans and Collection Plan Items
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collection_plans_and_plan_items_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_collections.htm
fetched_at: 2026-09-04
---

# Create Collection Plans and Collection Plan Items

Create collection plans for accounts to help your collections reps track and resolve unpaid invoices. Create collection plan items for unpaid invoices that are related to the collection plan's account, enabling your collections rep to focus on the payment collection for individual invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create collection plans and collection plan items:	Billing Collections and Recovery Specialist permission set
Create Collection Plans

A collection plan stores information about the related account, the related collection plan items, the total invoice balance, and the collection timeline. It also includes the payment promises obtained by the collections reps.

You can create Collection Plan records either from the Collections app or directly from the Collection Plans page.

From the App Launcher, find and select Collection Plans.
Click New.
Select the account for which you creating the collection plan.
Select a contact of the account for which you creating the collection plan.
Select a collection plan reason.
Select the usage type as Billing.
If required, specify the due date, closed date, total tax amount, and days past due.
The days past due value isn’t calculated automatically because a collection plan can include one or more invoices with different invoice due dates. We recommend that you provide a value based on your business requirements.
The payment batch run requests payments based on the target payment processing date on the payment schedule item. So, the due date or days past due values specified in the collection plan aren't considered during the collections or payment batch run process.
Save your work.
Create Collection Plan Items

Each collection plan item stores information about the related invoice and its outstanding balance.

You can create Collection Plan Item records either from the Collection Plan Items page or from the Collection Plan records. When you create Collection Plan Item records from a Collection Plan record page, the Create Collection Plan Items For Invoices flow is run. To use a customized version of this flow, save it as a new flow, make your changes, and then save and activate it.

From the App launcher, find and select Collection Plans.
Open the Collection Plan record that you want to generate the collection plan items for.
From the Invoices tab, select the invoices that you want to create collection plan items for. You can select up to 10 invoices.

When you go to Invoices tab, the Create Collection Plan Items For Invoices flow is run to display invoices. These invoices are related to the collection plan's account, aren't fully settled, and aren't related to the existing collection plan items.

Click Create.

The collection plan items that you create appear in Collection Plan Items related list.

When you select multiple invoices, if collection plan items aren't created for a few invoices, check the Revenue Transaction Error Logs related list on those Invoice records. The Error Message field of the logs show the reason for the failure.

NOTE

On the Invoices tab, the Balance value is the same as the invoice balance, but it appears in your personal currency. For example, if the balance of an invoice is 100 Canadian dollars, it appears as US$100 if your personal currency is U.S. Dollars. To avoid this confusion, change your personal currency to the transactional currency of the invoices.
