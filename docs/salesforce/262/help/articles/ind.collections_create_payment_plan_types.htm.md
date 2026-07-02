---
article_id: ind.collections_create_payment_plan_types.htm
title: Define Payment Plan Types to Create Payment Plans
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_payment_plan_types.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_payment_plans_for_financial_hardships.htm
fetched_at: 2026-06-21
---

# Define Payment Plan Types to Create Payment Plans

To help customers meet their payment commitments during financial hardship, it’s important to offer flexible payment options tailored to their financial account types and debt situations. To facilitate this, create payment schedule distribution methods, and the corresponding payment schedule treatment records, and payment schedule treatment detail records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create payment schedule distribution method records, payment schedule treatment records, and payment schedule treatment detail records:	Collections and Recovery Admin permission set

Create different payment plan types by defining payment schedule distribution methods. For example, you can offer a Weekly Payment Plan: 12-months schedule, or a Monthly Payment Plan: 12-months schedule. A payment schedule treatment contains a lookup to a distribution method. After you set up these payment schedule distribution methods, you must also create the corresponding payment schedule treatment and payment schedule treatment detail records.

To create payment schedule distribution method record, follow these steps. Repeat these steps to create payment schedule distribution method records for each payment plan type you intend to define.
From the App Launcher, find and select Payment Schedule Distribution Methods, and click New.
Enter the distribution method name. For example, Weekly Payment Plan: 12-months schedule.
Select a distribution method type. For example, if you plan to define a weekly payment plan, then select the distribution method type as Weekly.
Enter the distribution count, which indicates the total number of payments to be made. For example, if you plan to define a Weekly Payment Plan: 12-months schedule, then enter the distribution count as 52.
Specify the description and save your changes.
To create payment schedule treatment record, follow these steps. Repeat these steps to create payment schedule treatment records for each payment schedule distribution method that you have created earlier.
From the App Launcher, find and select Payment Schedule Treatments, and click New.
Enter a name. For example, Weekly Payment Plan: 12-months schedule.
Select Draft as the payment schedule treatment status.
Select User Action as the payment trigger source.
Specify a description.
To guide the user in selecting the most suitable payment plan, specify a payment plan tag. For example, requires approval or recommended.
Select Approval Required if the payment plan type you define needs approval from senior management.
If a payment schedule treatment record requires approval, make sure that you set up a payment approval process. If a payment requires approval‌, the payment schedule status and the corresponding payment schedule item status are automatically set to Approval Pending. After the payment is approved, make sure that the approval process updates the payment schedule status to Accepted and the corresponding payment schedule item status to Processing.
Save your changes.
To create payment schedule treatment details record, follow these steps. Repeat these steps to create payment schedule treatment detail records for each payment schedule treatment record that you created earlier.
From the App Launcher, find and select Payment Schedule Treatment Details, and click New.
Select the payment schedule distribution method to which you want to link this payment schedule treatment detail record. For example, Weekly Payment Plan: 12-months schedule.
Select the payment schedule treatment record to which you want to link this payment schedule treatment detail record. For example, Weekly Payment Plan: 12-months schedule.
Specify the description.
Select Percentage as the installment payment type.
For Percentage, enter 100.
Select User Input Date as the processing date reference.
Enter the date offset as 0.
Select the payment method selection type.
Save your changes.
To activate a payment schedule treatment record, follow these steps. Repeat these steps for each payment schedule treatment record that you created earlier.
From the App Launcher, find and select Payment Schedule Treatments.
Open a payment schedule treatment record that you created earlier.
Select Active as the payment schedule treatment status.
Save your changes.
