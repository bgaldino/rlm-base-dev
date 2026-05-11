---
article_id: ind.billing_collection_plan_payment_promise_collect.htm
title: Collect Payment Promises for a Collection Plan Item
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collection_plan_payment_promise_collect.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Collect Payment Promises for a Collection Plan Item

Record your customer's payment promises, and create payment schedules and payment schedule items for collection plan items. Collections reps can secure payments for the outstanding balance of the invoice related to the collection plan item.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To collect payment promises:	Billing Collections and Recovery Specialist permission set
To use dataraptors, integration procedures, and flexcards:	Omnistudio User permission set
To create and view payment schedules and payment schedule items:	

Payment Operations permission set

OR

Payment Admin permission set

When you click New Payment Promise on the Collect Payment Promises tab of a Collection Plan record, the Create Billing Promise to Pay flow is run. To use a customized version of this flow, save it as a new flow, make your changes, and then save and activate it.

Open the Collection Plan record that's related to the collection plan item for the invoice that you want to collect payment promises for.
From the Collect Payment Promises tab, click New Payment Promise.
The Create Billing Promise to Pay flow is run to display collection plan items that are related to the collection plan. The invoice balance value of the collection plan items is the same as the actual invoice balance value, but the currency is shown in the user's currency. To avoid confusion, change the user currency in your Salesforce org.
Select a collection plan item for which you want to create a payment schedule and payment schedule items.
Click Next.
A list of existing payment schedules that are related to the invoice of the selected collection plan item appear.
Enter the payment promise details.
Select the number of partial payments in which the customer wants to repay the overdue amount.
You can select up to three partial payments.
If the customer wants to make a single payment, in the First Part Payment Amount field, enter the total payment amount, and select a payment date.
If the customer wants to make multiple partial payments, enter the part payment amounts and select the corresponding payment date for each partial payment.
The sum of all the partial payments can be equal to or less than the invoice balance.
Select a saved payment method, click Next, and then click Finish.

The payment schedule and payment schedule items that are created for the selected collection plan item appear in the Collect Payment Promises tab. A payment batch run processes payment schedule items and applies the corresponding payments to invoices. See Payment Batch Run Overview

Instead of automatically creating payment schedules and payment schedule items for collection plan items, you can create them manually. When you manually create them, the currency ISO code of the collection plan item is used as the payment schedule's currency ISO code regardless of the currency ISO code that you choose on the New Payment Schedule page.
