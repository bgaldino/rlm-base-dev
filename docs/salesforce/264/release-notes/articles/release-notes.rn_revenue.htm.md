---
article_id: release-notes.rn_revenue.htm
title: Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_revenue.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
fetched_at: 2026-09-30
---

# Revenue Management

Learn about new features and enhancements for Agentforce Revenue Management.

Revenue Cloud is now Agentforce Revenue Management. You may see references to Revenue Cloud in our application and documentation.

Simplify Revenue Cloud Feature Discovery and Setup
With Salesforce Go, you can discover, set up, and configure Revenue Management features, all from a single location in Setup. This release adds the ability to configure high tech order orchestration from a prebuilt template for common order scenarios. Discover and configure key Billing features such as Invoice Management, Tax Calculation, Invoice Document Delivery, and Accounting Sub-Ledger for Accounts Receivables with guided setup steps, videos, and help resources.
Promotions in Revenue Management
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
Billing introduces key enhancements for flexible revenue operations such as weekly billing, new-sale ramp details, billing frequency changes during amendments, alongside catch-up bill runs and billing forecasts. Accelerate cash collections and recover bad debts by using tracking and visualization tools for collections. Expand payment capabilities and enhance payment flows by using self-service digital wallets, regional payment options, Lightning Web Runtime (LWR) Experience Cloud components, payment reconciliation, and credit balance refunds. Extend the Revenue Standard Tax Engine for custom tax rules and orchestrate the entire checkout flow with the Checkout API.
Salesforce Contracts
Improve contract governance by bringing existing business guidelines and rules into Salesforce Contracts with document playbooks. Run a risk analysis to identify deviations from your guidelines in redlined contracts. Simplify contract operations by reducing runtime user permission requirements and track recipient signing progress for document envelopes. Salesforce Contracts is now available in Government Cloud environments. Add clauses from your clause library to quotes as Quote Special Terms.
Salesforce Document Generation
Build consistent, accurate documents by using reusable clauses for Salesforce Document Generation. Clauses in the Clause Library support both merge tokens and placeholder tokens. Quote Special Terms support placeholder tokens only. Reference clauses in document templates so templates stay current as clause content changes. Rich text tables now retain their formatting in generated Word documents, including pricing tables, comparison charts, and data summaries.
Agentforce for Revenue Management
Manage approval workflows more efficiently with the Approval Agent.
Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements
Security enhancements for the Salesforce CPQ and Advanced Approvals managed packages address vulnerabilities that could affect your implementation. Review the enhancements and complete any applicable actions to keep your implementation secure and functional.
Revenue Management Release Note Changes by Month

We made these additions and changes to published release notes.

September 2026
Salesforce Contracts: Use Salesforce Contracts with Lightning Platform Licenses (Added the week of September 21, 2026)
Use Salesforce Contracts with Lightning Platform Starter or Plus licenses to reduce licensing costs.
Product Catalog Management: runtime_industries_cpq Namespace (Updated the week of September 7, 2026)
Added new classes and properties for working with a product's units of measure.
Salesforce CPQ and Advanced Approvals Managed Packages: Review and Complete Actions for Salesforce CPQ and Advanced Approvals Managed Package Security Enhancements (Added the week of August 31, 2026)
Security enhancements will be available effective September 3, 2026.
August 2026
Product Catalog Management: Reuse Existing Simple Products as Bundles (Removed the week of August 31, 2026)
This feature isn't quite ready yet, so we removed it for now.
