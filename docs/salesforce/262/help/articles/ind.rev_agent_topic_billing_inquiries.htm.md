---
article_id: ind.rev_agent_topic_billing_inquiries.htm
title: "Subagent: Billing Inquiries"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_topic_billing_inquiries.htm&type=5&release=262
release: 262
release_name: Summer '26
area: agents
fetched_at: 2026-05-12
---

# Subagent: Billing Inquiries

Use Agentforce to help internal teams quickly access and understand key billing information. The Billing Inquiries subagent answers questions about account balances, payment plans, upcoming payment dates, invoice details, and downloadable invoice documents. Users can ask about an account or a specific invoice, and the agent automatically identifies the right billing flow to run. The subagent consolidates information from Agentforce Revenue Management Billing so teams can resolve billing questions efficiently and confidently.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license and Agentforce Revenue Management Billing license with the Agentforce Employee Agent add-on. It requires the Einstein GPT, the Agentforce Service Agent add-on, the Flex Credits Metering add-on, and the Usage Management add-on.
Topic Details
API Name	BillingInquiries
Included actions	

Get Account Balance

Retrieve Next Due Payment

Generate Payment Plan Details

Get Invoice Document PDF


Required Setup	Set Up Agentforce for Revenue Management
Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTIONS ENGAGED	AGENT RESPONSE
“How much do I currently owe?”	Get Account Balance	The agent summarizes the net amount due across outstanding invoices, including debit memos, credit memos, payments, and refunds.
“Can you tell me the current account balance for my account?”	Get Account Balance	The agent retrieves posted invoices, credits, debits, payments, and refunds to summarize the outstanding balance for the requested account.
“When is my next payment due?”	Retrieve Next Due Payment	The agent identifies the earliest upcoming due date and the due amount for one or more invoices.
“What is the next payment for account ABC Corp?”	Retrieve Next Due Payment	The agent returns the next due amount and date for that account.
“Can you get me the payment plan for my invoice?”	Generate Payment Plan Details	The agent returns payment installment amounts, dates, and statuses for the specified invoice.
“Get the payment plan for invoice DOC-12345.”	Generate Payment Plan Details	The agent reads the invoice details and returns the full payment schedule.
“Can you show me my latest bill?”	Get Invoice Document PDF	The agent retrieves the most recent posted invoice and provides a downloadable PDF link.
“Download the latest invoice for this account.”	Get Invoice Document PDF	The agent fetches the latest invoice and provides the file link in Markdown format.
