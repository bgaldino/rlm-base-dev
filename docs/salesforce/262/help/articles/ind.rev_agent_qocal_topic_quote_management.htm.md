---
article_id: ind.rev_agent_qocal_topic_quote_management.htm
title: "Subagent: Quote Management"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_qocal_topic_quote_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: agents
fetched_at: 2026-05-12
---

# Subagent: Quote Management

Create and modify quotes and their quote line items in Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license with the Agentforce Employee Agent add-on.
Topic Details
API Name	quoteManagement
Included Revenue Actions	

Add Quote Line Item to Quote

Apply Discount To Quote Line Item

Create Amendment Quote

Create Initial Quote

Create Renewal Quote

Get Account Assets

Get Product Selling Model for Products

Query Quote Line Items (Beta)

Update Quote Details

Update Quote Line Item Details


Included Agentforce Platform Actions	

Get Record Details

Identify Object by Name

Identify Record by Name

Query Records

Summarize Record

Update Record


Required Setup	Set Up Agentforce for Revenue Management
Considerations
The agent is available to authenticated users in Lightning Experience. Customers and partners who use Experience Cloud don’t yet have access to external digital agents.
The agent supports only one currency in quotes. To provide support for multiple currencies, modify the Add QuoteLineItem to Quote flow to check if the Currency ISO Code field is available on the product record. See Set Up Agentforce for Revenue Management.
You can modify up to 10 quote line items at a time in an agent request. For example, you can create a quote with 10 quote line items, add 10 quote line items to an existing quote, or apply a discount on 10 quote line items in a single request.
Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTIONS ENGAGED	AGENT RESPONSE
“Add three units of QuantumBit Gold Platform to the Cloud Kicks Technology quote.”	
Identify Record By Name
Get Product Selling Model for Products
Add Quote Line Item to Quote
	The agent retrieves the default product selling model for QuantumBit Gold Platform and then confirms with the user if it can add the product to the Cloud Kicks Technology quote. After adding the product, the agent shares the link to the updated quote for the user to view or modify manually.
“Apply a discount to API Access so it’s sold at 60% of list price.”	
Identify Record By Name
Query Quote Line Items (Beta)
Apply Discount to Quote Line Item
	The agent calculates the discount percentage or amount for the product to be sold at 60% of list price and then updates the price fields.
“Create an amendment quote for Acme for both Laptop Bag and Mouse starting on 5/12 for -1 unit?”	
Identify Record By Name
Create Amendment Quote
	The agent creates an amendment quote for Acme with the updated product details, reducing their quantity by one and modifying their start date to 5/12.
“Update the quote status under Acme to Accepted.”	
Identify Record By Name
Update Quote Details
	The agent updates the status of the quote associated with Acme to Accepted.
“Sync Acme quote to its opportunity.”	
Get Record Details
Update Record Fields
	The agent syncs the Acme quote to its related opportunity.
“Unsync Acme quote to its opportunity.”	
Get Record Details
Update Record Fields
	The agent stops syncing the Acme quote to its related opportunity.
