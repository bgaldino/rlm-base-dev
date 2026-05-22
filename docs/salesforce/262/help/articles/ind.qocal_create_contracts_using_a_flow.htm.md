---
article_id: ind.qocal_create_contracts_using_a_flow.htm
title: Automate Contract Creation from Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_contracts_using_a_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Automate Contract Creation from Quotes and Orders

Use flows to automatically create contracts from a quote or an order. Create a flow that invokes the Create Contracts from Quote flow action when Agentforce Revenue Management quotes are changed to Accepted status. You can also add more conditions or customize the flow to perform other actions. Create contracts from orders by using a similar flow.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To open, edit, or create a flow in Flow Builder:	Manage Flow
From Setup, in the Quick Find box, enter Flows, and then select Flows.
Click New Flow.
Select Start from Scratch and click Next.
Select Record-Triggered Flow and click Create.
Select Quote or Order as the object.
Select A record is updated for the trigger configuration.
In the Set Entry Conditions section, specify these values.
Condition Requirements: All Conditions Are Met (AND)
Field: Status
Operator: Equals
Value: Accepted
Save your changes, and name your flow.
Click , search for and select Action.
In New Action, filter by Category, and select Revenue Cloud.
Click the Action search option and select Create Contract.
Add the Label and Source ID from the previous action, either Quote or Order object ({!$Record__Prior.Id}).
Save your changes.

After you complete the flow setup, add the Contract field to the Quote Details Page and the Order Details Page layouts to help users to view the linked contract record.

SEE ALSO
Automate Asset Creation from Orders by Using Flows
