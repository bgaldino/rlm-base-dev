---
article_id: ind.rev_agent_topic_billing_collections_management.htm
title: "Subagent: Billing Collections Management"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_topic_billing_collections_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: agents
fetched_at: 2026-05-12
---

# Subagent: Billing Collections Management

Use Agentforce to help teams quickly assess and act on customer account health. The Billing Collections Management subagent provides an at-a-glance view of financial standing, highlighting high-risk invoices based on payment history, disputes, and outstanding balances, along with recommended next actions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance,Unlimited, and Developer Editions of Agentforce Revenue Management Advanced license and Agentforce Revenue Management Billing license with the Agentforce Employee Agent add-on.
Subagent Details
API Name	BillingCollections
Included actions	

Get Account Billing Summary

Get Dunning Strategy


Required Setup	

Billing Collections

AND

Recovery Specialist

Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTION ENGAGED	AGENT RESPONSE
"What is the billing health summary for the Acme account?"	Get Account Billing Summary	The agent summarizes the outstanding balances, high-risk invoice counts, and historical payment trends.
"Give me a summary for high-risk invoices, late payment history, and open disputes for Acme account"	Get Account Billing Summary	The agent summarizes the account’s high-risk invoice counts, open disputes, and historical payment trends.
"What dunning strategy should I use for collection plan #CP-101?"	Get Dunning Strategy	The agent analyzes the collection plan along with prior customer communications, payment history, and open disputes to recommend the most effective dunning strategy to expedite payment recovery.
"Based on the high-risk score for this account, what is the recommended engagement strategy?"	Get Dunning Strategy	The agent evaluates the risk profile and suggests the most effective dunning orchestration to expedite payment recovery.
SEE ALSO
Manage Collections for Accounts in Billing
