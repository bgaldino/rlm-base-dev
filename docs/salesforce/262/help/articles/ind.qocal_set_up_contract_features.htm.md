---
article_id: ind.qocal_set_up_contract_features.htm
title: Set Up Contract Features in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_contract_features.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Contract Features in Agentforce Revenue Management

Agentforce Revenue Management offers capabilities for sales reps and partners to manage contracts. These features ensure data consistency by automatically pulling account and date details from source quotes or orders.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

Users can manually generate contracts via a dedicated button or automate the process by using flows triggered by quote status. The system supports contract-based pricing by capturing quote line prices or discounts as contract item prices. Also, the Contract Pricing Schedule component provides a visual interface for managing pricing tiers, while custom sequencing controls how volume discounts apply to transactions.

Add a New Contract Button
Help your sales reps create contracts directly from finalized records by using the New Contract button on the Quote or Order pages. This configuration streamlines the sales process by automatically copying essential details, such as the account name and start date, from the source record to the New Contract.
Add the Contract Pricing Schedule Component to Lightning Record Pages
Provide sales reps and contract managers with a simple, comprehensive interface for managing contract pricing by adding the Contract Pricing Schedule component to Contract pages. Customize the component to show only the information that your users need.
Map a Flow to Capture Quote Line Pricing on Contracts
Configure a flow to generate contracts from quotes automatically, helping sales reps to capture negotiated prices and discounts as contract item prices. This automation simplifies the contract lifecycle by giving users the choice to include quote line details or create a contract without specific pricing records.
Automate Contract Creation from Quotes and Orders
Use flows to automatically create contracts from a quote or an order. Create a flow that invokes the Create Contracts from Quote flow action when Agentforce Revenue Management quotes are changed to Accepted status. You can also add more conditions or customize the flow to perform other actions. Create contracts from orders by using a similar flow.
Configure Line Item Sequencing for Tiered Volume Discounts
Define a sequencing field to control the order in which the system applies tiered or volume contractual discounts to sales transactions.
