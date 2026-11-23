---
article_id: release-notes.rn_revenue.htm
title: Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_revenue.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
fetched_at: 2026-11-23
---

# Revenue Cloud

Learn about new features and enhancements for Revenue Cloud.

Simplify Revenue Cloud Feature Discovery and Setup
With Salesforce Go, you can discover, set up, and configure Revenue Cloud features, all from a single location in Setup. This release adds the ability to configure high tech order orchestration from a prebuilt template for common order scenarios. Discover and configure key Billing features such as Invoice Management, Tax Calculation, Invoice Document Delivery, and Accounting Sub-Ledger for Accounts Receivables with guided setup steps, videos, and help resources.
Revenue Cloud Accelerators
Start with prebuilt foundations and sample usage data. Create quotes with less data entry, and manage quote documents and e-signatures from Salesforce. Check orders before activation, and connect fulfillment to Field Service without building every process from scratch.
Promotions in Revenue Cloud
Pricing designers can set up promotions that users apply to transactions. Developers can use objects and APIs to manage promotions on sales transactions.
Large Transactions and Quote Processing
Process quotes and orders with up to 15,000 line items without timeouts or performance bottlenecks. Asynchronous processing keeps sales reps and billing teams working while calculations, synchronization, and document generation run in the background. Configure products, apply pricing rules, and generate documents for complex transactions with thousands of lines, nested bundles, and multilevel grouping.
Product Catalog Management
Set attribute display orders across levels to guide reps through configurations, and easily convert simple products into bundles without creating records. Replace the generic cog icon with a clear text button, and hide the Add button to prevent incorrect selections. Automate cache invalidation to maintain accurate product details, and cache list prices for instant updates. Quickly locate items by typing any part of a Product Name, Product Code, or Product SKU by using prefix and partial search.
Salesforce Pricing
Apply compounding uplifts to ramp deal segments, scale your pricing logic with pricing recipes and procedures for each cloud, and reusable list variables. Set weekly as a proration frequency, and get standard decimal notation in pricing API responses.
Product Configurator
Prevent Constraint Rules Engine from altering specified attributes or relations when it satisfies a constraint. Calculate the quantity of child products per instance of the parent product, rather than the quantity of child products across all bundles.
Transaction Management
Improve flexibility and productivity when managing quotes, orders, and asset lifecycle changes. Configure procedure plans for specific industries, backdate asset transactions, maintain time zone accuracy throughout the asset lifecycle, and update prices through price amendments. Work more efficiently in Sales Transaction Line Editor with enhanced filtering, automatic refresh, and configurable action buttons. Tailor transaction pages with Dynamic Forms.
Ramp Deals
Enhance pricing accuracy and billing flexibility for multiyear ramp deals. Apply compound price uplifts to match enterprise escalation patterns, and backdate amendments, renewals, and cancellations to correct billing for past periods.
Advanced Approvals
Reach every active member of an assigned group or queue in Slack through direct messages or channels. Keep approvals moving during planned absences with Advanced Approval Delegation. Protect sensitive approval work items in multistep approvals with separate sharing settings that limit reviewer visibility.
Dynamic Revenue Orchestrator
Orchestrate ramp deals. Submit amendments, renewals, and cancellations, and roll them back before they take effect. Keep actions, quantities, and dates accurate by using time-aware assets. Fulfill ramped asset amendments, apply staged assetization to ramped segments, sequence multiyear orchestration steps by time period, and align dependencies among fulfillment steps by using custom fulfillment scopes. Speed up design by cloning fulfillment workspaces, and gain visibility into multiyear orders with the enhanced Decomposition Viewer.
Usage Management
Renew usage subscriptions at the right time to keep pace with your customers' changing needs. Start renewals early when the business expands, or restore a service after expiration to win back customers. Adjust rates and grant quantities for both standard and ramped pricing schedules while maintaining asset continuity.
Billing
Billing introduces key enhancements for flexible revenue operations such as weekly billing, new-sale ramp details, billing frequency changes during amendments, alongside catch-up bill runs and billing forecasts. Accelerate cash collections and recover bad debts by using tracking and visualization tools for collections. Expand payment capabilities and enhance payment flows by using self-service digital wallets, regional payment options, Lightning Web Runtime (LWR) and Aura Experience Cloud components, payment reconciliation, credit balance refunds, and undo refund line application. Extend the Revenue Standard Tax Engine for custom tax rules and orchestrate the entire checkout flow with the Checkout API. Recover failed transaction journals from the JSON payload on Revenue Transaction Error Log records by executing a custom Apex class.
Salesforce Contracts
Improve contract governance by bringing existing business guidelines and rules into Salesforce Contracts with document playbooks. Run a risk analysis to identify deviations from your guidelines in redlined contracts. Simplify contract operations by reducing runtime user permission requirements and track recipient signing progress for document envelopes. Add clauses from your clause library to quotes as Quote Special Terms.
Salesforce Document Generation
Build consistent, accurate documents by using reusable clauses for Salesforce Document Generation. Clauses in the Clause Library support both merge tokens and placeholder tokens. Quote Special Terms support placeholder tokens only. Reference clauses in document templates so templates stay current as clause content changes. Rich text tables now retain their formatting in generated Word documents, including pricing tables, comparison charts, and data summaries.
Agentforce for Revenue Cloud
Manage approval workflows more efficiently with the Approval Agent.
Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements
Security enhancements for the Salesforce CPQ and Advanced Approvals managed packages address vulnerabilities that could affect your implementation. Review the enhancements and complete any applicable actions to keep your implementation secure and functional.
Revenue Cloud Release Note Changes by Month

We made these additions and changes to published release notes.

November 2026
Billing: Undo Refund Line Applications with Unapply Support (Added the week of November 9, 2026)
Billing: Recover Failed Transaction Journals Using Payload from Revenue Transaction Error Logs (Added the week of November 9, 2026)
Dynamic Revenue Orchestrator: Optimize License Spend with Read-Only Access to Dynamic Revenue Orchestrator (Added the week of November 9, 2026)
Salesforce Go Accelerators for Revenue Cloud: Keep Quote Approvals Moving with Automated Workflows (Added the week of Nov 2, 2026)
Salesforce Contracts: Author Contracts in Government Cloud (Removed the week of November 2, 2026)
This isn't available in Government Cloud yet, so we removed it for now.
October 2026
Billing: New Invocable Action in Billing (Updated the week of October 26, 2026)
Removed the asynchronous processing details for billing schedule creation actions because the feature isn’t publicly available yet.
Set Up Revenue Cloud with AI Agents: : Set Up Revenue Cloud in Minutes with an AI Agent (Beta) (Removed the week of October 26, 2026)
This feature isn't quite ready yet, so we removed it for now.
Set Up Revenue Cloud with AI Agents: Build a Revenue Cloud Product Catalog Just by Describing It to an AI Agent (Beta) (Removed the week of October 26, 2026)
This feature isn't quite ready yet, so we removed it for now.
Set Up Revenue Cloud with AI Agents: Set Up Revenue Cloud Pricing in Plain Language with an AI Agent (Beta) (Removed the week of October 26, 2026)
This feature isn't quite ready yet, so we removed it for now.
Set Up Revenue Cloud with AI Agents: Set Up Product Configuration Rules Conversationally with an AI Agent (Beta) (Removed the week of October 26, 2026)
This feature isn't quite ready yet, so we removed it for now.
Set Up Revenue Cloud with AI Agents: Protect Margins by Routing Discount Approvals on Quotes with an AI Agent (Beta) (Removed the week of October 26, 2026)
This feature isn't quite ready yet, so we removed it for now.
Salesforce Go Accelerators for Revenue Cloud: Revenue Cloud Accelerators (Added the week of October 12, 2026)
Billing: Automate Billing Schedule Reconciliations for Early Renewals of Future-Dated Orders (Added the week of October 12, 2026)
Billing: See Product Charges Together on an Invoice (Added the week of October 12, 2026)
Billing: Manage Saved Payment Methods in Aura Experience Sites (Added the week of October 12, 2026)
Large Transactions: Clone Large Quotes and Orders (Updated the week of October 5, 2026)
Product Configurator: Let Constraint Rules Assign Child Product Quantities in Bundles (Removed the week of October 5, 2026)
Transaction Management: Generate Documents for Quotes via CLM (Updated the week of October 5, 2026)
Transaction Management: Stack Renewals on Termed Assets with an Active Future-Dated Renewal (Updated the week of October 5, 2026)
Set Up Revenue Cloud with AI Agents: Set Up Revenue Cloud in Minutes with an AI Agent (Beta) (Added the week of October 5, 2026)
Set Up Revenue Cloud with AI Agents: Build a Revenue Cloud Product Catalog Just by Describing It to an AI Agent (Beta) (Added the week of October 5, 2026)
Set Up Revenue Cloud with AI Agents: Set Up Revenue Cloud Pricing in Plain Language with an AI Agent (Beta) (Added the week of October 5, 2026)
Set Up Revenue Cloud with AI Agents: Set Up Product Configuration Rules Conversationally with an AI Agent (Beta) (Added the week of October 5, 2026)
Set Up Revenue Cloud with AI Agents: Protect Margins by Routing Discount Approvals on Quotes with an AI Agent (Beta) (Added the week of October 5, 2026)
Salesforce Go for Revenue Cloud: Launch the Revenue Cloud Solution for Subscription Selling (Updated the week of September 29, 2026)
Product Catalog Management: Reuse Existing Simple Products as Bundles (Added the week of September 29, 2026)
September 2026
Salesforce Document Generation: Handle Document Generation Timeouts with Configurable Retry (Added the week of September 28, 2026)
Salesforce Contracts: Use Salesforce Contracts with Lightning Platform Licenses (Added the week of September 21, 2026)
Product Catalog Management: runtime_industries_cpq Namespace (Updated the week of September 7, 2026)
Added new classes and properties for working with a product's units of measure.
Salesforce CPQ and Advanced Approvals Managed Packages: Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements (Added the week of August 31, 2026)
Security enhancements will be available effective September 3, 2026.
August 2026
Product Catalog Management: Reuse Existing Simple Products as Bundles (Removed the week of August 31, 2026)
This feature isn't quite ready yet, so we removed it for now.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_revenue.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
