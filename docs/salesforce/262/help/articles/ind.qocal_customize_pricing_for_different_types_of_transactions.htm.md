---
article_id: ind.qocal_customize_pricing_for_different_types_of_transactions.htm
title: Pricing Customization for Different Transaction Types
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_customize_pricing_for_different_types_of_transactions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Pricing Customization for Different Transaction Types

Link custom fields to different pricing procedures to show unique prices based on the transaction type. For example, B2B customers receive volume discounts while B2C customers see standard pricing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create pricing procedures:	Salesforce Pricing Design Time User
To create Sales Transaction Type records:	Manage Agentforce Revenue Management
To create custom fields:	Customize Application
To add field-level security to profiles or permission sets:	Manage Profiles and Permission Sets
To create Flows:	Manage Flow
Before You Begin

Before you begin, create a pricing procedure and custom field for your use case. Also, create a custom field on the transaction object that your sales reps can select to trigger the pricing procedure.

Create a pricing procedure.
See Configure Your Pricing Procedure
Create a custom checkbox field and add it to the transaction object page layouts.
See Create Custom Fields.
Create a Sales Transaction Type
From the App Launcher, find and select Sales Transaction Types.
Click New.
Enter a name for your sales transaction type.
For example, B2C_Sales_Transaction
Select you new pricing procedure.
Save your changes.
Note the ID of the sales transaction type from the URL.
For example, if your URL is https://<your-instance>.force.com/lightning/r/SalesTransactionType/1ChDU000000000L0AQ/view, the ID is 1ChDU000000000L0AQ
Link the Custom Field and Sales Transaction Type With a Flow

Trigger the pricing procedure when sales reps select the custom field using a Flow.

From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click New Flow.
Select Start from Scratch and click Next.
Select Record-Triggered Flow and click Create.
Select an object. For example, you can select Quote or Order.
Select A record is created or updated for the trigger configuration.
In the Set Entry Conditions section, specify these details.
Condition Requirements: All Conditions Are Met (AND)
Field: Select the custom field that you’ve created. For example, B2C_Sales_Transaction
Operator: Equals
Value: True
Select Only when a record is updated to meet the condition requirements for the run frequency.
Select Fast Field Updates.
Add an Update Records element and map the Sales Transaction TypeID to the ID you noted earlier.
Give your flow a name and activate it.
