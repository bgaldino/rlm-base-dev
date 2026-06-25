---
article_id: ind.collections_create_decision_table_for_payment_plan_mapping.htm
title: Create a Decision Table for Payment Plan Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_create_decision_table_for_payment_plan_mapping.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_payment_plans_for_financial_hardships.htm
fetched_at: 2026-06-21
---

# Create a Decision Table for Payment Plan Mapping

Create a decision table by using the predefined template. The decision table helps you to map payment plan types according to your customer's financial account types and debt situation. Create a CSV file with the financial account type to payment plan type mapping details. Add this CSV file to the decision table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create, edit, and activate a decision table:	Rule Engine Designer
To run decision tables:	

Rule Engine Designer

OR

Rule Engine Runtime

Here’s an example table that shows the mapping between financial account types and payment plan types. Create a CSV file based on your business requirements to detail this mapping. Then, create a decision table and add the CSV data to it.

FINANCIAL ACCOUNT TYPE

	

PAYMENT PLAN TYPE


Home Loan	Monthly Payment Plan : 6-months schedule
Home Loan	Monthly Payment Plan : 12-months schedule
Mortgage Account	Bi-weekly Payment Plan: 6 months
Mortgage Account	Monthly Payment Plan: 18 months
Credit Card	One-time lump sum payment
Credit Card	Monthly Payment Plan: 3 months
Create a decision table by using the MapPaymentPlans template.
When you create a decision table, specify these values.
Select Decision Table as the lookup table type.
Specify FAPaymentPlanMapping as the decision table name. If you plan to change this name, make sure to update the name in the prebuilt expression set template that references this decision table.
Select application usage type as Default.
Select decision table type as Advanced.
Select the MapPaymentPlans template.
Add the CSV file to the decision table that you created earlier.
Make sure that the CSV file has an input column that is named as FinancialAccountType, and the output column that is named as PaymentPlans.
Activate the decision table.
