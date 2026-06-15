---
article_id: ind.billing_tax_configuration_engine.htm
title: Configure Tax Calculation for Invoices
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_configuration_engine.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Tax Calculation for Invoices

If you plan to use a partner app, your own engine, or calculate standard tax, create a tax engine provider and a tax engine. Then, create tax policies and treatments for each product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Determine the taxation needs for your products and implement the most appropriate solution amongst these:

Integrate Appexchange apps of partners such as Vertex or Avalara with the Billing TaxEngineAdapter Apex interface.
Integrate your own tax engine with the Billing TaxEngineAdapter Apex interface.
Calculate standard taxes based on flat rates.

This flowchart shows how users with the Billing Admin and Tax Admin permission sets can configure tax calculation for invoices in Agentforce Revenue Management.

Tax Setup Prerequisites
If you want to calculate standard taxes, calculate taxes by using your own tax engine, or by integrating the Billing TaxEngineAdapter Apex interface with a partner app, complete these prerequisites.
Configure Additional Tax Identification Details
Send additional tax identification details to your external tax engine. Meet regional tax compliance requirements by storing tax identification and exemption information on the Billing Profile and passing it to.
Extend Your Tax Interface
Enhance the existing tax interface by mapping additional fields for tax callouts. Use custom metadata types to send additional data in tax requests and persist more detailed information from tax responses.
Revenue Standard Tax Engine
Organizations often face challenges when managing taxes. Common issues include dependency on external tax vendors for simple scenarios, extra licensing and per-transaction costs, performance overhead from external API calls, and regulatory or data residency constraints. These challenges make tax management more complex and costly than necessary. The revenue standard tax engine addresses these issues by enabling internal tax calculation and storage for predictable tax structures. By handling simple tax scenarios internally, organizations can streamline their Agentforce Revenue Management processes.
/apex/HTViewHelpDoc?id=ind.Chunk745254737.htm#billing_tax_engine_and_engine_providers_create

/apex/HTViewHelpDoc?id=ind.Chunk524577630.htm#billing_tax_policies_and_treatments_create

/apex/HTViewHelpDoc?id=ind.Chunk1416918737.htm#billing_tax_address_invoice_line_override

Tax Calculation Process
Understand the tax calculation process for invoices.
