---
article_id: ind.billing_payment_schedules_and_payment_schedule_items.htm
title: Manually Create Payment Schedules and Payment Schedule Items
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_schedules_and_payment_schedule_items.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_schedules_and_payment_schedule_items_auto_manual.htm
fetched_at: 2026-09-04
---

# Manually Create Payment Schedules and Payment Schedule Items

Instead of automatically creating payment schedules and payment schedule items, you can create them manually.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
The Salesforce Payments feature is available with the Revenue Management Billing license, with a cost per transaction model for both native and Bring Your Own payment gateways. Contact your Salesforce account executive for more information.
If you purchased the Revenue Management Billing license on or before July 2025, contact your Salesforce account executive to add the Salesforce Payments feature to your existing license.
USER PERMISSIONS NEEDED
To create payment schedules and payment schedule items:	Payment Admin permission set
Manually Create Payment Schedules

Instead of automatically creating payment schedules, you can create them manually to store the details that are used to process payments for a particular record.

From the App Launcher, find and select Payment Schedules.
Click New.
Select the reference entity and reference record that you want to process payments for.
Select a status for the payment schedule.
If you want to configure the payment schedule further, select Draft.
If the payment schedule is ready to be processed by a payment batch run, select Open.
If a payment batch run successfully processes the payment schedule, the status changes to Completed. If a payment batch run fails to process the payment schedule, the status changes to Canceled.
Select a saved payment method as the default payment method for the payment schedule.
The saved payment method is used to collect payments for all the payment schedule items that are related to the payment schedule.
You can’t specify a card payment method as the default payment method in Salesforce orgs with the Revenue Management Billing license.
Enter any additional details about the payment schedule as comments.
Enter the total amount that you want the payment schedule to process as a payment for the reference record.
Save your work.

The Payment Schedule record that’s created has the account that’s related to the reference record as the payment account.

After you create a Payment Schedule record, create payment schedule items for that record.

Manually Create Payment Schedule Items

Instead of automatically creating payment schedule items, you can create them manually. A payment schedule item represents information about a single payment to be processed for a record and can have different payment configuration values, such as payment methods, payment dates, and payment amounts.

Create one or more payment schedule items for a payment schedule based on whether you want to process payments for a record in a single or multiple installments.

From the App Launcher, find and select Payment Schedules.
Open the Payment Schedule record that you want to create payment schedule items for, and go to the Related tab.
On the Payment Schedule Items related list, click New.
Select a status for the payment schedule item.
If you want to configure the payment schedule item further, select Draft.
If the payment schedule item is ready to be processed by a payment batch run, select Ready for Processing.
When a payment batch run picks up the payment schedule item for processing, the status changes to Processing.
When a payment batch run completes collecting the amount of the payment schedule by using the merchant account, the status changes to Processed.
When a payment batch run applies the payment schedule item to an invoice or invoice line, the status changes to Applied.
When a payment batch run fails to process the payment schedule, the status changes to Failed.
When a payment batch run fails to apply the payment schedule item to an invoice or invoice line, the status changes to Apply Failed.
When the balance of the corresponding invoice is less than that of the payment schedule line, the processing of the payment schedule line fails and the status changes to Canceled.
If you haven’t selected a default payment method for the payment schedule, select a saved payment method as the default payment method.

If you’ve specified a saved payment method for the Payment Schedule record, the Payment Schedule Item record has the same value.

You can’t specify a card payment method as the default payment method in Salesforce orgs with the Revenue Management Billing license.

To group all the payment schedule items that you want to process together, select a payment run matching value.
When you schedule payment batch runs, you can select a payment run matching value to process all the payment schedule items with the same value.
Select the date on which you want the payment batch run to process the payment schedule item.
Enter the amount that must be paid for the reference record by processing the payment schedule item.
Save your work.
